#!/usr/bin/env python3
# Author: Shane Harrell

from flask import Flask, request, Response
import sys,os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load database vars from .env
load_dotenv()

# Get database vars from .env
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

def create_conn_cursor():
    print (db_user, db_password, db_host, db_port, db_name)
    conn = psycopg2.connect(
        database=db_name,
        user=db_user,
        host=db_host,
        password=db_password,
        port=db_port,
        options = '-c search_path=ai_agent'
    )

    cur = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cur

def close_conn_cursor(conn, cur):
    cur.close()
    conn.close()

## CREATE the Database if not exists
create_db_schema = '''CREATE SCHEMA IF NOT EXISTS ai_agent'''

create_db_agent_table = '''CREATE TABLE IF NOT EXISTS ai_agent.agent (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    prompt JSONB,
    post_prompt JSONB,
    post_prompt_url TEXT,
    languages JSONB,
    params JSONB,
    hold_music TEXT,
    conscience TEXT,
    pronounce JSONB,
    swaig JSONB,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )'''

#create_db_swaig_table = '''CREATE TABLE IF NOT EXISTS ai_agent.swaig (
#    id SERIAL PRIMARY KEY,
#    name TEXT,
#    agent_id INT NOT NULL,
#    function JSONB,
#    FOREIGN KEY (agent_id) REFERENCES agent(id)
#    )'''

#create_db_languages_table = '''CREATE TABLE IF NOT EXISTS ai_agent.languages (
#  id SERIAL PRIMARY KEY,
#  name TEXT,
#  agent_id INT NOT NULL,
#  languages JSONB,
#  FOREIGN KEY (agent_id) REFERENCES agent(id)
#  )'''

create_db_queries = [create_db_schema, create_db_agent_table]

conn, cur = create_conn_cursor()
for query in create_db_queries:
    cur.execute(query)

conn.commit()
close_conn_cursor(conn, cur)


## API Services ##
ai_agent_api = Flask(__name__)

@ai_agent_api.route('/api/fabric/resources/ai_agents/<ai_agent_id>', methods=['GET'])
@ai_agent_api.route('/api/fabric/resources/ai_agents/<ai_agent_id>/<param>', methods=['GET'])
def ai_agent_get(ai_agent_id, param=None):
    response = { 'ERROR': 'Unknown Error' }
    response_code = 400

    try:
        ai_agent_id = int(ai_agent_id)
        if ai_agent_id <= 0:
            raise ValueError
    except ValueError:
        response = { 'ERROR': 'Agent ID must be a positive integer' }
        response_code = 400
        return Response(json.dumps(response), 400, mimetype='application/json') 

    params_list = ['prompt', 'post_prompt', 'languages', 'params', 'post_prompt_url', 'swaig', 'pronounce', 'conscience', 'hold_music']
    if param and param not in params_list:
        response = { 'ERROR': f"Param {param} is not a valid param" }
        response_code = 400
        return Response(json.dumps(response), response_code, mimetype='application/json')

    function_list = []

    conn, cur = create_conn_cursor()
    cur.execute(f"select * from agent where id={ai_agent_id}")
    rows = cur.fetchall()

    if not rows:
        response = { 'ERROR':  'The Agent does not exist' }
        return Response(json.dumps(response), 400, mimetype='application/json')

    if rows:
        row = rows[0]
        fields = [
        'prompt', 'post_prompt', 'post_prompt_url', 'languages', 'params',
        'hold_music', 'conscience', 'pronounce', 'swaig'
        ]
    
        ai_agent_object = {
            k: row[k.lower() if k != 'SWAIG' else 'swaig']
            for k in fields
            if row.get(k.lower() if k != 'SWAIG' else 'swaig') not in (None, "")
        }
        print (ai_agent_object)

    if param in ai_agent_object:
        v = ai_agent_object[param] 
        if param == 'swaig':
            param = param.upper()
        response = {param: v}
        response_code= 200
    elif param:
        response = {param: "null"}
        response_code = 200
    else:
        swml = {}
        swml['version'] = "1.0.0"
        swml['sections'] = {
            'main': [ {
                "ai": ai_agent_object
            } ]
        }

        response = swml
        response_code = 200
    
    close_conn_cursor(conn, cur)
    return Response(json.dumps(response), response_code, mimetype='application/json')


