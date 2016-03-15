"""                                                                              
 Text-Machine Lab: MUTT  

 File Name : metrics.py
                                                                              
 Creation Date : 17-02-2016
                                                                              
 Created By : Renan Campos                                               
                                                                              
 Purpose : Script containing wrappers to use various MT metrics suites.

"""

import os
import sys

import commands
import re

METRICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'metrics')

#
# coco-caption
#
# Add modules to path to make importing easy here:
sys.path.append(os.path.join(METRICS_DIR, 'coco-caption'))

from pycocotools.coco import COCO
from pycocoevalcap.eval import COCOEvalCap

def coco(sent_a, sent_b, ref_5, ref_10, ref_20, corruption, f):
  """
    Runs the coco evaluation for each ref list and prints to the output file.
  """

  print >>f, "Corruption:", corruption
  print >>f, "#  References:     5   |    10   |    20"
  print >>f, "-----------------------+---------+---------"
  coco_results= [coco_accuracy(sent_a, sent_b, ref_5),
                 coco_accuracy(sent_a, sent_b, ref_10),
                 coco_accuracy(sent_a, sent_b, ref_20)]
  for metric in coco_results[0].keys():
    print >>f, "   %10s: %0.5f | %0.5f | %0.5f" % (metric, 
                                               coco_results[0][metric], 
                                               coco_results[1][metric], 
                                               coco_results[2][metric])
  print >>f, "-----------------------+---------+---------"
  print >>f, ""

def coco_accuracy(sent_a, sent_b, refs):
  """
    For the coco-caption metric 
    to extract the accuracy of all the metrics that were run.
  """
  res   = {}
  total = 0.0
  for a, b in zip(coco_eval(sent_a, refs), coco_eval(sent_b, refs)):
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

def coco_eval(candidates_file, references_file):
  """
    Given the candidates and references, the coco-caption module is 
    used to calculate various metrics. Returns a list of dictionaries containing:
    -BLEU
    -ROUGE
    -METEOR
    -CIDEr
  """

  # This is used to suppress the output of coco-eval:
  old_stdout = sys.stdout
  sys.stdout = open(os.devnull, "w")
  try:
    # Derived from example code in coco-captions repo
    coco    = COCO( references_file )
    cocoRes = coco.loadRes( candidates_file )
  
    cocoEval = COCOEvalCap(coco, cocoRes)

    cocoEval.evaluate()
  finally:
    # Change back to standard output
    sys.stdout.close()
    sys.stdout = old_stdout
  
  return cocoEval.evalImgs

#
# badger
#
def badger(sent_a, sent_b, ref_5, ref_10, ref_20, corruption, f):
  """
    Runs the badger evaluation for each ref list and prints to the output file.
  """

  print >>f, "Corruption:", corruption
  print >>f, "#  References:     5   |    10   |    20"
  print >>f, "-----------------------+---------+---------"
  print >>f, "   %10s: %0.5f | %0.5f | %0.5f" % ('badger',
                                                 badger_accuracy(sent_a, sent_b, ref_5), 
                                                 badger_accuracy(sent_a, sent_b, ref_10), 
                                                 badger_accuracy(sent_a, sent_b, ref_20)) 
  print >>f, "-----------------------+---------+---------"
  print >>f, ""

def badger_accuracy(sent_a, sent_b, refs):
  """
    Calculates the accuracy for the badger metric.
  """

  count = 0.0
  total = 0.0
  for a,b in zip(badger_eval(sent_a, refs), badger_eval(sent_b, refs)):
    if a > b:
      count += 1
    total += 1
  return count / total


def badger_eval(cand_file, ref_file):
  """
    Runs badger and extracts a list of scores.
  """
  out_dir = os.path.join(METRICS_DIR, 'badger', 'willie', 'out')
  exec_file = os.path.join(METRICS_DIR, 'badger', 'badger.jar')
  cmd = 'java -jar %s -r %s -t %s -o %s' % (exec_file, ref_file,cand_file,out_dir)
  status,output = commands.getstatusoutput(cmd)
  
  # assert badger worked correctly
  check = 'Scoring \w+ doc example_set::doc1 seg (\d+) (\d+) references found'
  matches = re.findall(check, output)
#  for match in matches:
#      if match[1] != '1':
#          ind = int(match[0])
#          print ind
#          exit()


  # parse results
  metric_scores = []
  res_file = '%s/SmithWatermanGotohWindowedAffine/Badger-seg.scr' % out_dir
  with open(res_file, 'r') as f:
      for line in f.readlines():
          toks = line.strip().split('\t')
          score = float(toks[-1])
          metric_scores.append(score)

  return metric_scores
