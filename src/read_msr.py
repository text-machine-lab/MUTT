"""                                                                              
 Text-Machine Lab: MUT 

 File Name : read_msr.py
                                                                              
 Creation Date : 12-02-2016
                                                                              
 Created By : Willie Boag                                               
                                                                              
 Purpose : Reads the msr dataset and stores the data as a dictionary.
           msr         = { cluster : references }
           msr_reverse = { reference : cluster }

"""

import os
import sys
from collections import defaultdict

MSR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'msr', 'MSRVideoCorpus.csv')

def read_data(pfile):
    # Parse file
    descriptions = defaultdict(lambda:[])
    with open(pfile, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            tokens = line.strip().split(',')
            if len(tokens) < 8: continue      # ill-formatted
            link_id  = tokens[0]
            start    = tokens[1]
            end      = tokens[2]
            video_id = '%s_%s_%s' % (link_id,start,end)
            language = tokens[6]
            description = ','.join(tokens[7:]).strip('"')
            if language.lower() == 'english':
                descriptions[video_id].append( description )
            elif language.lower == 'eng':
                print 'lower!!'
                print tokens
                exit()
    return descriptions


def display_data(descriptions):
    # look at data
    #for video_id,phrases in descriptions.items():
    for video_id,phrases in sorted(descriptions.items(), key=lambda t:len(t[1])):
        print generate_url(video_id), len(phrases)
        #for phrase in phrases:
        #    print '\t', phrase
        #    #print video_id, '\t', phrase
        print

def generate_url(video_id):
    return 'https://www.youtube.com/watch?v=' + video_id

msr = read_data(MSR_FILE)

msr_reverse = defaultdict(list)
for imageID,refs in msr.items():
    for ref in refs:
        #if ref == 'Three young men run, jump, and kick off of a Coke machine.':
        #    print ref
        #    exit()
        msr_reverse[ref].append(imageID)

msr         = dict(msr        )
msr_reverse = dict(msr_reverse)


def main():
    display_data(msr)
    pass


if __name__ == '__main__':
    main()
