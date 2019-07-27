import configparser
import time

import requests
import tweepy

import messageConstants

class Twitter:

    def __init__(self, twitchChannel):
        config = configparser.ConfigParser()
        config.read('twitterSettings.txt')
        self.twitchChannel = twitchChannel
        self.cfg = {
            "consumer_key": config['TwitterSettings']['consumerKey'],
            "consumer_secret": config['TwitterSettings']['consumerSecret'],
            "access_token": config['TwitterSettings']['accessToken'],
            "access_token_secret": config['TwitterSettings']['accessTokenSecret']
        }
        self.clientID = config['TwitterSettings']['clientID']
        self.clientSecret = config['TwitterSettings']['clientSecret']  # might be unused
        self.accessToken = config['TwitterSettings']['oauth']
        self.headers = {'Accept': 'application/vnd.twitchtv.v3+json', 'Authorization': 'OAuth ' + self.accessToken, 'Client-ID': self.clientID}
        self.enableTwitterCommands = bool(config['TwitterSettings']['enableTwitterCommands'])

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
        tweet = self.getStreamTitle(ci.channel)
        twitterapi.update_status(status=tweet)
        return tweet

    def processBroadcasterCommands(self, message, ci):
        if self.enableTwitterCommands:
            if message == "!tweet":
                try:
                    tweet = self.tweetStream(ci)
                    print("Tweeted this message: " + tweet)
                    ci.sendMessage(messageConstants.TWEET_SUCCESS)
                except Exception as inst:
                    print(type(inst))
                    print(inst.args)
                    print(inst)
                    ci.sendMessage(messageConstants.TWEET_FAILURE)
                return True
            else:
                return False
        else:
            return False
