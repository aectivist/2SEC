import ollama 
import json
from SettingsAPI_Disc import weather_api_key

from discordTools import get_weather,      get_schedule
sec2_Function_Usecase = 0
Function_Passed = 0



def should_enable_tools(prompt: str) -> bool: #specific keywords to enable tools
    keywords = ["weather", "city", "temperature", "humidity", "wind", "test", "exam", "event", "school events", "school related news", "updates"
                ]
    
    if any(word.lower() in prompt.lower() for word in keywords):
        print("Key word detected, finding a match")
        return True
    else:
        print("nothing found loser")
        return False

#Creates the available functions that can be called by the model


Function_Found = False ## Flag to check if a function was called
import json
#Tools list for the model to use
tools_list = [ #Only to note but the weather model was only implemented for proof of concept that it works and Im not restarted 
                {
                    "type": "function",
                    "function": {
                        "name": "get_schedule",
                        "description": "Get ten calendar events and updates for BS-Cybersecurity (CSEC) College of Saint Benilde schedule related queries.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "description": "User's schedule related query"}
                            },
                            "required": ["prompt"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get the current weather for a city.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name to check weather for"}
                            },
                            "required": ["city"]
                        }
                    }
                }
                
            ]

#Function to handle the sec2 model and its function calls

def sec2_FUNCTION(prompt, messageX):
    global Function_Found, sec2_Function_Usecase
    sec2_Function_Usecase = 1
    messages = []
    messages.extend(messageX)
    system_notifymess =  {
            "role": "system",
            "content": "You will receive structured data (like JSON strings) or an analysis that may answer the user's prompt. When you do, interpret it and explain it clearly in a natural sentence. If you do not however receive anything useful then do not ask for examples, just state that no information can be found or if it's totally necessary then tell them to contact the moderator @.4ct. for help."

         }# Initial system message to set context
    

    # Call model
    
    if should_enable_tools(prompt):
        messages.append(system_notifymess)
        messages.append({'role': "user", "content": prompt})
        response = ollama.chat(model="2sec", messages=messages, tools=tools_list)
        print('resp = ', response['message']['content'])
        messages.append(response['message'])

        if not response['message'].get('tool_calls'):
            print("No function calls found in the response.")
            print(response['message']['content'])

            
        # Map available functions
        available_functions = {
        "get_schedule": lambda **kwargs: get_schedule(kwargs["prompt"]),
        "get_weather": lambda **kwargs: get_weather(kwargs["city"], weather_api_key)
        }

        if 'tool_calls' in response ['message']:
            for tool in response['message']['tool_calls']:
                name = tool['function']['name']
                args = tool['function']['arguments']  

                function_to_call = available_functions.get(name)
                if function_to_call:
                    print(f"Calling: {name} with args: {args}")
                    result = function_to_call(**args)

                    messages.append({
                        "role": "tool",
                        "name": name,
                        "content": result if isinstance(result, str) else json.dumps(result)
                    })

                    print("Function Output:", result)
                    Function_Found = True
                else:
                    print(f"Function {name} not found.")
        else:
            print("No tools found")
        
    else:
        messages.append({'role': "user", "content": prompt})

    

    
    # Generate final response after all tool calls
    messages.append({'role': "user", "content": prompt})
    response = ollama.chat(model="2sec", messages=messages)
    return response['message']['content']
    
