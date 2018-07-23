import json
import requests

def get_routes() :
    r = requests.get('http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=umd')
    routes = []
    for route in r.json()['route'] :
        if route['title'].find(route['tag']) == 0 :
            routes.append((route['tag'], route['title'][len(route['tag'])+1:]))
        else :
            routes.append((route['tag'], route['title']))
    return routes

def get_stops() :
    routes = get_routes()
    stops = {}
    stopsList = []
    for route in routes :
        r = requests.get('http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=umd&r=' + route[0])
        for stop in r.json()['route']['stop'] :
            if stop['title'] in stops :
                stops[stop['title']].add(stop['tag'])
            else :
                stops[stop['title']] = set([stop['tag']])

    for title, tags in stops.iteritems() :
        stopTag = reduce(lambda x,acc: acc+","+x, tags, "")[:-1]
        stopsList.append((stopTag, title))
    return stopsList

types = []

routeNameTypeValues = []
for route in sorted(get_routes(), key=lambda route: route[0]) :
    routeObj = {}
    routeObj['id'] = route[0]
    routeNameObj = {}
    routeNameObj['value'] = route[0] + " " + route[1]
    routeNameObj['synonyms'] = [route[0], route[1]]
    routeObj['name'] = routeNameObj
    routeNameTypeValues.append(routeObj)
routeNameTypeObj = {}
routeNameTypeObj['name'] = 'routeNameType'
routeNameTypeObj['values'] = routeNameTypeValues

stopNameTypeValues = []
for stop in sorted(get_stops(), key=lambda route: route[0]) :
    stopObj = {}
    stopObj['id'] = stop[0]
    stopNameObj = {}
    stopNameObj['value'] = stop[1]
    stopNameObj['synonyms'] = []
    stopObj['name'] = stopNameObj
    stopNameTypeValues.append(stopObj)
stopNameTypeObj = {}
stopNameTypeObj['name'] = 'stopNameType'
stopNameTypeObj['values'] = stopNameTypeValues

typesList = [routeNameTypeObj, stopNameTypeObj]

print json.dumps(typesList, indent=4)
