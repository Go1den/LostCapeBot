import configparser
import time

import requests
import tweepy

from src.modules.abstractChatCommands import AbstractChatCommands
from src.modules.twitter import twitterMessageConstants

class Twitter(AbstractChatCommands):

    def __init__(self, twitchChannel):
        config = configparser.ConfigParser()
        config.read('twitterSettings.txt')
        twitterSettings = config['TwitterSettings']
        self.twitchChannel = twitchChannel
        self.cfg = {
            "consumer_key": twitterSettings.get('consumerKey', ""),
            "consumer_secret": twitterSettings.get('consumerSecret', ""),
            "access_token": twitterSettings.get('accessToken', ""),
            "access_token_secret": twitterSettings.get('accessTokenSecret', "")
        }
        self.clientID = twitterSettings.get('clientID', "")
        self.clientSecret = twitterSettings.get('clientSecret', "")  # might be unused
        self.accessToken = twitterSettings.get('oauth', "")
        self.headers = {'Accept': 'application/vnd.twitchtv.v3+json', 'Authorization': 'OAuth ' + self.accessToken, 'Client-ID': self.clientID}
        self.enableTwitterCommands = bool(twitterSettings.get('enableTwitterCommands', "0"))

    def get_api(self):
        auth = tweepy.OAuthHandler(self.cfg['consumer_key'], self.cfg['consumer_secret'])
        auth.set_access_token(self.cfg['access_token'], self.cfg['access_token_secret'])
        return tweepy.API(auth)

    def getStreamTitle(self, ci):
        r = requests.get("https://api.twitch.tv/kraken/channels/" + ci.channel + "/", headers=self.headers)
        print(r.json())
        timestamp = time.time()
        streamTitle = str(r.json()["status"]) + "\n" + "twitch.tv/" + ci.channel + "?status=live&KappasPerMinute=" + str(timestamp)
        print(streamTitle)
        return streamTitle

    def tweetStream(self, ci):
        twitterapi = self.get_api()
        tweet = self.getStreamTitle(ci)
        twitterapi.update_status(status=tweet)
        return tweet

    def processBroadcasterCommands(self, message, ci):
        if self.enableTwitterCommands:
            if message == "!tweet":
                try:
                    tweet = self.tweetStream(ci)
                    print("Tweeted this message: " + tweet)
                    ci.sendMessage(twitterMessageConstants.TWEET_SUCCESS)
                except Exception as inst:
                    print(type(inst))
                    print(inst.args)
                    print(inst)
                    ci.sendMessage(twitterMessageConstants.TWEET_FAILURE)
                return True
            else:
                return False
        else:
            return False

    def processUserCommands(self, message, username, ci):
        # Method is defined to be consistent with the abstract, but there are no user commands for Twitter currently
        return
