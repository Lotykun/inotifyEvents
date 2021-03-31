# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import inotify.adapters
import sqlite3
import requests
import json
import yaml
from datetime import datetime, date, time, timedelta


def get_config():
    config_file = "conf.yml"
    with open(config_file) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def token(username, password):
    url = "http://symfonyneo4j.com/api/token"
    headers = {
        'content-type': 'application/json',
    }
    payload = {
        'email': username,
        'password': password
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    response_data = r.json()
    if 'code' in response_data:
        return response_data['message']
    else:
        return response_data['apiToken']


def post_create_video(token, json_data):
    url = "http://symfonyneo4j.com/api/videos/create?XDEBUG_SESSION_START=PHPSTORM"
    headers = {
        'content-type': 'application/json',
        'X-AUTH-TOKEN': token,
    }
    r = requests.post(url, data=json.dumps(json_data), headers=headers)
    return r


def post_create_strip(token, video_id):
    url = "http://symfonyneo4j.com/api/strips/create/" + video_id + "?XDEBUG_SESSION_START=PHPSTORM"
    headers = {
        'content-type': 'application/json',
        'X-AUTH-TOKEN': token,
    }
    r = requests.post(url, headers=headers)
    return r


def _main(configuration):
    i = inotify.adapters.Inotify()

    i.add_watch('/tmp/')

    with open('/tmp/test_file', 'w'):
        pass

    for event in i.event_gen(yield_nones=False):
        date_time_obj = datetime.now()
        new_date = date_time_obj - timedelta(seconds=10)
        current_timestamp = int(date_time_obj.timestamp())
        reference_timestamp_new = int(new_date.timestamp())
        # timestamp_str = date_time_obj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        # timestamp_new = new_date.strftime("%d-%b-%Y (%H:%M:%S.%f)")

        (_, type_names, path, filename) = event

        print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(path, filename, type_names))
        con_bd = sqlite3.connect('files.db')
        cursor = con_bd.cursor()
        cursor.execute("SELECT * FROM DETAILS d "
                       "WHERE d.'PATH' LIKE '" + configuration['dbPath'] + "' "
                       "AND d.'TIMESTAMP' > " + str(reference_timestamp_new) + 
                       "AND d.'SIZE' IS NOT NULL")
        
        for registry in cursor:
            registry_dict = {
                'data': {
                    'ID': registry[0],
                    'PATH': registry[1],
                    'SIZE': registry[2],
                    'TIMESTAMP': registry[3],
                    'TITLE': registry[4],
                    'DURATION': registry[5],
                    'BITRATE': registry[6],
                    'SAMPLERATE': registry[7],
                    'CREATOR': registry[8],
                    'ARTIST': registry[9],
                    'ALBUM': registry[10],
                    'GENRE': registry[11],
                    'COMMENT': registry[12],
                    'CHANNELS': registry[13],
                    'DISC': registry[14],
                    'TRACK': registry[15],
                    'DATE': registry[16],
                    'RESOLUTION': registry[17],
                    'THUMBNAIL': registry[18],
                    'ALBUM_ART': registry[19],
                    'ROTATION': registry[20],
                    'DLNA_PN': registry[21],
                    'MIME': registry[22],
                }
            }
            print(registry)
            if registry_dict['TITLE'] == filename:
                token_data = token(configuration['username'], configuration['password'])
                video_create_response = post_create_video(token=token_data, json_data=registry_dict)
                if video_create_response.status_code == requests.codes.ok:
                    content = video_create_response.json()
                    strip_create_response = post_create_strip(token=token_data, video_id=content['id'])
                    if strip_create_response.status_code == requests.codes.ok:
                        print('ok')
                    else:
                        content = strip_create_response.json()
                        print('Error creating Strip for Video Code: ' + str(strip_create_response.status_code) + ' ' +
                              content['message'])
                else:
                    content = video_create_response.json()
                    print(
                        'Error creating Video Code: ' + str(video_create_response.status_code) + ' '
                        + content['message']
                    )


if __name__ == '__main__':
    config = get_config()
    _main(configuration=config)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
