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
    


"""GET SCHEDULE"""
import datetime as dt
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError

import ollama
JsonCreds = r"C:\Users\aecti\OneDrive\Desktop\Projects\AI\2SEC-DISCORD\2SEC\scripts\2SEC\secrets\credentials.json"

SCOPES = ["https://www.googleapis.com/auth/calendar"]

Next10Schedules = []
msgagent = [{
    "role": "system",
    "content":  "You are not an AI assistant. You are an analyst bot providing detailed explanation on the student's schedule. You will be given two main things: the date, which you must reference, and the summary, which provides an overview of the event taking place. You do not speak or ask questions unless you are attempting to summarize the information within the array provided. For every date and summary of the schedule given, attempt to provide an overall analysis of the information in order for the user to better understand their schedule. Additionally, a prompt will be provided. Try to align your summary with the next provided prompt."
}]
def get_weather(prompt):
    global msgagent
    creds = None


    if os.path.exists(JsonCreds):
        print("it exists")
    else:
        print("ur cooked")

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

        event_result = service.events().list(calendarId="primary",timeMin=now,maxResults=10, singleEvents=True,orderBy="startTime").execute()

        events = event_result.get("items", [])

        if not events:
            print("No upcoming events found!")
            return
        
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
            appendable_event = start + " " + event["summary"]
            Next10Schedules.append(appendable_event)
        
            print()
        msgagent.append({"role": "user",
            "content": f'{Next10Schedules}' + f' PROMPT: {prompt}'})
        print(msgagent)
        response = ollama.chat(model="llama3.2:3b", messages=msgagent)
        print(response['message']['content'])

        return response['message']['content']
        


    except HttpError as error:
        print("Error occurred!: ", error)



if __name__ == "__main__":
    get_weather("Are there any tests")
