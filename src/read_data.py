"""                                                                              
 Text-Machine Lab: MUTT  

 File Name :                                                                  
                                                                              
 Creation Date : 17-02-2016
                                                                              
 Created By : Willie Boag
              Renan Campos

 Purpose : Read from the flickr, msr, and sick datasets
           for data in (flickr, msr):
             data         = {cluster : references}
             data_reverse = {references : cluster}
           sick is a list of entries (each entry is a dictionary of attributes)
"""


import os
import sys
from collections import defaultdict

################################################################################
# FLICKR DATA                                                                  #
################################################################################

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

################################################################################
# MSR DATA                                                                     #
################################################################################

MSR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'msr', 'MSRVideoCorpus.csv')

def read_msr_file(pfile):
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

msr = read_msr_file(MSR_FILE)

msr_reverse = defaultdict(list)
for imageID,refs in msr.items():
    for ref in refs:
        #if ref == 'Three young men run, jump, and kick off of a Coke machine.':
        #    print ref
        #    exit()
        msr_reverse[ref].append(imageID)

msr         = dict(msr        )
msr_reverse = dict(msr_reverse)

################################################################################
# SICK DATA                                                                    #
################################################################################

SICK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sick', 'SICK.txt')

def read_sick_file(filename):
    data = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        labels = lines[0].strip().split('\t')
        for line in lines[1:]:
            entry_items = {}
            for entry,label in zip(line.strip().split('\t'),labels):
                entry_items[label] = entry
            rel_score = 'relatedness_score'
            entry_items[rel_score] = float(entry_items[rel_score])
            data.append(entry_items)
    return data


# READ THE DATA
sick = read_sick_file(SICK_FILE)

