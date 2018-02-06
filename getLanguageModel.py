import json
import requests

def get_route_names_list() :
    r = requests.get('http://api.umd.io/v0/bus/routes/')
    values = []
    idList = []
    valList = []
    for route in r.json() :
        temp = umdio_route_to_alexa(route)
        if not temp['id'] in idList and not temp['name']['value'] in valList:
            idList.append(temp['id'])
            valList.append(temp['name']['value'])
            values.append(temp)
    return values

def umdio_route_to_alexa(route) :
    output = {}
    output['id'] = route['route_id']
    name = {}
    name['value'] = route['title']
    name['synonyms'] = route['title'].split(' ',1)
    output['name'] = name
    return output

def get_stop_names_list() :
    r = requests.get('http://api.umd.io/v0/bus/stops/')
    values = []
    idList = []
    valList = []
    for stop in r.json() :
        temp = umdio_stop_to_alexa(stop)
        if not temp['id'] in idList and not temp['name']['value'] in valList :
            idList.append(temp['id'])
            valList.append(temp['name']['value'])
            values.append(temp)
    return values

def umdio_stop_to_alexa(stop) :
    output = {}
    output['id'] = stop['stop_id']
    name = {}
    name['value'] = stop['title']
    name['synonyms'] = []
    output['name'] = name
    return output


model = {}
routeNameType = {}
routeNameType['name'] = 'routeNameType'
routeNameType['values'] = get_route_names_list()
stopNameType = {}
stopNameType['name'] = 'stopNameType'
stopNameType['values'] = get_stop_names_list()
model['types'] = [routeNameType, stopNameType]

print json.dumps(model, indent = 2)
