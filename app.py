from gevent import monkey;
monkey.patch_all()

import gevent
import os
from flask import Flask, render_template, request
from flask.ext.socketio import SocketIO, emit
from twython import TwythonStreamer

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
port = 5000

consumer_key = 'hDgwUvUp5ODnkCnNcmpXx1SjI'
consumer_secret = 'ZC9x8sv6GL0plhHkKeQPWL2UJTXeznoEDXSclJARPDkqeTgEtv'
access_token_key = '129161732-b6fdgdW3vhrwqyZoi9W2wBywiffZVLZVQwbspIRX'
access_token_secret = 'C8UH8bsXDqH5rbmP5g5UGqeUZZDQbns6J6uMgk5Oxw2xR'

class TwitterStreamer(TwythonStreamer):
    def __init__(self, *args, **kwargs):
        TwythonStreamer.__init__(self, *args, **kwargs)
        print("Initialized TwitterStreamer.")
        self.queue = gevent.queue.Queue()

    def on_success(self, data):
        self.queue.put_nowait(data)
        if self.queue.qsize() > 10000:
            self.queue.get()

    def on_error(self, status_code, data):
        print status_code, data, "TwitterStreamer stopped because of an error!"
        self.disconnect()


class Watch:
    def __init__(self):
        self.streamer = TwitterStreamer(consumer_key, consumer_secret, access_token_key, access_token_secret)
        locations = [-122.75,36.8,-121.75,37.8]
        self.green = gevent.spawn(self.streamer.statuses.filter, locations=locations)

    def check_alive(self):
        if self.green.dead:
            # stop everything
            self.streamer.disconnect()
            self.green.kill()
            # then reload
            self.__init__()


watch = Watch()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/tweets')
def tweets_connect():
    uid = request.namespace.socket.sessid
    print('Client %s connected' % uid)

    while True:
        try:
            tweet = watch.streamer.queue.get(timeout=5)
        except gevent.queue.Empty:
            watch.check_alive()
        else:
            emit('tweet', tweet, broadcast=True)


@socketio.on('disconnect', namespace='/tweets')
def tweets_disconnect():
    uid = request.namespace.socket.sessid
    print('Client %s disconnected' % uid)


if __name__ == '__main__':
    socketio.run(app, port=port, host="0.0.0.0")
