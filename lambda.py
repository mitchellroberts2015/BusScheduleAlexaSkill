from __future__ import print_function
import json
import requests

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_cardless_speechlet_response(output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def build_delegate_response():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = {}
    response['response'] = message
    return response


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    speech_output = "Welcome to Terp Tracker. " \
                    "Ask me what time a bus will arrive."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Sorry, don't know that one."
    should_end_session = False
    return build_response(session_attributes, build_cardless_speechlet_response(
        speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = ""
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def get_arrival_request(intent, request):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    """ Make sure we've got all the fields we need to make a query """
    if (not ('value' in intent['slots']['routeName'])) or (not ('value' in intent['slots']['stopName'])) :
        return build_delegate_response()
    else :
        print(intent['slots']['routeName'])
        print(intent['slots']['stopName'])
        stop_name = intent['slots']['stopName']['value']
        route_name = intent['slots']['routeName']['value']
        session_attributes = {}

        stop_status = intent['slots']['stopName']['resolutions']['resolutionsPerAuthority'][0]['status']['code']
        route_status = intent['slots']['routeName']['resolutions']['resolutionsPerAuthority'][0]['status']['code']
        if stop_status == "ER_SUCCESS_NO_MATCH" or route_status == "ER_SUCCESS_NO_MATCH" :
            return build_response(session_attributes, build_cardless_speechlet_response(
                "Sorry, I didn't understand that.", None, True))

        card_title = "Terp Tracker arrival times"
        stop_id = intent['slots']['stopName']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        stop_name = intent['slots']['stopName']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
        route_id = intent['slots']['routeName']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']
        route_name = intent['slots']['routeName']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
        speech_output = get_arrival_times_text(route_id, stop_id, route_name, stop_name)

        reprompt_text = "Sorry, I didn't understand that."
        should_end_session = True
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

def is_on_route(stopTag, routeTag) :
    r = requests.get('http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=umd&r=' + routeTag)
    for stop in r.json()['route']['stop'] :
        if stop['tag'] == stopTag :
            return True
    return False

def stop_on_route(stopTags, routeTag) :
    for stop in stopTags :
        if is_on_route(stop, routeTag) :
            return stop
    return None

def get_predictions(stopTag, routeTag) :
    r = requests.get('http://webservices.nextbus.com/service/publicJSONFeed?command=predictions&a=umd&r=' + routeTag + '&s=' + stopTag)
    if not 'predictions' in r.json() :
        return None
    if not 'direction' in r.json()['predictions'] :
        return []
    predictions = []
    for prediction in r.json()['predictions']['direction']['prediction'] :
        predictions.append(prediction['minutes'])
    return predictions

def get_arrival_times_text(route, stop, route_name, stop_name) :
    stopMatch = stop_on_route(stop.split(','), route)
    if stopMatch is None :
        return 'The ' + route_name + ' bus route does not include the ' + \
        stop_name + ' stop.'

    predictions = get_predictions(stopMatch, route)
    if len(predictions) == 0 :
        return 'The ' + route_name + ' bus is not currently operating.'

    if len(predictions) == 1 :
        return 'The ' + route_name + ' bus will arrive at the ' + \
        stopName +  ' stop in ' + predictions[0] + ' minute' + ('' if predictions[0] == 1 else 's') + '.'
    elif len(predictions) == 2 :
        return 'The ' + route_name + ' bus will arrive at the ' + \
        stopName +  ' stop in ' + predictions[0] + ' minute' + ('' if predictions[0] == 1 else 's') + \
        ' and ' + predictions[1] + ' minute' + ('' if predictions[0] == 1 else 's') + '.'
    else :
        output = 'The ' + route_name + ' bus will arrive at the ' + \
        stopName +  ' stop in '
        for time in predictions[:-1] :
            output += time + ' minute' + ('' if time == '1' else 's') + ', '
        output += 'and ' + predictions[-1] + ' minute' + ('' if predictions[-1] == 1 else 's') + '.'
        return output


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    elif intent_name == "getArrivals":
        return get_arrival_request(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] !=
        "amzn1.ask.skill.a1baf3a1-7e22-46b0-b202-4d26039289cb"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
