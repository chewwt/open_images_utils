import csv
import argparse

def collate(bbox_csv, relevant):
    bbox_imgs = []

    head = True
    with open(bbox_csv, newline='') as f:
        csvreader = csv.reader(f,delimiter=',')
        for row in csvreader:
            if head:
                head = False
                continue
            if (len(bbox_imgs) == 0 or row[0] != bbox_imgs[-1]) and \
              row[2] in relevant:
               bbox_imgs.append(row[0])

    bbox_imgs = sorted(bbox_imgs)

    print(len(bbox_imgs))
    return bbox_imgs

def get_classes(csv_c, csv_r):
    classes = {}
    relevant = set()

    with open(csv_c) as f:
        csvreader = csv.reader(f,delimiter=',')
        for row in csvreader:
            classes[row[1]] = row[0]

    with open(csv_r) as f:
        csvreader = csv.reader(f,delimiter=',')
        for row in csvreader:
            print(row[0], classes[row[0]])
            relevant.add(classes[row[0]])

    return relevant

def get_urls(imgs, img_csv):
    save = []
    # space = 0.0

    head = False
                
    with open(img_csv, 'r') as img_f:
        csvreader = csv.reader(img_f, delimiter=',')
        for row in csvreader:
            if not head: # skip first line
                head = True
                continue
            if row[0] in imgs:
                save.append((row[0], row[2], row[8]))
            #     space += float(row[8]) / (2**20)
            # else:
            #     continue
            # if len(save) % 50 == 0:
            #     print(space)


    # print(space)

    return save

def save_imgs(imgs, img_csv, out_csv):

    if out_csv is None:
        return

    # save = get_urls(imgs, img_csv)

    with open(out_csv, 'w', newline='') as out_f:
        csvwriter = csv.writer(out_f, delimiter=',')

        for elm in imgs:
            csvwriter.writerow([elm])

    print("images id saved to", out_csv)

def main(bbox_csv, img_csv, classes_csv, relevant_csv, out_csv):
    relevant = get_classes(classes_csv, relevant_csv)
    imgs = collate(bbox_csv, relevant)
    save_imgs(imgs, img_csv, out_csv)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('bbox_csv', help='OpenImages csv bounding box annotations file')
    p.add_argument('img_csv', help='OpenImages csv image url file')
    p.add_argument('classes_csv', help='csv file with classes and id')
    p.add_argument('relevant_csv', help='csv file with relevant classes')
    p.add_argument('--save', '-s', default=None, help='csv file with images to download')

    args = p.parse_args()
    main(args.bbox_csv, args.img_csv, args.classes_csv, args.relevant_csv, args.save)