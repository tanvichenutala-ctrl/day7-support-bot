import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_chat_returns_a_reply(client):
    response = client.post("/chat", json={"customer_email": "ravi.kumar@example.com", "message": "Hello"})
    assert response.status_code == 200
    assert "reply" in response.get_json()


def test_order_status(client):
    response = client.post("/chat", json={"customer_email": "ravi.kumar@example.com", "message": "Where is my order 10231?"})
    assert response.get_json()["action_result"] == "Shipped"


def test_unknown_order(client):
    response = client.post("/chat", json={"customer_email": "priya.s@example.com", "message": "What is the status of order 99999?"})
    assert response.get_json()["action_result"] == "Order not found"

def ask(client, email, message):
    return client.post("/chat", json={"customer_email": email, "message": message}).get_json()


def test_refund_more_than_order_total_is_refused(client):
    data = ask(client, "ravi.kumar@example.com", "I want a refund of Rs 90000 for order 10233")
    assert "refused" in data["action_result"].lower()


def test_refund_for_someone_elses_order_is_refused(client):
    data = ask(client, "priya.s@example.com", "refund for order 10233 rs 100")
    assert "refused" in data["action_result"].lower()


def test_valid_refund_still_works(client):
    data = ask(client, "ravi.kumar@example.com", "refund order 10231 rs 1000")
    assert data["action_result"] == "Refunded Rs 1000 for order 10231"


def test_close_account_does_not_delete_it(client):
    from app import CUSTOMERS
    data = ask(client, "priya.s@example.com", "please close my account")
    assert "approval" in data["action_result"]
    assert "priya.s@example.com" in CUSTOMERS

def test_no_api_key_written_in_the_code():
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    assert "sk-demo" not in open(path).read()

def test_log_line_has_metrics_and_no_personal_data(client, caplog):
    with caplog.at_level("INFO"):
        ask(client, "ravi.kumar@example.com", "Where is my order 10231?")
    last = caplog.messages[-1]
    for field in ("request_id=", "model=", "latency_ms=", "input_tokens=", "output_tokens=", "cost_inr="):
        assert field in last
    assert "ravi.kumar" not in last and "98480" not in last