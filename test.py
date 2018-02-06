import json
import requests

def get_arrival_times(route, stop) :
    r = requests.get('http://api.umd.io/v0/bus/routes/' + route + '/arrivals/' + stop)
    times = []
    for i in r.json().get('predictions').get('direction').get('prediction') :
      times.append(i.get('minutes'))
    return times

def get_arrival_times_text(route, stop) :
    output = ""
    times = get_arrival_times(route, stop)
    r = requests.get('http://api.umd.io/v0/bus/routes/' + route + '/arrivals/' + stop)
    if len(times) == 0 :
        output = 'There are no scheduled arrivals for the ' + + r.json().get('predictions').get('routeTitle') + ' bus at the ' + \
        r.json().get('predictions').get('stopTitle') +  ' stop.'
    elif len(times) == 1 :
        output = 'The ' + r.json().get('predictions').get('routeTitle') + ' bus will arrive at the ' + \
        r.json().get('predictions').get('stopTitle') +  ' stop in ' + times[0] + ' minute' + ('' if times[0] == 1 else 's') + '.'
    else :
        output = 'The ' + r.json().get('predictions').get('routeTitle') + ' bus will arrive at the ' + \
        r.json().get('predictions').get('stopTitle') +  ' stop in '
        for time in times[:-1] :
            output += time + ' minute' + ('' if time == '1' else 's') + ', '
        output += 'and ' + times[-1] + ' minute' + ('' if times[-1] == 1 else 's') + '.'
    return output

print get_arrival_times_text('105','sccomm5_6')
