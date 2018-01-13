import os
import requests
import config
import time
import json
from datetime import datetime
from dateutil import parser

from flask import Flask, render_template

application = Flask(__name__)


@application.route('/')
def hello_world():
    t_data = get_stats()
    print(t_data)
    last_streamed = ago(datetime.strptime(t_data['created_at'], '%Y-%m-%dT%H:%M:%SZ'))
    return render_template('home.html', twitch_data=t_data, last_streamed=last_streamed)


def get_stats():
    if not cache_valid():
        fetch_stats()
    return get_cache()


def fetch_stats():
    r = requests.get(config.TWITCH_GET_CHANNEL_ENDPOINT % config.TWITCH_USER_ID, headers={
        'Client-ID': config.TWITCH_API_CLIENT,
        'Accept': 'application/vnd.twitchtv.v5+json'
    })
    set_cache(r.json())


def cache_valid():
    return not (not os.path.exists(config.CACHE_FILE) or ((time.time() - os.path.getmtime(config.CACHE_FILE)) > config.CACHE_TIMEOUT))


def get_cache():
    pjson = ''
    with open(config.CACHE_FILE, 'r') as f:
        pjson = f.read()
        f.close()
    return json.loads(pjson)


def set_cache(data):
    with open(config.CACHE_FILE, 'w+') as f:
        f.truncate(0)
        f.seek(0)
        f.write(json.dumps(data))
        f.flush()
        f.close()


def ago(t):
    """
        Calculate a '3 hours ago' type string from a python datetime.
    """
    units = {
        'years': lambda diff: diff.days / 356,
    }
    diff = datetime.now() - t
    for unit in units:
        dur = units[unit](diff) # Run the lambda function to get a duration
        if dur > 0:
            unit = unit[:-dur] if dur == 1 else unit # De-pluralize if duration is 1 ('1 day' vs '2 days')
            return '%s %s' % (round(dur, 1), unit)
    return 'just now'


if __name__ == '__main__':
    application.run(port=5001)
