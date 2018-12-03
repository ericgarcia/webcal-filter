# webcal-filter
Many people have been having trouble syncing events to Google Calendar. The problem is that the Facebook ical export does not enforce the 75-character limit for the ical format.

I created a fix for this in Google App Engine. It's a simple app that returns an ical link after fixing the formatting. You can create your own app in Google App Engine to run this yourself or just use the app that I have running at https://fb-gcal-224419.appspot.com/calendar.

## 1) Copy the iCal url for your Facebook Events
The text after `url=` needs to be the link you get from copying the link from your Upcoming Events in Facebook:
![alt text](fb_events_link.png?raw=true "Get the iCal link for your Facebook Events")

## 2) Encode the url
The link url must be encoded, so you must first pass it through a tool like [this](www.url-encode-decode.com).

## 3) Replace {url} below with your encoded url to create a formatted calendar link
```
https://fb-gcal-224419.appspot.com/calendar?url={url}
```
## Use this new calendar link in Google Calendar
Once you have created your own formatted calendar link, you can paste this into the URL for a new calendar in Google Calendar.
### Example formatted link:
```
https://fb-gcal-224419.appspot.com/calendar?url=https%3A%2F%2Fwww.facebook.com%2Fevents%2Fical%2Fupcoming%2F%3Fuid%3D{uid}%26key%3D{key}
```
