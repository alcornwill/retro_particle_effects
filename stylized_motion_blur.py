
# todo hmm not producing the right effect anymore. something broken


import os
from os.path import join
from subprocess import Popen
import shutil
import math
import logging

processes = []  # todo should be property

def mkDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

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
    return math.pow(2, math.ceil(math.log(val) / math.log(2)))

def getTileX(sx, sy, n):
    k = math.sqrt(sx * sy * n)
    k = NextPow2(k)
    return math.ceil(max(k, sx) / sx)

class MotionBlur:
    # todo everything should be parameters
    images_dir = "C:\\tmp"  # directory containing images
    out_dir = "C:\\Users\\alcor_000\\Desktop"

    width = 128
    height = 128
    count = 3  # number of degredations (including first)
    space = 2  # number of frames between each degredation
    frame_skip = 2  # todo ability to turn off...

    def __init__(self):
        self.temp_dirs = []
        self.mask_dir = None
        self.temp_out_dir = None
        self.gradient_dir = None  # dir containing gradients
        self.images = None  # original .pngs

        # init
        self.gradient_dir = join(os.getcwd(), "gradients")
        self.update_dirs()

    def update_dirs(self):
        self.mask_dir = join(self.images_dir, "masks")
        self.temp_out_dir = join(self.images_dir, "output")
        self.images = []

        for fn in os.listdir(self.images_dir):
            if os.path.isfile(join(self.images_dir, fn)):
                self.images.append(fn)

    def produce_masks(self):
        logging.info("producing masks")
        mkDir(self.mask_dir)
        for fn in self.images:
            cmd("magick convert {input} -threshold 40%% -alpha off -negate {output}".format(
                    input=join(self.images_dir, fn),
                    output=join(self.mask_dir, fn)))
        wait_processes()

    def produce_degredations(self, count, space):
        logging.info("producing degredations")
        n = 0
        for filepath in self.images:
            filename, ext = os.path.splitext(filepath)
            tempDir = join(self.images_dir, filename)
            mkDir(tempDir)
            self.temp_dirs.append(tempDir)

            for i in range(count):
                y = n
                d = count
                while y >= 0 and d > 0:
                    s = int(100 / count) * d
                    filenext = self.images[y]

                    in_path = join(self.images_dir, filenext)
                    out_path = filename + "_" + str(d) + ".png"

                    cmd("magick convert {input} -modulate {value} -channel Alpha -evaluate Multiply {mult} {output}".format(
                            input=in_path,
                            output=out_path,
                            value=str(s),
                            mult=str(s / 100)),
                        cwd=tempDir)

                    y -= space
                    d -= 1
            n += 1
            wait_processes()

    def compose_frames(self):
        logging.info("composing frames")
        mkDir(self.temp_out_dir)

        # iterate over tempdirs instead? (if valid)
        n = 0
        for filepath in self.images:
            filename, ext = os.path.splitext(filepath)
            temp_dir = join(self.images_dir, filename)

            outputFrame = join(self.temp_out_dir, filepath)
            mods = os.listdir(temp_dir)
            mods.sort()
            shutil.copyfile(join(temp_dir, mods[-1]), outputFrame)
            # copy mask to temp folder and layer it
            tempMask = join(temp_dir, "mask.png")
            shutil.copyfile(join(self.mask_dir, filepath), tempMask)
            for i in range(1, len(mods)):
                f2 = join(temp_dir, mods[-1 - i])
                mask = join(self.mask_dir, self.images[1 + n - i])

                # I can't work out how to do this in one line, or with simpler 'composite' syntax
                # magick convert -alpha off %1 %2 -mask %3 -composite -compose copy_opacity +mask %4
                cmd("magick composite -compose darken {input1} {input2} {output}".format(
                        input1=tempMask, input2=mask, output=tempMask))
                wait_processes()

                cmd("magick convert {input} -mask {mask} -alpha Copy +mask {frame} -composite {output}".format(
                        input=f2,
                        frame=outputFrame,
                        mask=tempMask,
                        output=outputFrame),
                    cwd=self.images_dir)
                wait_processes()
            n += 1

    def apply_frame_skip(self, frame_skip):
        logging.info("applying frame skip")
        count = 0
        for image in os.listdir(self.temp_out_dir):
            full = join(self.temp_out_dir, image)
            if os.path.isfile(full) and count % frame_skip != 0:
                os.remove(full)
            count += 1

    def create_spritesheet(self, width, height, frame_skip):
        logging.info("creating spritesheet")
        frames = len(self.images)
        tileX = getTileX(width, height, frames / frame_skip)

        cmd("magick montage * -filter point -tile {tilex} -geometry {sizex}x+0+0 -background transparent {output}".format(
                tilex=str(tileX),
                sizex=str(width),
                output="spritesheet.png"),
            cwd=self.temp_out_dir)
        wait_processes()

        # copy to output dir
        shutil.copy(
            join(self.temp_out_dir, "spritesheet.png"),
            join(self.out_dir, "spritesheet.png")
        )

    def recolor_spritesheet(self):
        logging.info("creating recolored spritesheet")
        for gradient in os.listdir(self.gradient_dir):
            filename, ext = os.path.splitext(gradient)
            gpath = join(self.gradient_dir, gradient)
            rpath = join(self.out_dir, "spritesheet_{0}.png".format(filename))
            cmd("magick convert {input} {gradient} -channel RGB -interpolate NearestNeighbor -clut {output}".format(
                    input="spritesheet.png",
                    gradient=gpath,
                    output=rpath),
                cwd=self.temp_out_dir)
            wait_processes()

    def cleanup(self):
        logging.info("cleanup")
        for d in self.temp_dirs:
            shutil.rmtree(d)
        shutil.rmtree(self.mask_dir)
        shutil.rmtree(self.temp_out_dir)
        self.temp_dirs.clear()

    def run_all_stages(self):
        logging.info("running all stages")
        self.produce_masks()
        self.produce_degredations(self.count, self.space)
        self.compose_frames()
        self.apply_frame_skip(self.frame_skip)
        self.create_spritesheet(self.width, self.height, self.frame_skip)
        self.recolor_spritesheet()
        self.cleanup()
        logging.info("done")

if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
    logging.info("WARNING! not using blobs so very slow and probably shortens lifespan of hard drive")
    logging.info("(also could fill up your hard drive with junk or delete everything if not careful...)")
    # todo use argparser
    mb = MotionBlur()
    mb.run_all_stages()
