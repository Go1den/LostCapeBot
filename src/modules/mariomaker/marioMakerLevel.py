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
        outputString = "  " + self.name + " " + self.id + "  " if self.name != "" else "  " + self.id + "  "
        fileHandler.writeToFile('src/modules/mariomaker/currentLevel.txt', outputString)

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

    def getHTMLTableRowLevelSummary(self):
        return "<tr><td>" + self.maker + "</td><td>" + self.name + "</td><td>" + self.id + "</td><td>" + self.description + "</td><td>" + self.clearRate + "</td><td>" + self.rank + "</td><td>" + str(
            len(self.rankList)) + "</td></tr>"

    def truncateName(self):
        if len(self.name) <= 20:
            return self.name
        else:
            return self.name[:20] + "..."

    def getValueOrNbsp(self, value):
        if value == "":
            return "&nbsp;"
        else:
            return value

    def getClearRateOrNbsp(self):
        if self.clearRate == "":
            return "&nbsp;"
        else:
            return self.clearRate + " Clear Rate"

    def getCurrentLevelHTML(self, queueOpen):
        if queueOpen:
            queueDiv = "<div style=\"color:#00EE00; font-size: 18px; line-height: normal;\">⬤ Queue Open</div>"
        else:
            queueDiv = "<div style=\"color:#EE0000; font-size: 18px; line-height: normal;\">⬤ Queue Closed</div>"
        return "<div style=\"background-color:#FFFF00; padding: 50px 50px 50px 50px; width: 200px; height: 200px;\">" + \
               "<div style=\"background-color:black; padding: 8px 8px 12px 12px; border-radius: 25px; width: 200px; height: 140px; white-space: nowrap; line-height: normal;\">" + \
               "<div style=\"color:white; font-size: 28px; line-height: normal;\">" + self.getValueOrNbsp(self.maker) + "</div>" + \
               "<div style=\"color:white; font-size: 18px; line-height: normal;\">" + self.getValueOrNbsp(self.truncateName()) + "</div>" + \
               "<div style=\"color:#00FFFF; font-size: 28px; line-height: normal;\">" + self.getValueOrNbsp(self.id) + "</div>" + \
               "<div style=\"color:white; font-size: 18px; line-height: normal;\">" + self.getClearRateOrNbsp() + "</div>" + \
               queueDiv + "</div></div><script>setTimeout(function(){location.reload()},3000);</script>"

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
