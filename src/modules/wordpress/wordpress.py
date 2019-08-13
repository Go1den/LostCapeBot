import configparser

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import EditPost

class Wordpress:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('src/modules/wordpress/wordpressSettings.txt')
        wpSettings = config['WordpressSettings']
        self.enableWordpressCommands = bool(int(wpSettings.get('enableWordpressCommands', "0")))
        self.username = wpSettings.get('username', '')
        self.password = wpSettings.get('password', '')
        self.url = wpSettings.get('url', '')
        self.client = Client(self.url, self.username, self.password)

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
