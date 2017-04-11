import requests
from flask import Flask, render_template
from parsers import Event, PsuEngrEventParser


app = Flask(__name__)

def get_events():
    urls = {
        'http://www.engr.psu.edu/career/upcoming-events.aspx': PsuEngrEventParser(),
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

app.run(host='0.0.0.0', debug=True)
