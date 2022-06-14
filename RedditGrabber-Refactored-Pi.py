import os
import cv2
import praw
import config
import random
import requests
import imagehash
import pytesseract
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build
import numpy as np

# Initialize reddit instance
reddit = praw.Reddit(
    client_id=config.config_stuff2['client_id'],
    client_secret=config.config_stuff2['client_secret'],
    user_agent=config.config_stuff2['user_agent'],
)

# list of subreddits to grab memes from
subreddit_list = ["memes", "dankmemes", "shitposting", "Unexpected", "Wholesomememes", "me_irl", "meme",
                  "Memes_Of_The_Dank", "starterpacks", "animemes", "funny"]

subreddit = reddit.subreddit(random.choice(subreddit_list)).top(time_filter="day", limit=None)


def is_picture(url):
    """
    Checks if the url is a picture
    """
    return url.endswith(('jpg', 'jpeg', 'png'))


def submission_criterias(id, spoiler, over_18):
    """
    Returns true if a submission is new, not a spoiler and not over 18
    """
    return (id not in flatlist_rg) and (not spoiler) and (not over_18)


def no_badwords(sentence):
    """
    Returns True if there is no badword
    False otherwise
    """
    # insert your bad words here, I can't push to pastebin otherwise

    return not any(word in sentence for word in flatlist_bw)


def ocr_text():
    """
    Carry out OCR on an image according to
    our requirements and return its text, and if it has a bad word
    """
    img = cv2.imread('image.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    ocr_result = pytesseract.image_to_string(img)

    os.remove("image.jpg")

    ocr_text_list = [word.replace('\n', '') for word in ocr_result.split(' ')]

    return ocr_text_list, no_badwords(ocr_text_list)


def flatten(nested_list):
    """
    Flattens a nested list.
    I suggest using numpy.ravel() instead
    """
    return [item for items in nested_list for item in items]


def get_image(url):
    """
    Gets image from a url and returns its content
    and size.
    """
    # defines R variable as grabbing data from our selected url
    requests_content_length = requests.get(url)

    # divides file size by 1000 so we can get how many kilobytes it is
    length = float(requests_content_length.headers.get('content-length')) / 1000

    return requests_content_length.content, length


def write_image(content):
    """
    Write an image
    and return its content and hash in str and hex dtype
    """
    open("image.jpg", 'wb').write(content)
    hash = imagehash.dhash(Image.open("image.jpg"))
    return hash, str(hash)


def formatted_parameters(submission_object, length, hash):
    """
    Accepts a submission object and returns
    the parameters formatted as a list
    """

    lst = [submission_object.title
        , submission_object.id
        , f"https://www.reddit.com{submission_object.permalink}"
        , submission_object.url
        , length
        , hash]

    return [str(item) for item in lst]

def one_d_list_to_two_d_list(self):
    length_of_to_be_sent_list = len(self)
    reshaped_list = np.reshape(self, (1, length_of_to_be_sent_list))
    array_to_list = reshaped_list.tolist()
    return array_to_list

def add_to_spreadsheet(self):
    """
    Appends the list of items into the spreadsheet
    """
    sent_list = SHEET.values().append(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                      range="Reddit-Grabber-Log!A:F", valueInputOption="USER_ENTERED",
                                      body={"values": self}).execute()

if __name__ == "__main__":
    # Initialize pytesseract directory
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

    # Connect to google sheets API
    # And retrieve relevant data
    SERVICE_ACCOUNT_FILE = '/home/pi/Documents/Programming-Projects/Meme-Bot/keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    CREDS = None
    CREDS = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=CREDS)
    SHEET = service.spreadsheets()
    result_fb = SHEET.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID']
                                   , range="FB-Poster-Log!A:H").execute()
    values_fb = result_fb.get('values', [])
    result_rg = SHEET.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Reddit-Grabber-Log!A:F").execute()
    values_rg = result_rg.get('values', [])
    result_bw = SHEET.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                   range="Bad_Topics - NSFW!A:A").execute()
    values_bw = result_bw.get('values', [])

    # Lists of posts already existing in the SHEET
    flatlist_fb = flatten(values_fb)
    flatlist_rg = flatten(values_rg)
    flatlist_bw = flatten(values_bw)

    count = 0

    for submission in subreddit:
        if is_picture(submission.url) and submission_criterias(submission.id, submission.spoiler,
                                                               submission.over_18) and no_badwords(submission.title):
            # If our criteria is met get the image and keep contents and size
            image_content, image_length = get_image(submission.url)

            if image_length < 4000:
                # write the image and keep its hash
                image_hash, hash_str = write_image(image_content)
                submissions_list = formatted_parameters(submission, image_length, hash_str)
                *_, submission_hash = submissions_list

                array2d_submissions_list = one_d_list_to_two_d_list(submissions_list)

                # confirm image hash not already in spreadsheet
                if submission_hash not in (flatlist_rg + flatlist_fb):
                    # Check if image has no bad words
                    image_text, imgtext_nobadwords = ocr_text()

                    if imgtext_nobadwords:
                        # Add the list to the spreadsheet
                        add_to_spreadsheet(one_d_list_to_two_d_list(submissions_list))
                        print("Post logged to Reddit Grabber Spreadsheet")

                        count += 1
                        if count == 4:
                            break
                        else:
                            continue
                    else:
                        continue

                    # just for my own sanity, to make sure we completed the whole loop and script. THe proverbial "The end." lol
print("\nAll posts have been logged to the spreadsheet accordingly.")