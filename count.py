import time
import csv
import argparse
import os
import sys
import glob
import cv2

def get_imgs(folder):
    imgs = [i.name.split('.')[-2] for i in os.scandir(folder) if i.is_file()]
    print(len(imgs))
    imgs = sorted(imgs)
    return imgs

def compare_wanted(wanted, imgs, folder, delete, store, corrupt):
    index_w = 0
    index_i = 0

    count_w = 0
    count_un = 0
    count_err = 0
    count_del = 0 #should be similiar to count_un
    if corrupt:
        count_corrupt = 0
    if store is not None:
        missing = []

    def delete_file(img=None):
        nonlocal count_del

        def rm(img_):
            nonlocal count_del
            os.remove(img_)
            print("Removed", img_)
            count_del += 1

        if img is None:
            file = os.path.join(folder, '{0}.*'.format(imgs[index_i])) 
            for img in glob.glob(file):
                rm(img)
        else:
            rm(img)

    while index_w < len(wanted) and index_i < len(imgs):
        try:
            if (wanted[index_w] == imgs[index_i]):

                if corrupt:
                    file = os.path.join(folder, '{0}.*'.format(imgs[index_i])) 
                    for img in glob.glob(file):
                        im = cv2.imread(img)
                        if im is None:
                            count_corrupt += 1
                            print("Corrupted", img)
                            if delete:
                                delete_file(img=img)

                count_w += 1
                index_w += 1
                index_i += 1

            elif (wanted[index_w] < imgs[index_i]):
                print("ERROR?? wanted file may be missing:", wanted[index_w])
                print(index_w,"/", len(wanted), "   ", index_i, "/", len(imgs), "   " , imgs[index_i])
                # index_i += 1
                if store is not None:
                    missing.append(wanted[index_w])
                index_w += 1
                count_err += 1
            else:
                if delete:
                    delete_file()
                index_i += 1
                count_un += 1
        except Exception as e:
            print(index_w, index_i, count_w, count_un, count_err)
            print(e)
            break

    print("number of wanted imgs in folder", count_w)
    print("number of unwanted imgs in folder", count_un)
    print("number of wanted img missing in between", count_err)
    if corrupt:
        print("number of corrupted img", count_corrupt)

    if delete:
        print("number of unwanted imgs deleted", count_del)

    if store is not None:
        with open(store, 'w') as f:
            csvwriter = csv.writer(f,delimiter=',')

            for elm in missing:
                csvwriter.writerow([elm])
        print("saved missing files in", store)

def get_img_list(in_csv):
    img_list = []

    with open(in_csv,'r') as f:
        csvreader = csv.reader(f,delimiter=',')
        for row in csvreader:
            img_list.append(row[0].split('.')[-2])

    return img_list

def main(ann_csv, folder, delete, store, corrupt):
    imgs = get_imgs(folder)
    wanted = get_img_list(ann_csv)
    compare_wanted(wanted, imgs, folder, delete, store, corrupt)
    # print(imgs[0], wanted[0])

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('collated_ann_csv', help='collated annotations csv file from collate_ann.py')
    p.add_argument('folder', help='folder with images')
    p.add_argument('--delete', '-d', action='store_true',
                    help='whether to delete unwanted corrupted imgs')
    p.add_argument('--store', '-s', type=str, default=None,
                    help='whether to save missing imgs to a csv file')
    p.add_argument('--corrupt', '-c', action='store_true',
                    help='whether to check for corrupted images')
    args = p.parse_args()

    main(args.collated_ann_csv, args.folder, args.delete, args.store, args.corrupt)