import os
import sys
import logging
import datetime
import pickle
from mcp.server.fastmcp import FastMCP
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("calendar-mcp")

mcp = FastMCP("Google Calendar MCP Server")

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    try:
        if os.path.exists('calendar_token.pickle'):
            with open('calendar_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError("Missing credentials.json for Calendar API")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=5001)
            with open('calendar_token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        logger.error(f"Calendar auth error: {e}")
        raise

@mcp.tool()
def list_events(max_results: int = 5) -> str:
    """List upcoming events from Google Calendar."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary', timeMin=now, maxResults=max_results,
            singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events:
            return "No upcoming events found."
        output = []
        for e in events:
            summary = e.get('summary', '(No Title)')
            start = e['start'].get('dateTime', e['start'].get('date'))
            output.append(f"{summary} at {start}")
        return "\n".join(output)
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return "Failed to list events."

@mcp.tool()
def create_event(summary: str, start: str, end: str) -> str:
    """
    Create an event (ISO format e.g. 2025-06-01T10:00:00Z).
    """
    try:
        service = get_calendar_service()
        event = {
            'summary': summary,
            'start': {'dateTime': start, 'timeZone': 'UTC'},
            'end': {'dateTime': end, 'timeZone': 'UTC'}
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return "Failed to create event."

@mcp.tool()
def delete_event(event_id: str) -> str:
    """Delete an event by its ID."""
    try:
        service = get_calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"Deleted event {event_id}"
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        return "Failed to delete event."

@mcp.tool()
def update_event(event_id: str, summary: str) -> str:
    """Update the summary of an event."""
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        event['summary'] = summary
        updated = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return f"Updated event: {updated.get('htmlLink')}"
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        return "Failed to update event."

@mcp.tool()
def get_event_details(event_id: str) -> str:
    """Retrieve details of a specific event."""
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        summary = event.get('summary', '(No Title)')
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        return f"Summary: {summary}\nStart: {start}\nEnd: {end}"
    except Exception as e:
        logger.error(f"Error getting event details: {e}")
        return "Failed to get event details."

@mcp.tool()
def search_events_by_date(date_str: str) -> str:
    """
    Search and list all events on a specific date (format: YYYY-MM-DD).
    """
    try:
        service = get_calendar_service()
        start_of_day = f"{date_str}T00:00:00Z"
        end_of_day = f"{date_str}T23:59:59Z"

        events_result = service.events().list(
            calendarId='primary', timeMin=start_of_day, timeMax=end_of_day,
            singleEvents=True, orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return f"No events found on {date_str}."

        return "\n".join([f"{e.get('summary', '(No Title)')} at {e['start'].get('dateTime', e['start'].get('date'))}" for e in events])
    except Exception as e:
        logger.error(f"Error searching events by date: {e}")
        return "Failed to search events by date."

@mcp.tool()
def is_event_on_date(date_str: str) -> str:
    """
    Check if any event is scheduled on a given date (format: YYYY-MM-DD).
    """
    try:
        service = get_calendar_service()
        start_of_day = f"{date_str}T00:00:00Z"
        end_of_day = f"{date_str}T23:59:59Z"

        events_result = service.events().list(
            calendarId='primary', timeMin=start_of_day, timeMax=end_of_day,
            singleEvents=True, maxResults=1
        ).execute()

        events = events_result.get('items', [])
        return f"✅ Event exists on {date_str}" if events else f"❌ No events on {date_str}"
    except Exception as e:
        logger.error(f"Error checking events on date: {e}")
        return "Failed to check event."

@mcp.tool()
def search_events_by_keyword(keyword: str, max_results: int = 10) -> str:
    """
    Search events by title keyword.
    """
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary', timeMin=now, maxResults=100,
            singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        matched = [e for e in events if keyword.lower() in e.get('summary', '').lower()]

        if not matched:
            return f"No events found with keyword '{keyword}'."

        return "\n".join([f"{e.get('summary', '(No Title)')} at {e['start'].get('dateTime', e['start'].get('date'))}" for e in matched[:max_results]])
    except Exception as e:
        logger.error(f"Error searching events by keyword: {e}")
        return "Failed to search events by keyword."

@mcp.tool()
def count_events_in_range(start_date: str, end_date: str) -> str:
    """
    Count events between two dates (format: YYYY-MM-DD).
    """
    try:
        service = get_calendar_service()
        start = f"{start_date}T00:00:00Z"
        end = f"{end_date}T23:59:59Z"

        events_result = service.events().list(
            calendarId='primary', timeMin=start, timeMax=end,
            singleEvents=True
        ).execute()

        events = events_result.get('items', [])
        return f"🔢 Total events from {start_date} to {end_date}: {len(events)}"
    except Exception as e:
        logger.error(f"Error counting events: {e}")
        return "Failed to count events."

@mcp.tool()
def get_today_agenda() -> str:
    """
    Show events scheduled for today.
    """
    today = datetime.date.today().isoformat()
    return search_events_by_date(today)

@mcp.tool()
def list_holidays(country: str = "India", max_results: int = 10) -> str:
    """
    List upcoming holidays for a specified country. Currently supports basic predefined calendar IDs.

    :param country: Country name (e.g., India, US, UK)
    :param max_results: Max number of holidays to show
    """
    try:
        service = get_calendar_service()
        calendar_ids = {
            "India": "en.indian#holiday@group.v.calendar.google.com",
            "US": "en.usa#holiday@group.v.calendar.google.com",
            "UK": "en.uk#holiday@group.v.calendar.google.com"
        }

        # Default to India's holiday calendar if the country is not found
        cal_id = calendar_ids.get(country, "en.indian#holiday@group.v.calendar.google.com")
        now = datetime.datetime.utcnow().isoformat() + 'Z'

        # Fetch holidays from the specified calendar
        events_result = service.events().list(
            calendarId=cal_id,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        holidays = events_result.get('items', [])
        if not holidays:
            return f"No upcoming holidays found for {country}."

        # Format the output
        return "\n".join([f"{h.get('summary')} on {h['start'].get('date')}" for h in holidays])
    except Exception as e:
        logger.error(f"Error fetching holidays: {e}")
        return "Failed to fetch holidays."


@mcp.tool()
def hello_calendar(name: str = "Friend") -> str:
    return f"Hello {name}, welcome to your Google Calendar MCP!"

if __name__ == "__main__":
    mcp.run(transport="stdio")
