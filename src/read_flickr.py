"""                                                                              
 Text-Machine Lab: MUT 

 File Name : read_flickr.py
                                                                              
 Creation Date : 12-02-2016
                                                                              
 Created By : Willie Boag
                                                                              
 Purpose : Reads the flickr dataset and stores it as a dictionary.
           flickr         = { cluster : references }
           flickr_reverse = { reference : cluster }

"""

import os
from collections import defaultdict


FLICKR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'flickr', 'Flickr8k.token.txt')


def read_flickr_file(filename):
    data = defaultdict(list)
    with open(filename, 'r') as f:
        for line in f.readlines():
            toks = line.strip().split()
            imageID,refID = toks[0].split('#')
            ref = ' '.join(toks[1:]).lower()
            data[imageID].append(ref)
    return data



# READ THE DATA
flickr = read_flickr_file(FLICKR_FILE)

# note, duplicate sentences have ambiguous reference sets
flickr_reverse = defaultdict(list)
for imageID,refs in flickr.items():
    for ref in refs:
        #assert ref not in flickr_reverse, ref
        flickr_reverse[ref].append(imageID)

flickr         = dict(flickr        )
flickr_reverse = dict(flickr_reverse)


def main():

    # Rank data
    for imageID,refs in flickr.items():
        print imageID
        for ref in refs:
            print '\t', ref
        print



if __name__ == '__main__':
    main()

