# AI Agent API

This API allows you to manage AI agents, including creating, updating, retrieving, and deleting them.

## Endpoints

### Create AI Agent

- **URL**: `/api/fabric/resources/ai_agents`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "name": "Example Agent",
    "prompt": "Greet the user and thank them for using your services",
    "post_prompt": "Summarize the conversation",
    "post_prompt_url": "https://webhook.example.com/post_prompt",
    "languages": [
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
    ],
    "pronounce": [
        {
            "with": "bar",
            "replcace": "foo",
            "ignore_case": 1
        }
    ],
    "swaig": {
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
  }
  ```
- **Allowed Parameters**: name, prompt, post_prompt, post_prompt_url, swaig, languages, params, conscience, pronounce, hold_music
- **Response**: Returns the ID of the newly created AI agent

### Get AI Agent

- **URL**: `/api/fabric/resources/ai_agents/<agent_id>`
- **Method**: `GET`
- **Response**: Returns the AI agent details

### Get Specific AI Agent Parameter

- **URL**: `/api/fabric/resources/ai_agents/<agent_id>/<param>`
- **Method**: `GET`
- **Allowed Parameters**: name, prompt, post_prompt, post_prompt_url, swaig, languages, params, conscience, pronounce, hold_music
- **Response**: Returns the value of the specified parameter for the AI agent

### Update AI Agent

- **URL**: `/api/fabric/resources/ai_agents/<agent_id>`
- **Method**: `PUT`
- **Content-Type**: `application/json`
- **Body**: Include any fields you want to update, for example:
  ```json
  {
    "prompt": "New prompt text",
    "languages": ["en", "es", "fr"]
  }
  ```
- **Allowed Parameters**: name, prompt, post_prompt, post_prompt_url, swaig, languages, params, conscience, pronounce, hold_music
- **Response**: Confirmation of update

### Delete AI Agent

- **URL**: `/api/fabric/resources/ai_agents/<agent_id>`
- **Method**: `DELETE`
- **Response**: Confirmation of deletion


## Error Handling

The API returns appropriate HTTP status codes and error messages in case of failures. Common error scenarios include:

- 400 Bad Request: When the request body is not valid JSON
- 404 Not Found: When the specified AI agent is not found
- 500 Internal Server Error: For database errors or other internal issues


## Setup

Ensure you have the necessary Python packages installed and a PostgreSQL database set up with the correct schema. The API uses Flask and psycopg2 for database interactions.

- Use python virtual environment to manage dependencies - Optional / Recommended
    - `python3 -m venv ai-agent-api`
    - `source ai-agent-api/bin/activate`
- Install python dependencies
    - `pip install -r requirements.txt`
- Copy env.sample to create .env and update the .env with your database credentials

## Running the API

To run the API, execute the main.py file:

`python3 main.py`

<br>
<br>
<br>


## API Demo Script (api-demo.py)

The `api-demo.py` is an example script that provides an interface to interact with the AI Agent API. It allows you to perform GET, PUT, and POST operations on AI agents without having to write additional code or curl commands.

### Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)

### Configuration

Before using the script, ensure you've set up the following variables in the script:

- `domain`: The domain where your API is hosted (default is "localhost:5000")
- `api_url`: The full URL to the AI agents endpoint
- `headers`: The headers to be sent with each request (typically includes Content-Type)

### Usage

The script uses command-line arguments to determine which operation to perform:

Options:
- `-g` or `--get`: Perform a GET request
- `-p` or `--put`: Perform a PUT request
- `-P` or `--post`: Perform a POST request
- `-a` or `--agent`: Specify the AI agent ID (required for GET and PUT)
- `-m` or `--param`: Specify a parameter to retrieve (optional for GET)

### Examples

1. Create a new AI agent:
   ```
   python3 api-demo.py -P
   ```

2. Get all details of an AI agent:
   ```
   python3 api-demo.py -g --agent 123
   ```

3. Get a specific parameter of an AI agent:
   ```
   python3 api-demo.py -g --agent 123 --param prompt
   ```

4. Update an AI agent:
   ```
   python3 api-demo.py -p --agent 123
   ```


### Response

The script will print the raw response text from the API. You may want to parse this output depending on your needs.

### Note

This script is primarily for demonstration and testing purposes. In a production environment, you would typically want to add error handling, input validation, and possibly a more user-friendly interface.
