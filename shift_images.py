"""
Shift images with desired labels to another folder
"""

import time
import csv
import argparse
import shutil
import os
import sys
import glob

def get_classes(wanted):
    c = set()
    with open(wanted, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')

        for row in csvreader:
            c.add(squeeze_lower(row[0]))
    return c

def squeeze_lower(name):
    return name.replace(' ', '').lower()

def get_relevant_imgs(ann_csv):
    imgs = []

    with open(ann_csv, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')

        for row in csvreader:
            if len(imgs) == 0 or imgs[-1] != row[0]:
                imgs.append(row[0])
    # return imgs
    print(len(imgs), imgs[0], imgs[-1])

    return set(imgs)


def shift(imgs, folder, new_folder):

    files = [os.path.join(folder, f.name) for f in os.scandir(folder) if (f.is_file() and f.name in imgs)]
    # files = os.path.join(folder, '*.*') 
    # fs = glob.glob(files)
    # size = len(fs)

    # index = 0
    # print(files)
    for i, f in enumerate(files):
        # if imgs[index] in f: 
        shutil.copy2(f, new_folder)
        os.remove(f)
    #     print(f)
            # index += 1

        # if index >= len(imgs):
        #     break
            # if i % 100 == 0:
            #     print("done: ", i+1, "/", size, " ", (i+1) * 100.0 / size, "%")


def main(wanted, ann, folder, new_folder):
    classes = get_classes(wanted)
    imgs = get_relevant_imgs(ann)
    shift(imgs, folder, new_folder)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('wanted_labels', help='csv/txt file with wanted labels')
    p.add_argument('ann_csv', help='annotation file with desired images')
    p.add_argument('folder', help='image folder')
    p.add_argument('new_folder', help='folder to shift to')

    args = p.parse_args()

    main(args.wanted_labels, args.ann_csv, args.folder, args.new_folder)