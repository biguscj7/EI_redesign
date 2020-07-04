"""
This script is intended to run on the RPI Zero W to collect packets from a RFM69HCW radio. Intended output in initial
version is to push to adafruit.io as well as writing to a sqlite database. Alternatively, I could set up MQTT with
python to push directly from the RPI to the display. This would allow changing the display depending on script.

Consideration for future growth is adding a streamlit server to display the information from the sqlite database.

"""

# TODO: Import required packages
# RFM package, MQTT, sqlite3, adafruit.io


# TODO: Configure the RFM69HCW
def configure_radio():
    pass

# TODO: Set radio to listen for packets
def radio_listen():
    pass

# TODO: Periodically check for received packets
def check_packets():
    pass

# TODO: Parse received packets
def parse_packets():
    pass

# TODO: Send received information to adafruit or MQTT
def send_mqtt():
    pass

# TODO: Write received information to sqlite database
def db_connect():
    pass


if __name__ == '__main__':
    pass