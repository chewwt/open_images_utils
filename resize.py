import time
import argparse
import os
import glob
import cv2

def resize(folder, maxi, offset):
    files = os.path.join(folder, '*.*') 

    fs = glob.glob(files)
    size = len(fs)

    resize = 0

    for i,f in enumerate(fs):
        if i < offset:
            continue

        im = cv2.imread(f)
        # cv2.imshow('im', im)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        h, w, c = im.shape
        # print(h, w)

        scale = 1.0
        if h > maxi:
            scale = h / maxi
        if w > maxi and w < h:
            scale = w / maxi

        if scale != 1.0:
            imrs = cv2.resize(im, (int(w/scale), int(h/scale)), interpolation=cv2.INTER_AREA)
            resize += 1
            # print(imrs.shape[:2])
            cv2.imwrite(f,imrs)

        if i % 100 == 0:
            print("done: ", i+1, "/", size, " ", (i+1) * 100.0 / size, "%    resized: ", resize, '/', i+1-offset, " ", resize * 100.0 / (i+1-offset), "%")
    
def main(folder, maxi, offset):
    resize(folder, maxi, offset)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('folder', help='images folder')
    p.add_argument('maxi', type=int, help='max dimension size')
    p.add_argument('--offset', '-o', type=int, default=0,
                   help='Offset to where to start resize in image folder')

    args = p.parse_args()

    main(args.folder, args.maxi, args.offset)