import config # used to get the secret sensitive info needed for our APIs - not uploaded to github for security purposes
import praw # used for the reddit api - this is 100% needed for this code to work
import requests # needed to get image file size before we download images (to make sure we don't download images too large that we can't upload elsewhere).
import re # used to remove special characters from Titles before we log them to the log file (special characters were ruining the txt file, dunno why, help...)
import os # needed to get the file paths
import random #needed to pick a random subreddit to grab data from. In theory you don't have to pick a random one, you could do all at once or just one, either or.

#establishing our creds to gain access to the API before we start doing any calls.
reddit = praw.Reddit(
    client_id=config.config_stuff2['client_id'],
    client_secret=config.config_stuff2['client_secret'],
    user_agent=config.config_stuff2['user_agent'],
)
#list of subreddits to grab memes from
subreddit_list = ["memes", "dankmemes", "shitposting", "Unexpected", "Wholesomememes", "me_irl", "meme", "Memes_Of_The_Dank", "starterpacks", "justneckbeardthings", "animemes", "AnimalsBeingDerps", "funny"]

#picks a random subreddit from the above list
subreddit = reddit.subreddit(random.choice(subreddit_list)).hot(limit=None)

# this is a customizeable list of words that will be scanned in reddit post titles, if any of these words are found in the titles the post will not be logged for use. This helps clear the toxic posts out of the list.
# note that I'm not necessarily saying these words are bad things, it's just that typically when these words are mentioned, it's in a negative toxic context. Not that I disagree with any of these specifically.
bad_topics = ["faggot", "femboy", "nigger", "fat", "skinny", "horny", "masturbate", "anal", "sex", "racist", "homophobic"]

#establishes count for later count loop break
count = 0
#for loop which contains variables and parameters necessary for grabbing the type of data we want from reddit
for submission in subreddit:
    url = str(submission.url) #makes sure that the url we got from the api is a string variable
    pattern = r'[^A-Za-z0-9]+' # a list of the only kind of characters we want in our titles, everything else is removed
    title_no_specials = re.sub(pattern, ' ', submission.title) #removes all the special chars from titles
    if url.endswith("jpg") or url.endswith("jpeg") or url.endswith("png"): #make sure the post is an image

        if submission.spoiler == False: # make sure the post is not flagged as a spoiler

            if submission.over_18 == False: # make sure the post is not flagged as NSFW -- side note: this sucks, people still post bad crap anyways and mods don't remove it. be careful which subreddits you are scanning even with this on.
                r = requests.get(url) #defines R variable as grabbing data from our selected url
                length = float(r.headers.get('content-length')) / 1000 # divides file size by 1000 so we can get how many kilobytes it is

                for string in submission.title:
                    if not any(x in string for x in bad_topics):
                        if float(length) < 4000: # if it is less than 4 MB or 4000 KB (alternatively for cleaner numbers you can divide by 1,000,000 and do < 4 but eh.
                            sub_string = str(submission.title) # make sure our title is a string so we can do stuff with it

                            # Now we want to open up our log file to see if the post we're looking at is already in the log file, if it is not continue, if not skip to avoid duplicates.
                            with open('MemeBot/Reddit-Grabber-Log.txt', 'r+') as f:
                                f_contents = f.readlines() # read everything in the file and put it as an element in a list
                                stripped_lines = [s.strip() for s in f_contents] # strip the \n from the elements for cleaner data

                                if submission.id not in stripped_lines: # if we see the reddit post ID from what we want in the log file then skip if not continue

                                    # Now that we know we don't have duplicates, write the new submission to the reddit log file to be used later.
                                    with open('MemeBot/Reddit-Grabber-Log.txt','a+') as f:
                                        f.write(str(title_no_specials) + str("\n")) # write the title of the reddit post to line 1.
                                        f.write(str(submission.id) + str("\n")) # write the reddit post ID to line 2.
                                        f.write(str("https://www.reddit.com") + str(submission.permalink) + str("\n")) #write the permalink of the reddit post to line 3.
                                        f.write(str(submission.url) + str("\n")) # write the link to the image itself in the post to line 4.
                                        f.write(str(length) + str("\n\n")) #write the file size of the image we looked at in the post to line 5.
                                        print(str("Info logged to text file ") + str("- ") + str(count+1)) #print to the console every time it does this to say that we have written to the log file.
                                        count += 1 # increase the count from 0
                if count == 4: # when this count reaches 4 .........
                    break # .... stop the loop. finish program.
