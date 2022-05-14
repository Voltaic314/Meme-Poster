import os # used for getting date and time and file paths
import requests # used for getting img file size in later code
import random # used for picking a random log to use for posting
import config # used to call sensitive info
from datetime import datetime # used for date and time in the FB log posting so we know when things were posted to FB

page_id = "100516779334651" # ID of the FB page, can be found on FB > page > about > Page ID

now = datetime.now() # grabs the date and time
dt_string = now.strftime("%m/%d/%Y %H:%M:%S") #formats the date and time to this format

count = 0

with open('MemeBot/Reddit-Grabber-Log.txt', 'r+') as f: # starts the main loop
    f_contents = f.readlines() # store each line of the contents of the reddit log file (see reddit code for what is in this log)
    desired_lines = [s.strip() for s in f_contents] # strip all the \n's from each line so that we can just get the exact strings
    desired_lines_titles = desired_lines[0::6] #put everything from line 1, every 6 lines, into its own list.
    desired_lines_post_ids = desired_lines[1::6] #put everything from line 2, every 6 lines, into its own list.
    desired_lines_permalinks = desired_lines[2::6] #put everything from line 3, every 6 lines, into its own list.
    desired_lines_urls = desired_lines[3::6] #put everything from line 4, every 6 lines, into its own list.
    desired_lines_size = desired_lines[4::6] #put everything from line 5, every 6 lines, into its own list.

    #the below line is for zipping up all those lists together so that we can fit all the log contents together. Please see python zipping lists for what I mean
    desired_lines_zip = zip(desired_lines_titles, desired_lines_post_ids, desired_lines_permalinks, desired_lines_urls, desired_lines_size)

    #The above line was for specifying which lists to zip together, this below line is what is actually zipping them.
    zipped_list = list(desired_lines_zip)

    #create an empty list to fill with data
    random1 = []

    #pick a random item from the new zipped list
    random1 = random.choice(zipped_list)

    random_title = random1[0] #grab element one from random list item, this is the title of the randomly grabbed post
    random_id = random1[1] #grab element two from random list item, this is the id of the randomly grabbed post
    random_permalink = random1[2] #grab element two from random list item, this is permalink of the randomly grabbed post
    random_url = random1[3] #grab element two from random list item, this is the url to the image itself, of the randomly grabbed post
    random_size = random1[4] #grab element two from random list item, this is file size of the randomly grabbed post

    #now that we've picked a random file, see if it is already in the FB log post (this means we've posted this before), if it's not then continue on, if it is start again.
    with open('MemeBot/FB-Poster-Log.txt', 'r+') as g:
        g_contents = g.readlines() # put each line of the log file into a list
        if random_id not in g_contents: #scan the list to see if the randomly picked reddit post ID from reddit log file is already in the FB log file, if not continue...
            msg = str(random_url) #the message we are sending to the fb server and make sure it's a string
            post_url = 'https://graph.facebook.com/{}/photos'.format(page_id) #url that we will send our HTTP request to - to post it to FB
            payload = {
                "url": msg, #injecting our str(url) into the "url" section of the link itself
                "access_token": config.config_stuff['FB_Access_Token'] # giving our api token to our page referenced in the secret config file
              }
            r = requests.post(post_url, data=payload) #wraps up all the above info into a clean variable we can work with
            r_text = r.text
            print(r.text) # print the return text from FB servers to make sure the message went through properly or if not look at errors
            # Now that we posted the photo, and made sure the post actually went through, we want to log it so that we don't post it again (and good for tracking purposes too).
            with open('MemeBot/FB-Poster-Log.txt','a+') as h: #open the log file
                h.write(str(dt_string) + str("\n")) #on the first line, write the date and time
                h.write(str(r.text) + str("\n")) #on the second line, write FB's return code (which contains the FB post ID).
                h.write(str(random_title) + str("\n")) #on the third line, write the Title of the original Reddit post
                h.write(str(random_id) + str("\n")) #on the fourth line, write the ID of the Reddit post we used.
                h.write(str(random_permalink) + str("\n")) #on the fifth line, write the link of the reddit post
                h.write(str(random_url) + str("\n")) #on the sixth line, write the link to the image itself from the reddit post
                h.write(str(random_size) + str("\n\n")) # on the seventh line, write the file size of the image we used (mainly just wanted to do this for tracking purposes but this isn't really used other than to make sure it's below the posting limit).
                if page_id in r_text: # When you send a post to FB, if the post goes through it will return the page ID in the r.text, so this checks to make sure we actually made a real post instead of sending a bunch of error'd posts that didn't actually create a real post.
                    count += 1 # increases the count so that this breaks the loop later
                for x in h: # creates a for loop so that we can break out
                    if count == 1: # if the count goes from 0 to 1 (will because of the top condition) then...
                        break # ... break the loop. Note that the count will only go up if a successful post goes through. Meaning it can keep constantly posting errors over and over until it finally gets a successful post. This may get spammy, so we may want to add another conditional count for error responses so we don't spam FB api with 1,000 error posts per every post or something. lol