@ai_agent_api.route('/api/fabric/resources/ai_agents', methods=['POST'])
def create_ai_agent():
    if not request.is_json:
        response = { 'ERROR': 'Request must be JSON' }
        return Response(json.dumps(response), 400, mimetype='application/json')

    data = request.json

    name = data.get('name')
    if name is None:
        response = { 'ERROR': 'name is required' }
        return Response(response, 400, mimetype='application/json')

    prompt = data.get('prompt')
    if prompt is None:
        response = { 'ERROR': 'prompt is required' }
        return Response(response, 400, mimetype='application/json')

    post_prompt = data.get('post_prompt', None)
    
    post_prompt_url = data.get('post_prompt_url', None)

    default_languages = json.dumps( {
        "code": "en-US",
        "name": "English",
        "voice": "josh",
        "engine": "elevenlabs",
        "fillers": [
            "ok",
            "thanks"
        ]
    } )
    languages = data.get('languages', default_languages)

    default_params = json.dumps( {
        "local_tz": "America/Chicago",
        "ai_model": "gpt-4o-mini"
    } )
    params = data.get('params', default_params)

    conscience = data.get('conscience', None)

    pronounce = data.get('pronounce', None)

    hold_music = data.get('hold_music', None)

    swaig = data.get('swaig', None)

    conn, cur = create_conn_cursor()
    insert_into_db_query = '''INSERT INTO ai_agent.agent (name, prompt, post_prompt, post_prompt_url, languages, params, conscience, pronounce, hold_music, swaig) VALUES \
        (
        %s, 
        %s, 
        %s, 
        %s, 
        %s, 
        %s, 
        %s, 
        %s, 
        %s, 
        %s
        ) RETURNING id'''
    cur.execute(insert_into_db_query, (name, json.dumps(prompt), json.dumps(post_prompt), post_prompt_url, json.dumps(languages), json.dumps(params), conscience, json.dumps(pronounce), hold_music, json.dumps(swaig)))
    row = cur.fetchone()
    if row is not None:
        new_ai_agent_id = row['id']
    else:
        new_ai_agent_id = None
    conn.commit()
    close_conn_cursor(conn, cur)

    return Response(str(new_ai_agent_id), 200)

@ai_agent_api.route('/api/fabric/resources/ai_agents/<agent_id>', methods=['PUT'])
def update_ai_agent(agent_id):
    if not request.is_json:
        response = {'ERROR': 'Request must be JSON'}
        return Response(json.dumps(response), 400, mimetype='application/json')

    data = request.json

    try:
        agent_id = int(agent_id)
        if agent_id <= 0:
            raise ValueError
    except ValueError:
        response = {'ERROR': 'Agent ID must be a positive integer'}
        return Response(json.dumps(response), 400, mimetype='application/json')

    # Check if the agent exists
    conn, cur = create_conn_cursor()
    cur.execute("SELECT id FROM agent WHERE id = %s", (agent_id,))
    if cur.fetchone() is None:
        close_conn_cursor(conn, cur)
        response = {'ERROR': 'Agent not found'}
        return Response(json.dumps(response), 404, mimetype='application/json')

    # Prepare update data
    update_fields = []
    update_values = []

    if 'name' in data:
        update_fields.append("name = %s")
        update_values.append(data['name'])

    if 'prompt' in data:
        update_fields.append("prompt = %s")
        update_values.append(json.dumps(data['prompt']))

    if 'post_prompt' in data:
        update_fields.append("post_prompt = %s")
        update_values.append(json.dumps(data['post_prompt']))

    if 'languages' in data:
        update_fields.append("languages = %s")
        update_values.append(json.dumps(data['languages']))

    if 'params' in data:
        update_fields.append("params = %s")
        update_values.append(json.dumps(data['params']))

    if 'post_prompt_url' in data:
        update_fields.append("post_prompt_url = %s")
        update_values.append(data['post_prompt_url'])

    if 'conscience' in data:
        update_fields.append("conscience = %s")
        update_values.append(data['conscience'])

    if 'pronounce' in data:
        update_fields.append("pronounce = %s")
        update_values.append(json.dumps(data['pronounce']))

    if 'hold_music' in data:
        update_fields.append("hold_music = %s")
        update_values.append(data['hold_music'])

    if 'swaig' in data:
        update_fields.append("swaig = %s")
        update_values.append(json.dumps(data['swaig']))

    if not update_fields:
        close_conn_cursor(conn, cur)
        response = {'ERROR': 'No fields to update'}
        return Response(json.dumps(response), 400, mimetype='application/json')

    # Construct and execute update query
    update_query = f"UPDATE ai_agent.agent SET {', '.join(update_fields)} WHERE id = %s"
    update_values.append(agent_id)
    
    cur.execute(update_query, tuple(update_values))
    conn.commit()
    close_conn_cursor(conn, cur)

    response = {'SUCCESS': f'Agent {agent_id} has been updated'}
    return Response(json.dumps(response), 200, mimetype='application/json')


@ai_agent_api.route('/api/fabric/resources/ai_agents/<agent_id>', methods=['DELETE'])
def delete_ai_agent(agent_id):
    response = { 'ERROR': 'Unknown Error' }
    response_code = 400

    if not isinstance(int(agent_id), int):
        response = { 'ERROR': 'Agent ID must be an integer' }
        response_code = 400

    conn, cur = create_conn_cursor()
    select_ai_agent = f"SELECT id from agent where id={agent_id}"
    cur.execute(select_ai_agent)

    row = cur.fetchone()
    if row is not None:
        # Agent exists, proceed with the delete
        # TODO: are you authorized to do the delete for this agent
        delete_ai_agent = f"DELETE from agent where id={agent_id}"
        cur.execute(delete_ai_agent)
        conn.commit()
        response = { 'SUCCESS': 'The Agent has been removed' }
        response_code = 200
    else:
        # The Agent does not exist
        response = { 'ERROR': 'The Agent ID does not exist' }
        response_code = 400

    close_conn_cursor(conn, cur)
    return Response(json.dumps(response), response_code, mimetype='application/json')



if __name__ == '__main__':
    ai_agent_api.run(host='0.0.0.0', port=5000)




