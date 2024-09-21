from typing import List, Optional
from pydantic import BaseModel, Field
from flask import Flask, jsonify, make_response
from flask_pydantic import validate
from do_not_modify import ISO8601_TIMESTAMP_REGEX, HTTP_STATUS_OK, NOT_IMPLEMENTED_RESPONSE, HTTP_STATUS_NOT_IMPLEMENTED, run_db_query

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
  return make_response(jsonify(NOT_IMPLEMENTED_RESPONSE), HTTP_STATUS_NOT_IMPLEMENTED)
  
@app.route("/api/v1/events", methods=["GET"])
def get():
  return make_response(jsonify(NOT_IMPLEMENTED_RESPONSE), HTTP_STATUS_NOT_IMPLEMENTED)

@app.route("/api/v1/events/<string:event_id>/optimal-pricing", methods=["POST"])
@validate(body=OptimalPriceBodyModel)
def pricing(body: OptimalPriceBodyModel, event_id: str):
  return make_response(jsonify(NOT_IMPLEMENTED_RESPONSE), HTTP_STATUS_NOT_IMPLEMENTED)

if __name__ == "__main__":
  app.run(debug=True, port=8000)