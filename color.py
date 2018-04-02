from PIL import Image, ImageDraw
import binascii
import sys
import config

a = sys.argv

if '-h' in a:
    print('Example of usage: "python color.py in.jpg 10 10"\
            \nReturns 10 most common colors of in.jpg with +-10 color similarity in rgb\
            \nDecrease threshold and increase maximum amount of colors to get more colors.')
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
        max_colors = config.max_colors
    try:
        threshold = int(a[3])
    except (IndexError, ValueError):
        threshold = config.threshold

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


def luminance(pixel):
    r,g,b = pixel
    return (0.299*r + 0.587*g +  0.114*b)


# compare two colors to find out if they are similar
def is_similar(col1, col2, threshold=12):
    return abs(luminance(col1) - luminance(col2)) < threshold


# checks if color is too close to black or white
def black_white(col):
    black = (3,3,3) # not actually black since black would give 0 luminance
    white = (255,255,255)
    return is_similar(col, black, 24) or is_similar(col, white, 24)


# n most common colors in an image
def most_common(location, max_colors):
    try:
        im = Image.open(location).convert('RGB')
    except FileNotFoundError:
        print('Specify imagename, please.')
        sys.exit()
    w, h = im.size
    img_sz = w * h
    max_col_sz = int(img_sz / 1000 * -1)
    # multiplied by two we can compare colors and have some leftovers
    colors = sorted(im.getcolors(maxcolors=img_sz), key=lambda x: x[0])[max_col_sz:]
    colors = list(reversed(colors))
    # color comparison
    for color in colors:
        if black_white(color[-1]):
            colors.remove(color)
    for color1 in colors:
        for color2 in colors:
            if not color1 == color2:
                # could pass threshold here
                if is_similar(color1[-1], color2[-1], threshold):
                    if color1[0] > color2[0]:
                        colors.remove(color2)
                    else:
                        try:
                            colors.remove(color1)
                        # not in list (?)
                        except ValueError:
                            pass
    colors = colors[:max_colors]
    if len(colors) < max_colors:
        max_colors = len(colors)
    if max_colors <= 10: rows = 1
    elif max_colors > 10 and max_colors <= 20: rows = 2
    else:
        rows = int(max_colors // 10)
        if max_colors % 10 != 0: rows+=1
    max_x = max_colors
    if max_x > 10: max_x = 10
    new = Image.new('RGB', (100*max_x, 140 * rows))
    draw = ImageDraw.Draw(new)
    row = 0
    for color in colors:
        x0 = colors.index(color) * 100 - row * 1100
        y0 = row * 140
        if x0 > 999:
            row += 1
        y1 = y0 + 100
        x1 = x0 + 100
        draw.rectangle([x0, y0, x1, y1], fill=color[-1])
        text = str(color[-1]) + '\n' + rgb_to_hex(color[-1]) + '\n' + str(color[0]) +' times'
        draw.text((x0, y1),text=text, align='center')
    del draw
    new.save('out.png')
    print('Done.')
    sys.exit()

def rgb_to_hex(rgb):
    r,g,b = rgb
    return '#%02x%02x%02x' % (r,g,b)

most_common(location, max_colors)
