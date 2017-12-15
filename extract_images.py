"""
Download images
"""

import sys
import time
import argparse
import signal
import threading

import os
import csv
import glob
# import urllib.request
import requests
import imghdr
from PIL import Image
from io import BytesIO
import shutil
import queue

FAILED = []

# adapted from https://github.com/beniz/openimages_downloader/blob/master/openimages_downloader.py
def download_image(url, timeout, retry, sleep, verbose=False):
    count = 0
    while True:
        try:
            req = urllib.request.urlopen(url, timeout=timeout)
            if req is None:
                raise Exception('Cannot open URL {0}'.format(url))
            
            content = req.read()
            req.close()
            break

        except urllib.request.URLError as e:
            if isinstance(e.reason, socket.gaierror):
                count += 1
                time.sleep(sleep)
                if count > retry:
                    if verbose:
                        sys.stderr.write('Error: too many retries on {0}\n'.format(url))
                    raise
            else:
                if verbose:
                    sys.stderr.write('Error: URLError {0}\n'.format(e))
                raise
        except Exception as e:
            if verbose:
                sys.stderr.write('Error: unknown during download: {0}\n'.format(e))
                
    return content

def imgtype2ext(typ):
    """Converts an image type given by imghdr.what() to a file extension."""
    if typ == 'jpeg':
        return 'jpg'

    if typ is None:
        raise Exception('Cannot detect image type')
    
    return typ

def download(url, timeout, retry, sleep, name, out_dir, verbose=False):
    try:
        content = download_image(url, timeout, retry, sleep, verbose=verbose)
        ext = imgtype2ext(imghdr.what('', content))
        im = Image.open(BytesIO(content))

        path = os.path.join(out_dir, '{0}.{1}'.format(name, ext))
        im.save(path, "JPEG")

    except Exception as e:
        raise

def download2(url, timeout, retry, sleep, name, out_dir, verbose=False):

    count = 0
    while True:
        try:
            res = requests.get(url, stream=True, timeout=timeout)
            path = os.path.join(out_dir, '{0}.{1}'.format(name, url.split('.')[-1])) 
        
            if res.status_code == 200:
                with open(path, 'wb') as out_file:
                    shutil.copyfileobj(res.raw, out_file)
                del res
                break
            else:
                res.raise_for_status()

        except requests.exceptions.Timeout as e:
            count += 1
            time.sleep(sleep)
            if count > retry:
                if verbose:
                    sys.stderr.write('Error: too many retries on {0}\n'.format(url))
                raise

        except requests.exceptions.HTTPError as e:
            if verbose:
                sys.stderr.write('Error: URL not found {0}\n'.format(url))
            raise

        except Exception as e:
            raise

def make_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def get_img_list(in_csv):
    img_list = []

    with open(in_csv,'r') as f:
        csvreader = csv.reader(f,delimiter=',')
        for row in csvreader:
            img_list.append(row[0])

    return img_list

