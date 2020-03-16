
import unittest
import datetime, re

regex = re.compile(r"from='([A-Za-z0-9]+)@[A-Za-z0-9-]+")

def get_chat_history(username, testdata):
    POSITION_XML = 1
    #chat_rosters = Archiv.query.filter_by(username=username).group_by("bare_peer").all()
    #chat_rosters_bare_peers = [roster.bare_peer for roster in chat_rosters]
    chat_msgs = []
    #for bare_peer in chat_rosters_bare_peers:
        #results = Archiv.query.with_entities(Archiv.txt, Archiv.xml, Archiv.created_at, Archiv.kind).filter_by(username=username).filter_by(bare_peer=bare_peer).all()
    peer_msgs = {}
    list_peer_msgs = []
    for item in testdata:
        match = re.findall(regex, item[POSITION_XML])
        print(match)
        list_peer_msgs.append({"txt": item[0], "timestamp": item[2], "type": item[3], "from": match[0]})
    
    chat_msgs.append({"test": list_peer_msgs})
    print(chat_msgs)
    print(list(sorted(list_peer_msgs, key=lambda k: k["timestamp"])))
    return chat_msgs

class TestGetChatHistory(unittest.TestCase):

    def setUp(self):
        self.test_data = [('hallo', "<message xml:lang='en' to='test@ejabberd-server' from='testuser2@ejabberd-server/13327548113920231042259' type='chat' xmlns='jabber:client'><body>hallo</body><subject>first_message</subject></message>", datetime.datetime(2020, 2, 21, 14, 26, 22), 'chat'), ('wie geht es Ihnen?', "<message xml:lang='en' to='testuser2@ejabberd-server/13327548113920231042259' from='test@ejabberd-server/156650462527463612551026' type='chat' id='15813f3d-a577-4672-b205-b7db61640547' xmlns='jabber:client'><body>wie geht es Ihnen?</body></message>", datetime.datetime(2020, 2, 21, 14, 26, 38), 'chat'), ('mir geht es gut', "<message xml:lang='en' to='test@ejabberd-server' from='testuser2@ejabberd-server/13327548113920231042259' type='chat' xmlns='jabber:client'><body>mir geht es gut</body><subject>first_message</subject></message>", datetime.datetime(2020, 2, 21, 14, 26, 46), 'chat'), ('ljkjl', "<message xml:lang='en' to='testuser2@ejabberd-server/13327548113920231042259' from='test@ejabberd-server/156650462527463612551026' type='chat' id='874a8527-5038-4547-8efa-04f7b23b98a4' xmlns='jabber:client'><body>ljkjl</body></message>", datetime.datetime(2020, 2, 21, 14, 28, 25), 'chat'), ('lksjflksjdfkls', "<message xml:lang='en' to='testuser2@ejabberd-server' from='test@ejabberd-server/153310312677219130853394' type='chat' id='6eb312d3-2224-451c-a917-69d4b275b615' xmlns='jabber:client'><active xmlns='http://jabber.org/protocol/chatstates'/><body>lksjflksjdfkls</body></message>", datetime.datetime(2020, 3, 4, 13, 14, 54), 'chat'), ('laskdfksdjfsdf', "<message xml:lang='en' to='testuser2@ejabberd-server' from='test@ejabberd-server/153310312677219130853394' type='chat' id='7adb7d6d-b714-465f-b639-72deb3d917d9' xmlns='jabber:client'><active xmlns='http://jabber.org/protocol/chatstates'/><body>laskdfksdjfsdf</body></message>", datetime.datetime(2020, 3, 4, 13, 16, 4), 'chat'), ('alskdjfklsdjf', "<message xml:lang='en' to='testuser2@ejabberd-server' from='test@ejabberd-server/153310312677219130853394' type='chat' id='884644c0-0594-4893-b117-d09ec8948c07' xmlns='jabber:client'><active xmlns='http://jabber.org/protocol/chatstates'/><body>alskdjfklsdjf</body></message>", datetime.datetime(2020, 3, 4, 13, 22, 17), 'chat'), ('aslkfjdlkf', "<message xml:lang='en' to='test@ejabberd-server' from='testuser2@ejabberd-server/138130434412002491163490' type='chat' xmlns='jabber:client'><body>aslkfjdlkf</body><subject>first_message</subject></message>", datetime.datetime(2020, 3, 4, 13, 29, 57), 'chat'), ('aslfkasdkf', "<message xml:lang='en' to='testuser2@ejabberd-server/138130434412002491163490' from='test@ejabberd-server/153310312677219130853394' type='chat' id='5c0533dd-c962-4403-a165-78d0c63ecb3c' xmlns='jabber:client'><body>aslfkasdkf</body></message>", datetime.datetime(2020, 3, 4, 13, 30, 8), 'chat'), ('alsfjldksfj :-)', "<message xml:lang='en' to='testuser2@ejabberd-server/138130434412002491163490' from='test@ejabberd-server/153310312677219130853394' type='chat' id='06c8e636-2653-4132-b569-f14bbffd46a6' xmlns='jabber:client'><body>alsfjldksfj :-)</body></message>", datetime.datetime(2020, 3, 4, 13, 30, 22), 'chat'), (':-)\n', "<message xml:lang='en' to='test@ejabberd-server' from='testuser2@ejabberd-server/138130434412002491163490' type='chat' xmlns='jabber:client'><body>:-)\n</body><subject>first_message</subject></message>", datetime.datetime(2020, 3, 4, 13, 30, 33), 'chat'), ('aslöfjsdjf', "<message xml:lang='en' to='testuser2@ejabberd-server' from='test@ejabberd-server/136844124671322524783826' type='chat' id='246ce1b7-88e2-4fbe-a8ac-e5bdb30aa798' xmlns='jabber:client'><active xmlns='http://jabber.org/protocol/chatstates'/><body>aslöfjsdjf</body></message>", datetime.datetime(2020, 3, 7, 10, 16, 17), 'chat')]


    def test_get_chat_history(self):
        get_chat_history("test", self.test_data)


if __name__ == "__main__":
    unittest.main()