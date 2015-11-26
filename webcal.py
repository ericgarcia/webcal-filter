import logging
import webapp2

from google.appengine.api import urlfetch
from google.appengine.ext import vendor

vendor.add('lib')

import icalendar

class CalendarFilterPage(webapp2.RequestHandler):
  def get(self):
    calendar_url = self.request.get('url')
    result = urlfetch.fetch(calendar_url)
    # http://www.arsenal.com/_scripts/ical.ics?tid=1006&sid=123
    calendar = icalendar.Calendar.from_ical(result.content)

    filtered_cal = icalendar.Calendar()
    for k, v in calendar.items():
      filtered_cal.add(k, v)

    filter_spec = FilterSpec(self.request.get('filter'))

    for component in calendar.subcomponents:
      if filter_spec.ShouldFilter(component):
        filtered_cal.add_component(component)

    self.response.content_type = 'text/calendar'
    self.response.headers.add(
        'Cache-Control', 'max-age=3600')
    self.response.headers.add(
        'Content-Disposition', 'attachment; filename="calendar.ical"')
    self.response.out.write(filtered_cal.to_ical())


class FilterSpec(object):
  def __init__(self, filter_spec):
    split = filter_spec.split(':')
    self.property = split[0]
    self.content = split[1]

  def ShouldFilter(self, event):
    return self.property in event and self.content in event[self.property]


app = webapp2.WSGIApplication([
    ('/calendar', CalendarFilterPage),
], debug=True)
