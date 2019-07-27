import configparser
import socket

class ConnectionInfo:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('connectionSettings.txt')
        self.host = config['ConnectionSettings']['host']
        self.port = int(config['ConnectionSettings']['port'])
        self.nick = config['ConnectionSettings']['botTwitchName']
        self.password = config['ConnectionSettings']['botOauthPassword']
        self.channel = config['ConnectionSettings']['joinTwitchChannelLowercaseOnly']
        self.channeloauth = config['ConnectionSettings']['joinTwitchChannelOauthPassword']
        self.socket = socket.socket()

    # Method for sending a message to the channel
    def sendMessage(self, message):
        self.socket.send(bytes("PRIVMSG #" + self.channel + " :" + message + "\r\n", "UTF-8"))
        print(self.nick + ": " + message)
