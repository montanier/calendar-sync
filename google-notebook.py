# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-api-python-client==2.157.0",
#     "google-auth-oauthlib==1.2.1",
#     "icalendar==6.1.0",
#     "marimo",
#     "protobuf==5.29.3",
#     "pytz==2024.2",
#     "requests==2.32.3",
#     "recurring-ical-events==3.7.0",
# ]
# ///

import marimo

__generated_with = "0.13.7"
app = marimo.App(width="medium")


@app.cell
def _():
    from datetime import datetime, timedelta
    import pytz
    import os.path

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from icalendar import Calendar

    import marimo as mo
    import requests
    return (
        Calendar,
        Credentials,
        InstalledAppFlow,
        Request,
        build,
        datetime,
        mo,
        os,
        pytz,
        requests,
        timedelta,
    )


@app.cell
def _(mo):
    ics_url = mo.cli_args().get("ics")
    google_calendar = mo.cli_args().get("google")
    return google_calendar, ics_url


@app.cell
def _(ics_url, requests):
    r = requests.get(ics_url, allow_redirects=True)
    open('calendar.ics', 'wb').write(r.content)
    return


@app.cell
def _(Calendar, datetime, pytz, timedelta):
    import recurring_ical_events

    now = datetime.now(tz=pytz.timezone('Europe/Paris'))
    yesterday = now - timedelta(days=1)
    in_two_weeks = now + timedelta(days=14)

    events_to_push = []
     
    with open('calendar.ics', 'rb') as cal_file:
        gcal = Calendar.from_ical(cal_file.read())
        start_date = (2025, 5, 13)
        end_date =   (2025,  5, 14)
        for event in recurring_ical_events.of(gcal).between(yesterday, in_two_weeks):
            if event['X-MICROSOFT-CDO-BUSYSTATUS'] in ['BUSY', 'TENTATIVE']:
                start_event = datetime.fromisoformat(str(event['DTSTART'].dt))
                if start_event.tzinfo is None:
                    start_event = pytz.timezone('Europe/Paris').localize(start_event)
    
                end_event = datetime.fromisoformat(str(event['DTEND'].dt))
                if end_event.tzinfo is None:
                    end_event = pytz.timezone('Europe/Paris').localize(end_event)
    
                events_to_push.append((start_event, end_event))
    return (events_to_push,)


@app.cell
def _(events_to_push):
    events_to_push
    return


@app.cell
def _():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    return (SCOPES,)


@app.cell
def _(Credentials, InstalledAppFlow, Request, SCOPES, os):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return (creds,)


@app.cell
def _(build, creds, google_calendar):
    service = build("calendar", "v3", credentials=creds)
    calendar_id = google_calendar
    return calendar_id, service


@app.cell
def _(calendar_id, service):
    # remove previous events
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")

    for event_in_google_cal in events:
        start = event_in_google_cal["start"].get("dateTime", event_in_google_cal["start"].get("date"))
        print(start, event_in_google_cal["summary"])
        service.events().delete(calendarId=calendar_id, eventId=event_in_google_cal["id"]).execute()
        print("removed")
    return


@app.cell
def _(calendar_id, events_to_push, service):
    from pprint import pprint

    for event_to_add in events_to_push:

        event_body = {
            'summary': 'busy',
            'start': {
                'dateTime': event_to_add[0].isoformat(),
                'timeZone': 'Europe/Paris'
            },
            'end': {
                'dateTime': event_to_add[1].isoformat(),
                'timeZone': 'Europe/Paris'
            },
        }
        pprint(event_body)

        service.events().insert(calendarId=calendar_id, body=event_body).execute()
        print("added")
    return


if __name__ == "__main__":
    app.run()
