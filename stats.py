import subprocess
import time
import pyscreenshot as ImageGrab
from instabot import Bot
import os
import sys
from io import StringIO
import logging

logging.disable(logging.CRITICAL)
old_stdin = sys.stdin
old_stdout = sys.stdout
p = subprocess.Popen(["streamlink", "https://www.youtube.com/watch?v=qgylp3Td1Bw", "best", "-Q"])
time.sleep(10)
open = subprocess.Popen(["open", "-a", "VLC"])
time.sleep(10)
im = ImageGrab.grab(bbox=(20, 100, 2860, 1600))
os.system("killall VLC")
pngIm = im.convert('RGB')
pngIm.save('update.jpg')
result = StringIO()
sys.stdout = result
bot = Bot()
f = open('account.txt', 'r')
sys.stdin = f
bot.login()
sys.stdin = old_stdin
f.close()
bot.upload_photo("update.jpg", caption="Daily coronavirus updates.")
sys.stdout = old_stdout
os.remove("update.jpg" + ".REMOVE_ME")

