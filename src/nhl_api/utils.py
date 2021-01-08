from datetime import datetime, timezone
import nhl_api.object
import json


def convert_time(utc_dt):
    local_dt = datetime.strptime(
        utc_dt, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).astimezone(tz=None)
    return local_dt



