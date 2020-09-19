# TODO: Required imports
import pandas
import requests
import json
import time

# TODO: Make calls to get last 24 hrs of data (only on start of script)
def initial_data():
    """uses current time to pull last 24 hours of wind / temp / pressure / tide data from beaufort marine lab"""
    url_dict = {
        'wind': f'https://tidesandcurrents.noaa.gov/api/datagetter?product=wind&application=NOS.COOPS.TAC.WL&begin_date={yr_str}{mo_str}{dy_str}&range=48&station=8656483&time_zone=lst_ldt&units=english&interval=6&format=json',
        'temperature': f'https://tidesandcurrents.noaa.gov/api/datagetter?product=air_temperature&application=NOS.COOPS.TAC.WL&begin_date={yr_str}{mo_str}{dy_str}&range=48&station=8656483&time_zone=lst_ldt&units=english&interval=6&format=json',
        'pressure': f'https://tidesandcurrents.noaa.gov/api/datagetter?product=air_pressure&application=NOS.COOPS.TAC.WL&begin_date={yr_str}{mo_str}{dy_str}&range=48&station=8656483&time_zone=lst_ldt&units=english&interval=6&format=json',
        'tide': f'https://tidesandcurrents.noaa.gov/api/datagetter?product=water_level&application=NOS.COOPS.TAC.WL&begin_date={yr_str}{mo_str}{dy_str}&range=48&datum=MSL&station=8656483&time_zone=lst_ldt&units=english&format=json',
    }

    yr, mo, dy, _, _, _, _, _ = time.localtime()
    yr_str = str(yr)
    mo_str = _pad_date(mo)
    dy_str = _pad_date(dy)





def _pad_date(val):
    """adds a zero to date if single digit"""
    if val < 10:
        return '0' + str(val)
    else:
        return str(val)

# TODO: write data to pandas df


# TODO: Periodic call to get last XX minutes of data


# TODO: add recent data to pandas df



# TODO: generate web page with dash using dataframe


# TODO: Publish data to MQTT server for pushing to display



if __name__ == '__main__':
