import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print("Admin Connected!")
    sio.emit('request_admin_update')

@sio.on('admin_update')
def on_message(data):
    print("Admin received update:", data)

sio.connect('http://localhost:5000')
time.sleep(10)
sio.disconnect()
