"""                                                                              
 Text-Machine Lab: MUT 

 File Name : gather_refs.py
                                                                              
 Creation Date : 12-02-2016
                                                                              
 Created By : Willie Boag
              Renan Campos
                                                                              
 Purpose : Wrappers to map a sentence in sick to its original dataset, 
           and to extract all the reference sentences to that original sentence.

"""

from read_data  import sick, msr, msr_reverse, flickr, flickr_reverse

from nltk.tokenize import word_tokenize
from collections import defaultdict

def get_cluster(s1, s2, dataset):
  """
    Return "cluster" (i.e. video or picture name) that the sentences came from
  """

  if dataset == 'FLICKR':
    data_reverse = flickr_reverse
    sent_1 = ' '.join(word_tokenize(s1))
    sent_2 = ' '.join(word_tokenize(s2))
  else:
    data_reverse = msr_reverse
    sent_1 = s1
    sent_2 = s2

  if s1 not in data_reverse:
    return None
  if s2 not in data_reverse:
    return None


  candidates_1 = set(data_reverse[s1])
  candidates_2 = set(data_reverse[s2])
  
  if len(candidates_1 & candidates_2) > 0:
    return list(candidates_1 & candidates_2)[0]



def get_refs(sent, dataset):
  """
    For the given sentence of the given dataset, 
    return a list of references and id.
  """

  if dataset == 'FLICKR':

    key = closest_match(sent, dataset)
    
    clusters = flickr_reverse[key]
    cluster = clusters[0]

    refs = flickr[cluster]

  elif dataset == 'SEMEVAL':
    
    key = closest_match(sent, dataset)
    
    clusters = msr_reverse[key]
    cluster = clusters[0]
    refs = msr[cluster]

  else:
    raise Exception('Unknown dataset %s' % dataset)

  return cluster, refs


def closest_match(sent, dataset):
  """
    Using edit distance, find the closest key match to the given sentence.
  """

  min_dist = float('inf')
  match = None
  
  if dataset == 'FLICKR':
    data_reverse = flickr_reverse
  elif dataset == 'SEMEVAL':
    data_reverse = msr_reverse
  else:
    raise Exception('unknown dataset %s' % dataset)

  # take what you can get
  if sent in data_reverse:
      return sent

  bins = defaultdict(list)
  for s in data_reverse.keys():
    # Token-based edit distance
    dist = edit_distance(sent.split(), s.split())
    bins[dist].append(s)

  lowest = min(bins.keys())

  for s in bins[lowest]:
    dist = edit_distance(sent, s)

    # guaranteed okay
    if dist == 0:
      return s

    if dist < min_dist:
      min_dist = dist
      match = s

  assert match != None, 'no match found for %s' % sent

  return match



def edit_distance(s1, s2):

  m=len(s1)+1
  n=len(s2)+1

  tbl = {}
  for i in range(m): tbl[i,0]=i
  for j in range(n): tbl[0,j]=j
  for i in range(1, m):
    for j in range(1, n):
      cost = 0 if s1[i-1] == s2[j-1] else 1
      tbl[i,j] = min(tbl[i, j-1]+1, tbl[i-1, j]+1, tbl[i-1, j-1]+cost)

  return tbl[i,j]

def main():

  # build lookup table
  orig_to_cluster = {}

  for entry in sick:
    #print entry
    #print '\n\n\n'

    a = entry['sentence_A']
    a_orig = entry['sentence_A_original']
    a_data = entry['sentence_A_dataset']

    b = entry['sentence_B']
    b_orig = entry['sentence_B_original']
    b_data = entry['sentence_B_dataset']

    # filter out obvious negative examples
    if a_data != b_data:
      continue

    cluster = get_cluster(a_orig, b_orig, a_data)

    if cluster:
      print a_data
      print cluster
      print a_orig
      print b_orig
      print

    cluster, refs = get_refs(a_orig, a_data)

    print '\tcluster: ', cluster
    for ref in refs:
      print '\t\t', ref
    print '\n\n\n'


if __name__ == '__main__':
    main()
