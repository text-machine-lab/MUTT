"""                                                                              
 Text-Machine Lab: MUTT 

 File Name : gather_corruptions.py
                                                                              
 Creation Date : 12-02-2016
                                                                              
 Created By : Willie Boag
              Renan Campos
                                                                              
 Purpose : Reads through the SICK dataset and extracts corruptions.
           The corruptions are categorized and written to their own files.
"""

import os
import re
import random

from collections import defaultdict
from pattern.en import parse
from read_data import sick
from tools import edit_distance


CORR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'corruptions')

######################################
#  helpers
######################################

def is_passive(sent):
    return ('is being' in sent) or ('are being' in sent)


def is_negated_subj(sent):
    if 'There is no' in sent or 'There are no' in sent:
        return True
    return False


def is_negated_verb(sent):
    if ' is not ' in sent or ' are not ' in sent:
        return True
    return False


def one_word_diff(sent1, sent2):
  a_set = set(sent1.split())
  b_set = set(sent2.split())

  if (len(a_set) == len(b_set)):
    return len(a_set - b_set) == 1

  return False

def norm(sent):
    sent = sent.lower()
    sent = re.sub('[^A-Za-z0-9 ]', '', sent)
    sent = re.sub(' +', ' ', sent)
    sent = sent.strip()
    return sent


######################################
#  corruption predicates
######################################

def is_corruption_passive(entry):
    # TODO - also ensure discussing same thing

    if entry['relatedness_score'] < 3.5:
        return 0

    a = entry['sentence_A']
    b = entry['sentence_B']

    if is_passive(a) and not is_passive(b):
        return 1
    if is_passive(b) and not is_passive(a):
        return 2

    return 0



def is_corruption_negated_subj(entry):
    # TODO - also ensure discussing same thing (edit distance)
    a = entry['sentence_A']
    b = entry['sentence_B']
    if is_negated_subj(a) and not is_negated_subj(b):
        return 1
    if is_negated_subj(b) and not is_negated_subj(a):
        return 2
    return 0



def is_corruption_negated_verb(entry):
    # TODO - also ensure discussing same thing (edit distance)
    a = entry['sentence_A']
    b = entry['sentence_B']
    if is_negated_verb(a) and not is_negated_verb(b):
        return 1
    if is_negated_verb(b) and not is_negated_verb(a):
        return 2
    return 0



def is_corruption_shuffled(entry):
    a = entry['sentence_A']
    b = entry['sentence_B']
    
    if sorted(a.split()) == sorted(b.split()):
      norm_o = norm(entry['sentence_A_original'])

      if edit_distance(norm_o, norm(a)) > edit_distance(norm_o, norm(b)):
        return 1
      else:
        return 2

    return 0

def is_corruption_det_replace(entry):
    def normalize(sent):
        s = sent.lower().split()
        s = [ w for w in s if (w!='a' and w!='the') ]
        return s
    a = entry['sentence_A']
    b = entry['sentence_B']

    if normalize(a) == normalize(b):
      norm_o = norm(entry['sentence_A_original'])

      if edit_distance(norm_o, norm(a)) > edit_distance(norm_o, norm(b)):
        return 1
      else:
        return 2

    return 0



def are_near_synonyms(entry):
  a = entry['sentence_A']
  b = entry['sentence_B']

  # Are near synonyms but not qualifier replacement
  if one_word_diff(entry['sentence_A'], entry['sentence_B']):
    # S1S2 same set pair has a 94.2% chance of being labeled entailment
    if entry['entailment_label'] == 'ENTAILMENT' and not is_corruption_det_replace(entry):
      
      norm_o = norm(entry['sentence_A_original'])

      if edit_distance(norm_o, norm(a)) > edit_distance(norm_o, norm(b)):
        return 1
      else:
        return 2

  return 0


