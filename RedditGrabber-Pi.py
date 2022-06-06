import config # used to get the secret sensitive info needed for our APIs - not uploaded to github for security purposes
import praw # used for the reddit api - this is 100% needed for this code to work
import requests # needed to get image file size before we download images (to make sure we don't download images too large that we can't upload elsewhere).
import os # needed to get the file paths
import random # needed to pick a random subreddit to grab data from. In theory you don't have to pick a random one, you could do all at once or just one, either or.
from googleapiclient.discovery import build # python.exe -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from google.oauth2 import service_account # this and the above package are for the spreadsheet usage -- the pip command is a pain so I pasted it above.
from PIL import Image # for image hashing
import imagehash # also for image hashing
import pytesseract # used for optical character recognition within images, basically pulling text out of images so we can analyze it
import cv2 # used for parsing data and converting images before putting into tesseract OCR

#establishing our creds to gain access to the API before we start doing any calls.
reddit = praw.Reddit(
    client_id=config.config_stuff2['client_id'],
    client_secret=config.config_stuff2['client_secret'],
    user_agent=config.config_stuff2['user_agent'],
)

SERVICE_ACCOUNT_FILE = '/home/pi/Documents/Programming-Projects/Meme-Bot/keys.json' # points to the keys json file that holds the dictionary of the info we need.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] # website to send the oauth info to gain access to our data

creds = None #writes this variable to no value before overwriting it with the info we need, basically cleaning and prepping it
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES) #writes the creds value with the value from the keys json file above

service = build('sheets', 'v4', credentials=creds) # builds a package with all the above info and version we need and the right service we need


# Call the Sheets API
sheet = service.spreadsheets()

result = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                            range="FB-Poster-Log!A:H").execute()

values = result.get('values', []) #get values from spreadsheet

result2 = sheet.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                            range="Reddit-Grabber-Log!A:F").execute() # to specify this variable as all of the reddit grabber spreadsheet

values2 = result2.get('values', []) #get values from spreadsheet

#list of subreddits to grab memes from
subreddit_list = ["memes", "dankmemes", "shitposting", "Unexpected", "Wholesomememes", "me_irl", "meme",
                  "Memes_Of_The_Dank", "starterpacks", "animemes", "funny"]

#list of bad words / topics to avoid in our posts
bad_topics = ["faggot", "femboy", "nigger", "fat", "skinny", "horny", "masturbate", "anal", "sex",
              "racist", "homophobic", "rape", "rapist", "BDSM", "dom", "fucked", "hentai",
              "Joe Biden", "Biden", "Trump", "Donald Trump", "disease", "symptom", "Parkinson", "Alzhemier", "memeory loss",
              "COVID", "covid-19", "Virus", "bacteria", "Pandemic", "quarantine", "NATO", "Ukraine", "Russia", "Putin", "fatal",
              "lethal", "no cure", "cock", "pussy", "dick", "vagina", "penis", "reddit",
              "u/", "/r/", "feminists", "qanon", "shooting", "Uvalde",]

#picks a random subreddit from the above list
subreddit = reddit.subreddit(random.choice(subreddit_list)).hot(limit=None)


#flatten the list of lists returned from the fb poster spreadsheet
flatlist_fb = [item for items in values for item in items]

#flatten the list of lists returned from the reddit grabber spreadsheet
flatlist_rg =[item for items in values2 for item in items]

#reader = easyocr.Reader(['en'], gpu=False)

