from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

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

@app.route("/")
def home():
    return "Banking Portal Backend is running!"

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)
    if user and user["password"] == password:
        return jsonify(success=True, account=user["account"])
    return jsonify(success=False, message="Invalid credentials"), 401

@app.route("/api/transfer", methods=["POST"])
def transfer():
    data = request.get_json()
    to_account = data.get("toAccount")
    amount = float(data.get("amount"))

    user = users.get("user1")
    account = user["account"]

    if account["balance"] >= amount:
        account["balance"] -= amount
        account["transactions"].append({
            "type": "Transfer",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        return jsonify(success=True, message="Transfer successful", account=account)
    else:
        return jsonify(success=False, message="Insufficient balance"), 400

if __name__ == "__main__":
    app.run(debug=True)
