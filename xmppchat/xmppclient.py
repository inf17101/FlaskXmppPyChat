from sleekxmpp import ClientXMPP
from xmppchat.api import red
from datetime import datetime
import ssl


# ejabberd-server url: xmpp-dhbw.spdns.org

class EchoBot(ClientXMPP):
    """
        -- xmpp client class
        class for sending and recieving messages to xmpp server
    """

    def __init__(self, jid, passwd, custom_stream_id):
        super(EchoBot, self).__init__(jid, passwd)
        self.ssl_version = ssl.PROTOCOL_TLSv1_2 # set tls 1.2
        self.custom_stream_id = custom_stream_id
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)

    def start(self, event):
        """
            callback method after connecting to server
        """
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        """
            called from event_handler if a message has been recieved.
        """
        if msg['type'] in ('normal', 'chat'):
            from_jid = str(msg['from']).split('/')[0]
            msg_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            red.publish(self.custom_stream_id, "data: { \"msg\": \"%s\",\"from\": \"%s\",\"timestamp\": \"%s\",\"type\": \"%s\"}\n\n" % (msg['body'], from_jid, msg_timestamp, msg['type']))

    def push_message(self, to_jid, msg, subject, msg_type):
        try:
            self.send_message(mto=to_jid, mbody=msg, mtype=msg_type, msubject=subject)
        except Exception as e:
            print(str(e))
            raise e

