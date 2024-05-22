import datetime
import platform
import os


def timestampsToTime(timestamps, timestamp0):
    time = []
    for i in range(len(timestamps)):
        time.append((datetime.datetime.fromisoformat(timestamps[i]) -
                     datetime.datetime.fromisoformat(timestamp0)).total_seconds())

    return time


# TODO do usuniecia???
def getUserPath():
    if platform.system() == 'Windows':
        path = os.path.expanduser('~user')

    elif platform.system() in ('Linux', 'Darwin'):
        path = os.path.expanduser('~')

    else:
        path = os.getcwd()

    return path
