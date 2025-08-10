import os
import asyncio
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from whatsapp_api_client_python import API
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsapp-mcp")

load_dotenv()

mcp = FastMCP("WhatsApp MCP Server")

GREENAPI_INSTANCE_ID = os.getenv("GREENAPI_INSTANCE_ID")
GREENAPI_API_TOKEN = os.getenv("GREENAPI_API_TOKEN")

whatsapp = API.GreenAPI(GREENAPI_INSTANCE_ID, GREENAPI_API_TOKEN)

async def resolve_chat_id(contact_identifier: str) -> str:
    """Resolve a contact name or number to a WhatsApp chat ID."""
    if contact_identifier.isdigit():
        return f"{contact_identifier}@c.us"
    if "@c.us" in contact_identifier:
        return contact_identifier
    response = await asyncio.to_thread(whatsapp.serviceMethods.getContacts)
    if response.code != 200:
        raise ValueError("Failed to fetch contact list.")
    for contact in response.data:
        if contact_identifier.lower() in contact.get("name", "").lower():
            return contact["id"]
    raise ValueError(f"Contact '{contact_identifier}' not found.")

@mcp.tool()
async def open_session() -> str:
    """Check if the WhatsApp session is active."""
    try:
        response = await asyncio.to_thread(whatsapp.account.getStateInstance)
        return "WhatsApp session is active." if response.code == 200 else f"Failed: {response.data}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def send_message(contact: str, message: str) -> str:
    """Send a message to a contact."""
    try:
        chat_id = await resolve_chat_id(contact)
        response = await asyncio.to_thread(whatsapp.sending.sendMessage, chat_id, message)
        return f"Message sent to {contact}." if response.code == 200 else f"Failed: {response.data}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_chats(group: bool = None, count: int = None) -> str:
    """Retrieve the list of chats. Optionally filter by group/personal and limit count."""
    try:
        response = whatsapp.serviceMethods.getContacts()
        if response.code != 200:
            return f"Failed: {response.data}"

        contacts = response.data or []
        # Filter by group if specified
        if group is not None:
            contacts = [c for c in contacts if (c.get("type") == "group") == group]
        # Limit count if specified
        if count is not None:
            contacts = contacts[:count]

        if not contacts:
            return "No contacts found. If this persists, try rescanning the QR code or contact support."

        lines = []
        for contact in contacts:
            contact_type = contact.get("type", "")
            name = contact.get("name") or contact.get("contactName") or "No name"
            lines.append(f"{name} ({contact['id']}) [{contact_type}]")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def create_group(group_name: str, participants: list[str]) -> str:
    """Create a group chat."""
    try:
        # Ensure all participants are in WhatsApp chatId format
        chat_ids = []
        for p in participants:
            if p.endswith("@c.us") or p.endswith("@g.us"):
                chat_ids.append(p)
            elif p.isdigit():
                chat_ids.append(f"{p}@c.us")
            else:
                # Try to resolve by contact name
                chat_ids.append(await resolve_chat_id(p))

        payload = {
            "groupName": group_name,
            "chatIds": chat_ids
        }
        # Use asyncio.to_thread to avoid blocking if the client is sync
        response = await asyncio.to_thread(whatsapp.groups.createGroup, **payload)
        if response.code == 200 and response.data.get("created"):
            return (
                f"Group '{group_name}' created!\n"
                f"Group ID: {response.data.get('chatId')}\n"
                f"Invite Link: {response.data.get('groupInviteLink', 'N/A')}"
            )
        return f"Failed: {response.data}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_group_participants(group_id: str) -> str:
    """Get participants of a group chat."""
    try:
        response = await asyncio.to_thread(whatsapp.groups.getGroupData, group_id)
        if response.code == 200:
            participants = response.data.get("participants", [])
            return "\n".join(p["id"] for p in participants)
        return f"Failed: {response.data}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def view_messages(contact: str, limit: int = 5) -> str:
    """View recent messages from a contact."""
    try:
        chat_id = await resolve_chat_id(contact)
        try:
            limit = max(1, min(100, int(limit)))
        except ValueError:
            return "Error: limit must be a positive integer"
        payload = {"chatId": chat_id, "count": limit}
        response = await asyncio.to_thread(whatsapp.journals.getChatHistory, **payload)
        if response.code != 200 or not response.data:
            logger.error(f"API Error: {response.data}")
            return f"Failed to get messages: {response.data}"
        messages = response.data[::-1]
        formatted_messages = []
        for msg in messages:
            timestamp = msg.get("timestamp", "Unknown")
            message_type = msg.get("typeMessage", "Unknown")
            sender = msg.get("senderName", "You" if msg.get("type") == "outgoing" else "Unknown")
            status = f" [{msg.get('statusMessage', 'unknown')}]" if msg.get("type") == "outgoing" else ""
            if message_type == "textMessage":
                text = msg.get("textMessage", "No text")
                formatted_messages.append(f"[{timestamp}] {sender}{status}: {text}")
            elif message_type in ["imageMessage", "videoMessage", "documentMessage", "audioMessage", "stickerMessage"]:
                caption = msg.get("caption", "")
                file_type = message_type.replace("Message", "")
                url = msg.get("downloadUrl", "No URL")
                formatted_messages.append(f"[{timestamp}] {sender}{status} sent {file_type}: {caption} (URL: {url})")
            elif message_type == "locationMessage":
                location = msg.get("location", {})
                name = location.get("nameLocation", "Unknown location")
                coords = f"({location.get('latitude', '?')}, {location.get('longitude', '?')})"
                formatted_messages.append(f"[{timestamp}] {sender}{status} shared location: {name} {coords}")
            elif message_type == "contactMessage":
                contact_data = msg.get("contact", {})
                name = contact_data.get("displayName", "Unknown contact")
                formatted_messages.append(f"[{timestamp}] {sender}{status} shared contact: {name}")
            elif message_type == "pollMessage":
                poll_data = msg.get("pollMessageData", {})
                question = poll_data.get("name", "Unknown poll")
                options = ", ".join(opt.get("optionName", "") for opt in poll_data.get("options", []))
                formatted_messages.append(f"[{timestamp}] {sender}{status} created poll: {question} [Options: {options}]")
            elif message_type == "pollUpdateMessage":
                poll_data = msg.get("pollMessageData", {})
                question = poll_data.get("name", "Unknown poll")
                votes = [f"{vote['optionName']}: {len(vote['optionVoters'])}" for vote in poll_data.get("votes", [])]
                formatted_messages.append(f"[{timestamp}] Poll update for '{question}' - Votes: {', '.join(votes)}")
            elif message_type == "quotedMessage":
                text = msg.get("extendedTextMessage", {}).get("text", "No text")
                quoted_msg = msg.get("quotedMessage", {})
                quoted_type = quoted_msg.get("typeMessage", "unknown")
                formatted_messages.append(f"[{timestamp}] {sender}{status} replied to {quoted_type}: {text}")
            else:
                formatted_messages.append(f"[{timestamp}] {sender}{status} sent {message_type}")
            if msg.get("isDeleted"):
                formatted_messages[-1] += " (deleted)"
            elif msg.get("isEdited"):
                formatted_messages[-1] += " (edited)"
        return "\n\n".join(formatted_messages) if formatted_messages else "No messages found"
    except Exception as e:
        logger.error(f"Error in view_messages: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
async def get_message(message_id: str) -> str:
    """Retrieve a specific message by its ID."""
    try:
        response = await asyncio.to_thread(whatsapp.journals.getMessage, message_id)
        if response.code == 200:
            message = response.data
            return f"Message: {message.get('textMessageData', {}).get('textMessage', 'No text')}"
        return f"Failed to retrieve message: {response.data}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_last_incoming_messages(minutes: int = 1440) -> str:
    """View recent incoming messages across all chats."""
    try:
        minutes = max(1, int(minutes))
        response = await asyncio.to_thread(whatsapp.journals.lastIncomingMessages, minutes)
        if response.code != 200 or not response.data:
            logger.error(f"API Error: {response.data}")
            return f"Failed to get messages: {response.data}"
        messages = response.data[::-1]
        formatted_messages = []
        for msg in messages:
            timestamp = msg.get("timestamp", "Unknown")
            sender = msg.get("senderName", msg.get("senderContactName", "Unknown"))
            chat_id = msg.get("chatId", "Unknown Chat")
            message_type = msg.get("typeMessage", "Unknown")
            if message_type == "textMessage":
                text = msg.get("textMessage", "No text")
                formatted_messages.append(f"[{timestamp}] {sender} ({chat_id}): {text}")
            elif message_type in ["imageMessage", "videoMessage", "documentMessage", "audioMessage", "stickerMessage"]:
                caption = msg.get("caption", "")
                url = msg.get("downloadUrl", "No URL")
                formatted_messages.append(f"[{timestamp}] {sender} ({chat_id}) sent {message_type.replace('Message', '')}: {caption} (URL: {url})")
            elif message_type == "locationMessage":
                location = msg.get("location", {})
                name = location.get("nameLocation", "Unknown location")
                formatted_messages.append(f"[{timestamp}] {sender} ({chat_id}) shared location: {name}")
            elif message_type == "contactMessage":
                contact = msg.get("contact", {})
                name = contact.get("displayName", "Unknown contact")
                formatted_messages.append(f"[{timestamp}] {sender} ({chat_id}) shared contact: {name}")
            else:
                formatted_messages.append(f"[{timestamp}] {sender} ({chat_id}) sent {message_type}")
            if msg.get("isForwarded"):
                formatted_messages[-1] += f" (forwarded {msg.get('forwardingScore', 1)}x)"
            if msg.get("isDeleted"):
                formatted_messages[-1] += " (deleted)"
            if msg.get("isEdited"):
                formatted_messages[-1] += " (edited)"
        return "\n\n".join(formatted_messages) if formatted_messages else "No messages found"
    except Exception as e:
        logger.error(f"Error in get_last_incoming_messages: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
async def get_last_outgoing_messages(minutes: int = 1440) -> str:
    """View recent outgoing messages across all chats."""
    try:
        minutes = max(1, int(minutes))
        response = await asyncio.to_thread(whatsapp.journals.lastOutgoingMessages, minutes)
        if response.code != 200:
            logger.error(f"API Error: {response.data}")
            return f"Failed to get messages: {response.data}"
        if not response.data:
            return "No outgoing messages found"
        messages = response.data[::-1]
        formatted_messages = []
        for msg in messages:
            timestamp = msg.get("timestamp", "Unknown")
            message_id = msg.get("idMessage", "Unknown")
            chat_id = msg.get("chatId", "Unknown Chat")
            status = msg.get("statusMessage", "unknown")
            message_type = msg.get("typeMessage", "Unknown")
            if message_type == "extendedTextMessage":
                extended_data = msg.get("extendedTextMessage", {})
                text = extended_data.get("text", msg.get("textMessage", "No text"))
                description = extended_data.get("description", "")
                title = extended_data.get("title", "")
                message_text = f"[{timestamp}] ID: {message_id} To {chat_id} [{status}]: {text}"
                if title or description:
                    message_text += f"\nTitle: {title}\nDescription: {description}"
                if extended_data.get("isForwarded"):
                    message_text += f" (forwarded {extended_data.get('forwardingScore', 1)}x)"
                formatted_messages.append(message_text)
            elif message_type == "textMessage":
                text = msg.get("textMessage", "No text")
                formatted_messages.append(f"[{timestamp}] ID: {message_id} To {chat_id} [{status}]: {text}")
            elif message_type in ["imageMessage", "videoMessage", "documentMessage", "audioMessage", "stickerMessage"]:
                caption = msg.get("caption", "")
                url = msg.get("downloadUrl", "No URL")
                file_type = message_type.replace("Message", "")
                formatted_messages.append(
                    f"[{timestamp}] ID: {message_id} To {chat_id} [{status}] "
                    f"sent {file_type}: {caption} (URL: {url})"
                )
            else:
                formatted_messages.append(
                    f"[{timestamp}] ID: {message_id} To {chat_id} [{status}] "
                    f"sent {message_type}"
                )
            if msg.get("sendByApi"):
                formatted_messages[-1] += " (sent via API)"
            if msg.get("isDeleted"):
                formatted_messages[-1] += " (deleted)"
            if msg.get("isEdited"):
                formatted_messages[-1] += " (edited)"
        return "\n\n".join(formatted_messages)
    except Exception as e:
        logger.error(f"Error in get_last_outgoing_messages: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
async def mark_chat_unread(contact: str) -> str:
    """Mark chat messages as unread."""
    try:
        chat_id = await resolve_chat_id(contact)
        response = await asyncio.to_thread(whatsapp.marking.readChat, chat_id)
        return f"Chat marked as unread." if response.code == 200 else f"Failed: {response.data}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def check_whatsapp_number(phone: str) -> str:
    """Check if a phone number has WhatsApp account."""
    try:
        response = await asyncio.to_thread(whatsapp.serviceMethods.checkWhatsapp, phone)
        if response.code == 200:
            return "Phone number has WhatsApp" if response.data.get("existsWhatsapp") else "Phone number doesn't have WhatsApp"
        return f"Failed to check number: {response.data}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_contact_info(contact: str) -> str:
    """Get detailed information about a contact."""
    try:
        chat_id = await resolve_chat_id(contact)
        response = await asyncio.to_thread(whatsapp.serviceMethods.getContactInfo, chat_id)
        if response.code == 200:
            info = response.data
            return (
                f"Contact Info:\n"
                f"Name: {info.get('name', 'Unknown')}\n"
                f"Phone: {info.get('phone', 'Unknown')}\n"
                f"Status: {info.get('status', 'Unknown')}\n"
                f"Avatar: {info.get('avatar', 'No avatar')}"
            )
        return f"Failed to get contact info: {response.data}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_my_details() -> str:
    """Get detailed information about your WhatsApp account."""
    try:
        state, status, wa_settings, settings = await asyncio.gather(
            asyncio.to_thread(whatsapp.account.getStateInstance),
            asyncio.to_thread(whatsapp.account.getStatusInstance),
            asyncio.to_thread(whatsapp.account.getWaSettings),
            asyncio.to_thread(whatsapp.account.getSettings)
        )
        if not all(r.code == 200 for r in [state, status, wa_settings, settings]):
            errors = []
            if state.code != 200: errors.append("state")
            if status.code != 200: errors.append("status")
            if wa_settings.code != 200: errors.append("WA settings")
            if settings.code != 200: errors.append("account settings")
            return f"Failed to get: {', '.join(errors)}"
        status_data = status.data
        state_data = state.data
        wa_data = wa_settings.data
        settings_data = settings.data
        return (
        f"WhatsApp Account Status:\n"
        f"Phone Number: {wa_data.get('phone', 'Unknown')}\n"
        f"State: {state_data.get('stateInstance', 'Unknown')}\n"
        f"Connection: {status_data.get('statusInstance', 'Unknown')}\n"
        f"Avatar URL: {wa_data.get('avatar', 'No avatar')}\n"
        f"Device ID: {wa_data.get('deviceId', 'Unknown')}\n\n"
        f"Account Settings:\n"
        f"Webhook URL: {settings_data.get('webhookUrl', 'Not set')}\n"
        f"Message Delay: {settings_data.get('delaySendMessagesMilliseconds', 0)}ms\n"
        f"Mark Messages Read: {settings_data.get('markIncomingMessagesReaded', 'no')}\n"
        f"Keep Online: {settings_data.get('keepOnlineStatus', 'no')}\n"
        f"Notifications:\n"
        f"- Incoming: {settings_data.get('incomingWebhook', 'no')}\n"
        f"- Outgoing: {settings_data.get('outgoingWebhook', 'no')}\n"
        f"- Calls: {settings_data.get('incomingCallWebhook', 'no')}\n"
        f"- Polls: {settings_data.get('pollMessageWebhook', 'no')}\n"
        f"- Edits: {settings_data.get('editedMessageWebhook', 'no')}\n"
        f"- Deletions: {settings_data.get('deletedMessageWebhook', 'no')}"
    )
    except Exception as e:
        logger.error(f"Error in get_my_details: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
async def update_profile_picture(image_path: str) -> str:
    """Update your WhatsApp profile picture."""
    try:
        if not os.path.exists(image_path):
            return "Error: Image file not found"
        response = await asyncio.to_thread(whatsapp.account.setProfilePicture, image_path)
        return "Profile picture updated successfully" if response.code == 200 else f"Failed: {response.data}"
    except Exception as e:
        logger.error(f"Error in update_profile_picture: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool()
async def get_account_status() -> str:
    """Get the current status of your WhatsApp account connection."""
    try:
        state, status = await asyncio.gather(
            asyncio.to_thread(whatsapp.account.getStateInstance),
            asyncio.to_thread(whatsapp.account.getStatusInstance)
        )
        if state.code != 200 or status.code != 200:
            return "Failed to get account status"
        return (
            f"Account Status:\n"
            f"State: {state.data.get('stateInstance', 'Unknown')}\n"
            f"Status: {status.data.get('statusInstance', 'Unknown')}\n"
            f"Substatus: {status.data.get('subStatusInstance', 'Unknown')}"
        )
    except Exception as e:
        logger.error(f"Error in get_account_status: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")