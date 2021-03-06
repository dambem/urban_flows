import pathlib

# Authentication token
DEFAULT_TOKEN_PATH = pathlib.Path.home().joinpath('configs', 'awesome_token.txt')

# Log config
LOGGING = dict(
    format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s",
)

# The maximum number of readings to upload at once to /api/reading/bulk. The limit is 100.
BULK_READINGS_CHUNK_SIZE = 100

DEFAULT_READING_TYPE_GROUPS_FILE = 'reading_type_groups.json'
DEFAULT_AQI_STANDARDS_FILE = 'aqi-standards.json'

BASE_URL = 'http://ufportal.shef.ac.uk/api/'
