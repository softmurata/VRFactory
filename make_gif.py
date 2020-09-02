from PIL import Image, ImageDraw
import glob

image_pathes = glob.glob('*.png')

images = []
for img_path in image_pathes:
    img = Image.open(img_path)
    images.append(img)


images[0].save('figure.gif',
               save_all=True, append_images=images[1:], optimize=False, duration=40, loop=0)