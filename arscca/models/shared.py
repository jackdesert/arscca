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
