def send_progress(socketio, progress):
    socketio.emit('progress', {'progress': progress}, broadcast=True)