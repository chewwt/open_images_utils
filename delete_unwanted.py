import time
import csv
import argparse
import os
import threading
import signal
import sys
import glob

def get_wanted(wanted_csv):
    wanted = []
    with open(wanted_csv, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')
        for row in csvreader:
            wanted.append(row[0])

    return wanted

def trim(wanted, img_csv, folder, offset, index_offset, msg_sleep):
    count = 0
    num = offset
    index = index_offset
    deleted_count = num - index_offset
    error_count = 0
    done = False

    def trimmer():
        nonlocal count
        nonlocal index
        nonlocal deleted_count
        nonlocal error_count
        nonlocal done
        nonlocal num
        head = True

        with open(img_csv, 'r') as f:
            csvreader = csv.reader(f, delimiter=',')
            for row in csvreader:
                if head: # skip first line
                    head = False
                    continue

                count += 1
                if count < offset:
                    continue

                num += 1
                if wanted[index] == row[0]:
                    index += 1
                    continue
                else:
                    try:
                        file = os.path.join(folder, '{0}.*'.format(row[0])) 

                        for img in glob.glob(file):
                            os.remove(img)
                            deleted_count += 1
                            # sys.stdout.write('Removed {0}\n'.format(img))

                    except OSError:
                        sys.stderr.write('Error removing {0}\n'.format(file))
                        error_count += 1

        done = True

    def messenger():

        while not done:
            try:
                del_percent = deleted_count * 100.0 / (num)
                err_percent = error_count * 100.0 / (num)
                kept_percent = index * 100.0 / (num)
            except ZeroDivisionError:
                del_percent = 0
                err_percent = 0
                kept_percent = 0

            sys.stdout.write(
                'At #{7}, {0} / {1} ({2}%) deleted, {3} / {1} ({4}%) error, {5} / {1} ({6}%) kept\n'.format(
                    deleted_count, num, del_percent, error_count, err_percent, index, kept_percent, num))

            time.sleep(msg_sleep)

        sys.stderr.write('done')

    trimmer_thread = threading.Thread(target=trimmer, daemon=True)
    messenger_thread = threading.Thread(target=messenger, daemon=True)

    trimmer_thread.start()
    messenger_thread.start()

    while threading.active_count() > 0:
        time.sleep(0.1)
    # producer_thread.join()
    # for t in consumer_threads:
    #     t.join()
    # message_thread.join()

    sys.stderr.write('\ndone\n') 

def main(wanted_csv, img_csv, folder, offset, index_offset, msg_sleep):
    wanted = get_wanted(wanted_csv)
    trim(wanted, img_csv, folder, offset, index_offset, msg_sleep)

def signal_handler(signal, frame):
    print('User interrupt. Stopping program.')
    sys.exit(0)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('wanted_csv', help='csv file with wanted images')
    p.add_argument('img_csv', help='OpenImages csv image url file')
    p.add_argument('folder', help='folder to trim')
    p.add_argument('--offset', '-o', type=int, default=0,
                   help='Offset to where to start in the csv images file')
    p.add_argument('--index', '-i', type=int, default=0,
                   help='Offset to where to start in the csv wanted images file')
    p.add_argument('--msg', '-m', type=int, default=5,
                   help='Interval between messages')

    args = p.parse_args()
    signal.signal(signal.SIGINT, signal_handler)

    main(args.wanted_csv, args.img_csv, args.folder, args.offset, args.index, args.msg)