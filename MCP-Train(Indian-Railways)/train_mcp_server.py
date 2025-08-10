import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train-mcp")

load_dotenv()


# Initialize the MCP server
mcp = FastMCP("IRCTC MCP Server")

# Set your RapidAPI credentials
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")  # Ensure this environment variable is set
RAPIDAPI_HOST = "irctc1.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}"
INDIAN_RAIL_API_KEY = os.getenv("INDIAN_RAIL_API_KEY")  # Ensure this environment variable is set
INDIAN_RAIL_BASE_URL = "http://indianrailapi.com/api/v2"

HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST
}

@mcp.tool()
def station_name_to_code(station_name: str) -> dict:
    """
    Convert a station name to its code using Indian Rail API.
    Note name should be in uppercase (e.g., "ERODE JN").
    Parameters:
        station_name: The name of the station (e.g., "ERODE JN").
    """
    try:
        station_name = station_name.upper()
        url = f"{INDIAN_RAIL_BASE_URL}/StationNameToCode/apikey/{INDIAN_RAIL_API_KEY}/StationName/{station_name}"
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}



@mcp.tool()
def get_train_schedule_indian_rail(train_number: str) -> dict:
    """
    Get the schedule of a train by its number using Indian Rail API.
    Parameters:
        train_number: The train number (e.g., "19038").
    """
    try:
        url = f"{INDIAN_RAIL_BASE_URL}/TrainSchedule/apikey/{INDIAN_RAIL_API_KEY}/TrainNumber/{train_number}"
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_all_trains_on_station(station_code: str) -> dict:
    """
    Get all trains arriving at or departing from a station using Indian Rail API.
    Parameters:
        station_code: The station code (e.g., "NDLS").
    """
    try:
        url = f"{INDIAN_RAIL_BASE_URL}/AllTrainOnStation/apikey/{INDIAN_RAIL_API_KEY}/StationCode/{station_code}"
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def search_station(query: str) -> dict:
    """
    Search for a station by query.
    """
    try:
        url = f"{BASE_URL}/api/v1/searchStation"
        params = {"query": query}
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def search_train(query: str) -> dict:
    """
    Search for a train by query.
    """
    try:
        url = f"{BASE_URL}/api/v1/searchTrain"
        params = {"query": query}
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def find_trains_between_stations(from_station_code: str, to_station_code: str, date: str) -> dict:
    """
    Find trains between two stations on a specific date.
    Date format: YYYY-MM-DD
    """
    try:
        url = f"{BASE_URL}/api/v3/trainBetweenStations"
        params = {
            "fromStationCode": from_station_code,
            "toStationCode": to_station_code,
            "dateOfJourney": date
        }
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_train_schedule(train_number: str) -> dict:
    """
    Get the schedule of a train by its number.
    """
    try:
        url = f"{BASE_URL}/api/v1/getTrainSchedule"
        params = {"trainNo": train_number}
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_live_train_status(train_number: str, day: str = None) -> dict:
    """
    Get live status of a train.
    Optional File start day range from 0-4 0 = Day 1 1 = 1 Day Ago 2 = 2 Day Ago 3 = 3 Day Ago 4 = 4 Day Ago
    """
    try:
        url = f"{BASE_URL}/api/v1/liveTrainStatus"
        params = {
            "trainNo": train_number,
            "stratDay": day
        }
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_pnr_status(pnr_number: str) -> dict:
    """
    Get PNR status.
    """
    try:
        url = f"{BASE_URL}/api/v3/getPNRStatus"
        params = {"pnrNumber": pnr_number}
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def check_seat_availability(train_no: str, date: str, class_type: str, quota: str, from_station_code: str, to_station_code: str) -> dict:
    """
    Check seat availability for a train.
    Parameters:
        train_no: Train number (e.g., "19038").
        date: Date of journey in dd-mm-yyyy format.
        class_type: Class type (e.g., "2A").
        quota: Quota type (e.g., "GN").
        from_station_code: Source station code (e.g., "ST").
        to_station_code: Destination station code (e.g., "BVI").
    """
    try:
        url = f"{BASE_URL}/api/v1/checkSeatAvailability"
        params = {
            "trainNo": train_no,
            "date": date,
            "classType": class_type,
            "quota": quota,
            "fromStationCode": from_station_code,
            "toStationCode": to_station_code
        }
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_train_classes(train_number: str) -> dict:
    """
    Get available classes for a train.
    """
    try:
        url = f"{BASE_URL}/api/v1/getTrainClasses"
        params = {"trainNo": train_number}
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_fare(train_number: str, from_station_code: str, to_station_code: str) -> dict:
    """
    Get fare details for a train journey.
    """
    try:
        url = f"{BASE_URL}/api/v2/getFare"
        params = {
            "trainNo": train_number,
            "fromStationCode": from_station_code,
            "toStationCode": to_station_code,
        }
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_trains_by_station(station_code: str) -> dict:
    """
    Get trains arriving at or departing from a station on a specific date.
    """
    try:
        url = f"{BASE_URL}/api/v3/getTrainsByStation"
        params = {
            "stationCode": station_code
        }
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_live_station_status(from_station_code: str, hours: int, to_station_code: str = None) -> dict:
    """
    Get live status of trains at a station for the next few hours.
    Parameters:
        from_station_code: Source station code (e.g., "NDLS").
        hours: Number of hours to fetch live status for (e.g., 1).
        to_station_code: (Optional) Destination station code (e.g., "BVI").
    """
    try:
        url = f"{BASE_URL}/api/v3/getLiveStation"
        params = {
            "fromStationCode": from_station_code,
            "hours": hours
        }
        if to_station_code:
            params["toStationCode"] = to_station_code
        response = requests.get(url, headers=HEADERS, params=params, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    try:
        if "mcp dev" in " ".join(sys.argv):
            mcp.serve(host="127.0.0.1", port=5000, timeout=600)  # Set timeout to 600 seconds (10 minutes)
        else:
            mcp.serve(timeout=600)
    except Exception as e:
        logger.error(f"Error starting MCP server: {e}")