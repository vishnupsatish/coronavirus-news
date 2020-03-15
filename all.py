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

def returnimage():
    counter = 0
    for article in top_headlines["articles"]:
        print(str(counter) + ": " + article["title"])
        counter +=1
    articleNo = int(input("Which one would you like to upload? Input the number: "))

    url = top_headlines["articles"][articleNo]["urlToImage"]
    response = requests.get(url)
    content_type = response.headers['content-type']
    format = mimetypes.guess_extension(content_type)

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

    with Image.open("newdelete" + format) as image:
        text = top_headlines["articles"][articleNo]["title"]
        length = len(text.split())
        length = len(text)
        draw = ImageDraw.Draw(image)
        fontsize = int(width/(length/8))
        font = ImageFont.truetype("Chunk.ttf", fontsize)
        lines = 0
        for line in textwrap.wrap(text, width=int(width / fontsize * 1.5)):
            lines += 1
        offset = int((width/10))
        offset = (width - font.getsize(line)[1]*lines)/2
        for line in textwrap.wrap(text, width=int(width/fontsize*1.5)):
            #draw.text((margin, offset), line, font=font, fill="red")
            w, h = draw.textsize(line, font=font)
            draw.text(((width - w) / 2, (offset)), line, font=font, fill="red")
            offset += font.getsize(line)[1]
        image.save("image" + format)
        converted = image.convert('RGB')
        img_with_border = ImageOps.expand(converted, border=int(width/50), fill='black')
        img_with_border.save("image.jpg")
        img_with_border.show()
        os.remove("image" + format)
    os.remove("newdelete" + format)
    if input("Is the image okay? (y/n): ") == "y":
        os.system("killall Preview")
        post("image", "image.jpg")
    else:
        os.system("killall Preview")
        returnimage()

def dailystats():
    result = StringIO()
    sys.stdout = result
    p = subprocess.Popen(["streamlink", "https://www.youtube.com/watch?v=qgylp3Td1Bw", "best", "-Q"])  #, stdout=subprocess.PIPE)
    time.sleep(10)
    open = subprocess.Popen(["open", "-a", "VLC"])
    time.sleep(10)
    im = ImageGrab.grab(bbox=(20, 100, 2860, 1600))  # X1,Y1,X2,Y2
    os.system("killall VLC")
    pngIm = im.convert('RGB')
    pngIm.save('update.jpg')
    sys.stdin = old_stdin
    post("update", "update.jpg")
    sys.stdout = old_stdout


def post(type, image):
    if type == "image":
        caption = "Get more of the story at " + top_headlines["articles"][articleNo]["url"]
    else:
        caption = "Daily coronavirus updates."
    bot = Bot()
    f = open('account.txt','r')
    result = StringIO()
    sys.stdout = result
    sys.stdin = f
    bot.login()
    sys.stdin = old_stdin
    f.close()
    bot.upload_photo(image,caption=caption)
    sys.stdout = old_stdout
    os.remove(image + ".REMOVE_ME")



returnimage()

dailystats()