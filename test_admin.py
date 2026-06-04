import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print("Admin Connected to Render!")
    sio.emit('request_admin_update')

@sio.on('admin_update')
def on_message(data):
    print("Admin received update from Render:", data)

sio.connect('https://hakaton-escape-room-v1.onrender.com')
time.sleep(3)
sio.disconnect()
