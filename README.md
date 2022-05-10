# Meme-Poster
This project was created by Logan Maupin. I am a student at the University of Arizona Online. I'm majoring in Applied Computing - Applied Artificial Intelligence. My goal is to one day contribute work towards machine learning models to help the world in some way (like AI that can detect cancer accurately for example). For now, here's a silly project I made. It's not the best, could be a lot better and a lot more optomized but I'm not that good of a programmer, I really just started programming a few months ago so my code is kinda meh. If you know of any ways to improve the code feel free to propose suggestions or tips to me, thank you! 

###############################

About this code: This bot looks at a list of subreddits, picks 4 posts which contain images, also that aren't flagged as NSFW or spoilers, then saves those to a txt file, then the FB poster script posts from that text file given the image urls. 

Please note: This script requires API access to reddit that you must provide through your own reddit app, the key is not supplied in this code. FB is also the same way, for the FB Poster side of this code you will also need a token for a FB page as well. 

Also note: You will need a Reddit-Grabber-Log.txt and also FBPoster-Log.txt file to make this code work as well, best to store those in the same directory as the python scripts but you can path to them elsewhere if you need. 

So basically TLDR the way this code works is this flow: 

When you run RedditGrabber.py script, it looks at the list of subreddits, picks a random one, grabs 4 images from the hot posts of that subreddit, then uses reddit api to grab specific bits of data about those posts. It's not actually grabbing the images themselves but rather the metadata as follows: It grabs the Title of the post, the ID of the reddit post, the permalink of the post (like if you were to send the post to a friend), and then the url of the post (mainly this is the url of the image itself, usually ends in an image file extension). Once it has all that data it writes it to the txt log file that it references. but before it writes anything it always reads the file to see if it's a duplicate (i.e. if what it is about to write is already in the file - if it is then don't write it and try a different post next down the list). it does this until it gets 4 images and then stops the code.

Then you would run FBPoster script and it would take a random log from the reddit grabber log file, and grab the image url and use that to post to FB. right now this only works for images, not gifs or videos, but that's an easy fix, I'll be expanding this later on. but anyways so before it does that though it checks the fb poster log file to see if it's ever posted that image before, if it has it grabs a different one and checks the log and keeps doing this until it finds one it hasn't posted yet. It also picks at random so it's not in sequence. (you can change that in yours if you want - I just like the random element). Once it grabs one that isn't in the log it posts the image then writes that data to the log file. It will write the date and time, image url, permalink, title, and id, not in that order but yeah all that stuff. It also writes the file size in both of these logs just so I can check it is staying within the right parameters. 

Anyways that's how it works. It is scheduled in crontab on an AWS Ubuntu server so reddit grabber runs every hour at :05 minutes and FB poster runs every other (even) hours at :00 minutes I believe. 
