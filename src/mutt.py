"""                                                                              
 Text-Machine Lab: MUTT 

 File Name : mutt.py
                                                                              
 Creation Date : 17-02-2016
                                                                              
 Created By : Renan Campos                                       
                                                                              
 Purpose : Main script for machine translation Metrics Unit TesTing

"""

import os
import json

from gather_corruptions import gather_corruptions
from gather_references import gather_references

import metrics

TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
RES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')

def main():
  """
   Gathers the corruptions, then for each corruption type:
     -Create reference files containing 5, 10, 20 references per sentence
     -Create a json file containing the sentence A's
     -Create a json file containing the sentence B's
   Runs various machine translation metrics, and calculates the accuracy:
     score is based on whether sentence A received a higher score than B.
  """

  print "Gathering corruptions..."
  corruptions = gather_corruptions()

  for corruption, entries in corruptions.items():
    # If these files already exist, skip the corruption gathering and go to metrics testing.
    if os.path.isfile(os.path.join(TMP_DIR, corruption + '_a.json'))   and \
       os.path.isfile(os.path.join(TMP_DIR, corruption + '_b.json'))   and \
       os.path.isfile(os.path.join(TMP_DIR, corruption + '_r5.json'))  and \
       os.path.isfile(os.path.join(TMP_DIR, corruption + '_r10.json')) and \
       os.path.isfile(os.path.join(TMP_DIR, corruption + '_r20.json')):
       print "Reference files for", corruption, "found. Clear tmp to redo reference gathering." 
       continue

    # Open files
    f_sent_a  = open(os.path.join(TMP_DIR, corruption + '_a.json'),   'w') 
    f_sent_b  = open(os.path.join(TMP_DIR, corruption + '_b.json'),   'w')
    f_refs_5  = open(os.path.join(TMP_DIR, corruption + '_r5.json'),  'w')
    f_refs_10 = open(os.path.join(TMP_DIR, corruption + '_r10.json'), 'w')
    f_refs_20 = open(os.path.join(TMP_DIR, corruption + '_r20.json'), 'w')

    f_sent_a.write('[')
    f_sent_b.write('[')
    f_refs_5.write( '{\"type\":\"captions\", \"info\":{}, \"licenses\":[], \"type\":\"captions\", \"annotations\":[')
    f_refs_10.write('{\"type\":\"captions\", \"info\":{}, \"licenses\":[], \"type\":\"captions\", \"annotations\":[')
    f_refs_20.write('{\"type\":\"captions\", \"info\":{}, \"licenses\":[], \"type\":\"captions\", \"annotations\":[')

    print corruption, len(entries)
    print "Gathering references for each entry in", corruption, "..."
    
    ref_id_list  = [list(), list(), list()]
    ref_id_count = [0,0,0]
    hash_id = 0
    comma =""

    for entry in entries: 

      cluster, refs = gather_references(entry[1], entry[0])

      # We only want entries with 20+ references
      if len(refs) >= 20:

        f_sent_a.write(comma)
        f_sent_b.write(comma)
        f_sent_a.write(json.dumps({'image_id':hash_id, 'caption':unicode(entry[2], errors='ignore')}))
        f_sent_b.write(json.dumps({'image_id':hash_id, 'caption':unicode(entry[3], errors='ignore')}))
        
        f_refs_5.write(comma)
        f_refs_10.write(comma)
        f_refs_20.write(comma)
        
        comma = ""
        for ref in refs[:5]:
          f_refs_5.write(comma)
          f_refs_5.write(json.dumps({'image_id':hash_id, 'id': hash_id, 'caption':unicode(ref, errors='ignore')}))
          
          ref_id_list[0].append({'id': hash_id})
          
          comma = ",\n"
        comma = ""
        for ref in refs[:10]:
          f_refs_10.write(comma)
          f_refs_10.write(json.dumps({'image_id':hash_id, 'id': hash_id, 'caption':unicode(ref, errors='ignore')}))
          
          ref_id_list[1].append({'id': hash_id})
          
          comma = ",\n"
        comma = ""
        for ref in refs[:20]:
          f_refs_20.write(comma)
          f_refs_20.write(json.dumps({'image_id':hash_id, 'id': hash_id, 'caption':unicode(ref, errors='ignore')}))
          
          ref_id_list[2].append({'id': hash_id})
          
          comma = ",\n"
        comma = ",\n"
        hash_id += 1
 
        # dataset                 0
        # original sentence       1
        # sentence A              2
        # sentence B (corruption) 3
        # score                   4
    f_sent_a.write(']')
    f_sent_b.write(']')
    f_refs_5.write( '], \"images\":' + json.dumps(ref_id_list[0]) + '}')
    f_refs_10.write('], \"images\":' + json.dumps(ref_id_list[1]) + '}')
    f_refs_20.write('], \"images\":' + json.dumps(ref_id_list[2]) + '}')
 
    f_sent_a.close()
    f_sent_b.close()
    f_refs_5.close()
    f_refs_10.close()
    f_refs_20.close()

  # Run metrics tests
  for corruption in corruptions.keys():
    sent_a  = os.path.join(TMP_DIR, corruption + '_a.json') 
    sent_b  = os.path.join(TMP_DIR, corruption + '_b.json')
    refs_5  = os.path.join(TMP_DIR, corruption + '_r5.json')
    refs_10 = os.path.join(TMP_DIR, corruption + '_r10.json')
    refs_20 = os.path.join(TMP_DIR, corruption + '_r20.json')

    with open(os.path.join(RES_DIR, 'coco.txt'), 'a') as f:
      print >>f, "Corruption:", corruption
      print >>f, "#  References:     5   |    10   |    20"
      print >>f, "-----------------------+---------+---------"
      coco_results= [coco_accuracy(sent_a, sent_b, refs_5,  metrics.coco),
                     coco_accuracy(sent_a, sent_b, refs_10, metrics.coco),
                     coco_accuracy(sent_a, sent_b, refs_20, metrics.coco)]
      for metric in coco_results[0].keys():
        print >>f, "   %10s: %0.5f | %0.5f | %0.5f" % (metric, 
                                                   coco_results[0][metric], 
                                                   coco_results[1][metric], 
                                                   coco_results[2][metric])
      print >>f, "-----------------------+---------+---------"
      print >>f, ""

def coco_accuracy(sent_a, sent_b, refs, eval_func):
  """
    A special function for the coco-caption metric 
    to extract the accuracy of all the metrics that were run.
  """
  res   = {}
  total = 0.0
  for a, b in zip(eval_func(sent_a, refs), eval_func(sent_b, refs)):
    for metric in a.keys():
      if a[metric] > b[metric]:
        try:
          res[metric] += 1
        except:
          res[metric]  = 1
    total += 1

  for metric in res.keys():
    res[metric] /= total
  return res


def calculate_accuracy(sent_a, sent_b, refs, eval_func):
  total = 0
  right = 0.0
  for a, b in zip(eval_func(sent_a, refs), eval_func(sent_b, refs)):
    if a > b:
      right += 1
    total += 1
  return right/total

if __name__ == '__main__':
  main()
