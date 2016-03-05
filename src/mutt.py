"""                                                                              
 Text-Machine Lab: MUTT 

 File Name : mutt.py
                                                                              
 Creation Date : 17-02-2016
                                                                              
 Created By : Renan Campos                                       
                                                                              
 Purpose : Main script for machine translation Metrics Unit TesTing

"""

import os

from gather_corruptions import gather_corruptions
from gather_references import gather_references

import metrics
import writer

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
    if writer.check_json(corruption):
       print "JSON files for", corruption, "found. Clear tmp to redo reference gathering." 
       continue

    # Open files
    json_files = writer.init_json(corruption)

    print corruption, len(entries)
    print "Gathering references for each entry in", corruption, "..."

    for entry in entries: 

      cluster, refs = gather_references(entry[1], entry[0])

      # We only want entries with 20+ references
      if len(refs) >= 20:
        writer.write_json(json_files, entry, refs)

    # Close files
    writer.close_json(json_files)

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
