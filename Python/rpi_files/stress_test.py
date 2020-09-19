import board
import busio
import digitalio
import adafruit_rfm69
from pprint import pprint as pp
import json
import csv
from datetime import datetime as dt

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D25)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, RADIO_FREQ_MHZ)

# Print out some chip state:
print("Temperature: {0}C".format(rfm69.temperature))
print("Frequency: {0}mhz".format(rfm69.frequency_mhz))
print("Bit rate: {0}kbit/s".format(rfm69.bitrate / 1000))
print("Frequency deviation: {0}hz".format(rfm69.frequency_deviation))

with open('wx_data.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(['datetime', 'temp', 'RH', 'pressure', 'dewpoint', 'RSSI'])


with open('range_data.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(['datetime', 'distance', 'RSSI'])


while True:
    packet = rfm69.receive(timeout=3.0)
    if packet is None:
        pass
    else:
        packet_text = str(packet, "utf-8")
        # print("Received (ASCII): {0}".format(packet_text))
        results = json.loads(packet_text)
        pp(results)
        dt_info = dt.now().strftime("%Y%m%d-%H%M%S")
        if results['type'] == 'wx':
            with open('wx_data.csv', 'a') as file:
                writer = csv.writer(file)
                writer.writerow([dt_info,
                                 results['t'],
                                 results['h'],
                                 results['p'],
                                 results['dp'],
                                 rfm69.last_rssi,])
        elif results['type'] == 'dist':
            with open('range_data.csv', 'a') as file:
                writer = csv.writer(file)
                writer.writerow([dt_info,
                                 results['d'],
                                 rfm69.last_rssi,])