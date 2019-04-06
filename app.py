from datetime import datetime, timedelta
from json import JSONDecodeError

import pytz
import requests
from flask import Flask, Response, abort
from icalendar import Calendar, Event

app = Flask(__name__)

TIMEZONE = pytz.timezone('Asia/Yekaterinburg')


@app.route('/timetable/group/<c_id>')
def group_calendar(c_id):
    return generic_calendar(request_url='http://timetable.mris.mikhailche.ru/group/{}'.format(c_id))


@app.route('/timetable/prep/<c_id>')
def prep_calendar(c_id):
    return generic_calendar(request_url='http://timetable.mris.mikhailche.ru/prep/{}'.format(c_id))


@app.route('/timetable/aud/<c_id>')
def aud_calendar(c_id):
    return generic_calendar(request_url='http://timetable.mris.mikhailche.ru/aud/{}'.format(c_id))


def generic_calendar(request_url):
    r = requests.get(request_url)
    try:
        data = r.json()
    except JSONDecodeError:
        return abort(400)
    cal = Calendar()
    cal.add('prodid', '-//RSVPU timetable calendar//')
    cal.add('version', '2.0')
    for d in data:
        if not d:
            continue
        if len(d['name']) < 3:
            continue
        date_start = datetime.strptime(d['data'] + 'T' + d['time'], '%d.%m.%YT%H:%M')
        date_start.replace(tzinfo=TIMEZONE)

        name = ' '.join([d['name'], d['class_room'], d['name_of_pedagog']])

        event = Event()
        event.add('summary', name)
        event.add('dtstart', date_start)
        event.add('dtend', date_start + timedelta(hours=1, minutes=35))
        event.add('dtstamp', datetime.utcnow())
        cal.add_component(event)
    return Response(cal.to_ical(), mimetype='text/calendar')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
