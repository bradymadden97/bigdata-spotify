import requests as r
import urllib
import json
import config

baseURL = 'https://api.spotify.com/v1/'


# Endpoint
endpoint = 'search'

# Parameters
parameters = {
	'q': 'u2',
	'type': 'artist',
	'market': None,
	'limit': None,
	'offset': None,
}
querystring = ''.join([k + "=" + parameters[k] + "&" for k in parameters.keys() if parameters[k]])



data = r.get(baseURL+endpoint+'?'+querystring, headers={'Authorization':config.authToken})
print(json.dumps(data.json(), indent=4, sort_keys=True))