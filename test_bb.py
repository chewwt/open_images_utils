import csv
import argparse
import cv2
import os

def parse_csv(ann_csv):
    with open(ann_csv, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')
        objs = []
        # first = True
        count = 0
        img = None

        for row in csvreader:
            # if first:
            #     img = row[0]
            #     w = row[7]
            #     h = row[8]
            #     first = False
            #     count += 1

            if row[0] != img:
                if count <= 4:
                    img = row[0]
                    w = row[7]
                    h = row[8]
                    count += 1
                    objs = []
                else:
                    break

            class_name = row[2]

            xmin = int(float(row[3]) * float(w))
            xmax = int(float(row[4]) * float(w))
            ymin = int(float(row[5]) * float(h))
            ymax = int(float(row[6]) * float(h))
            
            objs.append([class_name, xmin, ymin, xmax, ymax])

    print(h, w)
    return img, objs

def draw(img, objs, folder):
    path = os.path.join(folder,'{0}'.format(img))
    img = cv2.imread(path)
    h, w, _ = img.shape
    print(h, w)
    for obj in objs:
        cv2.rectangle(img, (obj[1], obj[2]), (obj[3], obj[4]), (0,255,0), 2)
        cv2.putText(img, obj[0], (obj[1], obj[2]-5), 0, 0.3, (0,255,0))

    print(objs)
    factor = 2
    img = cv2.resize(img, (int(w/factor), int(h/factor))) 
    cv2.imshow("bbox", img)
    cv2.waitKey()
    cv2.destroyAllWindows()

# draw boxes for 1st image
def main(ann_csv, folder):
    img, objs = parse_csv(ann_csv)
    draw(img, objs, folder)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('ann_csv', help='bbox csv file')
    p.add_argument('folder', help='folder with the images')   

    args = p.parse_args()

    main(args.ann_csv, args.folder)
