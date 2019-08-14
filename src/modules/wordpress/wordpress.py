import configparser
import datetime

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import EditPost, NewPost, GetPost

class Wordpress:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('src/modules/wordpress/wordpressSettings.txt')
        wpSettings = config['WordpressSettings']
        self.enableWordpressCommands = bool(int(wpSettings.get('enableWordpressCommands', "0")))
        self.username = wpSettings.get('username', '')
        self.password = wpSettings.get('password', '')
        self.baseURL = wpSettings.get('baseURL', '')
        self.xmlrpcurl = wpSettings.get('xmlrpcurl', '')
        self.client = Client(self.xmlrpcurl, self.username, self.password)

    def editPost(self, title, content, id):
        try:
            post = WordPressPost()
            post.title = title
            post.content = content
            post.id = id
            post.post_status = 'publish'
            self.client.call(EditPost(post.id, post))
        except:
            print("Unable to edit post!")

    def newPost(self, title, content, category=None):
        try:
            post = WordPressPost()
            post.title = title
            post.content = content
            post.date = datetime.datetime.now()
            post.post_status = 'publish'
            if category is not None:
                post.terms_names = {
                    'category': category
                }
            postID = self.client.call(NewPost(post))
            wpPost = self.client.call(GetPost(postID))
            return self.baseURL + "/" + wpPost.slug
        except:
            print("Unable to post!")


