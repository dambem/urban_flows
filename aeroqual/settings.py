import pathlib

DEFAULT_CONFIG_FILE = pathlib.Path.home().joinpath('configs', 'aeroqual.cfg')

LOGGING = dict(
    # https://docs.python.org/3.8/library/logging.html#logrecord-attributes
    format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s',
)

DEFAULT_AVERAGING_PERIOD = 1

TIME_ZONE_MAP = {
    "(UTC+00:00) Dublin, Edinburgh, Lisbon, London": "Europe/London",
}

RENAME_COLUMNS = {
    'Time': 'timestamp',
    'NO2': 'AQ_NO2',
    'O3': 'AQ_O3',
    'PM2.5': 'AQ_PM25',
    'TEMP': 'MET_TEMP',
    'RH': 'MET_RH',
    'DP': 'DEW_POINT',
    'Ox': 'AQ_OX'  # OX = O3 + NO2
}

IGNORE_METRICS = {
    'O3 raw',
    'PM2.5 raw',
}

# Metadata assets
DESC_URL = 'https://cloud.aeroqual.com'
FAMILY = 'Aeroqual'
