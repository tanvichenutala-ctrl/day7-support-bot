# Customer Support Bot – Day 7 Challenge

A small Flask app for customer support. A customer sends a message, an AI model
decides on a reply and an action (check an order, refund, close an account), and
the app carries out that action.

The AI model is **fake** (`llm.py`), so the app runs without internet or a real key.
All customers, orders and keys in this repo are **made up**.

**Your job:** review this app like a security and quality reviewer. Find the risks,
rate them, fix the two most serious ones, and add monitoring.

## Run it

```
python -m venv .venv
.venv\Scripts\activate        (Windows)
source .venv/bin/activate     (Mac/Linux)
pip install -r requirements.txt
python app.py
```

The app runs at http://127.0.0.1:5000. Send requests with Postman:

- **POST** `http://127.0.0.1:5000/chat`
- Body (raw, JSON): `{"customer_email": "ravi.kumar@example.com", "message": "Where is my order 10231?"}`

## Run the tests

```
pytest -v
```

3 tests are included and they pass. A CI workflow in `.github/workflows/ci.yml`
runs them on every push and pull request.

## Files

| File | What it does |
|---|---|
| app.py | The web app, the tools the AI can use, and the /chat endpoint |
| llm.py | A fake AI model that returns a reply, an action and token usage |
| tests/test_app.py | Starter tests |
| Dockerfile | Builds the app as a Docker image |
| .github/workflows/ci.yml | Runs the tests on GitHub |
| logs/ | Where the app writes its log file |
