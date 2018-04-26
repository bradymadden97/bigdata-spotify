import requests
import urllib
import json
import config

###################################################################################################
# Variable declaration
###################################################################################################

URL_BASE = "https://api.spotify.com/v1/"
AUTH_TOKEN = config.authToken

###################################################################################################
# Function definitions
###################################################################################################


def api_search(q, qtype, market=None, limit=None, offset=None):
    parameters = {'q': q, 'type': qtype, 'market': market, 'limit': limit, 'offset': offset}
    querystring = ''.join([k + "=" + str(parameters[k]) + "&" for k in parameters.keys() if parameters[k]])
    data = requests.get(URL_BASE + 'search?' + querystring, headers={'Authorization':AUTH_TOKEN})
    return data.json()


def api_generic(endpoint, **kwargs):
    querystring = ''.join([k + "=" + str(kwargs[k]) + "&" for k in kwargs.keys() if kwargs[k]])
    data = requests.get(URL_BASE + endpoint + '?' + querystring, headers={'Authorization':AUTH_TOKEN})
    return data.json()


def print_json(jsondata):
    print(json.dumps(jsondata, indent=2, sort_keys=True))


###################################################################################################
# Driver function
###################################################################################################

if __name__ == '__main__':
    print_json(api_search('Kanye', 'artist'))
    print('\n\n\n')
    print_json(api_generic('me'))
