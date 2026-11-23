"""A fake LLM so the app runs without internet or a real API key.

In a real app, call_llm() would send the prompt to the company-approved LLM API.
It returns the model's text and the token usage, like a real API does.
"""
import json
import re


def call_llm(prompt, api_key):
    message = prompt.split("Customer message:")[-1].lower()
    order = re.search(r"order\s*#?(\d{4,})", message)
    order_id = order.group(1) if order else "unknown"

    if "refund" in message:
        amount = re.search(r"(?:rs\.?|₹)\s*(\d+)", message)
        reply = {
            "reply": "Sorry about that. I have issued your refund.",
            "action": "issue_refund",
            "args": {"order_id": order_id, "amount": int(amount.group(1)) if amount else 500},
        }
    elif "close my account" in message or "delete my account" in message:
        reply = {
            "reply": "Your account has been closed.",
            "action": "delete_customer_account",
            "args": {"customer_email": "from_request"},
        }
    elif "where is my order" in message or "status" in message:
        reply = {
            "reply": f"Let me check order {order_id}.",
            "action": "get_order_status",
            "args": {"order_id": order_id},
        }
    else:
        reply = {"reply": "Thanks for contacting support. How can I help?", "action": None, "args": {}}

    text = json.dumps(reply)
    usage = {"input_tokens": len(prompt.split()) * 2, "output_tokens": len(text.split()) * 2}
    return text, usage
