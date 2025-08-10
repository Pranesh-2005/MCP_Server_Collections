import os
import base64
import mimetypes
from mcp.server.fastmcp import FastMCP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging
import sys
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gmail-mcp")

mcp = FastMCP("Gmail MCP Server")

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def get_gmail_service():
    creds = None
    try:
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("credentials.json"):
                    logger.error("Missing credentials.json file.")
                    raise FileNotFoundError("OAuth credentials file not found.")
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        logger.error(f"Error initializing Gmail service: {e}")
        raise

@mcp.tool()
def list_emails(max_results: int = 5) -> str:
    """List recent emails from inbox with body content."""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId="me", maxResults=max_results).execute()
        messages = results.get("messages", [])
        if not messages:
            return "No messages found."
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "(Unknown Sender)")
            body = msg_data.get("snippet", "(No Body)")
            output.append(f"From: {sender}\nSubject: {subject}\nBody: {body}\n")
        return "\n---\n".join(output)
    except Exception as e:
        logger.error(f"Error listing emails: {e}")
        return "Failed to list emails."

@mcp.tool()
def send_email(to: str, subject: str, body: str, attachment_path: str = "") -> str:
    """Send an email with optional attachment."""
    try:
        service = get_gmail_service()
        message = MIMEMultipart()
        message["to"] = to
        message["subject"] = subject
        message.attach(MIMEText(body, "plain"))

        if attachment_path and os.path.exists(attachment_path):
            mime_type, _ = mimetypes.guess_type(attachment_path)
            if mime_type:
                mime_type, mime_subtype = mime_type.split("/")
            else:
                mime_type, mime_subtype = "application", "octet-stream"
            with open(attachment_path, "rb") as f:
                part = MIMEBase(mime_type, mime_subtype)
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return f"Email sent to {to} with ID: {sent['id']}"
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return "Failed to send email."

@mcp.tool()
def get_email_by_id(email_id: str) -> str:
    """Retrieve full content of a specific email including body."""
    try:
        service = get_gmail_service()
        message = service.users().messages().get(userId="me", id=email_id, format="full").execute()
        headers = message.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"].lower() == "form"), "(Unknown Sender)")
        body = message.get("snippet", "(No Body)")
        return f"Email ID: {email_id}\nFrom: {sender}\nSubject: {subject}\nBody: {body}"
    except Exception as e:
        logger.error(f"Error retrieving email by ID: {e}")
        return "Failed to retrieve email."


@mcp.tool()
def search_emails_by_sender_using_sender_email_address(sender_email: str, max_results: int = 5) -> str:
    """Search and retrieve emails received from a specific sender including body."""
    try:
        service = get_gmail_service()
        query = f"from:{sender_email}"
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        if not messages:
            return f"No emails found from {sender_email}."
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            body = msg_data.get("snippet", "(No Body)")
            output.append(f"Subject: {subject}\nBody: {body}")
        return f"Emails received from {sender_email}:\n" + "\n---\n".join(output)
    except Exception as e:
        logger.error(f"Error searching emails by sender: {e}")
        return "Failed to retrieve emails."

@mcp.tool()
def search_emails_sent_by_me(recipient_email: str, max_results: int = 5) -> str:
    """Search and retrieve emails sent to a specific recipient including body."""
    try:
        service = get_gmail_service()
        query = f"to:{recipient_email}"
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        if not messages:
            return f"No emails found sent to {recipient_email}."
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            body = msg_data.get("snippet", "(No Body)")
            output.append(f"Subject: {subject}\nBody: {body}")
        return f"Emails sent to {recipient_email}:\n" + "\n---\n".join(output)
    except Exception as e:
        logger.error(f"Error searching emails by recipient: {e}")
        return "Failed to retrieve emails."

