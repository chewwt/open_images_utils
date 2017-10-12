import cv2
import argparse
import shutil
import os
import glob
import numpy as np
import matplotlib.pyplot as plt

def copy_imgs(imgs, img_folder, store_folder):
    for img in imgs:
        shutil.copy2(os.path.join(img_folder, img), store_folder)

def get_imgs(image, folder, store, threshold, offset):
    img = cv2.resize(cv2.imread(image), (600, 600))
    values = []

    files = os.path.join(folder, '*.*') 

    fs = glob.glob(files)
    size = len(fs)
    found = []

    for i,f in enumerate(fs):
        if i < offset:
            continue

        img2 = cv2.resize(cv2.imread(f), (600, 600))

        diff = np.sum(abs(img2 - img))
        values.append(diff)

        if diff < threshold:
            found.append(f)
            if store is not None:
                shutil.copy2(f, store)

        if i % 100 == 0:
            print("done: ", i+1, "/", size, " ", (i+1) * 100.0 / size, "%    found: ", len(found), '/', i+1-offset, " ", len(found) * 100.0 / (i+1-offset), "%")

    return found, values

def histogram(values):
    plt.hist(values, bins='auto')
    plt.show()

def main(image, folder, store, threshold, offset):
    found, values = get_imgs(image, folder, store, threshold, offset)
    histogram(values)
    # copy_imgs(found, folder, store)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('image', help='image to sieve')
    p.add_argument('folder', help='image folder')
    p.add_argument('--store', '-s', default=None,
                   help='image folder to store dubious images')
    p.add_argument('--threshold', '-t', type=int, default=50,
                   help='max difference')
    p.add_argument('--offset', '-o', type=int, default=0,
                   help='Offset to where to start in image folder')

    args = p.parse_args()

    main(args.image, args.folder, args.store, args.threshold, args.offset)