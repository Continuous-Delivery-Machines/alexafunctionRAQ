import json
import os
import pymysql


def lambda_handler(event, context):
    # on session start : greetings and cloud formation stack info
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    # on intent
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    # on session end : farewell and cloud formation stack info
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])


def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    # our custom intents
    if intent_name == "TestIntent":
        return get_test_value()
    elif intent_name == "ProjectSizeByLanguage":
        return get_project_size_by_language()
    elif intent_name == "CommitsWithCursesByLanguage":
        return get_commits_with_curses_by_language()
    elif intent_name == "LanguagesUsedTogether":
        return get_languages_used_together()
    # the amazon-made Intents : basically placeholders, triggers farewell as well
    elif intent_name == "AMAZON.FallBackIntent":
        return handle_filler_request()
    elif intent_name == "AMAZON.HelpIntent":
        return handle_filler_request()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_filler_request()
    elif intent_name == "AMAZON.NavigateHomeIntent":
        return handle_filler_request()
    else:
        raise ValueError("Invalid intent")


# session is started -> message for our cloud formation stack
def on_session_started(session_started_request, session):
    print("Starting new session.")


# generic greeting
def on_launch(launch_request, session):
    session_attributes = {}
    card_title = "RAQ"
    speech_output = "Welcome to RAQ. " \
                    "Rarely Asked Questions."
    reprompt_text = "Welcome to RAQ."
    should_end_session = False
    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


#  session is over - message for our cloud formation stack
def on_session_ended(session_ended_request, session):
    print("Ending session.")


# handling all intents
def handle_filler_request():
    session_attributes = {}
    card_title = "Thanks for visiting RAQ. Bye."
    speech_output = "Thanks for visiting RAQ. Bye"
    should_end_session = True
    return build_response(session_attributes, card_title, speech_output, None, should_end_session)


def get_test_value():
    session_attributes = {}
    card_title = "Test Value : DB Version"
    reprompt_text = "Test Value : DB Version"
    should_end_session = False

    connection = connection_to_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            db_version = cursor.fetchone()
    except:
        db_version = -1
    else:
        cursor.close()
    finally:
        connection.close()

    print(db_version)
    speech_output = "Mr Johnson, our. database . well. how do i. say it. version is " + str(db_version)
    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


def get_project_size_by_language():
    session_attributes = {}
    card_title = "get project size by language"
    reprompt_text = ""
    should_end_session = False
    speech_output = "Filler"
    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


def get_commits_with_curses_by_language():
    session_attributes = {}
    card_title = "hexes and curses"
    speech_output = "hexes are bad. " \
                    "really bad."
    reprompt_text = "hexes are bad"
    should_end_session = False

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


def get_languages_used_together():
    session_attributes = {}
    card_title = "Filler"
    reprompt_text = ""
    should_end_session = False
    speech_output = "Filler"
    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)

# connect to Database - the encoded environment variables were put into the aws lambda console
def connection_to_db():
    return pymysql.connect(os.environ['DBENDPOINT'],
                           os.environ['DBUSER'],
                           os.environ['DBPASSWORD'],
                           os.environ['DBNAME'],
                           connect_timeout=5)


# function used for building the answer (JSON)
def build_response(session_attributes, title, output, reprompt_text, should_end_session):
        return {
            "version": "1.0",
            "sessionAttributes": session_attributes,
            "response": {

                "outputSpeech": {
                    "type": "PlainText",
                    "text": output
                },
                "card": {
                    "type": "Simple",
                    "title": title,
                    "content": output
                },
                "reprompt": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": reprompt_text
                    }
                },
                "shouldEndSession": should_end_session
            }
        }