#initializes loop
count = 0
#for loop which contains variables and parameters necessary for grabbing the type of data we want from reddit
for submission in subreddit:
    url = str(submission.url) #makes sure that the url we got from the api is a string variable
    if url.endswith("jpg") or url.endswith("jpeg") or url.endswith("png"): #make sure the post is an image

        if submission.id not in flatlist_rg: #make sure we don't grab the same reddit post twice -- dont need to hash images that we've already done before

            if submission.spoiler is False: # make sure the post is not flagged as a spoiler

                if not any(x in submission.title for x in bad_topics): # make sure no bad words are in the submission post titles.

                    if submission.over_18 == False: # make sure the post is not flagged as NSFW -- side note: this sucks, people still post bad crap anyways and mods don't remove it. be careful which subreddits you are scanning even with this on.
                        r = requests.get(url) #defines R variable as grabbing data from our selected url
                        length = float(r.headers.get('content-length')) / 1000 # divides file size by 1000 so we can get how many kilobytes it is

                        if float(length) < 4000: # if it is less than 4 MB or 4000 KB (alternatively for cleaner numbers you can divide by 1,000,000 and do < 4 but e
                            open("image.jpg", 'wb').write(r.content) #download the image from the "url" variable link using requests function
                            hash = imagehash.dhash(Image.open("image.jpg")) #hash the image we just saved

                            # define all of our variables as strings to be used later
                            submission_title_string = str(submission.title)
                            submission_id_string = str(submission.id)
                            submission_permalink_string = (str("https://www.reddit.com") + str(submission.permalink))
                            submission_length_string = str(length)
                            submission_hash_string = str(hash)

                            #check to make sure the hash of the image we just tested is in the spreadsheet. False means that it's not which means it's not a duplicate image (which is good).
                            check_hash_fb = submission_hash_string in flatlist_fb

                            #check to make sure the hash of the image we just tested is in the reddit grabber spreadsheet. (We want false values only here).
                            check_hash_rg = submission_hash_string in flatlist_rg


                            if check_hash_fb == False: #make sure the hash is not in the reddit post list already

                                if check_hash_rg == False:

                                    ##run OCR
                                    #point to where the tesseract files are in our directory
                                    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

                                    #read BGR values from image
                                    img=cv2.imread('image.jpg')

                                    #convert BGR values to RGB values
                                    img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                                    #give us the resulting text (strings) from the image
                                    ocr_result = pytesseract.image_to_string(img)
                                    os.remove("image.jpg")  # remove the image we just saved (since we don't actually need the file after hashing it)

                                    #this function converts the text from OCR into a list of individual strings, where each string is an element in a list
                                    def Convert(string):
                                        li = list(string.split(" "))
                                        return li
                                    list_text = Convert(ocr_result)

                                    # this section cleans up the list to remove the "\n' from each string in the newly created list
                                    replaced_list = []
                                    for s in list_text:
                                        replaced_list.append(s.replace("\n", ""))

                                    #check to see if within the meme itself if there are bad words in the list above
                                    check_ocr_bad_topics = [word for word in replaced_list if word in bad_topics]

                                    # if no matches of bad topics in the ocr text, then proceed. But if so, try a new image.
                                    if not check_ocr_bad_topics:

                                        # create an empty list to store data
                                        Spreadsheet_Values_Append = []

                                        #append list with data from variables above -- I wanted to do this with the count being 4 and have a list of lists containing 4 list which each represent rows but couldn't figure out the formatting so this will do for now.
                                        Spreadsheet_Values_Append.append([submission_title_string, submission_id_string, submission_permalink_string, url,submission_length_string, submission_hash_string])
                                        ## TODO: Fix formatting of this nonsense so we can post more than link in a single script run

                                        #increases the count to break the loop
                                        count += 1

                                        for x in subreddit:  # starting for loop to establish checking the count
                                            if count == 1:  # this value determines how many images to post to the reddit spreadsheet
                                                break  # ... break the loop. Note that the count will only go up if a successful post goes through. Meaning it can keep constantly posting errors over and over until it finally gets a successful post.
                                        break # break out of the original for loop above

#write 2d list to the final row of the spreadsheet (this is where it adds what it just found to the spreadsheet finally
request = sheet.values().append(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                range="Reddit-Grabber-Log!A:F", valueInputOption="USER_ENTERED",
                                body={"values": Spreadsheet_Values_Append}).execute()

print("Post logged to Reddit Grabber Spreadsheet")
