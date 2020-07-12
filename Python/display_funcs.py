"""
Working functions for display

Currently functional:
Hits API and returns a list of tuples with 'H' or 'L' and timestamp
Hits API and sets RTC time to New York city time


"""


import urequests
import ujson
import utime

def get_tides():
    """Hits api for 3 days of tides, returns a list of tuples w/ hi/lo and timestamp"""
    yr, mo, dy, _, _, _, _, _ = utime.localtime()
    yr_str = str(yr)
    print(yr_str)
    mo_str = pad_date(mo)
    print(mo_str)
    dy_str = pad_date(dy)
    print(dy_str)

    resp = urequests.get('https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date={}{}{}&range=72&datum=MLLW&station=8656467&time_zone=lst_ldt&units=english&interval=hilo&format=json'.format(yr_str, mo_str, dy_str))

    if resp.status_code == 200:
        long_list = tide_resp_to_list(ujson.loads(resp.content))
        return long_list
    else:
        print('Response code: ' + str(resp.status_code) + '\n')


def pad_date(val):
    """adds a zero to date if single digit"""
    if val < 10:
        return '0' + str(val)
    else:
        return str(val)

def tide_resp_to_list(resp_content):
    """Takes response from CO-OPS and returns list of tuples"""
    resp_list = []
    for x in resp_content['predictions']:
        tmstp = utime.mktime((int(x['t'][0:4]), int(x['t'][5:7]), int(x['t'][8:10]), int(x['t'][11:13]), int(x['t'][14:]), 0, 0, 0))
        resp_list.append((x['type'], tmstp))
    return resp_list

def set_rtc():
    """Query time API for offset and set the RTC to local time"""
    from machine import RTC
    rtc = RTC()

    resp = urequests.get('http://worldtimeapi.org/api/timezone/America/New_York')

    if resp.status_code == 200:
        time_data = ujson.loads(resp.content)
    else:
        print('Response: ' + str(resp.status_code))

    dt = time_data['datetime']
    rtc.datetime((int(dt[0:4]), int(dt[5:7]), int(dt[8:10]), 0, int(dt[11:13]), int(dt[14:16]), int(dt[17:19]), 0))