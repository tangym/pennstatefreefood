import requests
from flask import Flask, render_template
from parsers import Event, PsuEngrEventParser, PsuEventParser


app = Flask(__name__)

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
    return True

@app.route('/')
def index():
    events = get_events()
    events = list(filter(has_free_food, events))
    return render_template('index.html', events=events)

app.run(host='0.0.0.0', port=8000, debug=True)
