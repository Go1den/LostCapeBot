from PIL import Image
from pytesseract import pytesseract

class MarioMakerOCR:

    def __init__(self):
        self.levelName = ""
        # self.levelLikesAndPlays = ""
        self.levelMaker = ""
        self.levelDescription = ""
        self.levelClearRate = ""
        self.levelWorldRecord = ""
        self.levelWRHolder = ""
        self.levelCode = ""
        self.ocr(10)

    def allHaveValue(self):
        if self.levelName != "" and self.levelMaker != "" and self.levelDescription != "" and self.levelClearRate != "" and self.levelWorldRecord != "" and self.levelWRHolder != "" and self.levelCode != "":
            return True
        else:
            return False

    def ocr(self, retries):
        if retries > 0:
            try:
                im = Image.open('src/modules/mariomaker/screenshot.png')
                im.save('src/modules/mariomaker/ocr.png')
                im.close()
                ocrim = Image.open('src/modules/mariomaker/ocr.png')
                searchResultsTextLocation = ocrim.crop((106, 26, 317, 70))
                if pytesseract.image_to_string(searchResultsTextLocation) == "Search Results":
                    levelName = ocrim.crop((318, 138, 956, 184))
                    # levelLikesAndPlays = ocrim.crop((449, 182, 1054, 229))
                    levelMaker = ocrim.crop((813, 262, 1056, 304))
                    levelDescription = ocrim.crop((235, 316, 899, 408))
                    levelClearRate = ocrim.crop((474, 436, 662, 495))
                    levelWorldRecord = ocrim.crop((328, 437, 448, 469))
                    levelWRHolder = ocrim.crop((303, 466, 436, 494))
                    levelCode = ocrim.crop((695, 447, 890, 488))
                else:
                    levelName = ocrim.crop((395, 176, 1130, 221))
                    # levelLikesAndPlays = ocrim.crop((531, 217, 1124, 268))
                    levelMaker = ocrim.crop((838, 301, 1130, 342))
                    levelDescription = ocrim.crop((312, 354, 978, 444))
                    levelClearRate = ocrim.crop((572, 483, 715, 528))
                    levelWorldRecord = ocrim.crop((409, 479, 521, 504))
                    levelWRHolder = ocrim.crop((382, 505, 515, 531))
                    levelCode = ocrim.crop((778, 486, 961, 527))
                ocrim.close()
                if self.levelName == "" and pytesseract.image_to_string(levelName) != "":
                    self.levelName = pytesseract.image_to_string(levelName).strip()
                # if self.levelLikesAndPlays == "" and pytesseract.image_to_string(levelLikesAndPlays) != "":
                # self.levelLikesAndPlays = pytesseract.image_to_string(levelLikesAndPlays)
                if self.levelMaker == "" and pytesseract.image_to_string(levelMaker) != "":
                    self.levelMaker = pytesseract.image_to_string(levelMaker).strip().split()[-1]
                if self.levelDescription == "" and pytesseract.image_to_string(levelDescription) != "":
                    self.levelDescription = pytesseract.image_to_string(levelDescription).replace('\n', ' ').strip()
                if self.levelClearRate == "" and pytesseract.image_to_string(levelClearRate) != "" and "%" in pytesseract.image_to_string(levelClearRate):
                    self.levelClearRate = pytesseract.image_to_string(levelClearRate).strip()
                if self.levelWorldRecord == "" and pytesseract.image_to_string(levelWorldRecord) != "":
                    self.levelWorldRecord = pytesseract.image_to_string(levelWorldRecord).strip()
                if self.levelWRHolder == "" and pytesseract.image_to_string(levelWRHolder) != "":
                    self.levelWRHolder = pytesseract.image_to_string(levelWRHolder).strip()
                if self.levelCode == "" and pytesseract.image_to_string(levelCode) != "":
                    self.levelCode = pytesseract.image_to_string(levelCode).strip()
                if self.allHaveValue():
                    print("All OCR values populated successfully.")
                    return
                else:
                    self.ocr(retries - 1)
            except Exception as e:
                print(e)
                print("Error encountered during OCR, retrying...")
                self.ocr(retries - 1)
