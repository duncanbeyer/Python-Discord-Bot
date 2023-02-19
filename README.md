# Discord Music and Chat Bot

This bot was written by myself with a little help from the internet. The help is just in the form of finding plugins to access information and interact with the discord and YouTube APIs.

This project came about because YouTube changed their policies, so the discord music bots my friends and I had been using no longer supported Youtube links.

OpenAI ChatGPT Functionality has been added, the ;;chat command generates a response to a user prompt using the OpenAI ChatGPT API. The ;;image command generates an image based on the user prompt using the OpenAI DALLE-2 API.

I wrote the logic of this bot to match that of the FredBoat music bot that we used to use. The ;;play, ;;skip, and ;;stop commands for this bot work identically to how FredBoat used to work. 

# Constraints of Use:
If all you do with this bot is use ;;play with a YouTube link, it will work flawlessly. It does not yet have support for searching for a song using keywords, which I may implement later. 

# Logic
When the user commands the bot to play a song using a Youtube URL, the bot will parse out the unique string of characters in the url that defines the video. It will then check whether the video has already been downloaded either inside the main folder or inside the inner files library.

If the file exists in either location, then the bot adds a node containing the name of the file and the title of the song to a queue, and ensures that the file is in the main folder for when it is popped from the queue to play.

If the file does not exist in either location, there is a call to ytdl to download the file, after which it is renamed to the unique string from its url. 

As each song inside the main folder finished playing, it is added to a modified queue called dump. When the dump reaches more than 5 songs, meaning there are 6 mp3s in the main folder, it moves the least recently played song back to the files library, similar to a caching method. When a file in the main folder is replayed, it is moved to the end of the queue from whatever position it was in. By using the dump queue, the main folder containing the python scripts is not inundated in countless mp3 files. 

The skip command skips the song currently playing, moving directly to the next song in the queue. The skipped song is then added to the dump.

The stop command ends the song currently playing, empties the queue, disconnects the bot from the voice channel, and moves all the songs from the dump queue back into the files library.

I've added limit so that no song longer than 15 minutes can get downloaded. Previously there was nothing stopping anyone from trying to download very long videos to my hard drive.


# Legal Disclaimer
This is merely an example of a bot that would excel at downloading and playing songs from YouTube. I would never actually do that as it breaks the YouTube TOS.

