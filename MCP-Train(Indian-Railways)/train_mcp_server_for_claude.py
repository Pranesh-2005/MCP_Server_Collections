import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train-mcp")

load_dotenv()

# Initialize the MCP server
mcp = FastMCP("IRCTC MCP Server")
INDIAN_RAIL_API_KEY = os.getenv("INDIAN_RAIL_API_KEY")  # Ensure this environment variable is set
INDIAN_RAIL_BASE_URL = "http://indianrailapi.com/api/v2"

async def fetch_data(url: str) -> dict:
    """
    Helper function to fetch data asynchronously using aiohttp.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=300) as response:
                response.raise_for_status()
                return await response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def station_name_to_code(station_name: str) -> dict:
    """
    Convert a station name to its code using Indian Rail API.
    Parameters:
        station_name: The name of the station (e.g., "ERODE JN").
    """
    station_name = station_name.upper()
    url = f"{INDIAN_RAIL_BASE_URL}/StationNameToCode/apikey/{INDIAN_RAIL_API_KEY}/StationName/{station_name}"
    return await fetch_data(url)

@mcp.tool()
async def get_train_schedule_indian_rail(train_number: str) -> dict:
    """
    Get the schedule of a train by its number using Indian Rail API.
    Parameters:
        train_number: The train number (e.g., "19038").
    """
    url = f"{INDIAN_RAIL_BASE_URL}/TrainSchedule/apikey/{INDIAN_RAIL_API_KEY}/TrainNumber/{train_number}"
    return await fetch_data(url)

@mcp.tool()
async def get_all_trains_on_station(station_code: str) -> dict:
    """
    Get all trains arriving at or departing from a station using Indian Rail API.
    Parameters:
        station_code: The station code (e.g., "NDLS").
    """
    station_code = station_code.upper()
    url = f"{INDIAN_RAIL_BASE_URL}/AllTrainOnStation/apikey/{INDIAN_RAIL_API_KEY}/StationCode/{station_code}"
    return await fetch_data(url)

@mcp.tool()
async def get_live_station_status(station_code: str, hours: int) -> dict:
    """
    Get live status of trains at a station for the next few hours.
    Parameters:
        station_code: The station code (e.g., "NDLS").
        hours: Number of hours to fetch live status for (e.g., 2 or 4).
    """
    station_code = station_code.upper()
    url = f"{INDIAN_RAIL_BASE_URL}/LiveStation/apikey/{INDIAN_RAIL_API_KEY}/StationCode/{station_code}/hours/{hours}"
    return await fetch_data(url)

@mcp.tool()
async def get_live_train_status(train_number: str, date: str) -> dict:
    """
    Get live status of a train.
    Parameters:
        train_number: The train number (e.g., "19038").
        date: Date of journey in yyyymmdd format.
    """
    url = f"{INDIAN_RAIL_BASE_URL}/livetrainstatus/apikey/{INDIAN_RAIL_API_KEY}/trainnumber/{train_number}/date/{date}"
    return await fetch_data(url)

@mcp.tool()
async def get_train_fare(train_number: str, station_from: str, station_to: str, quota: str) -> dict:
    """
    Get fare details for a train journey.
    Parameters:
        train_number: The train number (e.g., "19038").
        station_from: Source station code (e.g., "NDLS").
        station_to: Destination station code (e.g., "BCT").
        quota: Quota type (e.g., "GN").
    """
    station_from = station_from.upper()
    station_to = station_to.upper()
    url = f"{INDIAN_RAIL_BASE_URL}/TrainFare/apikey/{INDIAN_RAIL_API_KEY}/TrainNumber/{train_number}/From/{station_from}/To/{station_to}/Quota/{quota}"
    return await fetch_data(url)

@mcp.tool()
async def get_train_information(train_number: str) -> dict:
    """
    Get detailed information about a train.
    Parameters:
        train_number: The train number (e.g., "19038").
    """
    url = f"{INDIAN_RAIL_BASE_URL}/TrainInformation/apikey/{INDIAN_RAIL_API_KEY}/TrainNumber/{train_number}"
    return await fetch_data(url)

@mcp.tool()
async def find_trains_between_stations(from_station: str, to_station: str) -> dict:
    """
    Find trains between two stations.
    Parameters:
        from_station: Source station code (e.g., "NDLS").
        to_station: Destination station code (e.g., "BCT").
    """
    from_station = from_station.upper()
    to_station = to_station.upper()
    url = f"{INDIAN_RAIL_BASE_URL}/TrainBetweenStation/apikey/{INDIAN_RAIL_API_KEY}/From/{from_station}/To/{to_station}"
    return await fetch_data(url)

if __name__ == "__main__":
    mcp.run(transport="stdio")