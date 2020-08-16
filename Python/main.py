from machine import RTC
import network
import utime
from LCD import CharLCD
import gc
import urequests
import ujson
from tide_class import Tide, LcdColor

NETWORKS = {
    'BIGUS': 'OzoF32*kMJ3gYdCqxmwpxnU&$@*2xM1o',
    'Copperhead': '9197341930',
    'copperhead': '9197341930',
    'Las Palmas': 'pollywolly'
}


def _check_networks():
    """Checks wifi networks in range and produces an intersection of sets on programmed networks"""
    global wlan
    my_avail_nets = []
    avail_nets = wlan.scan()
    global NETWORKS
    for name in NETWORKS.keys():  # loop through my nets
        for net in avail_nets:
            if net[0].decode('utf-8') == name:
                my_avail_nets.append(name)

    return my_avail_nets


def _timed_connect(net_name):
    """Implements timer for connecting to network, returns TRUE if connected"""
    start_time = utime.time()
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(net_name, NETWORKS[net_name])
        while not wlan.isconnected():
            if (utime.time() - start_time) > 15:  # try for 15 seconds then abort
                return False  # if still in loop at 15 seconds will return False
    return True  # returns True if above statement evals to True


def wifi_connect(close_nets):
    """Connect to wifi AP at beach"""
    global NETWORKS

    if len(close_nets) == 0:
        return "You've passed no nets to connect to."

    if wlan.isconnected():
        return ("You're already connected to %s network" % wlan.config('essid'))
    else:
        for i in close_nets:
            if _timed_connect(i):
                break

    print('network config:', wlan.ifconfig())


def network_disp():
    """Displays ssid, ip, and gateway info"""
    # TODO: Add printing which wifi the device is connected to
    global color, text

    ip, _, gateway, _ = wlan.ifconfig()

    # display ssid
    color.color_lcd('teal')
    text.clear()
    text.message('SSID:')
    text.set_line(1)
    text.message(wlan.config('essid'))
    utime.sleep(2)
    color.color_lcd('black')

    # display IP address
    color.color_lcd('red')
    text.clear()
    text.message('IP address:')
    text.set_line(1)
    text.message(ip)
    utime.sleep(2)
    color.color_lcd('black')

    # display router address
    color.color_lcd('blue')
    text.clear()
    text.message('Router address:')
    text.set_line(1)
    text.message(gateway)
    utime.sleep(2)
    color.color_lcd('black')

    # clear display
    text.clear()


def set_rtc():
    """Query time API for offset and set the RTC to local time"""
    if not wlan.isconnected():
        print("Can't update due to lack of connection")
        return False
    else:
        rtc = RTC()

        resp = urequests.get('http://worldtimeapi.org/api/timezone/America/New_York')

        if resp.status_code == 200:
            time_data = ujson.loads(resp.content)
            dt = time_data['datetime']
            rtc.datetime((int(dt[0:4]), int(dt[5:7]), int(dt[8:10]),
                          0, int(dt[11:13]), int(dt[14:16]), int(dt[17:19]), 0))
            print("Updated RTC time from internet.")
            return True
        else:
            print('Response: ' + str(resp.status_code))
            return False


def pad_date(val):
    """adds a zero to date if single digit"""
    if val < 10:
        return '0' + str(val)
    else:
        return str(val)


def tide_display(station):
    """Will use the tide list to display the current tide status"""
    global color, text

    _, _, _, hr_1, min_1, _, _, _ = utime.localtime(station.tide_list[0][1])
    _, _, _, hr_2, min_2, _, _, _ = utime.localtime(station.tide_list[1][1])
    first_time = pad_date(hr_1) + pad_date(min_1)
    second_time = pad_date(hr_2) + pad_date(min_2)

    if station.tide_list[0][0] == 'H':
        color.color_lcd('blue')
        text.clear()
        text.message(station.title, 2)
        text.set_line(1)
        text.message('Hi:{}  Lo:{}'.format(first_time, second_time))
        station.trim_list()
        utime.sleep(6)
        text.clear()
        color.color_lcd('black')
    elif station.tide_list[0][0] == 'L':
        color.color_lcd('green')
        text.clear()
        text.message(station.title, 2)
        text.set_line(1)
        text.message('Lo:{}  Hi:{}'.format(first_time, second_time))
        station.trim_list()
        utime.sleep(6)
        text.clear()
        color.color_lcd('black')


if __name__ == '__main__':
    print("\nBooting from boot.py")

    # Setup network
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # instantiates for text
    text = CharLCD(rs=4, en=5, d4=15, d5=0, d6=16, d7=2)
    color = LcdColor()

    print("Attempting network connection")
    wifi_connect(_check_networks())
    print("Network connection successful")
    network_disp()
    set_rtc()
    gc.collect()

    bogue = Tide('bogue')
    bogue.get_tides()
    spooners = Tide('spooners')
    spooners.get_tides()
    beaufort = Tide('beaufort')
    beaufort.get_tides()

    station_list = [bogue, spooners, beaufort]

    while True:  # Need to work over the below script, pulled in but not yet functional
        for station in station_list:
            tide_display(station)

        _, _, _, hr, minute, sec, _, _ = utime.localtime()

        # Attempt rtc update every 8 hours
        if hr in [0, 2, 4, 8, 10, 12, 14, 18, 20, 22] and minute == 0 and sec < 30:
            if not wlan.isconnected():
                wifi_connect()
            print("Periodic time update")
            set_rtc()

        # Attempt tide update every 6 hours
        if hr in [0, 2, 4, 8, 10, 12, 14, 18, 20, 22] and minute == 10 and sec < 30:
            if not wlan.isconnected():
                wifi_connect()
            print("Periodic tide update")
            for station in station_list:
                station.get_tides()

        # Manual garbage collection
        if hr in [0, 2, 4, 8, 10, 12, 14, 18, 20, 22] and minute == 5 and sec < 30:
            print(utime.localtime())
            gc.collect()
