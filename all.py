from newsapi import NewsApiClient
from instabot import Bot
import urllib
from PIL import Image, ImageFont, ImageDraw, ImageOps
import os
import sys
import textwrap
import requests
import mimetypes
import logging
import subprocess
import time
import pyscreenshot as ImageGrab
from io import StringIO
import pyautogui

# Mute logging from streamlink and instabot
logging.disable(logging.CRITICAL)

newsapi = NewsApiClient(api_key=os.getenv("NEWS_KEY"))
top_headlines = newsapi.get_top_headlines(language='en',
                                          country='ca',
                                          page_size=7,
                                          q="coronavirus")

old_stdin = sys.stdin
old_stdout = sys.stdout
articleNo = 0
account = 1

# Get the image with news title

def returnimage():
    counter = 0

    # Show all the articles and let the user select one

    for article in top_headlines["articles"]:
        print(str(counter) + ": " + article["title"])
        counter +=1
    global articleNo
    articleNo = int(input("Which one would you like to upload? Input the number: "))

    # Get the url of the image and its file extension

    url = top_headlines["articles"][articleNo]["urlToImage"]
    response = requests.get(url)
    content_type = response.headers['content-type']
    format = mimetypes.guess_extension(content_type)

    # Download the image, and if it does not work, prompt the user to select another article

    if format == None:
        format = "." + top_headlines["articles"][articleNo]["urlToImage"][-3:]
    while True:
        try:
            urllib.request.urlretrieve(top_headlines["articles"][articleNo]["urlToImage"], "needtodelete" + format)
        except:
            print("There was an error with that image. Please choose another one.")
            articleNo = int(input())
            continue
        if os.path.isfile("needtodelete" + format):
            break

    # Crop the image into a square

    with Image.open("needtodelete" + format) as image:
        width, height = image.size
        new_width = min(width, height)
        new_height = new_width
        width = new_height
        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2
        image = image.crop((left, top, right, bottom))
        image.save("newdelete" + format)
        os.remove("needtodelete" + format)

    # Add text on the image

    with Image.open("newdelete" + format) as image:
        image.show()
        text = top_headlines["articles"][articleNo]["title"]
        length = len(text.split())
        length = len(text)
        draw = ImageDraw.Draw(image)
        fontsize = int(width/(length/8))
        font = ImageFont.truetype("Chunk.ttf", fontsize)
        lines = 0

        for line in textwrap.wrap(text, width=int(width / fontsize * 1.5)):
            lines += 1

        offset = (width - font.getsize(line)[1]*lines)/2
        textcolour = input("Enter the text colour: ")
        os.system("killall Preview")

        # Wrap the text into multiple lines
        for line in textwrap.wrap(text, width=int(width/fontsize*1.5)):
            #draw.text((margin, offset), line, font=font, fill="red")
            w, h = draw.textsize(line, font=font)
            draw.text(((width - w) / 2, (offset)), line, font=font, fill=textcolour)
            offset += font.getsize(line)[1]

        # Add border, and save
        image.save("image" + format)
        converted = image.convert('RGB')
        img_with_border = ImageOps.expand(converted, border=int(width/50), fill='black')
        img_with_border.save("image.jpg")
        img_with_border.show()
        os.remove("image" + format)
    os.remove("newdelete" + format)

    # Ask user if the image is okay. If it isn't, redo the entire process.
    if input("Is the image okay? (y/n): ") == "y":
        os.system("killall Preview")
        post("image", "image.jpg")
    else:
        os.system("killall Preview")
        returnimage()

# Get the stats of the virus

def dailystats():
    print("Opening VLC, getting stats...")
    result = StringIO()
    sys.stdout = result

    # use streamlink to get HLS stream (.m3u8) of the coronavirus live stream (with permission)
    # Open in VLC

    p = subprocess.Popen(["streamlink", "https://www.youtube.com/watch?v=qgylp3Td1Bw", "best", "-Q"])  #, stdout=subprocess.PIPE)
    time.sleep(6)

    # Move mouse out of the way

    pyautogui.moveTo(1450, 0, duration=1)

    # Place VLC in focus (front)

    open = subprocess.Popen(["open", "-a", "VLC"])
    time.sleep(6)

    # After delaying (waiting for VLC to open), take screenshot of stats

    im = ImageGrab.grab(bbox=(20, 100, 2860, 1600))  # X1,Y1,X2,Y2
    os.system("killall VLC")
    pngIm = im.convert('RGB')
    pngIm.save('update.jpg')
    sys.stdin = old_stdin
    sys.stdout = old_stdout
    post("update", "update.jpg")


# Post the given image to Instagram

def post(type, image):
    if type == "image":
        caption = "Get more of the story at " + top_headlines["articles"][articleNo]["url"]
    else:
        caption = "Daily coronavirus updates."
    bot = Bot()
    f = open('account.txt','r')
    print("Uploading to Instagram...")
    result = StringIO()
    sys.stdout = result
    sys.stdin = f

    # Use instabot to upload image

    bot.login()
    sys.stdin = old_stdin
    f.close()
    bot.upload_photo(image,caption=caption)
    sys.stdout = old_stdout
    os.remove(image + ".REMOVE_ME")
    print("Uploaded.")




returnimage()

dailystats()