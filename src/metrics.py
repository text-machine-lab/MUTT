"""                                                                              
 Text-Machine Lab: MUTT  

 File Name : metrics.py
                                                                              
 Creation Date : 17-02-2016
                                                                              
 Created By : Renan Campos                                               
                                                                              
 Purpose : Script containing wrappers to use various MT metrics suites.

"""

import os
import sys

METRICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'metrics')

# Add modules to path to make importing easy here:
sys.path.append(os.path.join(METRICS_DIR, 'coco-caption'))

from pycocotools.coco import COCO
from pycocoevalcap.eval import COCOEvalCap

def coco(candidates_file, references_file):
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
  
  #TODO: Only return a specific metric

  return cocoEval.evalImgs
