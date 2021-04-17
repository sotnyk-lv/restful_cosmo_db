from flask import Flask, jsonify, request
from azure.cosmos import exceptions, CosmosClient, PartitionKey
import uuid
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
if "cosmos_db_credentials" not in config:
    raise RuntimeError("config.ini file should have cosmos_db_credentials section")
if "endpoint" not in config["cosmos_db_credentials"] or "key" not in config["cosmos_db_credentials"]:
    raise RuntimeError("config.ini file should have endpoint and key to the db")


endpoint = config["cosmos_db_credentials"]["endpoint"]
key = config["cosmos_db_credentials"]["key"]

database_name = 'Students'
container_name = 'StudentContainer'

client = CosmosClient(endpoint, key)

database = client.create_database_if_not_exists(id=database_name) 

container = database.create_container_if_not_exists(
    id=container_name, 
    partition_key=PartitionKey(path="/grade"),
    offer_throughput=400
)

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <h3>cosmos db database connection</h3></br>
    <p>
    - <a href="/restart">/restart</a> -> to restart database</br>
    - <a href="/get">/get</a> -> to get all queries</br>
    - <a href="/add">/add</a>?last_name=(user_last_name)&grade=(int_mark_for_student) [&first_name=(user_first_name)] -> add new student grade</br>
    - <a href="/get">/get</a>?last_name=(user_last_name) [&first_name=(user_first_name)] -> get all user grades</br>
    - <a href="/get_mean">/get_mean</a>?last_name=(user_last_name) [&first_name=(user_first_name)] -> get mean user grade</br>
    </p>
    """

@app.route("/restart")
def restart():
    client.delete_database(database_name)
    database = client.create_database_if_not_exists(id=database_name) 
    container = database.create_container_if_not_exists(
        id=container_name, 
        partition_key=PartitionKey(path="/grade"),
        offer_throughput=400
    )
    return jsonify({True})
    """
    <script>    
     window.setTimeout(function(){

       // Move to a new location or you can do something else
       window.location.href = "/";

    }, 5000);

    </script>"""

@app.route("/add")
def add():
    parameters = request.args.to_dict(flat=False)
    
    for key, value in parameters.items():
        parameters[key] = int(value[0]) if is_int(value[0]) else value[0]
    if 'last_name' not in parameters:
        return jsonify(False, {'error':'no_last_name'})
    if 'grade' not in parameters:
        return jsonify(False, {'error':'no_grade'})
    parameters['id'] = parameters['last_name'] + '_' + str(uuid.uuid4())

    container.create_item(body=parameters)
    
    return jsonify(parameters)

@app.route("/get")
def get():
    parameters = request.args.to_dict(flat=False)
    for key, value in parameters.items():
        parameters[key] = int(value[0]) if is_int(value[0]) else value[0]

    query = "SELECT * FROM c"

    if "last_name" in parameters and "first_name" in parameters:
        query += " WHERE c.last_name='" + parameters["last_name"] + "' AND c.first_name=" + parameters["first_name"]
    elif "last_name" in parameters:
        query += " WHERE c.last_name='" + parameters["last_name"] + "'"
    elif "first_name" in parameters:
        query += " WHERE c.first_name=" + parameters["first_name"] + "'"

    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    return jsonify(items)

@app.route("/get_mean")
def get_mean():
    parameters = request.args.to_dict(flat=False)
    for key, value in parameters.items():
        parameters[key] = int(value[0]) if is_int(value[0]) else value[0]

    query = "SELECT VALUE root FROM (SELECT c.last_name, AVG(c.grade) as grade From c"

    if "last_name" in parameters and "first_name" in parameters:
        query += " WHERE c.last_name='" + parameters["last_name"] + "' AND c.first_name=" + parameters["first_name"]
    elif "last_name" in parameters:
        query += " WHERE c.last_name='" + parameters["last_name"] + "'"
    elif "first_name" in parameters:
        query += " WHERE c.first_name=" + parameters["first_name"] + "'"
    query += " GROUP BY c.last_name) as root"
    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    return jsonify(items)

    return "get_mean"


def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    app.run(debug=True)
