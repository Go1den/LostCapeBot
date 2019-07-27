import configparser
import datetime
import statistics
import textwrap
import threading
import time

import fileHandler
import messageConstants
import pastebin

class MarioMaker:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('marioMakerSettings.txt')
        marioMakerSettings = config['MarioMakerSettings']
        self.enableMarioMakerCommands = bool(marioMakerSettings.get('enableMarioMakerCommands', "0"))
        self.maxQueueSize = int(marioMakerSettings.get('maxQueueSize', "5"))
        self.rankList = []
        self.queueOpen = False
        self.queue = []
        self.queueSummary = ""
        self.levelSummary = ""
        self.nextStage = ""
        fileHandler.writeToFile('currentLevel.txt', 'w', "")
        fileHandler.writeToFile('queueOpen.txt', 'w', "")
        self.startThread()

    def openQueue(self, ci):
        self.queueOpen = True
        ci.sendMessage(messageConstants.QUEUE_OPEN)

    def closeQueue(self, ci):
        self.queueOpen = False
        ci.sendMessage(messageConstants.QUEUE_CLOSED)
        fileHandler.writeToFile('queueOpen.txt', 'w', "")

    def clearQueue(self, ci):
        self.queue = []
        ci.sendMessage(messageConstants.QUEUE_CLEARED)

    def queueOpenThread(self):
        while True:
            if self.queueOpen:
                fileHandler.writeToFile('queueOpen.txt', 'w', "  The queue is open!  ")
                time.sleep(5)
            if self.queueOpen:
                fileHandler.writeToFile('queueOpen.txt', 'w', "  Type !add in chat!  ")
                time.sleep(5)

    def startThread(self):
        queueOpenThread = threading.Thread(target=self.queueOpenThread)
        queueOpenThread.start()

    def setMaxQueueSize(self, size, ci):
        self.maxQueueSize = size
        ci.sendMessage("The queue length has been adjusted to " + size + " levels.")

    def resetRankList(self):
        self.rankList = []

    def rankListIsEmpty(self):
        return len(self.rankList) == 0

    def validateUserNotAlreadyInRankList(self, user):
        for rank in self.rankList:
            if rank[0] == user:
                return False
        return True

    def calculateChatRank(self):
        chatRank = str(round(statistics.mean([rank[1] for rank in self.rankList]), 2))
        return chatRank + " out of 5"

    def addToRankList(self, user, score):
        if score in [1, 2, 3, 4, 5] and self.validateUserNotAlreadyInRankList(user):
            print(user + " ranked this course " + str(score) + " out of 5")
            self.rankList.append([user, score])
        else:
            print("Invalid rank attempt by " + user)

    def addToQueue(self, message, username, ci):
        if self.queueOpen:
            if self.validateLevelAndAddToQueue(message, username):
                position = len(self.queue)
                ci.sendMessage(username + ", your level was added to the queue in position #" + str(position) + "!")
                if len(self.queue) >= self.maxQueueSize:
                    self.queueOpen = False
                    ci.sendMessage(messageConstants.QUEUE_CLOSED)
                    fileHandler.writeToFile('queueOpen.txt', 'w', "")
        else:
            ci.sendMessage(messageConstants.QUEUE_CLOSED)

    def nextInQueue(self, ci):
        try:
            if not self.rankListIsEmpty():
                chatRank = self.calculateChatRank()
                ci.sendMessage("Chat's Course Rating: " + chatRank)
                self.queueSummary += "\n" + "Viewer Rating: " + chatRank + " (" + str(
                    len(self.rankList)) + " viewers voting)"
                self.resetRankList()
            self.nextStage = self.queue.pop(0)
            ci.sendMessage("Now playing " + self.nextStage[0] + "'s submission: " + self.nextStage[1])
            fileHandler.writeToFile('currentLevel.txt', 'w', "  " + self.nextStage[1] + "  ")
            self.queueSummary += "\n\n" + self.nextStage[0] + "'s submission: " + self.nextStage[1]
        except:
            ci.sendMessage(messageConstants.QUEUE_EMPTY)

    def playLevelNotInQueue(self, message, ci):
        if not self.rankListIsEmpty():
            chatRank = self.calculateChatRank()
            ci.sendMessage("Chat's Course Rating: " + chatRank)
            self.queueSummary += "\n" + "Viewer Rating: " + chatRank + " (" + str(
                len(self.rankList)) + " viewers voting)"
            self.resetRankList()
        self.nextStage = [ci.channel.capitalize(), message.split()[1]]
        fileHandler.writeToFile('currentLevel.txt', 'w', "  " + ci.channel.capitalize() + "'s Choice: " + message.split()[1] + "  ")
        ci.sendMessage("Now playing " + ci.channel.capitalize() + "'s choice: " + message.split()[1])
        self.queueSummary += "\n\n" + ci.channel.capitalize() + "'s choice: " + message.split()[1]

    def nameCurrentLevel(self, message):
        self.queueSummary += "\n" + message[6:]
        fileHandler.writeToFile('currentLevel.txt', 'w', "  " + message[6:] + "  " + self.nextStage[1] + "  ")

    def validateLevelAndAddToQueue(self, message, username):
        if self.validateUserNotAlreadyInQueue(username) and len(message.split()) > 1:
            levelCode = message.split()[1].replace("-", "")
            print("Stripped level code: " + levelCode)
            if self.validateLevelCode(levelCode):
                self.queue.append([username, self.padLevelCode(levelCode)])
                return True
            else:
                return False

    def validateLevelAndUpdateQueue(self, message, username, ci):
        if not self.validateUserNotAlreadyInQueue(username) and len(message.split()) > 1:
            levelCode = message.split()[1].replace("-", "")
            print("Stripped level code: " + levelCode)
            if self.validateLevelCode(levelCode):
                for x in self.queue:
                    if x[0] == username:
                        x[1] = self.padLevelCode(levelCode)
                ci.sendMessage(username + ", your level code was updated successfully!")
                return True
            else:
                return False

    def validateUserNotAlreadyInQueue(self, username):
        for level in self.queue:
            if level[0] == username:
                print(username + " already in queue.")
                return False
        return True

    def validateLevelCode(self, levelCode):
        if len(levelCode) == 9 and levelCode.isalnum():
            return True
        else:
            print("Invalid level code! " + levelCode)
            return False

    def padLevelCode(self, levelCode):
        segmentsOfLevelCode = textwrap.wrap(levelCode, 3)
        print("Level code: " + '-'.join(segmentsOfLevelCode))
        return '-'.join(segmentsOfLevelCode).upper()

    def removeFromQueue(self, username, ci):
        self.queue = [x for x in self.queue if x[0] != username]
        ci.sendMessage(messageConstants.QUEUE_REMOVEDUSER)

    def writeToPastebin(self, ci):
        try:
            todaysDateTime = datetime.date.today().strftime("%B %d, %Y")
            pb = pastebin.Pastebin()
            pastebinURL = pb.makePastebin("Mario Maker Queue from  " + todaysDateTime, self.queueSummary)
            ci.sendMessage("Summary of today's streamed levels: " + pastebinURL)
            self.queueSummary = ""
        except:
            ci.sendMessage(messageConstants.PASTEBIN_FAILURE)

    def processBroadcasterCommands(self, message, ci):
        if message == "!open":
            self.openQueue(ci)
            return True
        if message == "!close":
            self.closeQueue(ci)
            return True
        if message == "!clear":
            self.clearQueue(ci)
            return True
        if message.startswith("!size") and len(message.split()) == 2:
            self.setMaxQueueSize(message.split()[1], ci)
            return True
        if message == "!next":
            self.nextInQueue(ci)
            return True
        if message.startswith("!id"):
            self.playLevelNotInQueue(message, ci)
            return True
        if message.startswith("!name"):
            self.nameCurrentLevel(message)
            return True
        if message == "!summary":
            self.writeToPastebin(ci)
            return True
        else:
            return False

    def processUserCommands(self, message, username, ci):
        if message.startswith('!add') or message.startswith('!submit'):
            self.addToQueue(message, username, ci)
            return True
        if message.startswith('!update'):
            self.validateLevelAndUpdateQueue(message, username, ci)
            return True
        if message == "!cancel" or message == "!remove":
            self.removeFromQueue(username, ci)
            return True
        if (message.startswith('!rank') or message.startswith('!rate')) and len(message.split()) == 2:
            self.addToRankList(username, int(message.split()[1]))
            return True
        else:
            return False
