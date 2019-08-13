import configparser
import datetime
import threading
import time

from src import fileHandler
from src.modules.abstractChatCommands import AbstractChatCommands
from src.modules.mariomaker import marioMakerMessageConstants, marioMakerHelperMethods
from src.modules.mariomaker.marioMakerLevel import MarioMakerLevel
from src.modules.pastebin import pastebin
from src.modules.wordpress.wordpress import Wordpress

FILE_CURRENTLEVEL = 'src/modules/mariomaker/currentLevel.txt'
FILE_QUEUEOPEN = 'src/modules/mariomaker/queueOpen.txt'
FILE_SETTINGS = 'src/modules/mariomaker/marioMakerSettings.txt'
FILE_QUEUE = 'src/modules/mariomaker/queue.txt'

class MarioMaker(AbstractChatCommands):

    def __init__(self):
        config = configparser.ConfigParser()
        config.read(FILE_SETTINGS)
        marioMakerSettings = config['MarioMakerSettings']
        self.enableMarioMakerCommands = bool(int(marioMakerSettings.get('enableMarioMakerCommands', "0")))
        self.maxQueueSize = int(marioMakerSettings.get('maxQueueSize', "5"))
        self.enableOCR = bool(int(marioMakerSettings.get('enableOCR', "0")))
        self.wordpressPostID = int(marioMakerSettings.get('marioMakerPostID', "0"))
        self.wordpress = Wordpress()
        self.queueOpen = False
        self.queue = []
        self.queueSummary = ""
        self.currentLevel = None
        fileHandler.writeToFile(FILE_CURRENTLEVEL, "")
        fileHandler.writeToFile(FILE_QUEUEOPEN, "")
        self.startThread()
        self.writeQueueToFileAndWordpress()

    def openQueue(self, ci):
        self.queueOpen = True
        ci.sendMessage(marioMakerMessageConstants.QUEUE_OPEN)
        self.writeQueueToWordpress()

    def closeQueue(self, ci):
        self.queueOpen = False
        ci.sendMessage(marioMakerMessageConstants.QUEUE_CLOSED)
        fileHandler.writeToFile(FILE_QUEUEOPEN, "")
        self.writeQueueToWordpress()

    def clearQueue(self, ci):
        self.queue = []
        self.writeQueueToFileAndWordpress()
        ci.sendMessage(marioMakerMessageConstants.QUEUE_CLEARED)

    def queueOpenThread(self):
        while True:
            if self.queueOpen:
                fileHandler.writeToFile(FILE_QUEUEOPEN, "  The queue is open!  ")
                time.sleep(5)
            if self.queueOpen:
                fileHandler.writeToFile(FILE_QUEUEOPEN, "  Type !add in chat!  ")
                time.sleep(5)

    def startThread(self):
        queueOpenThread = threading.Thread(target=self.queueOpenThread)
        queueOpenThread.start()

    def setMaxQueueSize(self, size, ci):
        if size.isnumeric():
            self.maxQueueSize = int(size)
            ci.sendMessage("The queue length has been adjusted to " + size + " levels.")

    def writeQueueToFileAndWordpress(self):
        self.writeQueueToFile()
        self.writeQueueToWordpress()

    def writeQueueToFile(self):
        queueString = ""
        idx = 1
        for level in self.queue:
            queueString += str(idx) + '. ' + level.submitter + ' ' + level.id + "\n"
            idx += 1
        fileHandler.writeToFile(FILE_QUEUE, queueString)

    def writeQueueToWordpress(self):
        if self.wordpress.enableWordpressCommands:
            wpQueueString = "<table><tr><th>#</th><th>Submitter</th><th>Level ID</th></tr>"
            idx = 1
            for level in self.queue:
                wpQueueString += "<tr><td>" + str(idx) + '</td><td>' + level.submitter + '</td><td>' + level.id + "</td></tr>"
                idx += 1
            wpQueueString += "</table>"
            if self.queueOpen:
                queueStatus = "<h2 style=\"color: green\">The queue is open!</h2>"
            else:
                queueStatus = "<h2 style=\"color: red\">The queue is closed!</h2>"
            queueStatus += "Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d    %H:%M:%S") + "\n"
            self.wordpress.editPost('Mario Maker Queue', queueStatus + wpQueueString, self.wordpressPostID)

    def addToQueue(self, message, username, ci):
        if self.queueOpen:
            if self.validateLevelAndAddToQueue(message, username, ci):
                position = len(self.queue)
                ci.sendMessage(username + ", your level was added to the queue in position #" + str(position) + "!")
                self.writeQueueToFileAndWordpress()
                if len(self.queue) >= self.maxQueueSize:
                    self.queueOpen = False
                    ci.sendMessage(marioMakerMessageConstants.QUEUE_CLOSED)
                    fileHandler.writeToFile(FILE_QUEUEOPEN, "")
        else:
            ci.sendMessage(marioMakerMessageConstants.QUEUE_CLOSED)

    def nextInQueue(self, ci):
        try:
            if self.currentLevel is not None:
                self.currentLevel.sendCourseRatingChatMessage(ci)
                self.queueSummary += self.currentLevel.getLevelSummary()
            self.currentLevel = self.queue.pop(0)
            self.writeQueueToFileAndWordpress()
            self.currentLevel.sendNowPlayingChatMessageAndUpdateLevelFile(ci)
        except:
            ci.sendMessage(marioMakerMessageConstants.QUEUE_EMPTY)

    def playLevelNotInQueue(self, message, ci):
        try:
            if self.currentLevel is not None:
                self.currentLevel.sendCourseRatingChatMessage(ci)
                self.queueSummary += self.currentLevel.getLevelSummary()
            self.currentLevel = MarioMakerLevel(ci.channel.capitalize(), message.split()[1])
            self.currentLevel.sendNowPlayingChatMessageAndUpdateLevelFile(ci)
        except:
            ci.sendMessage(marioMakerMessageConstants.ERROR_PLAYING_LEVEL_NOT_IN_QUEUE)

    def validateLevelAndAddToQueue(self, message, username, ci):
        try:
            if self.validateUserNotAlreadyInQueue(username) and len(message.split()) > 1:
                levelCode = message.split()[1].replace("-", "")
                if marioMakerHelperMethods.validateLevelCode(levelCode):
                    self.queue.append(MarioMakerLevel(username, marioMakerHelperMethods.padLevelCode(levelCode)))
                    return True
                else:
                    return False
        except:
            ci.sendMessage(marioMakerMessageConstants.ERROR_INVALID_SUBMISSION)

    def validateLevelAndUpdateQueue(self, message, username, ci):
        try:
            if not self.validateUserNotAlreadyInQueue(username) and len(message.split()) > 1:
                levelCode = message.split()[1].replace("-", "")
                if marioMakerHelperMethods.validateLevelCode(levelCode):
                    for level in self.queue:
                        if level.submitter == username:
                            level.id = marioMakerHelperMethods.padLevelCode(levelCode)
                            self.writeQueueToFileAndWordpress()
                    ci.sendMessage(username + ", your level code was updated successfully!")
                    return True
                else:
                    return False
        except:
            ci.sendMessage(marioMakerMessageConstants.ERROR_INVALID_SUBMISSION)

    def validateUserNotAlreadyInQueue(self, username):
        for level in self.queue:
            if level.submitter == username:
                print(username + " is already in the queue.")
                return False
        return True

    def removeFromQueue(self, username, ci):
        self.queue = [level for level in self.queue if level.submitter != username]
        self.writeQueueToFileAndWordpress()
        ci.sendMessage(marioMakerMessageConstants.QUEUE_REMOVEDUSER)

    def writeToPastebin(self, ci):
        try:
            todaysDateTime = datetime.date.today().strftime("%B %d, %Y")
            pb = pastebin.Pastebin()
            pastebinURL = pb.makePastebin("Mario Maker Queue from  " + todaysDateTime, self.queueSummary)
            ci.sendMessage("Summary of today's streamed levels: " + pastebinURL)
            self.queueSummary = ""
        except:
            ci.sendMessage(marioMakerMessageConstants.PASTEBIN_FAILURE)

    def processBroadcasterCommands(self, message, ci):
        try:
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
            if message.startswith("!name") and len(message) > 5:
                if self.currentLevel is not None:
                    self.currentLevel.setName(message[6:])
                return True
            if message == "!summary":
                self.writeToPastebin(ci)
                return True
            if self.enableOCR and message == "!ocr" and self.currentLevel is not None:
                self.currentLevel.getOCRData()
            else:
                return False
        except:
            print(marioMakerMessageConstants.ERROR_BROADCASTER_COMMANDS)
            return False

    def processUserCommands(self, message, username, ci):
        try:
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
                if self.currentLevel is not None:
                    self.currentLevel.addToRankList(username, message.split()[1])
                return True
            else:
                return False
        except:
            print(marioMakerMessageConstants.ERROR_USER_COMMANDS)
            return False
