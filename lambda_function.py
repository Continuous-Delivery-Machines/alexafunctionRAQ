import json
import os
import pymysql


def lambda_handler(event, context):
    # on session start - output: welcome message and cloud formation stack info
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    # if the event was triggered by an uttered intent: check the intent name
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    # on session end - output: farewell and cloud formation stack info
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])


# check the intent name to get the intent type
def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    # the custom intents - output: will be determined later
    if intent_name == "TestIntent":
        return get_test_value()
    elif intent_name == "ProjectSizeByLanguage":
        return get_project_size_by_language(intent)
    elif intent_name == "CommitsWithCursesByLanguage":
        return get_commits_with_curses_by_language()
    elif intent_name == "LanguagesUsedTogether":
        return get_languages_used_together(intent)
    # the obligatory amazon-made Intents - output: basically placeholders
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


# session is started - output: message for our cloud formation stack
def on_session_started(session_started_request, session):
    print("Starting new session.")


# skill is started - output: generic greeting
def on_launch(launch_request, session):
    session_attributes = {}
    card_title = "RAQ"
    speech_output = "Welcome to RAQ. " \
                    "Rarely Asked Questions."
    reprompt_text = "Welcome to RAQ."
    should_end_session = False
    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


#  session is over - output: message for our cloud formation stack
def on_session_ended(session_ended_request, session):
    print("Ending session.")


# handling all amazon-made intents, ends the session and closes the skill - output: generic farewell
def handle_filler_request():
    session_attributes = {}
    card_title = "Thanks for visiting RAQ. Bye."
    speech_output = "Thanks for visiting RAQ. Bye"
    should_end_session = True
    return build_response(session_attributes, card_title, speech_output, None, should_end_session)


# test intent - output: database version via alexa or generic cover-up message on connection error
def get_test_value():
    session_attributes = {}
    card_title = "Test Value : DB Version"
    reprompt_text = "Something bad happened. Please try again later."
    speech_output = "Something bad happened. Please try again later."
    should_end_session = False
    connection = connection_to_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            db_version = cursor.fetchone()
    except:
        db_version = "unknown"
    else:
        cursor.close()
    finally:
        connection.close()
        reprompt_text = "Test my reprompt text"
        speech_output = "Testoutput: DB-Version is" + str(db_version)

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


# "average size by language" intent - output: language, size in byte or generic cover-up message on connection error
def get_project_size_by_language(intent):
    session_attributes = {}
    card_title = "Get the average project size for a language"
    reprompt_text = "Sorry, I don't know that one. Please try again."
    speech_output = "Sorry, I don't know that one. Please try again."
    should_end_session = False
    # if a programming language was found, build a query, ask the database and build the answer string
    programming_language = "Python"
    query_text = "SELECT TestTable.Attribute1 as attr1, TestTable.Attribute2 as attr2 FROM TestTable WHERE TestTable.Attribute1 = 'Python'"
    answer_text = get_database_information(query_text)
    if answer_text is not None:
        reprompt_text = "The average size of a" + programming_language + "project is" + answer_text + "Byte"
        speech_output = "The average size of a" + programming_language + "project is" + answer_text + "Byte"

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


# "language with most commits with curses" intent - output: language, amount or generic cover-up message on connection error
def get_commits_with_curses_by_language():
    session_attributes = {}
    card_title = "Get the most impolite language"
    reprompt_text = "Sorry, I don't know that one. Please try again."
    speech_output = "Sorry, I don't know that one. Please try again."
    should_end_session = False

    query_text = "SELECT TestTable.Attribute1 as attr1, TestTable.Attribute2 as attr2 FROM TestTable WHERE TestTable.Attribute1 = 'PHP'"
    answer_text = get_database_information(query_text)
    if answer_text is not None:
        reprompt_text = "The most commits with the word 'fuck' are found in" + answer_text + "projects"
        speech_output = "The most commits with the word 'fuck' are found in" + answer_text + "projects"

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


# "languages often used together" intent - output: language one and two or generic cover-up message on connection error
def get_languages_used_together(intent):
    session_attributes = {}
    card_title = "Get the languages best buddy"
    reprompt_text = "Sorry, I don't know that one. Please try again."
    speech_output = "Sorry, I don't know that one. Please try again."
    should_end_session = False

    # if a programming language was found, build a query, ask the database and build the answer string
    if "programminglanguage" in intent["slots"]:
        programming_language = intent["slots"]["programminglanguage"]["value"]
        query_text = "SELECT TestTable.Attribute1 as attr1, TestTable.Attribute2 as attr2 FROM TestTable WHERE TestTable.Attribute1 = 'C'"
        answer_text = get_database_information(query_text)
        if answer_text is not None:
            reprompt_text = programming_language + "is most commonly used with" + answer_text
            speech_output = programming_language + "is most commonly used with" + answer_text

    return build_response(session_attributes, card_title, speech_output, reprompt_text, should_end_session)


# connects to db,uses the prepared query string - output: required db entries as string
def get_database_information(query_string):
    connection = connection_to_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query_string)
            answer_from_db = cursor.fetchone()
    except:
        answer_from_db = None
    else:
        cursor.close()
    finally:
        connection.close()
    return answer_from_db


# connection to database - the encoded environment variables were put into the aws lambda console
def connection_to_db():
    return pymysql.connect(os.environ['DBENDPOINT'],
                           os.environ['DBUSER'],
                           os.environ['DBPASSWORD'],
                           os.environ['DBNAME'],
                           connect_timeout=5)


# function used for building the answer (JSON):
# session_attributes    - won't be used in this application
# title                 - card title for echo/simulator GUI
# output                - speech text for the answer
# reprompt_text         - speech text when nothing happened for a while
# should_end_session    - ends the session/closes the skill when true
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
