"""
Working functions for display

Currently functional:
Hits API and returns a list of tuples with 'H' or 'L' and timestamp
Hits API and sets RTC time to New York city time
Rotates display of last tide and next tide with station name (yellow = falling / green = rising)

Future function:
Add ability to pull weather from Duke Marine Lab and display as part of rotation
Create a Class for handling display rotations
Learn async to allow work to continue while screen is static
Clean up issues with failed updates
"""


import urequests
import ujson
import utime
from LCD import CharLCD
from machine import Pin, PWM, RTC

def get_tides(station, lcd, pin0):
    """Hits api for 3 days of tides, returns a list of tuples w/ hi/lo and timestamp"""
    url_dict = {
        'beaufort': 'https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date={}{}{}&range=72&datum=MLLW&station=8656483&time_zone=lst_ldt&units=english&interval=hilo&format=json',
        'bogue':  'https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date={}{}{}&range=72&datum=MLLW&station=TEC2837&time_zone=lst_ldt&units=english&interval=hilo&format=json',
        'spooners': 'https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date={}{}{}&range=72&datum=MLLW&station=8656467&time_zone=lst_ldt&units=english&interval=hilo&format=json',
    }

    day_ago = utime.time() - 86400
    yr, mo, dy, _, _, _, _, _ = utime.localtime(day_ago)
    yr_str = str(yr)
    #print(yr_str)
    mo_str = _pad_date(mo)
    #print(mo_str)
    dy_str = _pad_date(dy)
    #print(dy_str)

    color_lcd('yellow')
    lcd.clear
    lcd.message("Getting tides:")
    lcd.set_line(1)
    lcd.message(station)
    pin0.value(1)

    resp = urequests.get(url_dict[station].format(yr_str, mo_str, dy_str))

    lcd.clear()
    color_lcd('black')

    if resp.status_code == 200:
        print("Updated data for: " + station)
        long_list = _tide_resp_to_list(ujson.loads(resp.content))
        return {station: trim_list(long_list)}
    else:
        print('Response code: ' + str(resp.status_code) + '\n')


def trim_list(full_list):
    """Review list of tuples and remove all but most recent past event"""
    print("Executing list trim")
    timestamp = utime.time()
    first_future = 0

    # believe this broke on update at midnight as it didn't have a previous tide
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


def tide_display(tide_dict, lcd, pin0):
    """Will use the tide list to display the current tide status"""
    station_formal = {
        'bogue': 'Bogue Inlet',
        'spooners': 'Spooner\'s Creek',
        'beaufort': 'Beaufort Marina'
    }

    #print(tide_dict)

    for station in tide_dict.keys():
        _, _, _, hr_1, min_1, _, _, _ = utime.localtime(tide_dict[station][0][1])
        _, _, _, hr_2, min_2, _, _, _ = utime.localtime(tide_dict[station][1][1])
        hr_1 = _pad_date(hr_1)
        hr_2 = _pad_date(hr_2)
        min_1 = _pad_date(min_1)
        min_2 = _pad_date(min_2)

        if tide_dict[station][0][0] == 'H':
            color_lcd('yellow')
            lcd.clear
            lcd.message(station_formal[station], 2)
            lcd.set_line(1)
            lcd.message('Hi:{}{}  Lo:{}{}'.format(hr_1, min_1, hr_2, min_2))
            pin0.value(1)
            utime.sleep(6)
            lcd.clear()
            color_lcd('black')
        elif tide_dict[station][0][0] == 'L':
            color_lcd('green')
            lcd.clear
            lcd.message(station_formal[station], 2)
            lcd.set_line(1)
            lcd.message('Lo:{}{}  Hi:{}{}'.format(hr_1, min_1, hr_2, min_2))
            pin0.value(1)
            utime.sleep(6)
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
        'white': (0, 0, 0),
    }

    # instances of PWM pins for LCD color
    green_pin = PWM(Pin(12), freq=1000, duty=1000)
    blue_pin = PWM(Pin(14), freq=1000, duty=1000)
    red_pin = PWM(Pin(13), freq=1000, duty=1000)

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
        print('Entry not recognized, enter valid color, or RGB tuple')d