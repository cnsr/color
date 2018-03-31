from PIL import Image, ImageDraw
import binascii
import sys

a = sys.argv

if '-h' in a:
    print('Example of usage: "python color.py in.jpg 10"\
            \nReturns 10 most common colors of in.jpg')
    sys.exit()
else:
    try:
        if not a[1].lower().endswith(('jpg','png','jpeg')):
            location = 'in.jpg'
        else:
            location = a[1]
    except IndexError:
        location = 'in.jpg'
    try:
        max_colors = int(a[2])
    except (IndexError, ValueError):
        max_colors = 10

# get average color of the whole image
def color(location, res):
    im = Image.open(location)
    hist = im.histogram()
    if len(hist) > 256:
        r = hist[:256]
        g = hist[256:512]
        b = hist[512:768]
        if res == 'avg':
            return 'red: {0}\ngreen: {1}\nblue: {2}'.format(avg(r), avg(g),avg(b))
        else:
            return 'rgb({0},{1},{2})'.format(avg(r), avg(g),avg(b))
    else:
        return avg(hist)


# average color of band
def avg(band):
    return int(sum(a*b for a, b in enumerate(band)) / sum(band))


# n most common colors in an image
def most_common(location, max_colors):
    try:
        im = Image.open(location).convert('RGB')
    except FileNotFoundError:
        print('Specify imagename, please.')
        sys.exit()
    w, h = im.size
    img_sz = w * h
    colors = sorted(im.getcolors(maxcolors=img_sz), key=lambda x: x[0])[max_colors*-1:]
    colors = list(reversed(colors))
    new = Image.new('RGB', (100*max_colors, 140)) # add rows = 140 * rows
    draw = ImageDraw.Draw(new)
    for color in colors:
        x0 = colors.index(color) * 100
        x1 = x0 + 100
        y0 = 0
        y1 = 100
        draw.rectangle([x0, y0, x1, y1], fill=color[-1])
        text = str(color[-1]) + '\n' + rgb_to_hex(color[-1]) + '\n' + str(color[0]) +' times'
        draw.text((x0, y1),text=text, align='center')
    del draw
    new.save('out.png')

def rgb_to_hex(rgb):
    r,g,b = rgb
    return '#%02x%02x%02x' % (r,g,b)

most_common(location, max_colors)
