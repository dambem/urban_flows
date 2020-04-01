import argparse
import datetime
import logging

import pandas

import http_session
import parsers
import mappings
import settings
import utils
from utils import build_path

DESCRIPTION = """
This is a harvester to retrieve data from the DEFRA UK-AIR
[Sensor Observation Service](https://uk-air.defra.gov.uk/data/about_sos) via their API using the key-value pair (KVP)
binding.
"""

USAGE = """
python . --date 2020-01-01
"""

LOGGER = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--date', type=utils.parse_date, required=True, help="YY-MM-DD")
    parser.add_argument('-s', '--sep', type=str, default='|', help="Output CSV separator")

    args = parser.parse_args()

    return args


def download_data(session, date: datetime.date):
    data = session.get_observation_date(date=date)

    path = build_path(date=date, ext='xml', sub_dir='raw')

    # Serialise
    with open(path, 'w') as file:
        file.write(data)

        LOGGER.info("Wrote '%s'", file.name)

    return data


def get_data(session, date: datetime.date) -> iter:
    """
    :rtype: iter[dict]
    """
    data = download_data(session=session, date=date)

    parser = parsers.AirQualityParser(data)

    LOGGER.info("Feature Collection ID: %s", parser.id)

    # Iterate over observations
    for observation in parser.observations:

        for row in observation.result.iter_values():
            row['station'] = observation.station
            row['sampling_point'] = observation.sampling_point
            row['observed_property'] = observation.observed_property
            row['unit_of_measurement'] = observation.result.unit_of_measurement

            yield row


def validate(row: pandas.Series) -> bool:
    # Verified: http://dd.eionet.europa.eu/vocabulary/aq/observationverification
    if row['verification'] not in {1, 2}:
        return False

    # Validity http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity
    if row['validity'] < 0:
        return False

    return True


def parse(df: pandas.DataFrame) -> pandas.DataFrame:
    """Parse data types"""

    df['timestamp'] = pandas.to_datetime(df['timestamp'])

    data_types = dict(
        validity='int8',
        verification='uint8',
        value='float',
        sampling_point='category',
        observed_property='category',
        unit_of_measurement='category',
    )
    df = df.astype(data_types)

    return df


def transform(df: pandas.DataFrame) -> pandas.DataFrame:
    n_rows = len(df.index)

    # Filter selected stations
    df = df[df['station'].isin(settings.STATIONS)].copy()
    LOGGER.info("Removed %s invalid/unverified rows", n_rows - len(df.index))
    n_rows = len(df.index)

    # Map to UFO values
    df['unit_of_measurement'] = df['unit_of_measurement'].map(mappings.UNIT_MAP)
    df['observed_property'] = df['observed_property'].map(mappings.OBSERVED_PROPERTY_MAP)

    # Remove unnecessary column
    del df['StartTime']

    # Rename columns
    df = df.rename(columns={'EndTime': 'timestamp'})
    df = df.rename(columns=str.casefold)

    df = parse(df)

    # Validate
    df = df[df.apply(validate, axis=1)].copy()
    LOGGER.info("Removed %s invalid/unverified rows", n_rows - len(df.index))

    # Get station ID from station URL
    # e.g. "http://environment.data.gov.uk/air-quality/so/GB_Station_GB0037R" becomes "GB_Station_GB0037R"
    df['station'] = df['station'].apply(lambda s: s.rpartition('/')[2])

    # Output timestamp in ISO 8601
    df['timestamp'] = df['timestamp'].apply(lambda t: t.isoformat())

    # Aggregate
    df = df.groupby(['timestamp', 'station', 'observed_property', 'unit_of_measurement'])['value'].sum()

    # One column per metric
    df = df.unstack(['observed_property', 'unit_of_measurement'])

    # Zip headers into a 1D index (not MultiIndex)
    df.columns = df.columns.map('__'.join)

    return df


def serialise(df: pandas.DataFrame, path, **kwargs):
    df.to_csv(path, **kwargs)

    LOGGER.info("Wrote '%s' (%s rows)", path, len(df.index))


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Retrieve raw data
    session = http_session.SensorSession()
    rows = get_data(session, args.date)
    df = pandas.DataFrame.from_dict(rows)

    LOGGER.info("Retrieved %s rows", len(df.index))

    # Clean data
    df = transform(df)

    path = build_path(date=args.date, ext='csv', sub_dir='todb')
    serialise(df, path=path, sep=args.sep)


if __name__ == '__main__':
    main()
