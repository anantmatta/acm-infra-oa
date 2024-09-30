from typing import List, Optional
from pydantic import BaseModel, Field
from flask import Flask, jsonify, make_response
from flask_pydantic import validate
from do_not_modify import (
    ISO8601_TIMESTAMP_REGEX,
    HTTP_STATUS_OK,
    NOT_IMPLEMENTED_RESPONSE,
    HTTP_STATUS_NOT_IMPLEMENTED,
    run_db_query
)

# HTTP Codes
HTTP_STATUS_CREATED = 201
HTTP_ERROR = 500

# Error messages (as outlined in README)
HTTP_GET_EVENTS_ERROR_MESSAGE = {"error": "Could not read data. Please try again."}
HTTP_CREATE_EVENTS_ERROR_MESSAGE = {
    "error": "Could not write data. Please check your request body."
}
HTTP_OPTIMAL_PRICING_ERROR_MESSAGE = {
    "error": "Could not compute data. Please check your request body."
}

# Name of SQLite table w/ event info
EVENTS_TABLE_NAME = "events"

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
    # SQL query to add specified event
    query = f"""
  INSERT into {EVENTS_TABLE_NAME} (event_id, event_description, start_time, capacity, sold, price) 
  VALUES (:event_id, :event_description, :start_time, :capacity, :sold, :price);
  """

    # Try-catch for any errors in row insertion (e.g. duplicate event_id)
    try:
        new_event = dict(body)
        run_db_query(query, new_event)

        return make_response(jsonify(new_event), HTTP_STATUS_CREATED)

    # Catch-all for any exception
    except Exception as e:
        return make_response(jsonify(HTTP_CREATE_EVENTS_ERROR_MESSAGE), HTTP_ERROR)


@app.route("/api/v1/events", methods=["GET"])
def get():
    # SQL query to select all event info
    query = f"SELECT * FROM {EVENTS_TABLE_NAME};"

    # Try-catch for any errors in fetching data, calculating 'tickets_left', jsonify
    try:
        output = run_db_query(query).fetchall()

        for row in output:
            row["tickets_left"] = row["sold"] < row["capacity"]

        return make_response(jsonify(output), HTTP_STATUS_OK)

    # Catch-all for any exception
    except Exception as e:
        return make_response(jsonify(HTTP_GET_EVENTS_ERROR_MESSAGE), HTTP_ERROR)


# Current implementation of optimal-pricing has O(n*log(n)) time complexity, O(1) space complexity
@app.route("/api/v1/events/<string:event_id>/optimal-pricing", methods=["POST"])
@validate(body=OptimalPriceBodyModel)
def pricing(body: OptimalPriceBodyModel, event_id: str):
    # SQL query to retrieve 'capacity', 'sold' data for event_id
    get_event_query = (
        f"SELECT capacity, sold FROM {EVENTS_TABLE_NAME} where event_id = '{event_id}';"
    )

    try:
        event_info = run_db_query(get_event_query).fetchone()

        # Verify event exists in database
        if len(event_info) == 0:
            raise (f"No event with event_id '{event_id}'")

        # Determine number of available tickets; sort prices in descending order
        num_tickets = event_info["capacity"] - event_info["sold"]
        body.prices.sort(reverse=True)
        optimal_pricing = {"optimal_price": -1, "tickets_sold": 0, "max_profit": 0}

        # Determine best pricing strategy to sell to the number of buyers/tickets (whichever is lower)
        # Note: best price to sell to n people is lowest price among the n highest prices
        for n in range(0, min(len(body.prices), num_tickets), 1):
            potential_profit = body.prices[n] * (n + 1)
            if optimal_pricing["max_profit"] <= potential_profit:
                optimal_pricing["optimal_price"] = body.prices[n]
                optimal_pricing["tickets_sold"] = n + 1
                optimal_pricing["max_profit"] = potential_profit

        return make_response(jsonify(optimal_pricing), HTTP_STATUS_OK)

    # Catch-all for any exception
    except Exception as e:
        return make_response(HTTP_OPTIMAL_PRICING_ERROR_MESSAGE, HTTP_ERROR)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
