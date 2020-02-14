from sleekxmpp import ClientXMPP
import logging, ssl
import argparse
import threading, time


# ejabberd-server url: xmpp-dhbw.spdns.org

def test(*args, **kwargs):
    print(args, kwargs)


class EchoBot(ClientXMPP):
    """
        -- xmpp client class
        class for sending and recieving messages to xmpp server
    """

    def __init__(self, jid, passwd):
        super(EchoBot, self).__init__(jid, passwd)
        #self.ssl_version = ssl.PROTOCOL_TLSv1_2
        self.add_event_handler('session_start', self.start, threaded=True)
        self.add_event_handler('message', self.message, threaded=True)

    def start(self, event):
        self.send_presence()
        self.get_roster()
        #self['xep_0313'].retrieve(block=False, callback=test)

    def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            print("Recieved msg from: %s" % str(msg['from']).split('/')[0])
            print("Msg: %s" % msg['body'])
            # self.send_message(mto=msg['from'], mbody=f"Thanks for sending: {msg['body']}")
            # self.disconnect(wait=True)

    def push_message(self, msg, subject):
        self.send_message(mto="test@ejabberd-server", mbody=msg, mtype="chat", msubject=subject)

    def exit(self):
        self.process(block=False)

""" 
if __name__ == "__main__":
    xmpp_client = EchoBot("testuser2@ejabberd-server", "hallo123")
    plugins = ['xep_0030', 'xep_0004', 'xep_0060', 'xep_0199', 'xep_0313']
    xmpp_client['feature_mechanisms'].unencrypted_plain = True

    for item in plugins:
        xmpp_client.register_plugin(item)

    if xmpp_client.connect(("10.10.8.10", 5222)):
        print("success!")
        xmpp_client.process(block=True)
"""