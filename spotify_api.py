import requests
import json
import csv
import spotify_config

###################################################################################################
# Variable declaration
###################################################################################################

URL_BASE = "https://api.spotify.com/v1/"
AUTH_TOKEN = spotify_config.authToken

###################################################################################################
# Function definitions
###################################################################################################

def api_get_external_id(url):
	try:
		return api_generic('tracks/' + str(url.split('/')[-1]))['external_ids']['isrc']
	except:
		return None


def api_search(q, qtype, market=None, limit=None, offset=None):
    parameters = {'q': q, 'type': qtype, 'market': market, 'limit': limit, 'offset': offset}
    querystring = ''.join([k + "=" + str(parameters[k]) + "&" for k in parameters.keys() if parameters[k]])
    data = requests.get(URL_BASE + 'search?' + querystring, headers={'Authorization':AUTH_TOKEN})
    return data.json()


def api_generic(endpoint, **kwargs):
    querystring = ''.join([k + "=" + str(kwargs[k]) + "&" for k in kwargs.keys() if kwargs[k]])
    data = requests.get(URL_BASE + endpoint + '?' + querystring, headers={'Authorization':AUTH_TOKEN})
    return data.json()


def get_top_chart_json(filename):
    rlist = list()
    with open(filename, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        try:
            for row in reader:
                tempdict = dict()
                for key, val in row.items():
                    tempdict[key] = val
                rlist.append((tempdict['URL']))
        except UnicodeDecodeError:
            pass
    return rlist


def print_json(jsondata):
    print(json.dumps(jsondata, indent=2, sort_keys=True))


###################################################################################################
# Driver function
###################################################################################################

if __name__ == '__main__':
    print_json(get_top_chart_json('data/regional-global-daily-latest.csv'))
