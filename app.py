from datetime import datetime
import threading
import requests
from flask import Flask, render_template
from parsers import Event, PsuEngrEventParser, PsuEventParser


app = Flask(__name__)
events = []

def get_events():
    urls = {
        'http://www.engr.psu.edu/career/upcoming-events.aspx': 
            PsuEngrEventParser(),
        'http://www.events.psu.edu/cgi-bin/cal/webevent.cgi?cmd=listweek&cat=&sib=1&sort=m,e,t&ws=0&cf=list&set=1&swe=1&sa=1&de=1&tf=0&sb=1&stz=Default&cal=cal299': 
            PsuEventParser(),
    }
    events = []
    for url, parser in urls.items():
        r = requests.get(url)
        events += parser.parse(r.text)
    return events

def has_free_food(event):
    # keyword criterion
    # TODO: use a language model instead
    keywords = ['food', 'pizza', 'appetizer']
    for keyword in keywords:
        for desc in event.desc:
            if keyword in desc.lower():
                return True

    # time criterion
    # TODO: check whether two time span overlap or not
    lunch_start = datetime(1, 1, 1, 10, 30).time()
    lunch_end = datetime(1, 1, 1, 12, 30).time()
    dinner_start = datetime(1, 1, 1, 17, 00).time()
    dinner_end = datetime(1, 1, 1, 19, 30).time()
    if (lunch_start < event.start_time < lunch_end or 
        dinner_start < event.start_time < dinner_end):
        return True
    return False

@app.route('/')
def index():
    food_events = list(filter(has_free_food, events))
    return render_template('index.html', events=food_events)

def update_events():
    global events
    events = get_events()
    t = threading.Timer(1800, update_events)
    t.daemon = True
    t.start()

update_events()
app.run(host='0.0.0.0', port=8000, debug=True)
