import statistics

from src import fileHandler
from src.modules.mariomaker.marioMakerOCR import MarioMakerOCR

class MarioMakerLevel:

    def __init__(self, submitter="", id=""):
        self.name = ""
        self.maker = ""
        self.description = ""
        self.clearRate = ""
        self.worldRecord = ""
        self.wrHolder = ""
        self.id = id
        self.rankList = []
        self.submitter = submitter
        self.rank = ""

    def setName(self, name):
        self.name = name
        self.updateCurrentLevelFile()

    def rankListIsEmpty(self):
        return len(self.rankList) == 0

    def calculateChatRank(self):
        self.rank = str(round(statistics.mean([int(rank[1]) for rank in self.rankList]), 2)) + " out of 5"

    def sendCourseRatingChatMessage(self, ci):
        if not self.rankListIsEmpty():
            self.calculateChatRank()
            ci.sendMessage("Chat's Course Rating: " + self.rank)

    def updateCurrentLevelFile(self):
        outputString = self.name + " " + self.id if self.name != "" else self.id
        fileHandler.writeToFile('src/modules/mariomaker/currentLevel.txt', 'w', outputString)

    def sendNowPlayingChatMessageAndUpdateLevelFile(self, ci):
        self.updateCurrentLevelFile()
        ci.sendMessage("Now playing " + self.submitter + "'s submission: " + self.id)

    def validateUserCanRankThisLevel(self, user):
        if self.submitter == user or self.maker == user:
            return False
        for rank in self.rankList:
            if rank[0] == user:
                return False
        return True

    def addToRankList(self, user, score):
        if score in ['1', '2', '3', '4', '5'] and self.validateUserCanRankThisLevel(user):
            print(user + " ranked this course " + str(score) + " out of 5")
            self.rankList.append([user, score])
        else:
            print("Invalid rank attempt by " + user)

    def getMaker(self):
        return " created by " + self.maker if self.maker != "" else ""

    def getLevelSummary(self):
        resultString = ""
        resultString += self.submitter + "'s submission: " + self.id + "\n"
        if self.name != "":
            resultString += self.name + self.getMaker() + "\n"
        if self.description != "":
            resultString += self.description + "\n"
        if self.clearRate != "":
            resultString += "Clear Rate: " + self.clearRate + "\n"
        if not self.rankListIsEmpty():
            resultString += "Viewer Rating: " + self.rank + " (" + str(len(self.rankList)) + " viewers voting)" + "\n"
        return resultString + "\n"

    def getOCRData(self):
        marioMakerOCR = MarioMakerOCR()
        if marioMakerOCR.levelName != "":
            self.name = marioMakerOCR.levelName
        if marioMakerOCR.levelMaker != "":
            self.maker = marioMakerOCR.levelMaker
        if marioMakerOCR.levelDescription != "":
            self.description = marioMakerOCR.levelDescription
        if marioMakerOCR.levelClearRate != "":
            self.clearRate = marioMakerOCR.levelClearRate
        if marioMakerOCR.levelWorldRecord != "":
            self.worldRecord = marioMakerOCR.levelWorldRecord
        if marioMakerOCR.levelWRHolder != "":
            self.wrHolder = marioMakerOCR.levelWRHolder
        self.updateCurrentLevelFile()
