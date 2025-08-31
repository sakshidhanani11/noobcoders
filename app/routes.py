
from flask import render_template, jsonify
from . import app
from .database import SessionLocal
from .models import User

@app.route('/')
def home():
    return render_template('index.html')

# Test endpoint to fetch all users
@app.route('/users', methods=['GET'])
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    result = [
        {"id": u.id, "username": u.username, "email": u.email}
        for u in users
    ]
    db.close()
    return jsonify(result)