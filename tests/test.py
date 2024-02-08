import luas.api
from luas.api import LuasLine, LuasDirection
import json


import unittest
import requests_mock
from luas.api import LuasDirection, LuasLine
import luas.api
import os



def _file_path(file_name):
    thispath = os.path.dirname(__file__)
    return "{}/{}".format(thispath, file_name)

luas_client = luas.api.LuasClient()

# This will return the status text for the Green Line
green_line_status = luas_client.line_status(LuasLine.Green)
print(green_line_status)

# This will return the next tram from Balally, in the default direction (inbound)
next_bal = luas_client.next_tram('BAL')
print(next_bal)

All_trams=luas_client.all_trams('BAL')
print(All_trams)

# This will return the next outbound tram from Ranelagh
next_ran = luas_client.next_tram('RAN', LuasDirection.Outbound)
# print(next_ran)


# Return raw JSON for a stop
stop_details = luas_client.stop_details('Balally')
# print(stop_details)
data = json.dumps(stop_details)
# print("JSON string = ", data['trams'])
my_dict = json.loads(data)
# print(my_dict['trams'])
trams = my_dict['trams']

for i,val in enumerate(trams):
	if val['destination'] == 'Broombridge':
		print(val)
		print(val['due'])
		print(val['direction'])
		break

