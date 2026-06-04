from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import os
import json
import csv

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = 'escape_secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory store for students
# dict: sid -> {'name': str, 'score': int, 'room': str, 'status': str, 'time_left': str}
students = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/download_answers')
def download_answers():
    answers_path = os.path.join(os.path.dirname(__file__), 'answers')
    if os.path.exists(answers_path):
        return send_file(answers_path, as_attachment=True, download_name='answers.txt')
    return "Answers file not found", 404

@app.route('/export_students')
def export_students():
    csv_path = os.path.join(os.path.dirname(__file__), 'students_export.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Session ID', 'Name', 'Score', 'Room', 'Status', 'Time Left'])
        for sid, data in students.items():
            writer.writerow([sid, data.get('name', ''), data.get('score', 0), data.get('room', ''), data.get('status', ''), data.get('time_left', '')])
    if os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True, download_name='students_export.csv')
    return "Failed to create export", 500

@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in students:
        # Mark as disconnected
        students[request.sid]['status'] = 'Disconnected'
        emit('admin_update', list(students.values()), broadcast=True)

@socketio.on('student_join')
def handle_student_join(data):
    name = data.get('name', 'Unknown Hacker')
    students[request.sid] = {
        'id': request.sid,
        'name': name,
        'score': 0,
        'room': 'room-1',
        'status': 'Playing',
        'time_left': '45:00'
    }
    emit_admin_update()

@socketio.on('progress_update')
def handle_progress_update(data):
    if request.sid in students:
        student = students[request.sid]
        student['score'] = data.get('score', student['score'])
        student['room'] = data.get('room', student['room'])
        student['time_left'] = data.get('time_left', student['time_left'])
        emit_admin_update()

@socketio.on('request_admin_update')
def handle_admin_request():
    emit_admin_update()

@socketio.on('student_finish')
def handle_student_finish(data):
    if request.sid in students:
        student = students[request.sid]
        student['status'] = data.get('status', 'Finished')
        student['score'] = data.get('score', student['score'])
        student['time_left'] = data.get('time_left', student['time_left'])
        emit_admin_update()

def emit_admin_update():
    emit('admin_update', list(students.values()), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
