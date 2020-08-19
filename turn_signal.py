import cv2
from PIL import Image
from PIL import ImageStat
def turn_signal(input):
    im = Image.fromarray(cv2.cvtColor(input, cv2.COLOR_BGR2RGB))
    im = im.convert('L')
    stat = ImageStat.Stat(im)
    print(stat.mean[0])
