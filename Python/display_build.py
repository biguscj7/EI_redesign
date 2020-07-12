# This file is executed on every boot (including wake-boot from deepsleep)
from machine import RTC, PWM, Pin, Timer
import ntptime
import network
import utime
from LCD import CharLCD
import gc
import urequests

def wifi_connect():
    """Connect to wifi AP at beach"""
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('Copperhead', '9197341930')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    return wlan.ifconfig()

def startup_network_disp():
    ip, _, gateway, _ = wifi_connect()

    # display IP address
    red_pin.duty(0)
    lcd.clear()
    lcd.message('IP address:')
    lcd.set_line(1)
    lcd.message(ip)
    utime.sleep(5)

    # display router address
    red_pin.duty(1000)
    blue_pin.duty(0)
    lcd.clear()
    lcd.message('Router address:')
    lcd.set_line(1)
    lcd.message(gateway)
    utime.sleep(5)
    blue_pin.duty(1000)

    # clear display
    lcd.clear()
    gc.collect()


# yellow - red_pin.duty(0) / green_pin.duty(600)
green_pin = PWM(Pin(12), freq=1000, duty=1000)
blue_pin = PWM(Pin(14), freq=1000, duty=1000)
red_pin = PWM(Pin(13), freq=1000, duty=1000)

lcd = CharLCD(rs=4, en=5, d4=15, d5=0, d6=16, d7=2) # instantiate lcd

startup_network_disp()

