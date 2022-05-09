import config
import praw
import requests
import mimetypes
import re
import os
import random

reddit = praw.Reddit(
    client_id=config.config_stuff2['client_id'],
    client_secret=config.config_stuff2['client_secret'],
    user_agent=config.config_stuff2['user_agent'],
)
#list of subreddits to grab memes from
subreddit_list = ["memes", "greentext", "dankmemes", "4chan", "shitposting", "Unexpected", "Wholesomememes", "TheRealJoke"]
#picks a random subreddit from the above list
subreddit = reddit.subreddit(random.choice(subreddit_list)).hot(limit=None)

#establishes count for later count loop break
count = 0
#for loop which contains variables and parameters necessary for grabbing the type of data we want from reddit
for submission in subreddit:
    url = str(submission.url)
    pattern = r'[^A-Za-z0-9]+'
    title_no_specials = re.sub(pattern, ' ', submission.title)
    if url.endswith("jpg") or url.endswith("jpeg") or url.endswith("png"):
        if submission.spoiler == False:
            if submission.over_18 == False:
                r = requests.get(url)
                length = float(r.headers.get('content-length')) / 1000
                if float(length) < 4000:
                    sub_string = str(submission.title)
                    with open('MemeBot/Reddit-Grabber-Log.txt', 'r+') as f:
                        f_contents = f.readlines()
                        stripped_lines = [s.strip() for s in f_contents]
                        if submission.id not in stripped_lines:
                            with open('MemeBot/Reddit-Grabber-Log.txt','a+') as f:
                                f.write(str(title_no_specials) + str("\n"))
                                f.write(str(submission.id) + str("\n"))
                                f.write(str("https://www.reddit.com") + str(submission.permalink) + str("\n"))
                                f.write(str(submission.url) + str("\n"))
                                f.write(str(length) + str("\n\n"))
                                print(str("Info logged to text file ") + str("- ") + str(count+1))
                                count += 1
                if count == 4:
                    break