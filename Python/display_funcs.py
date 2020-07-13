"""
Working functions for display

Currently functional:
Hits API and returns a list of tuples with 'H' or 'L' and timestamp
Hits API and sets RTC time to New York city time


IDEA - Do hi/lo and lo high for each location use green for rising and red for falling
lcd.message('Beaufort tides', 2)
lcd.set_line(1)
lcd.message('Hi:0223  Lo:0000')

"""


import urequests
import ujson
import utime
from LCD import CharLCD
from machine import Pin, PWM, RTC

def get_tides():
    """Hits api for 3 days of tides, returns a list of tuples w/ hi/lo and timestamp"""
    yr, mo, dy, _, _, _, _, _ = utime.localtime()
    yr_str = str(yr)
    print(yr_str)
    mo_str = _pad_date(mo)
    print(mo_str)
    dy_str = _pad_date(dy)
    print(dy_str)

    resp = urequests.get('https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date={}{}{}&range=72&datum=MLLW&station=8656467&time_zone=lst_ldt&units=english&interval=hilo&format=json'.format(yr_str, mo_str, dy_str))

    if resp.status_code == 200:
        long_list = _tide_resp_to_list(ujson.loads(resp.content))
        return trim_list(long_list)
    else:
        print('Response code: ' + str(resp.status_code) + '\n')


def trim_list(full_list):
    """Review list of tuples and remove all but most recent past event"""
    timestamp = utime.time()
    print(timestamp)
    first_future = 0

    for x in range(len(full_list)):
        first_future = x
        if full_list[x][1] > timestamp:
            break

    for x in range(first_future - 2, -1, -1):
        full_list.pop(x)
    return full_list


def _pad_date(val):
    """adds a zero to date if single digit"""
    if val < 10:
        return '0' + str(val)
    else:
        return str(val)


def _tide_resp_to_list(resp_content):
    """Takes response from CO-OPS and returns list of tuples"""
    resp_list = []
    for x in resp_content['predictions']:
        tmstp = utime.mktime((int(x['t'][0:4]), int(x['t'][5:7]), int(x['t'][8:10]), int(x['t'][11:13]), int(x['t'][14:]), 0, 0, 0))
        resp_list.append((x['type'], tmstp))
    return resp_list


def tide_display(tide_list):
    """Will use the tide list to display the current tide status"""
    lcd = CharLCD(rs=4, en=5, d4=15, d5=0, d6=16, d7=2)

    # last tide display
    color_lcd('purple')
    lcd.clear
    _, _, _, hr, min, _, _, _ = utime.localtime(tide_list[0][1])
    hr = _pad_date(hr)
    min = _pad_date(min)
    if tide_list[0][0] == 'H':
        lcd.message('FALLING tide', 2)
        lcd.set_line(1)
        lcd.message('Hi tide @ {}{}L'.format(hr, min))
    elif tide_list[0][0] == 'L':
        lcd.message('RISING tide', 2)
        lcd.set_line(1)
        lcd.message('Low tide @ {}{}L'.format(hr, min))
    utime.sleep(5)
    lcd.clear()
    color_lcd('black')

    # next tide display
    color_lcd('blue')
    _, _, _, hr, min, _, _, _ = utime.localtime(tide_list[1][1])
    hr = _pad_date(hr)
    min = _pad_date(min)
    if tide_list[1][0] == 'H':
        lcd.message('RISING tide', 2)
        lcd.set_line(1)
        lcd.message('Hi tide @ {}{}L'.format(hr, min))
    elif tide_list[1][0] == 'L':
        lcd.message('FALLING tide', 2)
        lcd.set_line(1)
        lcd.message('Low tide @ {}{}L'.format(hr, min))
    utime.sleep(5)
    lcd.clear()
    color_lcd('black')


def color_lcd(color):
    """Accepts a color and sets the display to that color, reminder that duty cycles are 'backwards'"""
    color_dict = {
        'green': (1000, 0, 1000),
        'blue': (1000, 1000, 0),
        'red': (0, 1000, 1000),
        'yellow': (0, 600, 1000),
        'teal': (500, 500, 1000),
        'black': (1000, 1000, 1000),
        'purple': (500, 1000, 500),
        'orange': (0, 800, 1000),
    }


    if type(color) == str:
        color = color.lower()
        red_pin.duty(color_dict[color][0])
        green_pin.duty(color_dict[color][1])
        blue_pin.duty(color_dict[color][2])
    elif type(color) == tuple:
        red_pin.duty(color[0])
        green_pin.duty(color[1])
        blue_pin.duty(color[2])
    else:
        print('Entry not recognized, enter valid color, or RGB tuple')