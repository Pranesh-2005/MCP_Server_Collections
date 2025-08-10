# Google Calendar MCP Server

This project is a Google Calendar MCP Server that allows you to interact with your Google Calendar using various tools. You can list events, create events, delete events, update events, and more.

## Features
- List upcoming events
- Create new events
- Delete events by ID
- Update event summaries
- Retrieve event details
- Search events by date or keyword
- Count events within a date range
- Show today's agenda
- List holidays for a specific country

## Prerequisites

1. **Python 3.7 or higher** installed on your system.  
   [Download Python](https://www.python.org/downloads/)

2. **Google Calendar API enabled** in your Google Cloud Console.
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project (or select an existing one).
   - Go to **APIs & Services > Library**.
   - Search for "Google Calendar API" and click **Enable**.

3. **Create OAuth credentials** and download `credentials.json`:
   - In the Cloud Console, go to **APIs & Services > Credentials**.
   - Click **Create Credentials** > **OAuth client ID**.
   - Choose **Desktop app** as the application type.
   - Name it (e.g., "Calendar MCP").
   - Click **Create** and then **Download** the `credentials.json` file.
   - Place the `credentials.json` file in your project directory.

4. **Add Redirect URI as localhost with the same port as in your code**  
   - When creating the OAuth client ID, add a redirect URI in the format:  
     ```
     http://localhost:PORT/
     ```
     Replace `PORT` with the port number you use in your code for `flow.run_local_server(port=PORT)`.  
     For example, if your code uses `flow.run_local_server(port=5001)`, add:
     ```
     http://localhost:5001/
     ```
   - This ensures Google authentication works correctly with your local server.

## Installation

1. **Clone the repository** or copy the code files to your local machine:
   ```bash
   git clone https://github.com/yourusername/calendar-mcp.git
   cd calendar-mcp
   ```

2. **Install required Python packages**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

## Setup

1. **Place your `credentials.json` file** in the root directory of the project.

2. **Run the server for the first time to authenticate with Google:**
   ```bash
   python calclaude.py
   ```
   - This will open a browser window for Google authentication.
   - Sign in with your Google account and allow access.
   - After successful authentication, a `calendar_token.pickle` file will be created for future use.

## Usage

### Running the Server

Start the MCP server:
```bash
python calclaude.py
```

### Using the Tools

You can use the following tools to interact with your Google Calendar:

- **List Events:**  
  `list_events(max_results=5)`

- **Create Event:**  
  `create_event(summary="Meeting", start="2025-06-21T10:00:00Z", end="2025-06-21T11:00:00Z")`

- **Delete Event:**  
  `delete_event(event_id="event_id_here")`

- **Update Event:**  
  `update_event(event_id="event_id_here", summary="Updated Meeting")`

- **Get Event Details:**  
  `get_event_details(event_id="event_id_here")`

- **Search Events by Date:**  
  `search_events_by_date(date_str="2025-06-21")`

- **Check Events on Date:**  
  `is_event_on_date(date_str="2025-06-21")`

- **Search Events by Keyword:**  
  `search_events_by_keyword(keyword="Meeting", max_results=10)`

- **Count Events in Range:**  
  `count_events_in_range(start_date="2025-06-01", end_date="2025-06-30")`

- **Get Today's Agenda:**  
  `get_today_agenda()`

- **List Holidays:**  
  `list_holidays(country="India", max_results=10)`

- **Hello Calendar:**  
  `hello_calendar(name="Friend")`

## Notes

- If you encounter authentication issues, delete the `calendar_token.pickle` file and re-run the authentication step.
- Make sure your `credentials.json` file is valid and matches your Google Cloud project.
- **Always ensure the redirect URI in your Google Cloud Console matches the port used in your code for `flow.run_local_server(port=PORT)`**.