#
# nist
#
def nist(sent_a, sent_b, ref_5, ref_10, ref_20, corruption, f):
  """
    Runs the badger evaluation for each ref list and prints to the output file.
  """

  print >>f, "Corruption:", corruption
  print >>f, "#  References:     5   |    10   |    20"
  print >>f, "-----------------------+---------+---------"
  print >>f, "   %10s: %0.5f | %0.5f | %0.5f" % ('nist',
                                                 badger_accuracy(sent_a, sent_b, ref_5), 
                                                 badger_accuracy(sent_a, sent_b, ref_10), 
                                                 badger_accuracy(sent_a, sent_b, ref_20)) 
  print >>f, "-----------------------+---------+---------"
  print >>f, ""

def nist_accuracy(sent_a, sent_b, refs):
  """
    Calculates the accuracy for the nist metric.
  """

  count = 0.0
  total = 0.0
  for a,b in zip(nist_eval(sent_a, refs), badger_eval(sent_b, refs)):
    if a > b:
      count += 1
    total += 1
  return count / total


def nist_eval(cand_file, ref_file):
  """
    Runs nist and extracts a list of scores for bleu and nist.
  """

  exec_file = os.path.join(METRICS_DIR, 'nist', 'mteval-v13a.pl')
  # invoke nist
  cmd = 'perl mteval-v13a.pl -r %s -s %s -t %s' % (exec_file, ref_file,src_file,tst_file)
  status,output = commands.getstatusoutput(cmd)

  # parse results
  sections = output.split('# ' + '-'*72)

  nist_reg = 'NIST:  (\d\.\d+)   (\d\.\d+)   (\d\.\d+)   (\d\.\d+)   (\d\.\d+)'
  nist_match = re.search(nist_reg, sections[1])
  nist_scores = map(float, nist_match.groups())

  bleu_reg = 'BLEU:  (\d\.\d+)   (\d\.\d+)   (\d\.\d+)   (\d\.\d+)   (\d\.\d+)'
  bleu_match = re.search(bleu_reg, sections[1])
  bleu_scores = map(float, bleu_match.groups())

  return nist_scores, bleu_scores

#
# terp
#
def terp(sent_a, sent_b, ref_5, ref_10, ref_20, corruption, f):
  """
    Runs the terp evaluation for each ref list and prints to the output file.
  """

  print >>f, "Corruption:", corruption
  print >>f, "#  References:     5   |    10   |    20"
  print >>f, "-----------------------+---------+---------"
  print >>f, "   %10s: %0.5f | %0.5f | %0.5f" % ('terp',
                                                 terp_accuracy(sent_a, sent_b, ref_5), 
                                                 terp_accuracy(sent_a, sent_b, ref_10), 
                                                 terp_accuracy(sent_a, sent_b, ref_20)) 
  print >>f, "-----------------------+---------+---------"
  print >>f, ""

def terp_accuracy(sent_a, sent_b, refs):
  """
    Calculates the accuracy for the nist metric.
  """

  count = 0.0
  total = 0.0
  for a,b in zip(terp_eval(sent_a, refs), terp_eval(sent_b, refs)):
    # note: terp gives a higher score to the worst candidate
    print "a:", a
    print "b:", b
    if a < b:
      count += 1
    total += 1
  return count / total


def terp_eval(cand_file, ref_file):
  """
    Runs terp and extracts a list of scores for bleu and nist.
  """

  param_file = os.path.join(METRICS_DIR, 'terp', 'willie', 'params.param')
  res_file   = cand_file
  phrase_db = os.path.join(METRICS_DIR, 'terp', 'data', 'phrases.db')
  with open(param_file, 'w') as f:
      print >>f, 'Phrase Database (filename)               : ' + phrase_db
      print >>f, 'Reference File (filename)                : ' + ref_file
      print >>f, 'Hypothesis File (filename)               : ' + cand_file
      print >>f, 'Output Formats (list)                    : param nist pra'
      print >>f, 'Output Prefix (filename)                 : ' + res_file

  terpa = os.path.join(METRICS_DIR, 'terp', 'bin', 'terpa')

  # invoke terp
  cmd = '%s %s' % (terpa,param_file)
  status,output = commands.getstatusoutput(cmd)

  # parse results
  scores = list()
  with open(res_file + '.seg.scr', 'r') as f:
    for line in f:
      scores.append(float(line.split()[3]))

  return scores


