"""
Plot a histogram according to the confidence level, to see where to set threshold
"""

import numpy as np
import json
import argparse
import os
import glob
import matplotlib.pyplot as plt

def get_hier(out_path):
    files = os.path.join(out_path, '*.json')
    files = glob.glob(files)

    histo = []

    for f in files:
        # name = f.split('/')[-1]
        # name = name.split('.')[0]
        # f_names.append(name)

        with open(f, 'r') as j:
            data = json.load(j)
            # det[name] = {}
            for obj in data:
                histo.append(obj['confidence'])
                # if obj['confidence'] < confidence_thres:
                #     continue

                # if obj['label'] in det[name]:
                #     det[name][obj['label']].append([obj['topleft']['x'], 
                #         obj['bottomright']['x'], obj['topleft']['y'], obj['bottomright']['y']])
                # else:
                #     det[name].update({obj['label']: [[obj['topleft']['x'], 
                #         obj['bottomright']['x'], obj['topleft']['y'], obj['bottomright']['y']]]})

    return histo

def histogram(values):
    print(len(values), np.min(values))
    bins = np.linspace(0.0, 1.0, 100)
    plt.hist(values, bins)
    plt.show()

def main(out_path):
    values = get_hier(out_path) 
    histogram(values)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('out_path', help='folder of json results from darkflow')

    args = p.parse_args()

    main(args.out_path)
