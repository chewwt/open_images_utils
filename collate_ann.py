import csv
import argparse
import os
import glob
# import cv2
import get_image_size
import functools

def get_imgs(folder, bad_imgs):
    imgs = {}
    count = 0
    corrupted = []

    files = [f.name for f in os.scandir(folder) if (f.is_file() and f.name not in bad_imgs)]

    for i, f in enumerate(files):

        if i % 1000 == 0:
            print('progress', i / float(len(files)) * 100.0, '%   ', i, '/', len(files), '   ', ' no. of corrupted:', count)
       
        path = os.path.join(folder, f)
        try:
            width, height = get_image_size.get_image_size(path)
            imgs[f.split('.')[-2]] = (width, height, f)
        except Exception as e:
            print('problem with', path)
            print(e)
            count += 1   
            corrupted.append(f)

        # im = cv2.imread(path)
        # try:
        #     width, height, _ = im.shape
        #     imgs[f.split('.')[-2]] = (width, height)
        # except:
        #     print('problem with', path)
        #     count += 1

    print(len(imgs.keys()))
    print('problems with', count, 'imgs')
    print(corrupted)
    # print(type(imgs.pop()))
    return imgs

# Removed some fields, and add height and width of picture for convenience
# ImageID,LabelID,LabelName,XMin,XMax,YMin,YMax,Width,Height
def collate_ann(bbox_csv, imgs, class_d, chosen_set, maxi):
    count = {}
    new_bbox_ann = []
    head = True
    with open(bbox_csv, newline='') as f:
        csvreader = csv.reader(f,delimiter=',')
        for row in csvreader:
            if head:
                head = False
                continue
            if row[0] in imgs and is_relevant_class(row[2], class_d, chosen_set) and not maxed(count, row[2], class_d, maxi):
                new_bbox_ann.append([imgs[row[0]][2], row[2], class_d[row[2]], row[4], row[5], row[6], \
                                    row[7], imgs[row[0]][0], imgs[row[0]][1]])

                if class_d[row[2]] in count:
                    count[class_d[row[2]]] += 1
                else:
                    count[class_d[row[2]]] = 1

    new_bbox_ann = sorted(new_bbox_ann, key=functools.cmp_to_key(cmp))
    print(len(new_bbox_ann))

    pp(count)

    return new_bbox_ann

def is_relevant_class(class_id, class_d, chosen_set):
    return class_id in class_d and class_d[class_id] in chosen_set

def maxed(count, class_id, class_d, maxi):
    if maxi is None:
        return False
    elif class_d[class_id] in count and count[class_d[class_id]] >= maxi:
        return True
    else:
        return False

def pp(count):
    print()
    for k in count.keys():
        print(k, ":", count[k])

def cmp(x, y):
    num_x = int (x[0].split('.')[0], 16) + 0x200
    num_y = int(y[0].split('.')[0], 16) + 0x200

    return num_x - num_y

def save(new_bbox_ann, new_csv):
    index = 1
    files = glob.glob(new_csv)
    s = new_csv.split('/')
    path = '/'.join(s[0:-1])
    name, ext = s[-1].split('.')

    while len(files) > 0:
        print(new_csv, 'exists')
        new_csv = name + '_' + str(index) + '.' + ext
        new_csv = os.path.join(path,new_csv)
        files = glob.glob(new_csv)
        index += 1

    print('saving to', new_csv)

    with open(new_csv, 'w') as f:
        csvwriter = csv.writer(f, delimiter=',')

        for elm in new_bbox_ann:
            csvwriter.writerow(elm)

def get_classes(classes_csv):
    d = {}
    with open(classes_csv, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')

        for row in csvreader:
            name = squeeze_lower(row[1])
            d[row[0]] = name

    return d

def squeeze_lower(name):
    return name.replace(' ', '').lower()

def get_chosen(chosen):
    c = set()
    with open(chosen, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')

        for row in csvreader:
            c.add(squeeze_lower(row[0]))
    return c

def get_bad(bad):
    if bad is None:
        return set()
    else:
        return set(f.name for f in os.scandir(bad) if f.is_file())

def main(bbox_csv, classes_csv, folder, chosen, new_csv, max, bad):
    class_d = get_classes(classes_csv)
    chosen_set = get_chosen(chosen)
    bad_imgs = get_bad(bad)
    imgs = get_imgs(folder, bad_imgs)
    new_bbox_ann = collate_ann(bbox_csv, imgs, class_d, chosen_set, max)
    save(new_bbox_ann, new_csv)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('bbox_csv', help='original bbox csv file')
    p.add_argument('classes_csv', help='classes csv file') 
    p.add_argument('folder', help='folder with the images')
    p.add_argument('chosen', help='csv file with chosen classes')
    p.add_argument('new_csv', help='collated bbox to save in')    
    p.add_argument('--max', '-m', type=int, default=None,
                    help='max number of objects for each class')
    p.add_argument('--bad', '-b', default=None,
                    help='folder with bad images to be excluded')

    args = p.parse_args()

    main(args.bbox_csv, args.classes_csv, args.folder, args.chosen, args.new_csv, args.max, args.bad)

 