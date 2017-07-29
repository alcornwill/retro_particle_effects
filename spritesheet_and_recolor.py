
# todo use PIL maybe (easier for other people to use then)
# todo color(0,0,0) == transparent

from os import listdir, makedirs, getcwd
from os.path import splitext, isfile, exists, join
from subprocess import Popen
import struct
from math import pow, ceil, log, sqrt

gradient_dir = join(getcwd(), "gradients")
images_dir = "C:/tmp"
processes = []
images = []

def mkDir(path):
    if not exists(path):
        makedirs(path)
        
def wait_processes():
    # wait for modulate processes
    for p in processes:
        stdout, stderr = p.communicate()
    processes.clear()

def cmd(cmd_str, cwd=None):
    if cwd:
        p = Popen(cmd_str, cwd=cwd)
    else:
        p = Popen(cmd_str)
    processes.append(p)

def NextPow2(val):
    return pow(2, ceil(log(val) / log(2)))

def getTileX(sx, sy, n):
    k = sqrt(sx * sy * n)
    k = NextPow2(k)
    return ceil(max(k, sx) / sx)
    
def get_image_info(path):
    with open(path, 'rb') as f:
        data = f.read()
    w, h = struct.unpack('>LL', data[16:24])
    return int(w), int(h)
    
def create_spritesheet():
    w, h = get_image_info(join(images_dir, images[0]))
    frames = len(images)
    tileX = getTileX(w, h, frames)
    output = join(outdir, "spritesheet.png")
    cmd("magick montage * -filter point -tile {tilex} -geometry {sizex}x+0+0 -background transparent {output}".format(
            tilex=str(tileX),
            sizex=str(w),
            output=output),
        cwd=images_dir)
    wait_processes()

def recolor_spritesheet():
    input = "spritesheet.png"
    iname, ext = splitext(input)
    for gradient in listdir(gradient_dir):
        gname, ext = splitext(gradient)
        gpath = join(gradient_dir, gradient)
        output = "{}_{}.png".format(iname, gname)
        cmd("magick convert {input} {gradient} -channel RGB -interpolate NearestNeighbor -clut {output}".format(
                input=input,
                gradient=gpath,
                output=output),
            cwd=outdir)
    wait_processes()
        
for fn in listdir(images_dir):
    if isfile(join(images_dir, fn)):
        images.append(fn)

outdir =  join(images_dir, "output")
mkDir(outdir)
create_spritesheet()
recolor_spritesheet()