import os, sys
import datetime
import imageio
from pprint import pprint
import time
import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

temp_folder = "C:/temp/"

e = sys.exit

def create_gif(filenames, duration):
    images = []
    for filename in filenames:
        images.append(imageio.imread(temp_folder+ filename))
    output_file = 'Gif-%s.gif' % datetime.datetime.now().strftime('%Y-%M-%d-%H-%M-%S')
    imageio.mimsave(output_file, images, duration=duration)


def change_size(filenames):
    for filename in filenames:
        foo = Image.open(filename)
        foo = foo.resize((4400, 3400), Image.ANTIALIAS)
        foo.save(temp_folder + filename, optimize = True, quality=95)

def write_name(filenames):
    for filename in filenames:
        img = Image.open(temp_folder + filename)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("calibri.ttf", 200)
        print(filename.split('_')[0])
        draw.text((300,400), filename.split('_')[0], (30,144,255), font=font)
        img.save(temp_folder + filename)

if __name__ == "__main__":
    script = sys.argv.pop(0)
    duration = 1
    filenames = sorted(filter(os.path.isfile, [x for x in os.listdir('.') if x.endswith(".jpg")]),
                       key=lambda p: os.path.exists(p) and os.stat(p).st_mtime or time.mktime(
                           datetime.now().timetuple()))
    change_size(filenames)
    write_name(filenames)
    create_gif(filenames, duration)