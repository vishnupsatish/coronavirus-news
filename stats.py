import subprocess
import time
import pyscreenshot as ImageGrab
from instabot import Bot
import os
import sys
from io import StringIO
import logging
import pyautogui

logging.disable(logging.CRITICAL)
old_stdin = sys.stdin
old_stdout = sys.stdout

# Post the given image to Instagram

def post(type, image):
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

dailystats()