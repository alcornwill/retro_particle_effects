
from os import listdir, getcwd
from os.path import splitext, join, basename
from subprocess import Popen
from argparse import ArgumentParser

processes = []
        
def filename(path):
    b = basename(path)
    fn, ext = splitext(b)
    if fn == '':
        return None
    return fn
        
def wait_processes():
    for p in processes:
        stdout, stderr = p.communicate()
    processes.clear()

def cmd(cmd_str, cwd=None):
    if cwd:
        p = Popen(cmd_str, cwd=cwd)
    else:
        p = Popen(cmd_str)
    processes.append(p)

def make_recolors(input, gradients, output):
    # todo stop doing cwd, make paths absolute
    iname = filename(input)
    for gradient in listdir(gradients):
        gpath = join(gradients, gradient)
        gname = filename(gradient)
        out_name = "{}_{}.png".format(iname, gname)
        cmd("magick convert {input} -alpha copy -channel A {gradient} -channel RGB -interpolate NearestNeighbor -clut {output}".format(
                input=input,
                gradient=gpath,
                output=out_name),
            cwd=output)
    wait_processes()
    
if __name__ == "__main__":
    parser = ArgumentParser(description="Recolor image with set of gradients")
    parser.add_argument('-i', '--input', help="input image file")
    parser.add_argument('-g', '--gradients', help="folder containing gradients")
    parser.add_argument('-o', '--output', help="output folder")
    # todo -v --verbose

    args = parser.parse_args()
    make_recolors(**vars(args))
    