from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

app = Flask(__name__)
app.debug=True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

socketio = SocketIO(app, manage_session=False, logger=True, engineio_logger=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/chatroom', methods=['GET', 'POST'])
def chatroom():
    # Get form data and store into session variables
    if request.method == 'POST':
        username = request.form['username']
        room = request.form['room']
        session['username'] = username
        session['room'] = room
        return render_template('chatroom.html', session=session)
    else:
        # if the user is logged in
        if (session.get('username') is not None):
            return render_template('chatroom.html', session=session)
        else:
            return redirect(url_for('index'))


@socketio.on('join', namespace='/chatroom')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('username') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chatroom')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chatroom')
def left(message):
    room=session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)


if __name__ == '__main__':
    socketio.run(app)
