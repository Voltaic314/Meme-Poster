import os
import requests
import random
import config
from datetime import datetime

page_id = "100516779334651"

now = datetime.now()
dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

with open('MemeBot/Reddit-Grabber-Log.txt', 'r+') as f:
    f_contents = f.readlines()
    desired_lines = [s.strip() for s in f_contents]
    desired_lines_titles = desired_lines[0::6]
    desired_lines_post_ids = desired_lines[1::6]
    desired_lines_permalinks = desired_lines[2::6]
    desired_lines_urls = desired_lines[3::6]
    desired_lines_size = desired_lines[4::6]
    desired_lines_zip = zip(desired_lines_titles, desired_lines_post_ids, desired_lines_permalinks, desired_lines_urls, desired_lines_size)
    zipped_list = list(desired_lines_zip)
    random1 = []
    random1 = random.choice(zipped_list)
    random_title = random1[0]
    random_id = random1[1]
    random_permalink = random1[2]
    random_url = random1[3]
    random_size = random1[4]
    with open('MemeBot/FB-Poster-Log.txt', 'r+') as g:
        g_contents = g.readlines()
        if random_id not in g_contents:
            msg = random_url
            image_location = str(random_url)
            post_url = 'https://graph.facebook.com/{}/photos'.format(page_id)
            payload = {
                "url": image_location,
                "access_token": config.config_stuff['FB_Access_Token']
              }
            r = requests.post(post_url, data=payload)
            print(r.text) # print the return text from FB servers to make sure the message went through properly or if not look at errors
            r_text = r.text
            with open('MemeBot/FB-Poster-Log.txt','a+') as h:
                h.write(str(dt_string) + str("\n"))
                h.write(str(r_text) + str("\n"))
                h.write(str(random_title) + str("\n"))
                h.write(str(random_id) + str("\n"))
                h.write(str(random_permalink) + str("\n"))
                h.write(str(random_url) + str("\n"))
                h.write(str(random_size) + str("\n\n"))