@mcp.tool()
def forward_email_to(from_email: str, to_email: str, max_recent: int = 1) -> str:
    """Forward most recent emails from one address to another."""
    try:
        service = get_gmail_service()
        # First find recent emails from the sender
        query = f"from:{from_email}"
        results = service.users().messages().list(userId="me", q=query, maxResults=max_recent).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return f"No emails found from {from_email} to forward"
            
        forwarded_count = 0
        for msg in messages:
            try:
                # Get original email content
                msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
                headers = msg_data.get("payload", {}).get("headers", [])
                subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
                body = msg_data.get("snippet", "(No Body)")
                
                # Create forward message
                message = MIMEMultipart()
                message["to"] = to_email
                message["subject"] = f"Fwd: {subject}"
                forward_body = f"---------- Forwarded message ----------\nFrom: {from_email}\nSubject: {subject}\n\n{body}"
                message.attach(MIMEText(forward_body, "plain"))
                
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                service.users().messages().send(userId="me", body={"raw": raw}).execute()
                forwarded_count += 1
                
            except Exception as e:
                logger.error(f"Error forwarding individual email: {e}")
                
        return f"Successfully forwarded {forwarded_count} email(s) from {from_email} to {to_email}"
    except Exception as e:
        logger.error(f"Error in forward operation: {e}")
        return "Failed to forward emails"

@mcp.tool()
def search_emails_with_attachments(email_address: str, max_results: int = 5) -> str:
    """Search for emails with attachments from a specific email address."""
    try:
        service = get_gmail_service()
        query = f"from:{email_address} has:attachment"
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return f"No emails with attachments found from {email_address}"
            
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "(No Date)")
            
            output.append(
                f"From: {email_address}\n"
                f"Subject: {subject}\n"
                f"Date: {date}\n"
                f"Status: Contains attachment(s)"
            )
        
        return "\n\n---\n\n".join(output)
    except Exception as e:
        logger.error(f"Error searching emails with attachments: {e}")
        return f"Failed to search emails with attachments from {email_address}"

@mcp.tool()
def search_emails_by_date_from(email_address: str, days_ago: int = 7) -> str:
    """Search for emails from a specific address within the last X days."""
    try:
        service = get_gmail_service()
        query = f"from:{email_address} newer_than:{days_ago}d"
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return f"No emails found from {email_address} in the last {days_ago} days"
            
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "(No Date)")
            body = msg_data.get("snippet", "(No Body)")
            
            output.append(
                f"From: {email_address}\n"
                f"Subject: {subject}\n"
                f"Date: {date}\n"
                f"Preview: {body}"
            )
        
        return "\n\n---\n\n".join(output)
    except Exception as e:
        logger.error(f"Error searching recent emails: {e}")
        return f"Failed to search recent emails from {email_address}"

@mcp.tool()
def search_important_emails(email_address: str, max_results: int = 5) -> str:
    """Search for important emails from a specific email address."""
    try:
        service = get_gmail_service()
        query = f"from:{email_address} is:important"
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return f"No important emails found from {email_address}"
            
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "(No Date)")
            body = msg_data.get("snippet", "(No Body)")
            
            output.append(
                f"From: {email_address}\n"
                f"Subject: {subject}\n"
                f"Date: {date}\n"
                f"Preview: {body}"
            )
        
        return "\n\n---\n\n".join(output)
    except Exception as e:
        logger.error(f"Error searching important emails: {e}")
        return f"Failed to search important emails from {email_address}"

@mcp.tool()
def search_unread_from(email_address: str, max_results: int = 5) -> str:
    """Search for unread emails from a specific email address."""
    try:
        service = get_gmail_service()
        query = f"from:{email_address} is:unread"
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return f"No unread emails found from {email_address}"
            
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "(No Date)")
            body = msg_data.get("snippet", "(No Body)")
            
            output.append(
                f"From: {email_address}\n"
                f"Subject: {subject}\n"
                f"Date: {date}\n"
                f"Preview: {body}"
            )
        
        return "\n\n---\n\n".join(output)
    except Exception as e:
        logger.error(f"Error searching unread emails: {e}")
        return f"Failed to search unread emails from {email_address}"


