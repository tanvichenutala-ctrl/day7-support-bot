"""Customer Support Bot (Day 7 Challenge: risk review).

A small Flask app. A customer sends a message, the LLM decides on a reply
and an action, and the app carries out the action.
"""
import json
import logging

from flask import Flask, jsonify, request

from llm import call_llm

app = Flask(__name__)

API_KEY = "sk-demo-4f9a2c71-FAKE-KEY-for-training-only"

logging.basicConfig(filename="logs/app.log", level=logging.INFO)

ORDERS = {
    "10231": {"status": "Shipped", "amount": 1299},
    "10232": {"status": "Delivered", "amount": 499},
    "10233": {"status": "Processing", "amount": 2499},
}
CUSTOMERS = {
    "ravi.kumar@example.com": {"name": "Ravi Kumar", "phone": "+91 98480 12345", "active": True},
    "priya.s@example.com": {"name": "Priya Sharma", "phone": "+91 99890 67890", "active": True},
}
REFUNDS = []
MAX_AUTO_REFUND = 1000          # refunds above this need a human
PENDING_APPROVALS = []          # requests a human must approve

ORDERS = {
    "10231": {"status": "Shipped", "amount": 1299, "owner": "ravi.kumar@example.com"},
    "10232": {"status": "Delivered", "amount": 499, "owner": "priya.s@example.com"},
    "10233": {"status": "Processing", "amount": 2499, "owner": "ravi.kumar@example.com"},
}


# ---------- Tools the LLM can use ----------

def get_order_status(order_id):
    order = ORDERS.get(order_id)
    return order["status"] if order else "Order not found"


def issue_refund(order_id, amount, customer_email):
    """The app checks every refund. The AI only asks for it."""
    order = ORDERS.get(order_id)
    if not order or order["owner"] != customer_email:
        return "Refund refused: order not found for this customer"
    if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
        return "Refund refused: invalid amount"
    if amount > order["amount"]:
        return "Refund refused: amount is more than the order total"
    if any(r["order_id"] == order_id for r in REFUNDS):
        return "Refund refused: this order was already refunded"
    if amount > MAX_AUTO_REFUND:
        PENDING_APPROVALS.append({"type": "refund", "order_id": order_id, "amount": amount})
        return "Refund sent to a human agent for approval"
    REFUNDS.append({"order_id": order_id, "amount": amount})
    return f"Refunded Rs {amount} for order {order_id}"


def delete_customer_account(customer_email):
    """The AI can never delete an account. It only raises a request."""
    PENDING_APPROVALS.append({"type": "close_account", "customer": customer_email})
    return "Account closure request sent to a human agent for approval"


TOOLS = {
    "get_order_status": get_order_status,
    "issue_refund": issue_refund,
    "delete_customer_account": delete_customer_account,
}

def run_action(action, args, email):
    """Run an AI-chosen action only if it is allowed, with safe arguments."""
    if action not in TOOLS:
        return "Action not allowed"
    if action == "get_order_status":
        return get_order_status(str(args.get("order_id", "")))
    if action == "issue_refund":
        return issue_refund(str(args.get("order_id", "")), args.get("amount"), email)
    # The account to close always comes from the request, never from the AI.
    return delete_customer_account(email)

# ---------- Chat endpoint ----------

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
    logging.info("PROMPT: %s", prompt)

    text, usage = call_llm(prompt, API_KEY)
    result = json.loads(text)

    action = result.get("action")
    action_result = None
    if action:
        action_result = run_action(action, result.get("args", {}), email)

    logging.info("REPLY to %s: %s", email, result["reply"])
    return jsonify({"reply": result["reply"], "action_result": action_result})


if __name__ == "__main__":
    app.run(debug=True)
