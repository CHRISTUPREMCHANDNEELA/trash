from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
CORS(app)
app.secret_key = 'super_secret_key'

USERS_FILE = 'users.json'
TRANSACTIONS_FILE = 'transactions.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        print(f"Warning: {USERS_FILE} not found. Returning empty user list.")
        return []
    with open(USERS_FILE, 'r') as f:
        try:
            users = json.load(f)
            print(f"✅ Loaded {len(users)} users from {USERS_FILE}")
            return users
        except json.JSONDecodeError as e:
            print(f"❌ Error reading {USERS_FILE}: {e}")
            return []

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_transactions():
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    with open(TRANSACTIONS_FILE, 'r') as f:
        return json.load(f)

def save_transactions(txns):
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump(txns, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/transfer')
def transfer_page():
    return render_template('transfer.html')

@app.route('/transactions')
def txn_page():
    return render_template('transactions.html')

@app.route('/api/users', methods=['GET'])
def list_users():
    users = load_users()
    return jsonify({'accounts': [u['account_no'].strip() for u in users]})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    users = load_users()
    for user in users:
        if user['username'] == data['username'] and check_password_hash(user['password'], data['password']):
            return jsonify({
                'status': 'success',
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'account_no': user['account_no'],
                    'balance': user['balance']
                }
            })
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.json
    users = load_users()
    txns = load_transactions()

    to_account = data['to_account'].strip().upper()
    from_user = next((u for u in users if u['id'] == data['from_user_id']), None)
    to_user = next((u for u in users if u['account_no'].strip().upper() == to_account), None)

    print("🔍 Incoming transfer request:")
    print("  From user id:", data['from_user_id'])
    print("  To account:", to_account)
    print("  All user accounts:", [u['account_no'].strip().upper() for u in users])

    if not from_user:
        print("❌ Sender not found")
        return jsonify({'status': 'error', 'message': 'Sender not found'}), 404
    if not to_user:
        print("❌ Recipient not found")
        return jsonify({'status': 'error', 'message': 'Recipient not found'}), 404
    if from_user['account_no'].strip().upper() == to_user['account_no'].strip().upper():
        return jsonify({'status': 'error', 'message': 'Cannot transfer to the same account'}), 400
    if data['amount'] <= 0:
        return jsonify({'status': 'error', 'message': 'Amount must be greater than zero'}), 400
    if from_user['balance'] < data['amount']:
        return jsonify({'status': 'error', 'message': 'Insufficient balance'}), 400

    from_user['balance'] -= data['amount']
    to_user['balance'] += data['amount']

    from_user['balance'] = round(from_user['balance'], 2)
    to_user['balance'] = round(to_user['balance'], 2)

    now = datetime.utcnow().isoformat()
    txns.append({'user_id': from_user['id'], 'type': 'transfer', 'amount': -data['amount'], 'date': now})
    txns.append({'user_id': to_user['id'], 'type': 'transfer', 'amount': data['amount'], 'date': now})

    save_users(users)
    save_transactions(txns)

    print("✅ Transfer successful")
    return jsonify({'status': 'success', 'message': 'Transfer successful'})

@app.route('/api/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    txns = load_transactions()
    user_txns = [t for t in txns if t['user_id'] == user_id]
    user_txns.sort(key=lambda x: x['date'], reverse=True)
    return jsonify([{
        'date': datetime.fromisoformat(t['date']).strftime('%Y-%m-%d %H:%M'),
        'type': t['type'],
        'amount': t['amount']
    } for t in user_txns])

def init_files():
    if not os.path.exists(USERS_FILE):
        default_user = {
            'id': 1,
            'username': 'rahul123',
            'password': generate_password_hash('1234'),
            'account_no': 'SB123456',
            'balance': 10000.0,
            'name': 'Rahul'
        }
        save_users([default_user])

    if not os.path.exists(TRANSACTIONS_FILE):
        save_transactions([])

if __name__ == '__main__':
    init_files()
    app.run(debug=True)