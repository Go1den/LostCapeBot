from src.modules.mariomaker import marioMaker
from src.modules.twitchirc import connectionInfo
from src.modules.twitter import twitter

ci = connectionInfo.ConnectionInfo()

marioMakerModule = marioMaker.MarioMaker()
twitterModule = twitter.Twitter(ci.channel)

modules = [marioMakerModule, twitterModule]

def parseBroadcasterMessage(message):
    if message == "!goodbye":
        ci.sendMessage("I uhh die- I died!")
        ci.socket.close()
        exit(1)
    else:
        for module in modules:
            if module.processBroadcasterCommands(message, ci):
                return

def parseUserMessage(message, username):
    for module in modules:
        if module.processUserCommands(message, username, ci):
            return

# Connecting to Twitch IRC
ci.socket.connect((ci.host, ci.port))
ci.socket.send(bytes("PASS " + ci.password + "\r\n", "UTF-8"))
ci.socket.send(bytes("NICK " + ci.nick + "\r\n", "UTF-8"))
ci.socket.send(bytes("JOIN #" + ci.channel + " \r\n", "UTF-8"))

ci.sendMessage(ci.nick + " is online!")

while True:
    line = str(ci.socket.recv(1024))
    if "End of /NAMES list" in line:
        break

while True:
    for line in ci.socket.recv(1024).decode().split('\\r\\n'):
        parts = line.split(":")
        if "PING" in parts[0]:
            print(line[1])
            ci.socket.send(bytes("PONG %s\r\n" % parts[1], "UTF-8"))
        if len(parts) < 3:
            continue
        if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
            message = parts[2][:len(parts[2])].strip()
            username = parts[1].split("!")[0].strip()
            usernameLower = username.lower().strip()
            try:
                print(username + ": " + message)
            except:
                print(username + " has posted something with an invalid character(s)")
            else:
                if usernameLower == ci.channel:
                    parseBroadcasterMessage(message)
                else:
                    parseUserMessage(message, username)
