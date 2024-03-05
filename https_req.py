import requests
import json
import api_key as ak
import os
from time import strftime, localtime
import text_handler
import names
# import names


def update_data_create_files(request_options_file):
    if os.stat(request_options_file).st_size == 0:
        print('ОШИБКА! Нет данных о спутниках для совершения запросов на сервер')
    else:
        # remove old commands and responses files (if files are there)
        if os.listdir(names.commands_dir_path) and os.listdir(names.responses_dir_path):
            for file_command in os.listdir(names.commands_dir_path):
                file_command_path = names.commands_dir_path + '/' + file_command
                os.remove(file_command_path)
            for file_request in os.listdir(names.responses_dir_path):
                file_request_path = names.responses_dir_path + '/' + file_request
                os.remove(file_request_path)

        input_satellites = []

        with open(request_options_file, 'r') as file:
            for line in file:
                input_satellites.append(line)
        
        # test print (need to check what we have in options file)
        # print('input satellites data:')
        # for sat_req_data in input_satellites:
        #     print(sat_req_data, end='')
        # print()

        # satellites_dir = 'satellites'
        # passes_dir = 'responses'

        # responses_dir_path = './' + names.satellites_dir + '/' + names.responses_dir
        # if not os.path.isdir(responses_dir_path):
        #     os.mkdir(responses_dir_path)

        # TODO add this options to file so user could install it with his desires
        observer_lat = 51.671667
        observer_lng = 39.210556
        observer_alt = 99
        days = 10
        min_elevation = 40
        api_key = ak.api_key

        # sat_id = 46494 

        # iterate over each satellite from file 
        # we need it to get sat_id of each satellite and make corresponding request to n2yo api
        for sat_req_data in input_satellites:
            # get sat_id from satellite
            sat_id = int(sat_req_data.split('=')[1])

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

            # perform get request with corresponding url
            response = requests.get(url_get_req)
            response_data = response.text

            # print(response_data)

            # parse json in list
            data = json.loads(response.text)
            # print(data)

            # test print
            # print('Info:')
            # print(data['info']['satid'])
            # print(data['info']['satname'])
            # print(data['info']['transactionscount'])
            # print(data['info']['passescount'])

            sat_name =              data['info']['satname'] 
            transactions_count =    data['info']['transactionscount']
            passes_counter =        data['info']['passescount']

            # passes_file_path = passes_info_path + '/' + str(sat_name) + '.txt'
            # response_file_path =  responses_dir_path + '/' + str(sat_id) + names.response_postfix + '.txt'

            response_buffer = []

            # with open(response_file_path, 'w') as file:

            # TODO FIX IT first value:number - important pos of :
            info_values_string = 'sat_id: %i\nsat_name: %s\ntransactions_count: %i\npasses_count: %i\n'%(
            # info_values_string = 'sat_name: %s\nsat_id: %i\ntransactions_count: %i\npasses_count: %i\n'%(
                sat_id,
                sat_name,
                transactions_count,
                passes_counter
            )

            # test 
            # add line to buffer
            splitted_string = info_values_string.split('\n')
            for item in splitted_string:
                response_buffer.append(item + '\n')

            # add string to file
            # file.write(info_values_string)
            # test print
            # print(info_values_string)

            if(passes_counter != 0):
                passes = data['passes']
                local_pass_number = 0
                for pass_item in passes:
                    local_pass_number += 1
                    time_format     = '%d.%m.%Y %H:%M'
                    start_utc       = pass_item['startUTC']
                    end_utc         = pass_item['endUTC']

                    # print(start_utc)
                    # print(end_utc)

                    start_utc_converted = strftime(time_format, localtime(start_utc))
                    end_utc_converted   = strftime(time_format, localtime(end_utc))

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
                    
                    # test 
                    # add line to buffer
                    splitted_string = formatted_time.split('\n')
                    for item in splitted_string:
                        response_buffer.append(item + '\n')

                    # todo write time formatted string to file
                    # file.write(formatted_time)
                    # test print 
                    # print(formatted_time, end='')

                    start_az    = pass_item['startAz'] 
                    end_az      = pass_item['endAz']
                    az_values   = 'startAz: %lf\nendAz: %lf\n'%(start_az, end_az)

                    # test
                    # add line to buffer
                    splitted_string = az_values.split('\n')
                    for item in splitted_string: 
                        response_buffer.append(item + '\n')

                    # todo write start/end az values string to file
                    # file.write(az_values)
                    # test print
                    # print(az_values, end='')

                    start_az_compass    = pass_item['startAzCompass']
                    end_az_compass      = pass_item['endAzCompass']

                    az_compass_values   = 'startAzCompass: %s\nendAzCompass: %s\n'%(start_az_compass, end_az_compass)

                    # test
                    # add line to buffer
                    splitted_string = az_compass_values.split('\n')
                    for item in splitted_string:
                        response_buffer.append(item + '\n')

                    # todo write az_compass values string to file
                    # file.write(az_compass_values)
                    # test print
                    # print(az_compass_values, end='')

                    max_az          = pass_item['maxAz']
                    max_az_compass  = pass_item['maxAzCompass']
                    max_el          = pass_item['maxEl']
                    max_utc         = pass_item['maxUTC']

                    max_values = 'maxAz: %lf\nmaxAzCompass: %s\nmaxEl: %lf\nmaxUTC: %s\n'%(
                        max_az,
                        max_az_compass,
                        max_el,
                        max_utc
                    )

                    # test
                    # add line to buffer
                    splitted_string = max_values.split('\n')
                    for item in splitted_string:
                        response_buffer.append(item + '\n')

                    #todo write max values string to file
                    # file.write(max_values)
                    # test print
                    # print(max_values, end='')

            else:
                print('No passes counter in response for satellite %s with id %i'%(sat_name, sat_id))

            # print('file %s was created with size: %i bytes'%(response_file_path, os.path.getsize(response_file_path)))

            # create file by sat list
            # pass_data_list = []
            # with open(response_file_path, 'r') as file:
            #     for line in file:
            #         pass_data_list.append(line) 
            
            # test print

            # remove external elements from buffer
            filtered_buffer = list(filter(lambda element: element != '\n', response_buffer)) 
            # send filtered buffer to function to create files 
            text_handler.create_files_by_response_list(filtered_buffer)