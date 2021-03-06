import os
import re
import subprocess

from intents import determine_intent
from speech_to_text import speech_to_text
import re

DEFAULT_TEXT_TO_SAY = "Sorry, I could not understand"


def speak(output: str):
    subprocess.run(['python3', 'text-to-speech/tts.py', output])


def execute_weather_action(weather_intent):
    process = subprocess.run(['python3', 'daemon/barryd.py', 'config', 'get', 'weather_api_key'],
                             stdout=subprocess.PIPE)
    weather_api_key = process.stdout.decode('utf-8').rstrip()
    if weather_api_key == '':
        try:
            with open('actions/weather/api_key') as f:
                weather_api_key = f.read()
        except FileNotFoundError:
            speak("You do not have a weather API key")
            return

    city = weather_intent.get('Location')
    if city is None:
        process = subprocess.run(['python3', 'daemon/barryd.py', 'config', 'get', 'city'],
                                 stdout=subprocess.PIPE)
        output = process.stdout.decode('utf-8').rstrip()
        if output != '':
            city = output
        else:
            speak("No location is specified")
            return

    process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'weather', weather_api_key, city],
                             stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8').rstrip()

    speak(output)


def execute_joke_action():
    process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'joke'], stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8').rstrip()

    speak(output)


def execute_what_is_action(what_is_intent):
    subject = what_is_intent.get('Subject')
    if subject is None:
        speak("Please specify a subject")
        return

    process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'what_is', subject], stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8').rstrip()

    speak(output)


def execute_time_action():
    process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'time'], stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8').rstrip()

    speak(output)


def execute_news_action(news_intent):
    process = subprocess.run(['python3', 'daemon/barryd.py', 'config', 'get', 'news_api_key'],
                             stdout=subprocess.PIPE)
    news_api_key = process.stdout.decode('utf-8').rstrip()
    if news_api_key == '':
        try:
            with open('actions/news/api_key') as f:
                news_api_key = f.read()
        except FileNotFoundError:
            speak("You do not have a news API key")
            return

    topic = news_intent.get('Topic')
    if topic is not None:

        process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'news', news_api_key, topic],
                                 stdout=subprocess.PIPE)
        output = process.stdout.decode('utf-8').rstrip()

        speak(output)
    else:
        speak('Please provide a topic')


def execute_todo_action(todo_intent):
    action = todo_intent.get('TodoCommand')
    list_type = todo_intent.get('ListType')

    storage_path = os.getcwd() + "/actions/todo/lists.json"
    if action == 'add' or action == 'remove':
        item = todo_intent.get('Item')

        process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'todo', action, list_type, item, storage_path],
                                 stdout=subprocess.PIPE)
        output = process.stdout.decode('utf-8').rstrip()
        speak(output)
    elif action == 'get' or action == 'tell me':
        process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'todo', 'get', list_type, storage_path],
                                 stdout=subprocess.PIPE)
        output = process.stdout.decode('utf-8').rstrip()
        speak(output)
    elif action == 'clear':
        process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'todo', action, list_type, storage_path],
                                 stdout=subprocess.PIPE)
        output = process.stdout.decode('utf-8').rstrip()
        speak(output)
    else:
        speak("Unknown action")


def execute_alarm_action(alarm_intent):
    time = alarm_intent.get('Time')
    weekday = alarm_intent.get('Weekday')

    pattern = re.compile(r'(\d\d?)[: ](\d\d)')
    match = pattern.search(time)
    if match is None:
        speak("Please specify time and day for the alarm")
        return

    hours = match.group(1)
    minutes = match.group(2)

    if weekday is None:
        process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'alarm', hours, minutes],
                                 stdout=subprocess.PIPE)
        output = process.stdout.decode('utf-8').rstrip()
        speak(output)
    else:
        process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'alarm', hours, minutes, weekday],
                                 stdout=subprocess.PIPE)
        output = process.stdout.decode('utf-8').rstrip()
        speak(output)


def execute_reminder_action(reminder_intent):
    action = reminder_intent.get('Action')

    tokens = reminder_intent.get('Time').split(' ')
    seconds, minutes, days, hours = '0', '0', '0', '0'

    for i, token in enumerate(tokens):
        if token == 'seconds':
            seconds = tokens[i - 1]
        elif token == 'minutes':
            minutes = tokens[i - 1]
        elif token == 'hours':
            hours = tokens[i - 1]
        elif token == 'days':
            days = tokens[i - 1]

    process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'reminder', seconds, minutes, hours, days, action],
                             stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8').rstrip()
    speak(output)


