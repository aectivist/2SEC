import json
import httpx


"""GET WEATHER"""
def get_weather(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'  # Use 'imperial' for Fahrenheit
    }

    try: 
        response = httpx.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        json_response = {
            "city": data['name'],
            "temperature": data['main']['temp'],
            "description": data['weather'][0]['description'],
            "humidity": data['main']['humidity'],
            "wind_speed": data['wind']['speed']
        }
        return json.dumps(json_response, indent=4)  # Return as a formatted JSON string
    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
    

    


import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError
JsonCreds = r"\secrets\credentials.json"

SCOPES = ["http://www.googleapis.com/auth/calendar"]

def main():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(JsonCreds, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    try:
        service = build("calendar", "v3", credentials=creds)

        now = dt.datetime.now().isoformat() + "Z"

        event_result = service.events().list(calendarID="primary", timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime") #gives 10 upcoming events

        events = event_result.get("items", [])

        if not events:
            print("No upcoming events found!")
            return
        
        for event in events:
            start = event["start"].get("dateTime", event["Start"].get("date"))
            print(start, event["Summary"])
            print()
    except HttpError as error:
        print("Error occurred!: ", error)

if __name__ == "__main__":
    main()