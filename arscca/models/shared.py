import re
import redis

class Shared:
    REDIS = redis.StrictRedis(host='arscca-redis', port=6379, db=1, decode_responses=True)


    REDIS_KEY_LIVE_EVENT          = 'live-event'
    REDIS_KEY_LIVE_EVENT_DRIVERS  = 'live-event-drivers'
    REDIS_KEY_LIVE_EVENT_REVISION = 'live-event-revision'
    REDIS_KEY_LIVE_EVENT_RUN_GROUPS = 'live-event-run-groups'
    REDIS_KEY_S3_PHOTOS = 's3-photos'

    NOT_JUST_WHITESPACE_REGEX = re.compile('[^\s]')