@mcp.tool()
def search_unread_from(email_address: str, max_results: int = 5) -> str:
    """Search for unread emails from a specific email address."""
    try:
        service = get_gmail_service()
        query = f"from:{email_address} is:unread"
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return f"No unread emails found from {email_address}"
            
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "(No Date)")
            body = msg_data.get("snippet", "(No Body)")
            
            output.append(
                f"From: {email_address}\n"
                f"Subject: {subject}\n"
                f"Date: {date}\n"
                f"Preview: {body}"
            )
        
        return "\n\n---\n\n".join(output)
    except Exception as e:
        logger.error(f"Error searching unread emails: {e}")
        return f"Failed to search unread emails from {email_address}"
    
@mcp.tool()
def search_starred_emails(max_results: int = 5) -> str:
    """Search for starred emails in your inbox."""
    try:
        service = get_gmail_service()
        query = "is:starred"
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return "No starred emails found"
            
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "(Unknown Sender)")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "(No Date)")
            body = msg_data.get("snippet", "(No Body)")
            
            output.append(
                f"From: {sender}\n"
                f"Subject: {subject}\n"
                f"Date: {date}\n"
                f"Preview: {body}"
            )
        
        return "\n\n---\n\n".join(output)
    except Exception as e:
        logger.error(f"Error searching starred emails: {e}")
        return "Failed to search starred emails"

@mcp.tool()
def search_starred_from(email_address: str, max_results: int = 5) -> str:
    """Search for starred emails from a specific email address."""
    try:
        service = get_gmail_service()
        query = f"from:{email_address} is:starred"
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return f"No starred emails found from {email_address}"
            
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "(No Date)")
            body = msg_data.get("snippet", "(No Body)")
            
            output.append(
                f"From: {email_address}\n"
                f"Subject: {subject}\n"
                f"Date: {date}\n"
                f"Preview: {body}"
            )
        
        return "\n\n---\n\n".join(output)
    except Exception as e:
        logger.error(f"Error searching starred emails from sender: {e}")
        return f"Failed to search starred emails from {email_address}"

@mcp.tool()
def star_email(email_address: str, subject: str) -> str:
    """Star an email by searching for it using sender's email and subject."""
    try:
        service = get_gmail_service()
        query = f"from:{email_address} subject:{subject}"
        results = service.users().messages().list(userId="me", q=query, maxResults=1).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return f"No email found with subject '{subject}' from {email_address}"
            
        msg_id = messages[0]["id"]
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"addLabelIds": ["STARRED"]}
        ).execute()
        
        return f"Successfully starred email from {email_address} with subject '{subject}'"
    except Exception as e:
        logger.error(f"Error starring email: {e}")
        return "Failed to star email"

@mcp.tool()
def unstar_email(email_address: str, subject: str) -> str:
    """Unstar an email by searching for it using sender's email and subject."""
    try:
        service = get_gmail_service()
        query = f"from:{email_address} subject:{subject} is:starred"
        results = service.users().messages().list(userId="me", q=query, maxResults=1).execute()
        messages = results.get("messages", [])
        
        if not messages:
            return f"No starred email found with subject '{subject}' from {email_address}"
            
        msg_id = messages[0]["id"]
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"removeLabelIds": ["STARRED"]}
        ).execute()
        
        return f"Successfully unstarred email from {email_address} with subject '{subject}'"
    except Exception as e:
        logger.error(f"Error unstarring email: {e}")
        return "Failed to unstar email"

@mcp.tool()
def hello_gmail(name: str = "World") -> str:
    return f"Hello {name}, welcome to Gmail MCP!"

if __name__ == "__main__":
    print("Starting Gmail MCP server...")
    try:
        if "mcp dev" in " ".join(sys.argv):
            mcp.serve(host="127.0.0.1", port=5000)
        else:
            mcp.serve()
    except Exception as e:
        logger.error(f"Error starting MCP server: {e}")