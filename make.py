
from sys import argv, exit
from os.path import join, exists, basename, splitext
from os import listdir, getcwd, makedirs
from re import escape, match
from subprocess import call
from shutil import copytree, rmtree
from spritesheet import make_spritesheet
from recolor import make_recolors


imgdir = "C:\\tmp"
outdir = join(imgdir, "output")
spritesheet = "spritesheet.png"
gradient_dir = join(getcwd(), "gradients/gradients")
blends_dir = join(getcwd(), "blends")

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
    
def wildcard_to_regex(r):
    r = escape(r)
    r = r.replace('\\*', '.*')
    return r

def process_images():
    make_spritesheet(folder=imgdir, output=join(outdir, spritesheet))
    make_recolors(spritesheet, gradient_dir, outdir)

def auto_process_blends(filenames):
    # render and copy to 'render' folder
    mkdir("render")
    for fn in filenames:
        filepath = join(blends_dir, fn)
        call("blender {} -b -a".format(filepath))
        process_images()
        final = join("render", filename(filepath))
        if exists(final):
            rmtree(final)
        copytree(outdir, final)
        
if __name__ == "__main__":

    if len(argv) == 1:
        # just process images in tmp folder
        process_images()
        exit()
    elif len(argv) == 2:
        # can be wildcard
        r = wildcard_to_regex(argv[1])
        filenames = [string for string in listdir(blends_dir) if match(r, string)]
        auto_process_blends(filenames)
    else:
        # process named blend files
        filenames = argv[1:]
        filenames = [join(blends_dir, fn) for fn in filenames]
        auto_process_blends(filenames)
    
    
    