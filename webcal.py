import webapp2

from google.appengine.api import urlfetch
from google.appengine.ext import vendor

vendor.add('lib')

import icalendar

class MainPage(webapp2.RequestHandler):
  def get(self):
    result = urlfetch.fetch(
        'http://www.arsenal.com/_scripts/ical.ics?tid=1006&sid=123')
    calendar = icalendar.Calendar.from_ical(result.content)

    filtered_cal = icalendar.Calendar()
    filtered_cal.add('prodid', '-//Filtered Arsenal Calendar//foo//')
    filtered_cal.add('version', '2.0')

    for component in calendar.subcomponents:
      if 'LOCATION' in component:
        if 'Emirates Stadium' in component['LOCATION']:
          filtered_cal.add_component(component)

    self.response.content_type = 'text/calendar'
    self.response.headers.add(
        'Cache-Control', 'max-age=3600')
    self.response.out.write(filtered_cal.to_ical())


app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
