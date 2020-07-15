# This file is executed on every boot (including wake-boot from deepsleep)
from machine import RTC, PWM, Pin, Timer
import network
import utime
from LCD import CharLCD
import gc
import urequests
import ujson
import df


def wifi_connect():
    """Connect to wifi AP at beach"""
    # TODO: Need to add time to abort attempted connection
    # TODO: Need to add multiple networks
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('BIGUS', 'OzoF32*kMJ3gYdCqxmwpxnU&$@*2xM1o')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    return wlan.ifconfig()


def startup_network_disp():
    """Displays ip and gateway info on display as part of bootup"""
    # TODO: Add printing which wifi the device is connected to
    ip, _, gateway, _ = wifi_connect()

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
    from machine import RTC
    rtc = RTC()

    resp = urequests.get('http://worldtimeapi.org/api/timezone/America/New_York')

    if resp.status_code == 200:
        time_data = ujson.loads(resp.content)
    else:
        print('Response: ' + str(resp.status_code))

    dt = time_data['datetime']
    rtc.datetime((int(dt[0:4]), int(dt[5:7]), int(dt[8:10]), 0, int(dt[11:13]), int(dt[14:16]), int(dt[17:19]), 0))



# instantiates for text
lcd = CharLCD(rs=4, en=5, d4=15, d5=0, d6=16, d7=2)
# instances of PWM pins for LCD color
green_pin = PWM(Pin(12), freq=1000, duty=1000)
blue_pin = PWM(Pin(14), freq=1000, duty=1000)
red_pin = PWM(Pin(13), freq=1000, duty=1000)

# Functions run at startup
startup_network_disp()
set_rtc()
gc.collect()
