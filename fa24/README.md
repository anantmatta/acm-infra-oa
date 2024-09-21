# Infra Team Interviews - Fall 2024

**Please read this entire document before starting!!**

## Overview

ACM@UIUC is currently building a ticketing and event sales system. Within this system, we need to support a few core functions to ensure that ACM members have a good experience buying tickets and ACM generates the most revenue possible.


## Problem Description

As an Infra team member, you have been tasked with building a simple API that supports a few key functions. 


### List Events

Create an API route `GET /api/v1/events` to list all events in the database. For each event, you should also return whether or not there are tickets left (should ticket sales be enabled).

#### Response Body

```jsonc
[
    {
        "event_id": "string",              // Event identifier
        "event_description": "string",     // Description of the event
        "start_time": "string",            // Start time of the event in ISO 8601 format
        "capacity": "integer",             // Total number of tickets available
        "sold": "integer",                 // Number of tickets sold
        "price": "number",                 // Price per ticket
        "tickets_left": "boolean"          // Whether there are tickets available
    }
]
```

If the server encounters an error reading the data, it should return the following (with HTTP Status Code 500):

```jsonc
{
    "error": "Could not read data. Please try again."
}
```

### Create Events

Create an API route `POST /api/v1/events` to add an event to the database. 

#### Request Body

It should accept a body in the following form:

```jsonc
{
    "event_id": "string",            // Unique identifier for the event (required)
    "event_description": "string",   // Description of the event (required)
    "start_time": "string",          // Start time of the event in ISO datetime format (required)
    "capacity": "integer",           // Total number of tickets available (required)
    "sold": "integer",               // Number of tickets sold (default: 0, optional)
    "price": "number"                // Price per ticket (required)
}

```
You should use a library such as `pydantic` to validate that the input conforms to the schema below. We've provided a sample validation class in the code.

#### Response Body

When an event is successfully created, return a response that confirms the event details  (with HTTP Status Code 201):

```jsonc
{
    "event_id": "string",
    "event_description": "string",
    "start_time": "string",
    "capacity": "integer",
    "sold": "integer",
    "price": "number"
}
```

If the server encounters an error writing the data, it should return the following (with HTTP Status Code 500):

```jsonc
{
    "error": "Could not write data. Please check your request body."
}
```

### Get optimal pricing

We want to make sure that ACM@UIUC makes the optimal profit from hosting a given event. Suppose we employ a dynamic pricing strategy which allows us to change the price of an event ticket based on what people are willing to pay for a ticket. In this strategy, we must charge all people the same price, but we somehow have foresight of what people are willing to pay.

For example, suppose we have 3 people willing to buy a ticket at prices `[11, 10, 9]` and we set our price to `10`. In this case:

* Person A buys a ticket at 10, since they're willing to pay 11 but pay 10 since that's the price. 
* Person B buys a ticket at 10, since they're willing to pay 10. 
* Person C does not buy a ticket, since the price is 10 but they're willing to pay 9.

Create an API route `POST /api/v1/events/{event_id}/optimal-pricing` that, given an event ID and an array of prices that people are willing to pay for a ticket, computes the maximum profit that can be achieved from the event using the dynamic pricing strategy.

If multiple strategies result in optimal profit, return the pricing strategy which sells the most number of tickets.

Note that you may not sell more tickets than are available for this event, even if there are people willing to pay for them.

#### Requirements

* **If you are a freshman or sophomore undergrad student (graduating Spring 2027 or Spring 2028):** We will not be judging your solution on its runtime efficiency, just its accuracy (you may brute force the solution). Showcase your programming skills while making sure your solution is clean and readable!

* **All other students (or if you're a sophomore applying for team lead):** We need to support a lot of tickets/pricing queries, so be efficient! Your solution should run in *O(n log n)* time with up to *O(n^2)* extra space.

#### Request Body

```jsonc
{
  "prices": [number, number, number, ...]   // Array of prices people are willing to pay (required)
}
```

### Response Body

When the profit is successfully computed, return the data (with HTTP status 200):

```jsonc
{
    "optimal_price": "number",    // The optimal price to set for maximum profit. if it is not possible to sell any tickets, this should be -1.
    "tickets_sold": "integer",    // The number of tickets sold at this optimal price (or 0 if tickets cannot be sold).
    "max_profit": "number"        // The maximum profit that can be achieved (or 0 if tickets cannot be sold).
}
```

If the server encounters an error computing the data, it should return the following (with HTTP Status Code 500):

```jsonc
{
    "error": "Could not compute data. Please check your request body."
}
```



## Getting Started

We have given you a SQLite database, as well as a few helper function structures, to get you started. 

You must have Python >= 3.10 installed to run this application. If you don't please install it now. 

First, run `make install` to install the dependencies for this application.

Next, run `make local` to run your API server locally. You can then use tools like Postman to make queries to your API server. You can also open `http://localhost:8000` in your web browser to make sure the application is running.

You can press `Ctrl-C` in the command line to stop the webserver.

## Testing your code

We have also provided you with a comprehensive test suite to test your solution. Run `make test` to test your code.

We will review your code manually and with different data: do not attempt to game the test cases by hardcoding data!

## Helpful Notes

* If you corrupt your database, run `make reset_db` to get a clean copy of the database again.
* If you don't know how to use SQLite3 with Python, see [the Python docs](https://docs.python.org/3/library/sqlite3.html#tutorial) for a helpful tutorial.
* The imported validation library will automatically handle verification failed responses.

## Submitting your code

You may only submit your `server.py` file! All other files will not be graded. We will use our copies of all other files.

Please submit your code code to PrairieLearn, under the course "ACM 101: ACM@UIUC Infrastructure Committee, Fall 2024". You will have to enroll in the course at https://us.prairielearn.com/pl/enroll.

There, you should see the assignment "Infra Take-Home Assessment". Upload your code there. You only have one attempt (run testing on your local machine). 

## Policy on LLMs
You may use any LLM of your choosing (ChatGPT, Claude, Copilot, etc.) provided you follow these guidelines:

1. You must provide a report of the entire conversation you had with the LLM (ChatGPT link, screenshots, etc.) with your submission.
2. The majority of the code must be yours; do not lift significant portions of the code from the LLM!
