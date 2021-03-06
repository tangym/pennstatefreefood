from datetime import timedelta
from bs4 import BeautifulSoup
import dateparser


class Event:
    def __init__(self, desc=[], location='', date='', time=''):
        self.desc = desc
        self.location = location
        self.date = dateparser.parse(date).date()
        time = time.split('-')
        if len(time) == 2:
            self.start_time = dateparser.parse(time[0])
            self.end_time = dateparser.parse(time[1])
            if 'a' not in time[0] and 'p' in time[1]:
                self.start_time += timedelta(hours=12)
            self.start_time, self.end_time = self.start_time.time(), self.end_time.time()
        else:
            self.start_time = dateparser.parse(time[0])
            self.end_time = None
            if 'a' not in time[0]:
                self.start_time += timedelta(hours=12)
            self.start_time = self.start_time.time()

    #
    def __str__(self):
        return '%s' % self.__dict__
    #
    def __repr__(self):
        return '%s(%r)' % (self.__class__, self.__dict__)


class BaseParser:
    def parse(self, text):
        soup = BeautifulSoup(text)
        return Event(self.contents(soup))
    #
    def contents(self, node):
        result = []
        try:
            if node.contents:
                for content in node.contents:
                    result += self.contents(content)
        except AttributeError as ae:
            if node.string and node.string.strip():
                result += [node.string.strip().replace('\u2013', '-')]
        return result


class PsuEngrEventParser(BaseParser):
    def parse(self, text):
        soup = BeautifulSoup(text)
        events = soup.findAll('div', {'class': 'Event_Block'})
        events = [self.__parse_event(event) for event in events]
        return events
    #
    def __parse_event(self, soup):
        event = self.contents(soup)
        try:
            date_index, time_index = (i for i in range(len(event)) 
                                        if dateparser.parse(event[i]))
        except ValueError as ve:
            # TODO: cannot parse the time of this event
            print(ve)
            return None
        # `location` is considered to be next to `time`
        # TODO: detect this field using `re` or keywords
        location_index = max(date_index, time_index) + 1
        desc = [event[i] for i in range(len(event)) 
                         if i not in [date_index, time_index, location_index]]
        return Event(desc, event[location_index], 
                     event[date_index], event[time_index])


class PsuEventParser(BaseParser):
    def parse(self, text):
        soup = BeautifulSoup(text)
        events = soup.findAll('td', {'class': 'listeventbg'})
        events = [[events[i + j] for j in range(4)]
                                 for i in range(len(events))[::4]]
        events = [self.__parse_event(event) for event in events]
        return events
    #
    def __parse_event(self, soups):
        # soups[0] is event icon
        date = self.contents(soups[1])[0]
        time = self.contents(soups[2])[0]
        desc = self.contents(soups[3])

        # `location` is considered to be next to `time`
        # TODO: detect this field using `re` or keywords
        if 'Location:' in desc:
            location_index = desc.index('Location:') + 1
            location = desc[location_index]
            desc = [desc[i] for i in range(len(desc)) 
                             if i not in [location_index - 1, location_index]]
        else:
            location = None
        return Event(desc, location, date, time)
