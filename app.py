"""Customer Support Bot (Day 7 Challenge: risk review).

A small Flask app. A customer sends a message, the LLM decides on a reply
and an action, and the app carries out only the allowed action.
"""

import json
import logging
import time
import uuid

from flask import Flask, jsonify, request
from llm import call_llm

app = Flask(__name__)

API_KEY = "sk-demo-4f9a2c71-FAKE-KEY-for-training-only"
MODEL_NAME = "fake-llm"
COST_PER_TOKEN_INR = 0.0005

logging.basicConfig(filename="logs/app.log", level=logging.INFO)

ORDERS = {
    "10231": {"status": "Shipped", "amount": 1299},
    "10232": {"status": "Delivered", "amount": 499},
    "10233": {"status": "Processing", "amount": 2499},
}

CUSTOMERS = {
    "ravi.kumar@example.com": {
        "name": "Ravi Kumar",
        "phone": "+91 98480 12345",
        "active": True,
    },
    "priya.s@example.com": {
        "name": "Priya Sharma",
        "phone": "+91 99890 67890",
        "active": True,
    },
}

REFUNDS = []


def get_order_status(order_id):
    order = ORDERS.get(order_id)
    return order["status"] if order else "Order not found"


# These functions remain for the challenge, but are not exposed to chat requests.
def issue_refund(order_id, amount):
    REFUNDS.append({"order_id": order_id, "amount": amount})
    return f"Refunded Rs {amount} for order {order_id}"


def delete_customer_account(customer_email):
    CUSTOMERS.pop(customer_email, None)
    return f"Deleted account {customer_email}"


TOOLS = {
    "get_order_status": get_order_status,
}


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    email = data.get("customer_email", "")
    message = data.get("message", "")
    customer = CUSTOMERS.get(email, {})

    prompt = (
        "You are a helpful support agent. Reply in JSON with reply, action and args.\n"
        f"Customer name: {customer.get('name')}\n"
        f"Customer email: {email}\n"
        f"Customer phone: {customer.get('phone')}\n"
        f"Customer message: {message}"
    )

    logging.info("Chat request received")

    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    text, usage = call_llm(prompt, API_KEY)
    latency_ms = (time.perf_counter() - start_time) * 1000

    input_tokens = usage["input_tokens"]
    output_tokens = usage["output_tokens"]
    estimated_cost_inr = (input_tokens + output_tokens) * COST_PER_TOKEN_INR

    logging.info(
        "request_id=%s model=%s latency_ms=%.2f input_tokens=%d "
        "output_tokens=%d cost_inr=%.6f",
        request_id,
        MODEL_NAME,
        latency_ms,
        input_tokens,
        output_tokens,
        estimated_cost_inr,
    )

    result = json.loads(text)
    action = result.get("action")
    action_result = None

    if action == "get_order_status":
        args = result.get("args") or {}
        order_id = args.get("order_id")
        if isinstance(order_id, str):
            action_result = get_order_status(order_id)
        else:
            result["reply"] = (
                "I couldn't verify that order. Please contact support."
            )

    elif action in {"issue_refund", "delete_customer_account"}:
        result["reply"] = (
            "I can't perform that action automatically. "
            "Please contact support; no changes were made."
        )
        action_result = {"status": "not_executed"}

    elif action is not None:
        result["reply"] = "I couldn't safely process that request."

    logging.info("Chat response sent")
    return jsonify(
        {"reply": result["reply"], "action_result": action_result}
    )


if __name__ == "__main__":
    app.run(debug=True)