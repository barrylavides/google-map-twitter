from gevent import monkey;
monkey.patch_all()

import gevent
import os
from flask import Flask, render_template, request, jsonify
from flask.ext.socketio import SocketIO, emit
from twython import TwythonStreamer

app = Flask(__name__)
app.debug = True
app.host = '0.0.0.0'
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

    def on_error(self, status_code, data):
        print status_code, data, "TwitterStreamer stopped because of an error!"
        self.disconnect()


class Watch:
    def __init__(self, sw_lng=None, sw_lat=None, ne_lng=None, ne_lat=None):
        print 'Start stream'
        self.streamer = TwitterStreamer(consumer_key, consumer_secret, access_token_key, access_token_secret)
        
        # CA
        #locations = [-122.75,36.8,-121.75,37.8]

        if sw_lng == None:
            # Metro Manila
            self.sw_lng = 120.9172569
            self.sw_lat = 14.3493861
            self.ne_lng = 121.132012
            self.ne_lat = 14.781217
        else:
            self.sw_lng = sw_lng
            self.sw_lat = sw_lat
            self.ne_lng = ne_lng
            self.ne_lat = ne_lat

        locations = [self.sw_lng, self.sw_lat, self.ne_lng, self.ne_lat]
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


@app.route('/change_location', methods=['POST'])
def change_location():
    data = request.json

    # Change stream location
    sw_lng = data['sw']['lng']
    sw_lat = data['sw']['lat']
    ne_lng = data['ne']['lng']
    ne_lat = data['ne']['lat']
    
    watch.__init__(sw_lng, sw_lat, ne_lng, ne_lat)

    return jsonify({
        'status': 'Received',
        'data': data
    }), 200


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
    socketio.run(app, port=port)
