import os # used for getting date and time and file paths
import requests # used for getting img file size in later code
import random # used for picking a random log to use for posting
import config # used to call sensitive info
from datetime import datetime # used for date and time in the FB log posting so we know when things were posted to FB
from googleapiclient.discovery import build # for spreadsheet stuff
from google.oauth2 import service_account # also for spreadsheet stuff

page_id = "100516779334651" # ID of the FB page, can be found on FB > page > about > Page ID

now = datetime.now() # grabs the date and time
dt_string = now.strftime("%m/%d/%Y %H:%M:%S") # formats the date and time to this format

SERVICE_ACCOUNT_FILE = 'keys.json' # points to the keys json file that holds the dictionary of the info we need.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] # website to send the oauth info to gain access to our data

creds = None #writes this variable to no value before overwriting it with the info we need, basically cleaning and prepping it
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES) #writes the creds value with the value from the keys json file above

service = build('sheets', 'v4', credentials=creds) # builds a package with all the above info and version we need and the right service we need

# Call the Sheets API
sheet = service.spreadsheets()

result = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                            range="FB-Poster-Log!A:H").execute() # to specify this variable as all of the FB log sheet values

values = result.get('values', []) #get values from spreadsheet

result2 = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                            range="Reddit-Grabber-Log!A:F").execute() # to specify this variable as all of the reddit grabber spreadsheet

values2 = result2.get('values', []) #get values from spreadsheet

#create an empty list to fill with data
random1 = []

#pick a random item from the new zipped list
random1 = random.choice(values2)

# basically labeling each item in the index if we ever need to use them
random_title = random1[0] #grab element one from random list item, this is the title of the randomly grabbed post
random_id = random1[1] #grab element two from random list item, this is the id of the randomly grabbed post
random_permalink = random1[2] #grab element two from random list item, this is permalink of the randomly grabbed post
random_url = random1[3] #grab element two from random list item, this is the url to the image itself, of the randomly grabbed post
random_size = random1[4] #grab element two from random list item, this is file size of the randomly grabbed post
random_hash = random1[5]


count = 0

#now that we've picked a random file, see if it is already in the FB log post (this means we've posted this before), if it's not then continue on, if it is start again.
if random_hash not in values: # scan all ouf our FB logs to see if the hash of the image we picked has already been posted.
    msg = str(random_url) #the message we are sending to the fb server and make sure it's a string
    post_url = 'https://graph.facebook.com/{}/photos'.format(page_id) #url that we will send our HTTP request to - to post it to FB
    payload = {
        "url": msg, #injecting our str(url) into the "url" section of the link itself
        "access_token": config.config_stuff['FB_Access_Token'] # giving our api token to our page referenced in the secret config file
      }
    r = requests.post(post_url, data=payload) #wraps up all the above info into a clean variable we can work with
    print(r.text) # print the return text from FB servers to make sure the message went through properly or if not look at errors

    r_text = str(r.text) # defining this as a string variable to use later (just to be safe -- probably redundant).

    if page_id in r_text:  # When you send a post to FB, if the post goes through it will return the page ID in the r.text, so this checks to make sure we actually made a real post instead of sending a bunch of error'd posts that didn't actually create a real post.
        random_permalink_string = (str("http://www.reddit.com") + str(random_permalink))  # without concatenating, random_permalink only gives back /r/.... without the url part of it

        Spreadsheet_Values_Append = []  # create a list to put the data of each variable defined above into

        # append that list to include the info (append probably isn't necessary since it's the only items in the list, but will fix later. TODO: fix later ;)
        Spreadsheet_Values_Append.append(
            [dt_string, r_text, random_title, random_id, random_permalink_string, random_url, random_size, random_hash])

        # Now that we posted the photo, we want to log it so that we don't post it again (and good for tracking purposes too).
        request = sheet.values().append(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                        range="FB-Poster-Log!A:H", valueInputOption="USER_ENTERED",
                                        body={
                                            "values": Spreadsheet_Values_Append}).execute()  #this appends the spreadsheet to fit the list (row) of data onto the last row of the values.

        count += 5  # increases the count so that this breaks the loop later
    else:
        count += 1  # increases the count by 1 so the script now has one less try to attempt to post to FB. If this count ever reaches 10 or more it will break the loop. (which is good) theoretically also means the bot could fail 10 times and then we'd just have to wait until the next interval. But that's alright

    for x in values: #starting for loop to establish checking the count
        if count >= 5:  # if the count goes to 5 (will because of the top condition) then...
            break  # ... break the loop. Note that the count will only go up if a successful post goes through. Meaning it can keep constantly posting errors over and over until it finally gets a successful post.
## program end
