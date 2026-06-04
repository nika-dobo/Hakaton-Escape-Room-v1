import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print("Student Connected!")
    sio.emit('student_join', {'name': 'TestStudent'})

@sio.event
def disconnect():
    print("Disconnected!")

sio.connect('http://localhost:5000')

time.sleep(2)
sio.emit('progress_update', {'score': 10, 'room': 'room-2', 'time_left': '44:00'})
time.sleep(2)
sio.disconnect()