def execute_timer_action(timer_intent):
    tokens = timer_intent.get('Time').split(' ')
    seconds, minutes, days, hours = '0', '0', '0', '0'

    for i, token in enumerate(tokens):
        if token == 'seconds':
            seconds = tokens[i - 1]
        elif token == 'minutes':
            minutes = tokens[i - 1]
        elif token == 'hours':
            hours = tokens[i - 1]
        elif token == 'days':
            days = tokens[i - 1]

    process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'timer', seconds, minutes, hours, days],
                             stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8').rstrip()
    speak(output)

def execute_agenda_action(agenda_intent) -> bool:
    process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'read-google-calendar'], stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8').rstrip()

    speak(output)
    return True


def execute_add_event_action(input) -> bool:
    event_name_re = re.search('called (?P<event_name>.+?)(?=from|to|at|on|until)', input)
    location_re = re.search('at (?P<location>[a-zA-Z0-9 ]+?)(?=from|to|at|on|until)', input)
    start_date_re = re.search('(on the)(?<!until the) ((?P<start_date>\d+?)(?=st|nd|rd|th))', input)
    start_time_re = re.search('at (?P<start_time>([0-9]{1,4}:?[0-9]{0,2} ?(p\.m\.|a\.m\.)?)).*', input)
    end_date_re = re.search('(until the) ((?P<end_date>\d+?)(?=st|nd|rd|th))', input)
    end_time_re = re.search('(?<=until the \d{2}(st|nd|rd|th) of) \w*? at (?P<end_time>([0-9]{1,4}:?[0-9]{0,2} ?(p\.m\.|a\.m\.)?))', input)

    event_name = event_name_re.groupdict()['event_name']

    if location_re.groupdict()['location'] is not None:
        location = location_re.groupdict()['location']
        start_date = start_date_re.groupdict()['start_date']
        end_date = end_date_re.groupdict()['end_date']
        if start_time_re.groupdict()['start_time'] is not None:
            start_time = start_time_re.groupdict()['start_time']
            end_time = end_time_re.groupdict()['end_time']
            process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'add-event', event_name, location,
                                      start_date, start_time, end_date, end_time],
                                     stdout=subprocess.PIPE)
        else:
            process = subprocess.run(
                ['python3', 'daemon/barryd.py', 'exec', 'add-event', event_name, location, start_date,
                 end_date],
                stdout=subprocess.PIPE)
    else:
        start_date = start_date_re.groupdict()['start_date']
        end_date = end_date_re.groupdict()['end_date']
        if start_time_re.groupdict()['start_time'] is not None:
            start_time = start_time_re.groupdict()['start_time']
            end_time = end_time_re.groupdict()['end_time']
            process = subprocess.run(['python3', 'daemon/barryd.py', 'exec', 'add-event', event_name,
                                      start_date, start_time, end_date, end_time],
                                     stdout=subprocess.PIPE)
        else:
            process = subprocess.run(
                ['python3', 'daemon/barryd.py', 'exec', 'add-event', event_name, start_date,
                 end_date],
                stdout=subprocess.PIPE)

    output = process.stdout.decode('utf-8').rstrip()

    speak(output)
    return True


if __name__ == "__main__":
    text = speech_to_text.recognize(speech_to_text.get_audio(timeout=10, phrase_time_limit=10, save=False))
    print(text)
    if text is None:
        speak(DEFAULT_TEXT_TO_SAY)
        exit(0)

    # The daemon has to be started in order to execute a command
    intent = determine_intent(text)

    if intent is None:
        speak(DEFAULT_TEXT_TO_SAY)
        exit(0)

    intent_type = intent.get('intent_type')
    if intent_type == 'WeatherIntent':
        execute_weather_action(intent)
    elif intent_type == 'JokeIntent':
        execute_joke_action()
    elif intent_type == 'WhatIsIntent':
        execute_what_is_action(intent)
    elif intent_type == 'TimeIntent':
        execute_time_action()
    elif intent_type == 'NewsIntent':
        execute_news_action(intent)
    elif intent_type == 'TodoIntent':
        execute_todo_action(intent)
    elif intent_type == 'AlarmIntent':
        execute_alarm_action(intent)
    elif intent_type == 'ReminderIntent':
        execute_reminder_action(intent)
    elif intent_type == 'TimerIntent':
        execute_timer_action(intent)
    elif intent.get('intent_type') == 'AgendaIntent':
        execute_agenda_action(intent)
    elif intent.get('intent_type') == 'AddEventIntent':
        execute_add_event_action(text)
