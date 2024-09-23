#!/usr/bin/env python3

import requests
import json
import argparse
import sys


domain = "<path_to_api>:5000"
api_url = f"http://{domain}/api/fabric/resources/ai_agents"

headers = {
    "Content-Type": "application/json",
}

name = "Example Agent"
prompt = "Greet the user and thank them for using your services"
post_prompt = "Summarize the conversation"
post_prompt_url = "https://webhook.example.com/post_prompt"
languages = [
        {
            "engine": "elevenlabs",
            "voice": "rachel",
            "function_fillers": [
                "umm",
                "uh",
                "hmm...",
                "lets see",
                "ok"
            ],
            "code": "en_us",
            "name": "English"
        }
]
pronounce = [
    {
        "with": "bar",
        "replace": "foo",
        "ignore_case": 1
    }
]
swaig = {
    "function": "lookup_caller",
    "purpose": "lookup the caller in the database to verify they exist already",
    "web_hook_url": "webhook.com/lookup_caller",
    "argument": {
      "type": "object",
      "properties": {
        "phone_number": {
          "type": "string",
          "description": "the callers phone_number"
        }
      }
    }
}

data = {
    "name": name,
    "prompt": {
        "text": prompt,
        "top_p": 0.5,
        "temperature": 0.5
    },
    "post_prompt": {
        "text": post_prompt,
        "top_p": 0.5,
        "temperature": 0.5
    },
    "post_prompt_url": post_prompt_url,
    "languages": languages,
    "pronounce": pronounce,
    "swaig": swaig
}


parser = argparse.ArgumentParser()
parser.add_argument("-g", "--get", action="store_true", help="Get the AI agent")
parser.add_argument("-p", "--put", action="store_true", help="Put the AI agent")
parser.add_argument("-P", "--post", action="store_true", help="Post the AI agent")
parser.add_argument("-a", "--agent", type=int, help="The AI agent ID")
parser.add_argument("-m", "--param", type=str, help="The AI agent param")
args = parser.parse_args()


if args.agent:
    agentid = args.agent
    if args.get:
        if args.param:  
            param = args.param 
            response = requests.request("GET", url=f"{api_url}/{agentid}/{param}", headers=headers)
        else:
            response = requests.request("GET", url=f"{api_url}/{agentid}", headers=headers)
    elif args.put:
        response = requests.request("PUT", url=f"{api_url}/{agentid}", headers=headers, data=json.dumps(data))

elif args.post:
    response = requests.request("POST", url=f"{api_url}", headers=headers, data=json.dumps(data))


else:
    print("Invalid option")
    sys.exit(2)
    

print (response.text)