def are_sem_opposites(entry):
  a = entry['sentence_A']
  b = entry['sentence_B']

  # Are near synonyms but not qualifier replacement
  if one_word_diff(entry['sentence_A'], entry['sentence_B']):
    # S1S3 same set pairs only have a 0.9% chance of being labeled entailment
    if entry['entailment_label'] != 'ENTAILMENT' and not is_corruption_det_replace(entry):
      
      norm_o = norm(entry['sentence_A_original'])

      if edit_distance(norm_o, norm(a)) > edit_distance(norm_o, norm(b)):
        return 1
      else:
        return 2

  return 0

################################################################################
#  main                                                                        #
################################################################################

corruptions = { 
# Meaning altering
                'sem_opps':(are_sem_opposites, 'Replace words with semantic opposites'),
                'neg_subj': (is_corruption_negated_subj, 'negated subject') ,
                'neg_verb': (is_corruption_negated_verb, 'negated action') ,
                'shuffled': (is_corruption_shuffled, 're-order words') ,
# Meaning preserving
                'det_sub': (is_corruption_det_replace, 'replace DTs') ,
                'near_syms': (are_near_synonyms, 'synonyms/similar word replacement'),
                'passive': (is_corruption_passive, 'active to passive') ,
              }

def gather_corruptions():
    """
      Gathers the specified corruptions, and writes them to a file.
      Returns a dictionary {corruption : [entries]}
    """
    out = {}

    # filtered
    def same_orig(entry):
        return norm(entry['sentence_A_original']) == norm(entry['sentence_B_original'])

    filtered = filter(same_orig, sick)

    # for each corruption
    for corruption, (f_corr, description) in corruptions.items():
        out[corruption] = apply_corruption(filtered, corruption, f_corr, description)
   
    return out


def filter_corruptions(f_corr, entries):
    """
      Goes through each entry, and applies f_corr, a corruption predicate.
      If the predicate returns true, it adds the entry to the results.
    """

    filtered = []
    for entry in entries:
        e = f_corr(entry)
        if e == 0:
             continue

        dataset = entry['sentence_A_dataset']
        orig    = entry['sentence_A_original']
        score   = entry['relatedness_score']
        if e == 1:
            sent    = entry['sentence_B']
            corr    = entry['sentence_A']
        elif e == 2:
            sent    = entry['sentence_A']
            corr    = entry['sentence_B']

        filt = (dataset, orig, sent, corr, score)
        filtered.append(filt)
    return filtered



def apply_corruption(entries, corruption, f_corr, description):
    """ 
      Goes through enties finding the ones that match the desired corruption
      Creates a file for the corruption and outputs statistics about those found.
    """

    # build corruption filename
    outname = os.path.join(CORR_DIR, '%s.txt' % corruption)

    # filter for corruption (ensure format of (dataset,orig,sent,corr,score) )
    corrupted = filter_corruptions(f_corr, entries)

    scores = [ e[-1] for e in corrupted ]

    mean = sum(scores) / (len(scores) + 1e-10)
    variance = sum([(s-mean)**2 for s in scores]) / (len(scores) + 1e-10)
    stddev = variance ** 0.5

    with open(outname, 'w') as f:
        print >>f, corruption
        print >>f, description
        print >>f, ''

        print >>f, 'num:    ', len(corrupted)
        print >>f, 'mean:   ', mean
        print >>f, 'stddev: ', stddev
        print >>f, '\n'

        ranked = sorted(corrupted, key=lambda e:e[-1])
        
        for entry in ranked:
            dataset = entry[0]
            orig    = entry[1]
            sent    = entry[2]
            corr    = entry[3]
            score   = entry[4]
            print >>f, '\tdataset:    ', dataset
            print >>f, '\torig:       ', orig
            print >>f, '\tsent:       ', sent
            print >>f, '\tcorr:       ', corr
            print >>f, '\tscore:      ', score
    return ranked

if __name__ == '__main__':
    gather_corruptions()
