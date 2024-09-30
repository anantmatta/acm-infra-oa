from typing import List, Optional
from pydantic import BaseModel, Field
from flask import Flask, jsonify, make_response
from flask_pydantic import validate
from do_not_modify import ISO8601_TIMESTAMP_REGEX, HTTP_STATUS_OK, NOT_IMPLEMENTED_RESPONSE, HTTP_STATUS_NOT_IMPLEMENTED, run_db_query

HTTP_STATUS_CREATED = 201
HTTP_ERROR = 500

HTTP_GET_EVENTS_ERROR_MESSAGE = {"error": "Could not read data. Please try again."}
HTTP_CREATE_EVENT_ERROR_MESSAGE = {"error": "Could not write data. Please check your request body."}
HTTP_PRICING_ERROR_MESSAGE = {"error": "Could not compute data. Please check your request body."}

EVENTS_TABLE = "events"

# Use the run_db_query function to run your queries.
app = Flask("acm-uiuc-infra-interview-fa24")

class PostBodyModel(BaseModel):
  event_id: str
  event_description: Optional[str] | None = ""
  start_time: str = Field(pattern=ISO8601_TIMESTAMP_REGEX)
  capacity: Optional[int] = 0
  price: float
  sold: int = 0

class OptimalPriceBodyModel(BaseModel):
  prices: List[float]
  
@app.route("/", methods=["GET"])
def home():
  return make_response("The application is running. Good luck!", HTTP_STATUS_OK)

@app.route("/api/v1/events", methods=["POST"])
@validate()
def post(body: PostBodyModel):
  query = f'''
  INSERT into {EVENTS_TABLE} (event_id, event_description, start_time, capacity, sold, price) 
  VALUES (:event_id, :event_description, :start_time, :capacity, :sold, :price);
  '''

  try:
    new_event = dict(body)
    run_db_query(query, new_event)

    return make_response(jsonify(new_event), HTTP_STATUS_CREATED)
  
  except Exception as e:
    return make_response(jsonify(HTTP_CREATE_EVENT_ERROR_MESSAGE), HTTP_ERROR)
  
@app.route("/api/v1/events", methods=["GET"])
def get():
  query = f"SELECT event_id, event_description, start_time, capacity, sold, price FROM {EVENTS_TABLE};"
  
  try:
    output = run_db_query(query).fetchall()
    
    for row in output:
      row['tickets_left'] = (row["sold"] < row["capacity"])
    
    return make_response(jsonify(output), HTTP_STATUS_OK)
  
  except Exception as e:
    return make_response(jsonify(HTTP_GET_EVENTS_ERROR_MESSAGE), HTTP_ERROR)

@app.route("/api/v1/events/<string:event_id>/optimal-pricing", methods=["POST"])
@validate(body=OptimalPriceBodyModel)
def pricing(body: OptimalPriceBodyModel, event_id: str):
  return make_response(jsonify(NOT_IMPLEMENTED_RESPONSE), HTTP_STATUS_NOT_IMPLEMENTED)

if __name__ == "__main__":
  app.run(debug=True, port=8000)