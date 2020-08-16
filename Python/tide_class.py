import urequests
import network
import ujson
import utime
from machine import Pin, PWM


class Tide():
    """This class is to represent a station and it's tide data. It will handle updating tide data and maintaining
    an appropriate length list"""
    _station_dict = {
        'beaufort': (
        'https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date={}{}{}&range=72&datum=MLLW&station=8656483&time_zone=lst_ldt&units=english&interval=hilo&format=json',
        'Bogue Inlet'),
        'bogue': (
        'https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date={}{}{}&range=72&datum=MLLW&station=TEC2837&time_zone=lst_ldt&units=english&interval=hilo&format=json',
        'Beaufort Marina'),
        'spooners': (
        'https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date={}{}{}&range=72&datum=MLLW&station=8656467&time_zone=lst_ldt&units=english&interval=hilo&format=json',
        'Spooner\'s Creek'),
    }

    def __init__(self, station):
        self.station = station
        self.title = Tide._station_dict[station][1]
        self.url = Tide._station_dict[station][0]
        self.tide_list = []

    def get_tides(self):  # pin0, pin2
        """Hits api for 3 days of tides, returns a list of tuples w/ hi/lo and timestamp"""

        day_ago = utime.time() - 86400
        yr, mo, dy, _, _, _, _, _ = utime.localtime(day_ago)
        yr_str = str(yr)
        # print(yr_str)
        mo_str = self._pad_date(mo)
        # print(mo_str)
        dy_str = self._pad_date(dy)
        # print(dy_str)

        print(str(self.url).format(yr_str, mo_str, dy_str))
        resp = urequests.get(str(self.url).format(yr_str, mo_str, dy_str))

        if resp.status_code == 200:
            print("Updated data for: " + self.station)
            self.tide_list.clear()
            self._tide_resp_to_list(ujson.loads(resp.content))
            self.trim_list()
        else:
            print('Response code: ' + str(resp.status_code) + '\n')

    def trim_list(self):
        """Review list of tuples and remove all but most recent past event"""
        print("Executing list trim")
        timestamp = utime.time()
        first_future = 0

        # believe this broke on update at midnight as it didn't have a previous tide
        for x in range(len(self.tide_list)):
            first_future = x
            if self.tide_list[first_future][1] > timestamp:
                break

        for x in range(first_future - 2, -1, -1):
            self.tide_list.pop(x)

    def _tide_resp_to_list(self, resp_content):
        """Takes response from CO-OPS and returns list of tuples"""
        for x in resp_content['predictions']:
            tmstp = utime.mktime(
                (int(x['t'][0:4]), int(x['t'][5:7]), int(x['t'][8:10]), int(x['t'][11:13]), int(x['t'][14:]), 0, 0, 0))
            self.tide_list.append((x['type'], tmstp))

    def _pad_date(self, val):
        """adds a zero to date if single digit"""
        if val < 10:
            return '0' + str(val)
        else:
            return str(val)


class LcdColor():
    """This class will handle coloring the LCD display"""

    def __init__(self):
        self.green_pin = PWM(Pin(12), freq=1000, duty=1000)
        self.blue_pin = PWM(Pin(14), freq=1000, duty=1000)
        self.red_pin = PWM(Pin(13), freq=1000, duty=1000)
        self.color_dict = {
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

    def color_lcd(self, color):
        """This method colors the LCD based on an string input or tuple of RGB values"""
        if type(color) == str:
            color = color.lower()
            self.red_pin.duty(self.color_dict[color][0])
            self.green_pin.duty(self.color_dict[color][1])
            self.blue_pin.duty(self.color_dict[color][2])
        elif type(color) == tuple:
            self.red_pin.duty(color[0])
            self.green_pin.duty(color[1])
            self.blue_pin.duty(color[2])
        else:
            print('Entry not recognized, enter valid color, or RGB tuple')
