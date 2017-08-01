
# create spritesheet

import struct
from math import pow, ceil, log, sqrt
from sys import argv, exit
from os.path import basename, splitext, dirname, join, abspath, isabs, relpath, exists
from os import listdir, makedirs, getcwd
from subprocess import call
from argparse import ArgumentParser

def mkdir(path):
    if path == "":
        return
    if not exists(path):
        makedirs(path)

def filename(path):
    b = basename(path)
    fn, ext = splitext(b)
    if fn == '':
        return None
    return fn
        
def readtext(path):
    with open(path, 'rb') as f:
        return f.read()

def writetext(path, data):
    with open(path, 'w') as f:
        f.write(data)

def get_image_info(path):
    data = readtext(path)
    w, h = struct.unpack('>LL', data[16:24])
    return int(w), int(h)

def next_pow_2(val):
    return pow(2, ceil(log(val) / log(2)))

def get_tile_x(sx, sy, n, pow2=True):
    k = sqrt(sx * sy * n)
    if pow2:
        k = next_pow_2(k)
    return ceil(max(k, sx) / sx)

def surround(text, c):
    return c + text + c
    
def get_images(path=None, name=None):
    path = path or getcwd()
    images = []
    for fn in listdir(path):
        if fn.endswith('.png') and (name is None or fn.startswith(name)):
            images.append(fn)
    # images.sort()
    images = [join(path, image) for image in images]
    return images
    
def write_spritesheet(images, tx, width, out_path):
    # todo use PIL?
    # https://stackoverflow.com/questions/35438802/making-a-collage-in-pil
    quoted = [surround(fn, '"') for fn in images]
    cmd = 'magick montage {} -filter point -tile {} -geometry {}x+0+0 -background transparent {}'.format(
        " ".join(quoted),
        tx,
        width,
        out_path)
    call(cmd, shell=True)
    
def write_metadata(path, n, tx, width, height):
    # lines = [', '.join((str((i % tx) * width), str(int(i / tx) * height))) for i in range(n)]
    data = [n, tx, width, height]
    lines = [str(line) for line in data]
    text = '\n'.join(lines)
    writetext(path, text)
    
def make_spritesheet(name=None, folder=None, pow2=True, output=""):
    images = get_images(folder, name)
    n = len(images)
    if n == 0: exit("no images found")
    width, height = get_image_info(images[0])
    tx = get_tile_x(width, height, n, pow2=pow2)
    
    outdir = dirname(output)
    outdir = outdir if isabs(outdir) else join(folder, outdir)
    mkdir(outdir)    
    out_name = filename(output) or name or "output"
    out_path = join(folder, outdir, out_name + ".png")
    out_txt = join(folder, outdir, out_name + ".txt")
    
    write_spritesheet(images, tx, width, out_path)
    write_metadata(out_txt, n, tx, width, height)
    
    
if __name__ == "__main__":
    parser = ArgumentParser(description="Create spritesheet from set of images")
    # todo allow name use wildcards
    # todo -i -images arg 'append' directly specify paths
    parser.add_argument('-n', '--name', 
                        help="name images start with. otherwise will operate on all images in folder")
    parser.add_argument('-f', '--folder', 
                        help="folder containing images. otherwise working directory")
    parser.add_argument('-p', '--pow2', action='store_false', default=True,
                        help="spritesheet dimensions must be power of two")
    parser.add_argument('-o', '--output', default="output", help="path to output file or folder")
    # todo -v --verbose

    args = parser.parse_args()
    make_spritesheet(**vars(args))
    