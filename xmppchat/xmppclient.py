from sleekxmpp import ClientXMPP
from xmppchat.api import red
import logging, ssl
import argparse
import threading, time
from datetime import datetime


# ejabberd-server url: xmpp-dhbw.spdns.org

def test(*args, **kwargs):
    print(args, kwargs)

class EchoBot(ClientXMPP):
    """
        -- xmpp client class
        class for sending and recieving messages to xmpp server
    """

    def __init__(self, jid, passwd, custom_stream_id):
        super(EchoBot, self).__init__(jid, passwd)
        #self.ssl_version = ssl.PROTOCOL_TLSv1_2
        print("custom stream id: {}".format(custom_stream_id))
        self.custom_stream_id = custom_stream_id
        print("Self argument custom stream id: {}".format(self.custom_stream_id))
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        #self['xep_0313'].retrieve(block=False, callback=test)

    def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            #print("Recieved msg from: %s" % str(msg['from']).split('/')[0])
            from_jid = str(msg['from']).split('/')[0]
            #print("Msg: %s" % msg['body'])
            msg_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            #print("Self.stream_id", self.custom_stream_id)
            #print("Recieved msg: ", "data: { \"msg\": \"%s\",\"from\": \"%s\",\"timestamp\": \"%s\",\"type\": \"%s\"}\n\n" % (msg['body'], from_jid, msg_timestamp, msg['type']))
            red.publish(self.custom_stream_id, "data: { \"msg\": \"%s\",\"from\": \"%s\",\"timestamp\": \"%s\",\"type\": \"%s\"}\n\n" % (msg['body'], from_jid, msg_timestamp, msg['type']))

    def push_message(self, to_jid, msg, subject, msg_type):
        self.send_message(mto=to_jid, mbody=msg, mtype=msg_type, msubject=subject)
