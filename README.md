# LostCapeBot
LostCapeBot is a Twitch chat bot designed to have flexibility with modules like Pastebin, Twitter, and Mario Maker.

Each module has it's own settings file. You will want to read these thoroughly and update them all in order to get the most out of this bot. I STRONGLY RECOMMEND DOING THIS FIRST.

I have very thoroughly detailed the steps necessary to get the bot running in each of these txt files. Please read them carefully.

When properly configured, these are the available commands:

General bot commands:

  !goodbye - Removes the bot from the chat and exits the program.

Twitter:

  !tweet - Broadcaster only command that tweets the current stream title and a link to the stream. Unlike standard tweets, this refreshes your stream title correctly and won't show a title that is days old. Take that, Twitter!
  
Mario Maker:

  !add or !submit - Followed by a level code, this will add a level to the queue.
  
  !update - Updates an ID already in the queue. Useful if the submitter goofed up. Stops working once the level is "active"
  
  !remove or !cancel - Removes a level from the queue if one is found by the person who typed this
  
  !next - Broadcaster only command that grabs the next level from the queue and puts it in currentLevel.txt
  
  !name - Broadcaster only command that appends the name of the level in currentLevel.txt
  
  !rank or !rate - When followed by a number from 1 to 5, a viewer can rank the current level. The ranks are averaged when !next or !id is typed.
  
  !id - Broadcaster only command that, when followed by a level ID, immediately puts that level as the next level. Useful for overriding the queue.
  
  !summary - Creates a pastebin containing the complete queue for the day's stream. Returns the URL to the chat.
  
