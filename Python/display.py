import urequests
import ujson

#TODO: get high/low tide at Beaufort
def get_hilo():
    today_dt = dt.now()
    tmrw_dt = today_dt + timedelta(days=1)
    beaufort_resp = urequests.get(f'https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application='
                                 f'NOS.COOPS.TAC.WL&begin_date={today_dt.strftime("%Y%m%d")}&'
                                 f'end_date={tmrw_dt.strptime("%Y%m%d")}&datum=MLLW&station=8656483&time_zone='
                                 f'lst_ldt&units=english&interval=hilo&format=json')
    beaufort_dict = ujson.loads(beaufort_resp.content)

    #TODO: parse hi/low tide info
    beaufort_hi_list = [dt.strptime(x['t'],'%Y-%m-%d %H:%M') for x in beaufort_dict['predictions'] if x['type'] == 'H']
    beaufort_lo_list = [dt.strptime(x['t'],'%Y-%m-%d %H:%M') for x in beaufort_dict['predictions'] if x['type'] == 'L']

# Check seconds for rotating display

# Check minutes for changing 'next hi/lo'


# Check hours for updating


#TODO: get current weather from a station

#TODO: parse weather into variables

#TODO: create a clock to periodically update the high/low tides

#TODO: create a clock to update the display

#TODO: decide on displays 

#TODO: Update display
