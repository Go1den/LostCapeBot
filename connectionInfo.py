import configparser
import socket

class ConnectionInfo:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('connectionSettings.txt')
        connectionSettings = config['ConnectionSettings']
        self.host = connectionSettings.get('host', "irc.chat.twitch.tv")
        self.port = int(connectionSettings.get('port', "6667"))
        self.nick = connectionSettings.get('botTwitchName', "")
        self.password = connectionSettings.get('botOauthPassword', "")
        self.channel = connectionSettings.get('joinTwitchChannelLowercaseOnly', "")
        self.channeloauth = connectionSettings.get('joinTwitchChannelOauthPassword', "")
        self.socket = socket.socket()

    # Method for sending a message to the IRC channel
    def sendMessage(self, message):
        self.socket.send(bytes("PRIVMSG #" + self.channel + " :" + message + "\r\n", "UTF-8"))
        print(self.nick + ": " + message)
