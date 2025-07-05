from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend (for local testing)

# 🧑 Mock user data
users = {
    "user1": {
        "password": "pass123",
        "account": {
            "accountNumber": "SB123456789",
            "balance": 5000.0,
            "transactions": [
                {"type": "Deposit", "amount": 5000, "date": "2024-01-01"}
            ]
        }
    }
}

# Serve the frontend page
@app.route("/")
def index():
    return render_template("index.html")

# 🔐 Login endpoint
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)
    if user and user["password"] == password:
        return jsonify(success=True, account=user["account"])
    return jsonify(success=False, message="Invalid credentials"), 401

# 💸 Fund transfer endpoint
@app.route("/api/transfer", methods=["POST"])
def transfer():
    data = request.get_json()
    to_account = data.get("toAccount")
    amount = float(data.get("amount"))

    user = users.get("user1")  # Simulating single logged-in user
    account = user["account"]

    if account["balance"] >= amount:
        # Deduct from balance
        account["balance"] -= amount
        # Log the transaction
        account["transactions"].append({
            "type": "Transfer",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        return jsonify(success=True, message="Transfer successful", account=account)
    else:
        return jsonify(success=False, message="Insufficient balance"), 400

# 🏃 Run the Flask server
if __name__ == "__main__":
    app.run(debug=True)
