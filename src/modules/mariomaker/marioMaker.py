import configparser
import datetime

from src import fileHandler
from src.modules.abstractChatCommands import AbstractChatCommands
from src.modules.mariomaker import marioMakerMessageConstants, levelCodeMethods
from src.modules.mariomaker.marioMakerLevel import MarioMakerLevel
from src.modules.pastebin import pastebin
from src.modules.wordpress.wordpress import Wordpress

FILE_CURRENTLEVEL = 'src/modules/mariomaker/currentLevel.txt'
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
        self.wordpressCurrentLevelPostID = int(marioMakerSettings.get('marioMakerCurrentLevelPostID', "0"))
        self.summaryPastebin = bool(int(marioMakerSettings.get('summaryPastebin', "0")))
        self.summaryWordpress = bool(int(marioMakerSettings.get('summaryWordpress', "0")))
        self.queueURL = marioMakerSettings.get('queueURL', '')
        self.wordpress = Wordpress()
        self.queueOpen = False
        self.queue = []
        self.queueSummary = ""
        self.htmlTableRowsOfPlayedLevels = ""
        self.currentLevel = None
        fileHandler.writeToFile(FILE_CURRENTLEVEL, "")
        self.writeQueueToFileAndWordpress()
        self.writeCurrentLevelToWordpress()

    def openQueue(self, ci):
        self.queueOpen = True
        ci.sendMessage(marioMakerMessageConstants.QUEUE_OPEN)
        ci.sendMessage(marioMakerMessageConstants.QUEUE_URL.format(self.queueURL))
        self.writeQueueToWordpress()
        self.writeCurrentLevelToWordpress()

    def closeQueue(self, ci):
        self.queueOpen = False
        ci.sendMessage(marioMakerMessageConstants.QUEUE_CLOSED)
        ci.sendMessage(marioMakerMessageConstants.QUEUE_URL.format(self.queueURL))
        self.writeQueueToWordpress()
        self.writeCurrentLevelToWordpress()

    def clearQueue(self, ci):
        self.queue = []
        self.writeQueueToFileAndWordpress()
        ci.sendMessage(marioMakerMessageConstants.QUEUE_CLEARED)

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

    def getQueueStatusAsHTML(self):
        if self.queueOpen:
            queueStatus = "<h2 style=\"color: green\">The queue is open!</h2>"
        else:
            queueStatus = "<h2 style=\"color: red\">The queue is closed!</h2>"
        queueStatus += "Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d    %H:%M:%S") + "\n"
        return queueStatus

    def getQueueAsHTMLTable(self):
        wpQueueString = "<div><b>Queue</b></div><table><tr><th>#</th><th>Submitter</th><th>Level ID</th></tr>"
        idx = 1
        for level in self.queue:
            wpQueueString += "<tr><td>" + str(idx) + '</td><td>' + level.submitter + '</td><td>' + level.id + "</td></tr>"
            idx += 1
        wpQueueString += "</table>"
        return wpQueueString

    def getPlayedLevelsAsHTMLTable(self):
        wpPlayedLevelsString = "<div><b>Today's Completed Levels</b></div><table><tr><th>Maker</th><th>Level Name</th><th>Level ID</th><th>Description</th><th>Clear %</th><th>Rank</th><th>Votes</th></tr>"
        wpPlayedLevelsString += self.htmlTableRowsOfPlayedLevels + "</table>"
        return wpPlayedLevelsString

    def getCurrentLevelAsHTML(self):
        if self.currentLevel:
            return "<div><b>Currently playing " + self.currentLevel.submitter + "'s submission: " + self.currentLevel.name + " " + self.currentLevel.id + "</b></div><br>"
        else:
            return ""

    def writeQueueToWordpress(self):
        if self.wordpress.enableWordpressCommands:
            postContent = self.getQueueStatusAsHTML() + self.getCurrentLevelAsHTML() + self.getQueueAsHTMLTable() + self.getPlayedLevelsAsHTMLTable()
            self.wordpress.editPost('Mario Maker Queue', postContent, self.wordpressPostID)

    def addToQueue(self, message, username, ci):
        if self.queueOpen:
            if self.validateLevelAndAddToQueue(message, username, ci):
                position = len(self.queue)
                ci.sendMessage(username + ", your level was added to the queue in position #" + str(position) + "!")
                self.writeQueueToFileAndWordpress()
                if len(self.queue) >= self.maxQueueSize:
                    self.closeQueue(ci)
        else:
            ci.sendMessage(marioMakerMessageConstants.QUEUE_CLOSED)
            ci.sendMessage(marioMakerMessageConstants.QUEUE_URL.format(self.queueURL))

    def gatherDataFromLastLevel(self, ci):
        if self.currentLevel is not None:
            print("Gathering data from last level...")
            self.currentLevel.sendCourseRatingChatMessage(ci)
            self.queueSummary += self.currentLevel.getLevelSummary()
            self.htmlTableRowsOfPlayedLevels += self.currentLevel.getHTMLTableRowLevelSummary()

    def writeCurrentLevelToWordpress(self):
        try:
            if self.currentLevel is not None:
                currentLevelHTML = self.currentLevel.getCurrentLevelHTML(self.queueOpen)
            else:
                currentLevelHTML = MarioMakerLevel().getCurrentLevelHTML(self.queueOpen)
            self.wordpress.editPost('Mario Maker Current Level', currentLevelHTML, self.wordpressCurrentLevelPostID)
        except:
            print("Unable to edit current level post!")

    def nextInQueue(self, ci):
        try:
            self.gatherDataFromLastLevel(ci)
            if self.queue:
                self.currentLevel = self.queue.pop(0)
            else:
                self.currentLevel = None
            self.writeQueueToFileAndWordpress()
            self.writeCurrentLevelToWordpress()
            self.currentLevel.sendNowPlayingChatMessageAndUpdateLevelFile(ci)
        except:
            ci.sendMessage(marioMakerMessageConstants.QUEUE_EMPTY)

    def playLevelNotInQueue(self, message, ci):
        try:
            levelCode = message.split()[1]
            if len(levelCode) == 9:
                levelCode = levelCodeMethods.pad(levelCode)
            self.gatherDataFromLastLevel(ci)
            self.currentLevel = MarioMakerLevel(ci.channel.capitalize(), levelCode)
            self.writeQueueToWordpress()
            self.writeCurrentLevelToWordpress()
            self.currentLevel.sendNowPlayingChatMessageAndUpdateLevelFile(ci)
        except:
            ci.sendMessage(marioMakerMessageConstants.ERROR_PLAYING_LEVEL_NOT_IN_QUEUE)

    def validateLevelAndAddToQueue(self, message, username, ci):
        try:
            if self.validateUserNotAlreadyInQueue(username) and len(message.split()) > 1:
                levelCode = message.split()[1].replace("-", "")
                if levelCodeMethods.validate(levelCode):
                    self.queue.append(MarioMakerLevel(username, levelCodeMethods.pad(levelCode)))
                    return True
                else:
                    return False
        except:
            ci.sendMessage(marioMakerMessageConstants.ERROR_INVALID_SUBMISSION)

    def validateLevelAndUpdateQueue(self, message, username, ci):
        try:
            if not self.validateUserNotAlreadyInQueue(username) and len(message.split()) > 1:
                levelCode = message.split()[1].replace("-", "")
                if levelCodeMethods.validate(levelCode):
                    for level in self.queue:
                        if level.submitter == username:
                            level.id = levelCodeMethods.pad(levelCode)
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

    def postQueueSummaryToWordpress(self, ci):
        if self.wordpress.enableWordpressCommands:
            try:
                todaysDateTime = datetime.date.today().strftime("%B %d, %Y")
                wordpressURL = self.wordpress.newPost("Mario Maker Queue from  " + todaysDateTime, self.getPlayedLevelsAsHTMLTable(), "Mario Maker")
                if self.summaryWordpress:
                    ci.sendMessage("Summary of today's streamed levels: " + wordpressURL)
            except:
                ci.sendMessage(marioMakerMessageConstants.WORDPRESS_FAILURE)

    def postQueueSummaryToPastebin(self, ci):
        try:
            todaysDateTime = datetime.date.today().strftime("%B %d, %Y")
            pb = pastebin.Pastebin()
            pastebinURL = pb.makePastebin("Mario Maker Queue from  " + todaysDateTime, self.queueSummary)
            if self.summaryPastebin:
                ci.sendMessage("Summary of today's streamed levels: " + pastebinURL)
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
                    self.writeCurrentLevelToWordpress()
                return True
            if message == "!summary":
                self.postQueueSummaryToPastebin(ci)
                self.postQueueSummaryToWordpress(ci)
                self.queueSummary = ""
                return True
            if self.enableOCR and message == "!ocr" and self.currentLevel is not None:
                self.currentLevel.getOCRData()
                self.writeCurrentLevelToWordpress()
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
