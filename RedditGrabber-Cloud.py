import config # used to get the secret sensitive info needed for our APIs - not uploaded to github for security purposes
import praw # used for the reddit api - this is 100% needed for this code to work
import requests # needed to get image file size before we download images (to make sure we don't download images too large that we can't upload elsewhere).
import os # needed to get the file paths
import random #needed to pick a random subreddit to grab data from. In theory you don't have to pick a random one, you could do all at once or just one, either or.
from googleapiclient.discovery import build # for spreadsheet stuff
from google.oauth2 import service_account # also for spreadsheet stuff
from PIL import Image # for image hashing
import imagehash # also for image hashing
import numpy as np

#establishing our creds to gain access to the API before we start doing any calls.
reddit = praw.Reddit(
    client_id=config.config_stuff2['client_id'],
    client_secret=config.config_stuff2['client_secret'],
    user_agent=config.config_stuff2['user_agent'],
)

SERVICE_ACCOUNT_FILE = 'keys.json' # points to the keys json file that holds the dictionary of the info we need.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] # website to send the oauth info to gain access to our data

creds = None #writes this variable to no value before overwriting it with the info we need, basically cleaning and prepping it
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES) #writes the creds value with the value from the keys json file above

service = build('sheets', 'v4', credentials=creds) # builds a package with all the above info and version we need and the right service we need

# Call the Sheets API
sheet = service.spreadsheets()

result2 = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                            range="Reddit-Grabber-Log!A:F").execute() # to specify this variable as all of the reddit grabber spreadsheet

values2 = result2.get('values', []) #get values from spreadsheet

#list of subreddits to grab memes from
subreddit_list = ["memes", "dankmemes", "shitposting", "Unexpected", "Wholesomememes", "me_irl", "meme", "Memes_Of_The_Dank", "starterpacks", "justneckbeardthings", "animemes", "AnimalsBeingDerps", "funny"]

#list of bad words / topics to avoid in our posts
bad_topics = ["faggot", "femboy", "nigger", "fat", "skinny", "horny", "masturbate", "anal", "sex", "racist", "homophobic", "rape", "rapist", "BDSM", "dom", "fucked", "hentai", "Joe Biden", "Biden", "Trump", "Donald Trump"]

#picks a random subreddit from the above list
subreddit = reddit.subreddit(random.choice(subreddit_list)).hot(limit=None)

#establishes count for later count loop break
count = 0
#for loop which contains variables and parameters necessary for grabbing the type of data we want from reddit
for submission in subreddit:
    url = str(submission.url) #makes sure that the url we got from the api is a string variable
    if url.endswith("jpg") or url.endswith("jpeg") or url.endswith("png"): #make sure the post is an image

        if submission.id not in values2: #make sure we don't grab the same reddit post twice -- dont need to hash images that we've already done before

            if submission.spoiler == False: # make sure the post is not flagged as a spoiler

                for string in submission.title: # create for loop (for loop-ception!)

                    if not any(x in string for x in bad_topics): # make sure no bad words are in the submission post titles.

                        if submission.over_18 == False: # make sure the post is not flagged as NSFW -- side note: this sucks, people still post bad crap anyways and mods don't remove it. be careful which subreddits you are scanning even with this on.
                            r = requests.get(url) #defines R variable as grabbing data from our selected url
                            length = float(r.headers.get('content-length')) / 1000 # divides file size by 1000 so we can get how many kilobytes it is

                            if float(length) < 4000: # if it is less than 4 MB or 4000 KB (alternatively for cleaner numbers you can divide by 1,000,000 and do < 4 but e
                                open("image.jpg", 'wb').write(r.content) #download the image from the "url" variable link using requests function
                                hash = imagehash.dhash(Image.open("image.jpg")) #hash the image we just saved
                                os.remove("image.jpg") #remove the image we just saved (since we don't actually need the file after hashing it

                                # define all of our variables as strings to be used later
                                submission_title_string = str(submission.title)
                                submission_id_string = str(submission.id)
                                submission_permalink_string = (str("https://www.reddit.com") + str(submission.permalink))
                                submission_length_string = str(length)
                                submission_hash_string = str(hash)

                                if submission_hash_string not in values2: #make sure the hash is not in the reddit post list already

                                    # create an empty list to store data
                                    Spreadsheet_Values_Append = []

                                    #append list with data from variables above -- I wanted to do this with the count being 4 and have a list of lists containing 4 list which each represent rows but couldn't figure out the formatting so this will do for now.
                                    Spreadsheet_Values_Append.append([submission_title_string, submission_id_string, submission_permalink_string, url,submission_length_string, submission_hash_string])
                                    ## TODO: Fix the formatting so that it can support multiple lists within the list properly

                                    count += 1 # increase the count from 0
                                if count == 1: # when this count reaches 4 .........
                                    break # .... stop the loop. go update values.

request = sheet.values().append(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                range="Reddit-Grabber-Log!A:F", valueInputOption="USER_ENTERED",
                                body={"values": Spreadsheet_Values_Append}).execute()
