import os
import cv2
import json
import praw
import config
import random
import requests
import facebook
import imagehash
import numpy as np
import pytesseract
from PIL import Image
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build


def is_picture(url):
    """
    Checks if the url is a picture
    """
    return url.endswith(('jpg', 'jpeg', 'png'))


def submission_criteria(spreadsheet_1d_values, post_id, spoiler, over_18):
    """
    Returns true if a submission is new, not a spoiler and not over 18
    """
    return (post_id not in spreadsheet_1d_values) and (not spoiler) and (not over_18)


def no_badwords(sentence):
    """
    Returns True if there is no bad word
    False otherwise
    """
    # insert your bad words here, I can't push to pastebin otherwise
    values_bw = get_sheet_values("Bad_Topics - NSFW!A:A")
    flatlist_bw = flatten(values_bw)
    return not any(word.lower() in sentence for word in flatlist_bw)


def ocr_text():
    """
    Carry out OCR on an image according to
    our requirements and return its text, and if it has a bad word
    """

    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
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
    Gets image from an image url and returns its content
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
    Image_hash = imagehash.dhash(Image.open("image.jpg"))
    return Image_hash, str(Image_hash)


def formatted_parameters(dt_string, fb_response, submission_title, submission_id, submission_permalink, submission_url, length, hash_string):
    """
    Accepts a submission object and returns
    the parameters formatted as a list
    """

    lst = [dt_string,
           fb_response,
           submission_title,
           submission_id,
           f"https://www.reddit.com{submission_permalink}",
           submission_url,
           length,
           hash_string]

    return [str(item) for item in lst]


def one_d_list_to_two_d_list(self):
    length_of_to_be_sent_list = len(self)
    reshaped_list = np.reshape(self, (1, length_of_to_be_sent_list))
    array_to_list = reshaped_list.tolist()
    return array_to_list


def spreadsheet_creds():
    SERVICE_ACCOUNT_FILE = '/home/pi/Documents/Programming-Projects/Meme-Bot/keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    CREDS = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=CREDS)
    return service.spreadsheets()


def get_sheet_values(sheet_name_and_range):
    SHEET = spreadsheet_creds()
    call_for_sheet_info = SHEET.values().get(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                                             range=sheet_name_and_range).execute()
    sheet_info = call_for_sheet_info.get('values', [])
    return sheet_info


def add_to_spreadsheet(self):
    """
    Appends the list of items into the spreadsheet
    """
    SHEET = spreadsheet_creds()
    SHEET.values().append(spreadsheetId=config.config_stuff4['SAMPLE_SPREADSHEET_ID'],
                          range="FB-Poster-Log!A:H", valueInputOption="USER_ENTERED",
                          body={"values": self}).execute()


def get_date_and_time():
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def post_to_fb(url):
    fb_page_id = "100516779334651"
    msg = url
    post_url = 'https://graph.facebook.com/{}/photos'.format(fb_page_id)
    payload = {
        "url": msg,
        "access_token": config.config_stuff['FB_Access_Token']
    }

    post_to_fb_request = requests.post(post_url, data=payload)
    print(post_to_fb_request.text)

    return post_to_fb_request.text


def get_post_id(request):
    return_text_dict = json.loads(request)
    post_id = return_text_dict.get('id')
    return post_id


def edit_fb_caption(post_id, submission_title):
    fb_page_id = "100516779334651"
    # define fb variable for next line with our access info
    fb = facebook.GraphAPI(access_token=config.config_stuff['FB_Access_Token'])

    # edit caption of existing fb post we just made
    fb.put_object(parent_object=fb_page_id + '_' + post_id, connection_name='',
                  message="Original caption: " + '"' + submission_title + '"' + "\n\nP.S. This post was created by a bot. To learn more about how it works, check out the Github page here: https://github.com/Voltaic314/Meme-Poster")
    return print("Caption has been edited to post successfully.")


def get_meme():
    # Initialize reddit instance
    reddit = praw.Reddit(
        client_id=config.config_stuff2['client_id'],
        client_secret=config.config_stuff2['client_secret'],
        user_agent=config.config_stuff2['user_agent'],

    )
    values_rs = get_sheet_values("Reddit-Sources!A:A")
    flatlist_rs = flatten(values_rs)
    values_fb = get_sheet_values("FB-Poster-Log!A:H")
    flatlist_fb = flatten(values_fb)
    subreddit = reddit.subreddit(random.choice(flatlist_rs)).top(time_filter="day", limit=None)

    for submission in subreddit:
        if is_picture(submission.url) and submission_criteria(flatlist_fb, submission.id, submission.spoiler,
                                                              submission.over_18) and no_badwords(submission.title):
            # If our criteria is met get the image and keep contents and size
            image_content, image_length = get_image(submission.url)

            if image_length < 4000:
                # write the image and keep its hash
                image_hash, hash_str = write_image(image_content)

                # confirm image hash not already in spreadsheet
                if hash_str not in flatlist_fb:
                    # Check if image has no bad words
                    image_text, imgtext_nobadwords = ocr_text()

                    if imgtext_nobadwords:
                        # Add the list to the spreadsheet
                        return submission.title, submission.id, submission.permalink, submission.url, image_length, hash_str

                    else:
                        continue


if __name__ == "__main__":
    submission_title, submission_id, submission_permalink, submission_url, image_length, hash_str = get_meme()
    dt_string = str(get_date_and_time())
    send_to_FB_request = post_to_fb(submission_url)
    post_id = get_post_id(send_to_FB_request)
    fb_page_id = "100516779334651"
    if fb_page_id in send_to_FB_request:
        edit_fb_caption(post_id, submission_title)
        submission_list = formatted_parameters(dt_string, send_to_FB_request, submission_title, submission_id, submission_permalink, submission_url, image_length, hash_str)
        array2d_submissions_list = one_d_list_to_two_d_list(submission_list)
        add_to_spreadsheet(array2d_submissions_list)
        print("Post has been posted to FB and logged to the spreadsheet")