# download all images
def download_openimages(in_csv,
                        imgs_csv,
                        out_dir, 
                        timeout=10, 
                        retry=10, 
                        num_jobs=1,
                        sleep_after_dl=0.2,
                        verbose=True,
                        offset=0,   
                        msg=10):

    make_directory(out_dir)

    img_list = get_img_list(in_csv)

    count_total = len(img_list) - offset

    # count_total = 0
    # with open(in_csv) as f:
    #     csvreader = csv.reader(f,delimiter=',')
    #     for row in csvreader:
    #         count_total += 1
    # count_total -= offset

    sys.stderr.write('Total: {0}\n'.format(count_total))

    num_jobs = max(num_jobs, 1)

    entries = queue.Queue(num_jobs*3)
    done = False

    counts_fail = [0 for i in range(num_jobs)]
    counts_success = [0 for i in range(num_jobs)]

    def producer():
        nonlocal done
        count = 0
        index = offset
        with open(imgs_csv) as f:
            head = False
            csvreader = csv.reader(f, delimiter=',')
            for row in csvreader:
                if not head: # skip first line
                    head = True
                    continue
                elif index >= len(img_list):
                    break
                elif count >= offset and row[0] == img_list[index]:
                    name = row[0]
                    url = row[2]
                    index += 1
                    entries.put((name, url), block=True)
                count += 1

        entries.join()
        done = True

    def consumer(i):
        nonlocal done
        while not done:
            try:
                name, url = entries.get(timeout=1)
            except:
                continue

            try:
                if name is None:
                    if verbose:
                        sys.stderr.write('Error: Invalid line: {0}\n'.format(line))
                    counts_fail[i] += 1
                    continue

                rpath = os.path.join(out_dir, '{0}.*'.format(name))
                lf = glob.glob(rpath)

                if len(lf) > 0:
                    sys.stdout.write("skipping: already have {0}\n".format(lf[0]))
                    counts_success[i] += 1
                    entries.task_done()
                    continue

                download2(url, timeout, retry, sleep_after_dl, name, out_dir, verbose=verbose)

                # im.thumbnail(img_size, Image.ANTIALIAS)
                
                counts_success[i] += 1
                time.sleep(sleep_after_dl)

            except Exception as e:
                counts_fail[i] += 1
                FAILED.append((name,url,e))
                if verbose:
                    sys.stderr.write('Error: {0} / {1}: {2}\n'.format(name, url, e))
            
            entries.task_done()

    def message_loop():
        nonlocal done
        if verbose:
            delim = '\n'
        else:
            delim = '\r'

        while not done:
            count_success = sum(counts_success)
            count = count_success + sum(counts_fail)
            rate_done = (offset + count) * 100.0 / (offset + count_total)
            if count == 0:
                rate_success = 0
            else:
                rate_success = count_success * 100.0 / count
            sys.stderr.write(
                '{0} / {1} ({2}%) done, {3} / {0} ({4}%) succeeded                    {5}'.format(
                    offset + count, offset + count_total, rate_done, count_success, rate_success, delim))

            time.sleep(msg)
        sys.stderr.write('done')

    producer_thread = threading.Thread(target=producer, daemon=True)
    consumer_threads = [threading.Thread(target=consumer, args=(i,), daemon=True) for i in range(num_jobs)]
    message_thread = threading.Thread(target=message_loop, daemon=True)

    producer_thread.start()
    for t in consumer_threads:
        t.start()
    message_thread.start()

    # while threading.active_count() > 0:
    #     time.sleep(0.1)
    producer_thread.join()
    for t in consumer_threads:
        t.join()
    message_thread.join()

    sys.stderr.write('\ndone\n')          
  
def signal_handler(signal, frame):
    print('User interrupt. Stopping program.')
    print(FAILED)
    sys.exit(0)

def crop_bbox():
    pass


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('in_csv', help='csv file with image indexes to download')
    p.add_argument('imgs_csv', help='OpenImages csv images file')
    p.add_argument('out_dir', help='Output directory')
    p.add_argument('--jobs', '-j', type=int, default=1,
                   help='Number of parallel threads to download')
    p.add_argument('--timeout', '-t', type=int, default=10,
                   help='Timeout per image in seconds')
    p.add_argument('--retry', '-r', type=int, default=10,
                   help='Max count of retry for each image')
    p.add_argument('--sleep', '-s', type=float, default=0.2,
                   help='Sleep after download each image in second')
    p.add_argument('--verbose', '-v', action='store_true',
                   help='Enable verbose messages')
    p.add_argument('--offset', '-o', type=int, default=0,
                   help='Offset to where to start in the csv images file')
    p.add_argument('--msg', '-m', type=int, default=10,
                   help='Logging message every x seconds')
    args = p.parse_args()

    signal.signal(signal.SIGINT, signal_handler)

    download_openimages(args.in_csv, args.imgs_csv, args.out_dir,
                        timeout=args.timeout, retry=args.retry,
                        num_jobs=args.jobs, verbose=args.verbose, 
                        offset=args.offset, msg=args.msg, sleep_after_dl=args.sleep)