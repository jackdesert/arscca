import re
import redis


class Shared:

    # Note: arscca.test.msreg_test defines its own redis on localhost
    REDIS = redis.StrictRedis(
        host='arscca-redis',
        port=6379,
        db=1,
        socket_connect_timeout=5,
        decode_responses=True,
    )

    REDIS_KEY_LIVE_EVENT = 'live-event'
    REDIS_KEY_LIVE_EVENT_DRIVERS = 'live-event-drivers'
    REDIS_KEY_LIVE_EVENT_REVISION = 'live-event-revision'
    REDIS_KEY_LIVE_EVENT_RUN_GROUPS = 'live-event-run-groups'
    REDIS_KEY_S3_PHOTOS = 's3-photos'
    REDIS_KEY_BARCODES = 'barcodes'
    REDIS_KEY_BARCODE_FILENAME = 'barcode-filename'

    NOT_JUST_WHITESPACE_REGEX = re.compile(r'[^\s]')

    CORS_DOMAINS = frozenset(['http://arscca.org'])

    MSREG_RAW_PATH = '/tmp/msreg_raw.txt'
    MSREG_AUGMENTED_PATH = '/tmp/msreg_augmented.txt'

    # Match any of the following and it is detected as Rallycross
    # - A car class called #SA (stock all wheel drive) (this was included 2021 and later)
    # - A bit of html that says "RallyX Mode" (this was included previous to 2021)
    # - Put "RallyX" in the title, which will either show up in the html <title> or in a th with align=center.
    RALLYX_REGEX = re.compile(r'(\*\* RallyX Mode )|( href="#SA">)|(<title>.*RallyX.*</title>)|(align=center>[^<]*RallyX.*?<)')
    ASPHALT_RALLY_REGEX = re.compile(r'cumulative-scoring')

    PAX_STRING = 'PAX'
    # Normally I would not use a space in a dictionary key,
    # but it does make the report prettier
    NOVICE_PAX_STRING = 'NOVICE PAX'
