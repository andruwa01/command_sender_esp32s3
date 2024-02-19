import requests
import json
import api_key as ak
from time import strftime, localtime

observer_lat = 51.671667
observer_lng = 39.210556
observer_alt = 99
days = 10
min_elevation = 40
api_key = ak.api_key

sat_id = 46494 

url_get_req = "https://api.n2yo.com/rest/v1/satellite/radiopasses/%i/%f/%f/%f/%i/%i/&apiKey=%s"%(
    sat_id,
    observer_lat,
    observer_lng,
    observer_alt,
    days,
    min_elevation,
    api_key
)

# print(url_get_req)

response = requests.get(url_get_req)
response_data = response.text

# print(response_data)

data = json.loads(response_data)

# print('Info:')
# print(data['info']['satid'])
# print(data['info']['satname'])
# print(data['info']['transactionscount'])
# print(data['info']['passescount'])

sat_name = data['info']['satname'] 
transactions_count = data['info']['transactionscount']
passes_counter = data['info']['passescount']

info_values_string = 'sat_id: %i\nsat_name: %s\ntransactions_count: %i\npasses_count: %i\n'%(
    sat_id,
    sat_name,
    transactions_count,
    passes_counter
)

print(info_values_string)

passes = data['passes']

local_pass_number = 0
for pass_item in passes:
    local_pass_number += 1
    time_format = '%d.%m.%Y %H:%M'

    start_utc = pass_item['startUTC']
    end_utc = pass_item['endUTC']

    # print(start_utc)
    # print(end_utc)

    start_utc_converted = strftime(time_format, localtime(start_utc))
    end_utc_converted = strftime(time_format, localtime(end_utc))

    # print('startUTC: ' + start_utc_converted)
    # print('endUTC: ' + end_utc_converted)

    if(local_pass_number < 10):
        formatted_time = '#0%i start %s end %s\n'%(
                local_pass_number,
                start_utc_converted,
                end_utc_converted
            )
    else:
        formatted_time = '#%i start %s end %s\n'%(
                    local_pass_number,
                    start_utc_converted,
                    end_utc_converted
                )
    
    print(formatted_time, end='')
    