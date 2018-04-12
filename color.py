from PIL import Image, ImageDraw
import binascii
import sys
from operator import itemgetter
import argparse


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sort", help="sort colors from darker to lighter", action="store_true", default=False,
                        dest='sort')
    parser.add_argument('image', type=str, help="choose input image, default value is use in.jpg")
    parser.add_argument('-m', action="store", dest="max_colors", type=int, help="Amount of colors you want to receive\
    (less than 20). Defaults to 10.")
    parser.add_argument('-t', action="store", dest="threshold", type=int, help="Color comparison threshold, lesser value means\
    more different colors. Defaults to 12")
    a = parser.parse_args()
    location = a.image
    max_colors = a.max_colors
    threshold = a.threshold

    if not location.lower().endswith(('jpg','png','jpeg')):
        raise Exception('Unsupported filetype.')
    if not threshold:
        threshold = 12
    if not max_colors:
        max_colors = 10
    return (location, max_colors, threshold, a.sort)


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


def sort_by_luminance(colors):
    ret = []
    for color in colors:
        lum = luminance(color[-1])
        ret.append((color[0], round(lum, 2), color[-1]))
    return sorted(ret, key=itemgetter(1))

# n most common colors in an image
def most_common(location, max_colors, threshold, sort=False):
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
    if sort:
        colors = sort_by_luminance(colors)
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

def main():
    try:
        location, max_colors, threshold, sort = setup()
        most_common(location, max_colors, threshold, sort)
    except Exception as e:
        print(e)
        sys.exit()

if __name__ == '__main__':
    main()
