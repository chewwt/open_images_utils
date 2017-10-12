import csv
import argparse
import shutil
import os

def get_count(class_csv, number):
    count = {}

    with open(class_csv, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')
        for row in csvreader:
            count[row[0]] = number

    return count

def get_imgs(ann_csv, count):
    imgs = []

    with open(ann_csv, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')

        for row in csvreader:
            if check_class(count, row[2]) and (len(imgs) == 0 or imgs[-1] != row[0]):
                count[row[2]] -= 1
                imgs.append(row[0])
            
            if check_count(count):
                break

    print(imgs)
    print(len(imgs))
    return imgs

def check_count(count):
    for k in count.keys():
        if count[k] > 0:
            return False

    return True

def check_class(count, c):
    if count[c] > 0:
        return True
    else:
        return False

def count_classes(ann_csv, imgs):
    index = 0
    count = {}

    with open(ann_csv, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')

        for row in csvreader:
            if get_number(row[0]) > get_number(imgs[index]):
                index += 1

            if index >= len(imgs):
                break

            if imgs[index] == row[0]:
                if row[2] in count:
                    count[row[2]] += 1
                else:
                    count[row[2]] = 1

    pp(count)
    return count

def get_number(img_name):
    return img_name.split('.')[0]

def pp(count):
    print()
    for k in count.keys():
        print(k, ":", count[k])

def copy_imgs(imgs, img_folder, store_folder):
    for img in imgs:
        shutil.copy2(os.path.join(img_folder, img), store_folder)

def main(ann_csv, class_csv, img_folder, store_folder, number):
    count = get_count(class_csv, number)
    imgs = get_imgs(ann_csv, count)
    actual_count = count_classes(ann_csv, imgs)
    copy = copy_imgs(imgs, img_folder, store_folder)

#  need annotations to count
if __name__ == '__main__':
    p = argparse.ArgumentParser()

    p.add_argument('ann_csv', help='csv file with ground truth annotation')
    p.add_argument('class_csv', help='csv file with wanted classes')
    p.add_argument('img_folder', help='folder with images')
    p.add_argument('store_folder', help='folder to store selected images')
    p.add_argument('--number', '-n', type=int, default=2,
                    help='number of objects to store for each class')
    args = p.parse_args()

    main(args.ann_csv, args.class_csv, args.img_folder, args.store_folder, args.number)