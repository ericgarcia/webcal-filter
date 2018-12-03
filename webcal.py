import jinja2
import logging
import os
import webapp2

from google.appengine.api import urlfetch
from google.appengine.ext import vendor

vendor.add('lib')

import icalendar

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class CalendarFilterPage(webapp2.RequestHandler):
  def get(self):
    calendar_url = self.request.get('url')
    
    result = urlfetch.fetch(calendar_url)
    calendar = icalendar.Calendar.from_ical(result.content)

    for component in calendar.subcomponents:
      for k, v in component.items():
        if isinstance(v, icalendar.prop.vText):
          component[k] = '\n'.join([line if len(line) < 75 else line[:74] for line in v.splitlines()])

    self.response.content_type = 'text/calendar'
    self.response.headers.add(
        'Cache-Control', 'max-age=3600')
    self.response.headers.add(
        'Content-Disposition', 'attachment; filename="calendar.ical"')
    self.response.out.write(calendar.to_ical())


class CalendarViewPage(webapp2.RequestHandler):
  def get(self):
    calendar_url = self.request.get('url')
    filter_spec = self.request.get('filter')
    calendar_filter = CalendarFilter(filter_spec)
    filtered_calendar = calendar_filter.Filter(calendar_url)

    events = [self.CreateEvent(e) for e in filtered_calendar.subcomponents if e.name == 'VEVENT']

    template = JINJA_ENVIRONMENT.get_template('calendar.html')
    self.response.write(template.render({
        'events': events,
        'title': filtered_calendar['X-WR-CALNAME'],
    }))

  def CreateEvent(self, vevent):
    event = {}
    logging.info(vevent)
    if 'SUMMARY' in vevent:
      event['name'] = vevent['SUMMARY']
    if 'DTSTART' in vevent:
      event['date_start'] = vevent['DTSTART'].dt.strftime('%A %d %B %Y %H:%M')
    if 'DTEND' in vevent:
      event['date_end'] = vevent['DTEND'].dt.strftime('%A %d %B %Y %H:%M')
    if 'LOCATION' in vevent:
      event['location'] = vevent['LOCATION']
    return event


class CalendarFilter(object):
  def __init__(self, filter_spec):
    self.filter = FilterSpec(filter_spec)

  def Filter(self, url):
    result = urlfetch.fetch(url)
    # http://www.arsenal.com/_scripts/ical.ics?tid=1006&sid=123
    calendar = icalendar.Calendar.from_ical(result.content)

    filtered_cal = icalendar.Calendar()
    for k, v in calendar.items():
      filtered_cal.add(k, v)

    for component in calendar.subcomponents:
      if self.filter.ShouldFilter(component):
        filtered_cal.add_component(component)
    return filtered_cal



class FilterSpec(object):
  def __init__(self, filter_spec):
    split = filter_spec.split(':')
    self.property = split[0]
    self.content = split[1]

  def ShouldFilter(self, event):
    return self.property in event and self.content in event[self.property]


app = webapp2.WSGIApplication([
    ('/calendar', CalendarFilterPage),
    ('/view', CalendarViewPage),
], debug=True)
