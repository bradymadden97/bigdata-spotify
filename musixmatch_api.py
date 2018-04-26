import requests
import urllib
import json
import musixmatch_config

###################################################################################################
# Variable declaration
###################################################################################################

URL_BASE = "http://api.musixmatch.com/ws/1.1/"
API_TOKEN = musixmatch_config.apiKey

###################################################################################################
# Function definitions
###################################################################################################


def api_generic(endpoint, **kwargs):
	kwargs['apikey'] = API_TOKEN
	querystring = ''.join([k + "=" + str(kwargs[k]) + "&" for k in kwargs.keys() if kwargs[k]])
	data = requests.get(URL_BASE + endpoint + '?' + querystring)
	return data.json()


def print_json(jsondata):
	print(json.dumps(jsondata, indent=2, sort_keys=True))


###################################################################################################
# Driver function
###################################################################################################

if __name__ == '__main__':
	print('\n\n\n')
	print_json(api_generic('track.lyrics.get', track_isrc='TCACG1582632'))
