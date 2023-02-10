import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import random
import asyncio
import youtube_dl
import os
import json
import shutil
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, Request
import time
import node_queue
from pytube import YouTube
import threading
from concurrent.futures import ThreadPoolExecutor
import yt_dlp
import urllib.request


currently_playing = ""
current_channel = ''


def run_discord_bot():

    intents = discord.Intents.all()
    intents.members = True
    intents.message_content = True
    client = commands.Bot(command_prefix=";;", intents=discord.Intents.all())
    client.remove_command("help")
    queue = node_queue.node_queue()
    dump = node_queue.node_queue()
    yd1_opts = {  # necessary jibberish jargon for youtube_dl to function
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    # These variables are initialized once inside the run method and the never get changed. They
    # are used to communicate with the discord and Youtube APIs.

    def fix_dl(newurl):
        # This method takes a fixes url and uses it to find a downloaded mp3, then renames it and places it into
        # the  /files/ folder
        print(newurl)
        print(type(newurl))
        for file in os.listdir("./"):
            print(os.getcwd())
            print(file)
            print(len(file))
            print(type(file))
            if file.endswith("[" + newurl[:11] + "]" + newurl[11:]):
                os.rename(r"./" + file, r"./files/" + newurl)
                break

    def check_queue(ctx):
        # This method pops a Node from the top of the queue and plays it. Of course the after parameter recursively
        # calls this method's handler.
        global currently_playing
        question = queue.pop()
        voice = ctx.guild.voice_client
        file_name = question.url
        currently_playing = file_name
        source = FFmpegPCMAudio(question.url)
        # voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        player = voice.play(source, after=lambda x=None: check_queue_helper(ctx))

    def check_queue_helper(ctx):
        # This method detects if a song just ended or was skipped and adds it to the dump, then checks if there are
        # any songs in the queue. If so it moves the next song into the right folder and calls check_queue to play it
        global currently_playing
        print(currently_playing)
        if currently_playing != "":
            dump_it(currently_playing)
            currently_playing = ""
        if queue.get_size() > 0:
            move_to_queue(queue.head_peep().get_newurl())
            check_queue(ctx)

    def fix_url(url):
        i = len(url)
        j = 0
        final = ""
        while j < i:
            if url[j:j+3] == "?v=":
                final = url[j+3:j+14]
                return final + ".mp3"
            j += 1



        # This method takes a youtube url and cuts out the unique 11 character string and returns it and
        # .mp3 on the end.
        # return url[32:] + ".mp3"

    @client.command()
    async def help(ctx):
        await ctx.send("use ;;play to queue a link from youtube and have the bot play it. Use ;;stop to empty the queue and disconnect the bot. Use ;;skip to skip a song.")


    @client.command(pass_context=True)
    async def play(ctx, url:str):
        # This method prepares the bot to play a song if the user who commanded it is in a voice channel.
        global current_channel
        global currently_playing
        if ctx.author.voice is not None: # if the user is connected to a vc (ctx.author.voice is not a boolean, it is
            # either some VoiceState variable information if the user is connected or it is None
            if is_connected(ctx) is None or False: # If the bot is connected to a different vc or not connected at all
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
                current_channel = channel
                # source = FFmpegPCMAudio(r"C:\Users\crazz\PycharmProjects\pythonProject\opener.mp3")
                # player = voice.play(source, after=lambda x=None: check_queue(ctx))
                # The bot connects to the user's channel and updates its internal channel information to the same.
            elif current_channel != ctx.author.voice.channel:  # if the bot is connected to a different vc
                voice = await ctx.guild.voice_client.disconnect()
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
                current_channel = channel
                # disconnect from whatever the bot is in, connect to the vc of the user, and update its internal
                # channel information
        else: # if the user is not connected to a voice channel
            await ctx.send("The user is not in a voice channel")
            return

        url_opener = urlopen(Request(url, headers={'User-Agent': 'Mozilla'}))
        videoInfo = bs(url_opener, features="html.parser")
        video_title = videoInfo.title.get_text()
        # This information is all just used to retrieve the title of the Youtube video from the given link

        newurl = fix_url(url)
        print(newurl)
        queue.add(newurl, video_title, url)
        # The method calls the queue to add a node using the given inputs
        with yt_dlp.YoutubeDL(yd1_opts) as ydl:
            # This line above just simplifies the long term into ydl for clarity
            print(does_exist(newurl))
            if does_exist(newurl) is False: # if the loop finished and the song did not already exists in the directory
                # await ctx.send("Hold on while I download " + video_title)
                download_yt(url, ydl)
                #The download should take <4 seconds
                fix_dl(newurl)
                # fix_dl is called with the fixed url to reformat the name
            else:
                if dump.contains(newurl):
                    dump.remove(newurl)
                    # In the case that the song was recently played and is now in the dump queue, this conditional
                    # removes it from the dump queue. When the song is eventually played it will be added back in.

        await ctx.send("I just queued " + video_title)
        voice = ctx.guild.voice_client # set voice equal to the server VoiceClient

        if is_playing(ctx) is False or None:
            # if the bot is not playning anything yet
            currently_playing = newurl
            move_to_queue(newurl) # make sure the song is in the correct folder to play
            source = FFmpegPCMAudio(queue.pop().url)
            player = voice.play(source, after=lambda x=None: check_queue_helper(ctx))
        # No need for an else statement because if the bot is already playing then when it finishes it must call
        # check_queue where it will find this song and play it

    def move_to_queue(newurl):
        # This method makes sure that the inputted song is in the right folder so that it can be played.
        for file in os.listdir(r"./"):
            if file.endswith(newurl):
                return
        os.rename(r"./files/" + newurl, r"./" + newurl)

    def move_to_files(newurl):
        # This method moves an mp3 from the folder where it can be played back to the files library of mp3s.
        os.rename(r"./" + newurl, r"./files/" + newurl)




    @client.command(pass_context=True)
    async def p(ctx, url:str):
        await play(ctx, url)
    # I use the p command more than play because it is just quicker

    def download_yt(url, ydl):
        print("in download_yt now")
        print(url)
        ydl.download([url])
        # because this is based on yt_dlp and not youtube_dl, the download is near instantaneous. Otherwise,
        # youtube_dl is so slow that it would cause issues blocking the shard hartbeat. There are no such issues
        # with yt_dlp at the moment.
        print("just finished download_yt")
        return True

    def is_playing(ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        # This method uses the ctx parameter. If the voice client is not connected, then it returns none, if it is
        # connected but not playing, it returns False, and if it is connected and playing it returns True. Because
        # it could possible return None, calls to this method must check for None by asking if is_playing(ctx) is
        # None or False instead of if is_playing(ctx) == None or False.
        return voice_client and voice_client.is_playing()

    def is_connected(ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        # If the voice client is not connected it will return False or None. If it is connected it will return
        # True. Because
        # it could possible return None, calls to this method must check for None by asking if is_connected(ctx) is
        # None or False instead of if is_connected(ctx) == None or False.
        return voice_client and voice_client.is_connected()

    def does_exist(newurl):
        # This method checks the os dir to see if the file is downloaded already. It returns True if it is downloaded
        # aka it exists and False if it is not downloaded aka does not exist. It also checks the files library folder
        path = r"./"
        for file in os.listdir(path): # For each file in the directory
            if file == (newurl):
                return True
        path = r"./files"
        for file in os.listdir(path):
            if file == newurl:
                move_to_queue(newurl)
                return True
        return False

    @client.command()
    async def stop(ctx):
        global current_channel
        voice = ctx.guild.voice_client
        if is_playing(ctx):
            player = voice.stop()
        queue.empty()
        current_channel = ""
        final = await voice.disconnect()
        purge()
        # This method exists so that the user can stop the queue and tell the bot to leave. It empties the queue
        # and stops the currently playing song and purges the dump and disconnects the bot.

    @client.command()
    async def skip(ctx):
        # This method is used to skip a song if one is playing. It does not need to play the next song from here
        # because the the previous song is done playing, the after method calls check_queue handler again.
        voice = ctx.guild.voice_client
        if is_playing(ctx):
            player = voice.stop()
            url_opener = urlopen(Request("https://www.youtube.com/watch?v=" + currently_playing, headers={'User-Agent': 'Mozilla'}))
            videoInfo = bs(url_opener, features="html.parser")
            video_title = videoInfo.title.get_text()
            await ctx.send("Just skipped " + video_title)
        if is_playing(ctx) is None or False:
            await ctx.send("Nothing was playing")

    def dump_it(newurl):
        if queue.contains(newurl):
            # If the song that just finished has already been queued again, don't add it to the dump yet.
            return
        if dump.contains(newurl) == False:
            # If the url is not yet in dump, add it.
            dump.add(newurl)
            print("The Dump is:")
            print(dump)
        if dump.get_size() > 5:
            # If the dump is more than 5 songs, pop the least recently played and move it back to the files library
            move_to_files(dump.pop().get_newurl())

    def purge():
        # Move every file in the dump back to the files library
        i = dump.get_size()
        while i > 0:
            newurl = dump.pop().get_newurl()
            move_to_files(newurl)
            i = i - 1

    @client.command()
    async def print_length(ctx, url):
        too_big(fix_url(url))

    # def too_big(newurl):
    #     api_key = "AIzaSyAPHB2eC85bINlQLrjI81zrREkIgpADnFA"
    #     searchUrl = "https://www.googleapis.com/youtube/v3/videos?id=" + newurl + "&key=" + api_key + "&part=contentDetails"
    #     req = Request(searchUrl)
    #     response = urlopen(req).read()
    #     data = json.loads(response)
    #     all_data = data['items']
    #     contentDetails = all_data[0]['contentDetails']
    #     duration = contentDetails['duration']
    #     print(duration)

    client.run('Insert Token Here')

