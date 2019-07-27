import configparser
import urllib

class Pastebin:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('pastebinSettings.txt')
        pastebinSettings = config['PastebinSettings']
        self.apiDevKey = pastebinSettings.get('apiDevKey', "")
        self.apiUserKey = pastebinSettings.get('apiUserKey', "")
        self.url = 'http://pastebin.com/api/api_post.php'
        self.pastebinPrivacy = int(pastebinSettings.get('pastebinPrivacy', "0"))

    # Method for posting to pastebin, returns the URL of the pastebin
    def makePastebin(self, title, content):
        pastebin_vars = dict(
            api_option='paste',
            api_dev_key=self.apiDevKey,
            api_user_key=self.apiUserKey,
            api_paste_name=title,
            api_paste_code=content,
            api_paste_private=self.pastebinPrivacy
        )
        return urllib.request.urlopen(self.url, urllib.parse.urlencode(pastebin_vars).encode('utf8')).read().decode("utf-8")
