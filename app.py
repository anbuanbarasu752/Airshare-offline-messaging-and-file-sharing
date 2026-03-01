import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

socketio = SocketIO(app)
users = {}

# Create uploads folder if not exists
if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")

@app.route("/")
def home():
    return render_template("index.html")

# 🔥 FILE UPLOAD ROUTE
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        return jsonify({"url": "/" + filepath})
    return jsonify({"error": "Upload failed"})


# JOIN
@socketio.on("join")
def handle_join(username):
    users[request.sid] = username
    emit("message", {
        "user": "System",
        "msg": f"{username} joined the chat",
        "time": datetime.now().strftime("%H:%M")
    }, broadcast=True)

# MESSAGE
@socketio.on("message")
def handle_message(data):
    emit("message", {
        "user": data["user"],
        "msg": data["msg"],
        "time": datetime.now().strftime("%H:%M")
    }, broadcast=True)

# DISCONNECT
@socketio.on("disconnect")
def handle_disconnect():
    username = users.get(request.sid)
    if username:
        emit("message", {
            "user": "System",
            "msg": f"{username} left the chat",
            "time": datetime.now().strftime("%H:%M")
        }, broadcast=True)
        users.pop(request.sid)

if __name__ == "__main__":
    socketio.run(app)