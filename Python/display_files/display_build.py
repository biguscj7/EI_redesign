"""
This file should be uploaded to MCU as 'boot.py.' It will run every time the MCU is booted.
"""



# This file is executed on every boot (including wake-boot from deepsleep)
from machine import RTC, PWM, Pin
import network
import utime
from LCD import CharLCD
import gc
from display_files import urequests
import ujson
import df


def _check_networks():
    """Checks wifi networks in range and produces an intersection of sets on programmed networks"""
    global wlan
    my_avail_nets = []
    avail_nets = wlan.scan()
    global networks
    for name in networks.keys(): # loop through my nets
        for net in avail_nets:
            if net[0].decode('utf-8') == name:
                my_avail_nets.append(name)

    return my_avail_nets


def _timed_connect(net_name):
    """Implements timer for connecting to network, returns TRUE if connected"""
    start_time = utime.time()
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(net_name, networks[net_name])
        while not wlan.isconnected():
            if (utime.time() - start_time) > 15:  # try for 15 seconds then abort
                return False # if still in loop at 15 seconds will return False
    return True # returns True if above statement evals to True


def wifi_connect(close_nets):
    """Connect to wifi AP at beach"""
    global networks

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
    ip, _, gateway, _ = wlan.ifconfig()

    # display ssid
    df.color_lcd('teal')
    lcd.clear()
    lcd.message('SSID:')
    lcd.set_line(1)
    lcd.message(wlan.config('essid'))
    utime.sleep(2)
    df.color_lcd('black')

    # display IP address
    df.color_lcd('red')
    lcd.clear()
    lcd.message('IP address:')
    lcd.set_line(1)
    lcd.message(ip)
    utime.sleep(2)
    df.color_lcd('black')

    # display router address
    df.color_lcd('blue')
    lcd.clear()
    lcd.message('Router address:')
    lcd.set_line(1)
    lcd.message(gateway)
    utime.sleep(2)
    df.color_lcd('black')

    # clear display
    lcd.clear()


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


def trim_master():
    """Used to trim list in master dictionary"""
    global station_data

    for station, tide_list in station_data.items():
        if tide_list[1][1] < utime.time():
            update_list = df.trim_list(tide_list)
            station_data.update({station: update_list})


def tide_update():
    """Updates tide data from NOAA"""
    print("Tide time trigger update")
    global station_data

    for name in station_data.keys():
        tide_resp = df.get_tides(name, lcd) # pin0, pin2
        if type(tide_resp) == dict:
            station_data.update(tide_resp)



if __name__ == '__main__':
    print("\nBooting from boot.py")
    #pin0 = Pin(0, Pin.OUT)
    #pin2 = Pin(2, Pin.OUT)
    #pin0.value(1)
    #pin2.value(1)

    networks = {
        'BIGUS': 'OzoF32*kMJ3gYdCqxmwpxnU&$@*2xM1o',
        'Copperhead': '9197341930',
        'copperhead': '9197341930',
        'Las Palmas': 'pollywolly'
    }
    # Setup network
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # instantiates for text
    lcd = CharLCD(rs=4, en=5, d4=15, d5=0, d6=16, d7=2)

    # instances of PWM pins for LCD color
    green_pin = PWM(Pin(12), freq=1000, duty=1000)
    blue_pin = PWM(Pin(14), freq=1000, duty=1000)
    red_pin = PWM(Pin(13), freq=1000, duty=1000)

    print("Attempting network connection")
    wifi_connect(_check_networks())
    print("Network connection successful")
    network_disp()
    set_rtc()
    gc.collect()

    # list of tuples is payload for each key
    station_data = {'bogue': None, 'spooners': None, 'beaufort': None}

    for name in station_data.keys():
        tide_resp = df.get_tides(name, lcd) # pin0, pin2
        if type(tide_resp) == dict:
            station_data.update(tide_resp)

    while True:
        df.tide_display(station_data, lcd) # pin0, pin2
        for name in station_data.keys():
            trim_master()

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
            tide_update()

        if hr in [0, 2, 4, 8, 10, 12, 14, 18, 20, 22] and minute == 5 and sec < 30:
            print(utime.localtime())
            gc.collect()