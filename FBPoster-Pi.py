import os  # used for getting date and time and file paths
import requests  # used for getting img file size in later code
import random  # used for picking a random log to use for posting
import config  # used to call sensitive info
from datetime import datetime  # used for date and time in the FB log posting so we know when things were posted to FB
from googleapiclient.discovery import build  # for spreadsheet stuff
from google.oauth2 import service_account  # also for spreadsheet stuff
import facebook  # to add captions and comments to existing posts.
import json # to decipher the dictionary we get back in return from FB servers. (Mainly this is used to edit captions to the posts).

# ID of the FB page, can be found on FB > page > about > Page ID
page_id = "100516779334651"

# grabs the date and time
now = datetime.now()

# formats the date and time to this format
dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

# points to the keys json file that holds the dictionary of the info we need.
SERVICE_ACCOUNT_FILE = '/home/pi/Documents/Programming-Projects/Meme-Bot/keys.json'

# website to send the oauth info to gain access to our data
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# writes this variable to no value before overwriting it with the info we need, basically cleaning and prepping it
creds = None

# writes the creds value with the value from the keys json file above
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# builds a package with all the above info and version we need and the right service we need
service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()

# to specify this variable as all of the FB log sheet values
result_fb = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                               range="FB-Poster-Log!A:H").execute()

# get values from spreadsheet
values_fb = result_fb.get('values', [])

# to specify this variable as all of the reddit grabber spreadsheet
result_rg = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                               range="Reddit-Grabber-Log!A:F").execute()

# get values from spreadsheet
values_rg = result_rg.get('values', [])

count = 0  # establishes count

# setup primary for loop
for string in values_fb:

    # create an empty list to fill with data
    chosen_post = []

    # pick a random value from reddit spreadsheet
    chosen_post = random.choice(values_rg)

    # basically labeling each item in the index if we ever need to use them
    # grab element one from random list item, this is the title of the randomly grabbed post
    random_title = chosen_post[0]

    # grab element two from random list item, this is the id of the randomly grabbed post
    random_id = chosen_post[1]

    # grab element three from random list item, this is permalink of the randomly grabbed post
    random_permalink = chosen_post[2]

    # grab element four from random list item, this is the url to the image itself, of the randomly grabbed post
    random_url = chosen_post[3]

    # grab element five from random list item, this is file size of the randomly grabbed post
    random_size = chosen_post[4]

    # grab element six from random list item, this is the image hash of the reddit image
    random_hash = chosen_post[5]

    # converts hash to string value just to be safe for the next step
    random_hash_string = str(random_hash)

    # create a flatten list from the list of lists, this way we can do searches thorugh it lke hash check for example
    flatlist_fb_sheet = [item for items in values_fb for item in items]

    # look for hash in the FB post log
    check_hash = random_hash_string in flatlist_fb_sheet

    # make sure that the hash did not come up in the search results - if none then it's not a duplicate image
    if check_hash == False:

        # the message we are sending to the fb server and make sure it's a string
        msg = str(random_url)

        # url that we will send our HTTP request to - to post it to FB
        post_url = 'https://graph.facebook.com/{}/photos'.format(page_id)

        payload = {
            "url": msg,  # injecting our str(url) into the "url" section of the link itself
            "access_token": config.config_stuff['FB_Access_Token']
            # giving our api token to our page referenced in the secret config file
        }

        # wraps up all the above info into a clean variable we can work with
        r = requests.post(post_url, data=payload)

        # print the return text from FB servers to make sure the message went through properly or if not look at errors
        print(r.text)

        # defining this as a string variable to use later (just to be safe -- probably redundant).
        r_text_str = str(r.text)

        r_text_dict = json.loads(r.text)

        # make sure the post we sent is not an error and actually sent through as a real post
        check_no_error = page_id in r_text_str

        # If "check_no_error" is True then that means there were no error return code from FB servers, meaning the post went through
        # When you send a post to FB, if the post goes through it will return the page ID in the r.text, so this checks to make sure we actually made a real post instead of sending a bunch of error'd posts that didn't actually create a real post.
        if check_no_error == True:

            # without concatenating, random_permalink only gives back /r/.... without the url part of it
            random_permalink_string = str(random_permalink)

            # create an empty list to store our list of values to write to teh spreadsheet (spreadsheet requires a 2d list aka list of lists
            spreadsheet_values_append = []

            # append that list to include the info (append probably isn't necessary since it's the only items in the list, but will fix later. TODO: fix later ;)
            spreadsheet_values_append.append(
                [dt_string, r_text_str, random_title, random_id, random_permalink_string, random_url, random_size,
                 random_hash])

            # Now that we posted the photo, we want to log it so that we don't post it again (and good for tracking purposes too).
            # this appends the spreadsheet to fit the list (row) of data onto the last row of the values.
            request = sheet.values().append(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                            range="FB-Poster-Log!A:H", valueInputOption="USER_ENTERED",
                                            body={"values": spreadsheet_values_append}).execute()


            # really just using this as a confirmation to make sure the code got this far.
            print("Logged to FB Poster Spreadsheet")

            # create an empty list
            random_generated = []

            # fill the list with the random info we grabbed to recreate the row we grabbed
            random_generated = [random_title, random_id, random_permalink_string, random_url, random_size, random_hash]

            # take values 2 and remove the randomly generated info from the 2d list in python
            values_rg.remove(random_generated)

            # clear all the values in the reddit spreadsheet
            request_clear = sheet.values().clear(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                                 range="Reddit-Grabber-Log!A:F").execute()

            # replace those empty cells with the new list that doesn't contain the one that FB Poster random choice grabbed
            request_rewrite = sheet.values().update(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                                    range="Reddit-Grabber-Log!A:F", valueInputOption="RAW",
                                                    body={"values": values_rg}).execute()

            count += 5  # increases the count so that this breaks the loop later

        else:
            count += 1  # increases count by 1, try to post 4 more times then stop when count = 5.

    else:
        continue  # try to find a different hash string that isn't in the loop.

    # starting for loop to establish checking the count
    for x in values_fb:

        # if the count goes to 5 (will because of the top condition) then...
        if count >= 5:
            # break the loop. Note that the count will only go up if a successful post goes through. Meaning it can keep constantly posting errors over and over until it finally gets a successful post.
            break
    break

# define the post id for later use -- specifically this is dictionary key from the r.text return text from fb servers after we post
post_id = r_text_dict.get('id')

# define fb variable for next line with our access info
fb = facebook.GraphAPI(access_token=config.config_stuff['FB_Access_Token'])

# edit caption of existing fb post we just made
fb.put_object(parent_object=page_id + '_' + post_id, connection_name='',
              message="Original caption: " + '"' + random_title + '"' + "\n\nP.S. This post was created by a bot. To learn more about how it works, check out the Github page here: https://github.com/Voltaic314/Meme-Poster")

# print to show successful post & edit made.
print("Caption has been edited to post successfully.")
