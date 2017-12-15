"""
Prints the statistics according to the annotation csv file from collate_ann.py
"""

import csv
import argparse

def parser(collated_ann_csv):
    imgs = set()
    classes = {}

    with open(collated_ann_csv, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')
        for row in csvreader:
            if row[0] not in imgs:
                imgs.add(row[0])

            if row[2] in classes:
                classes[row[2]] += 1
            else:
                classes[row[2]] = 1

    return imgs, classes

def pp(imgs, classes):
    print("Total number of imgs:", len(imgs))
    for k in classes:
        print(k, ":", classes[k])

def main(collated_ann_csv):
    imgs, classes = parser(collated_ann_csv)
    pp(imgs, classes)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('collated_ann_csv', help='Collated annotation file from collate_ann.py')

    args = p.parse_args()
    main(args.collated_ann_csv)