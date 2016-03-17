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

import generate_corruptions as g_c

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

  if not g_c.check_generated():
    g_files = g_c.init_generate_corruptions()
    gen = True
  else:
    print "Generated corruption files already created. clear tmp to redo reference gathering."
    gen = False
  for corruption, entries in corruptions.items():
    # If these files already exist, skip the corruption gathering and go to metrics testing.
    if writer.check_json(corruption) and writer.check_xml(corruption):
       print "Files for", corruption, "found. Clear tmp to redo reference gathering." 
       continue

    # Open files
    json_files = writer.init_json(corruption)
    xml_files  = writer.init_xml(corruption)

    print corruption, len(entries)
    print "Gathering references for each entry in", corruption, "..."

    count = 0
    for entry in entries: 
    
      cluster, refs = gather_references(entry[1], entry[0])

      # We only want entries with 20+ references
      if len(refs) >= 20:
        count += 1
        writer.write_json(json_files, entry, refs)
        writer.write_xml(xml_files, entry, refs)

        if gen:
          g_c.generate_corruptions(g_files, entry, refs)

    # Close files
    writer.close_json(json_files)
    writer.close_xml(xml_files)
    print "Corruption: %s, Count: %d" % (corruption, count)

  if gen:
    g_c.close_generated_files(g_files)
  
  # Run metrics tests
  coco_file = open(os.path.join(RES_DIR, 'coco.txt'), 'w')
  badger_file = open(os.path.join(RES_DIR, 'badger.txt'), 'w')
  terp_file = open(os.path.join(RES_DIR, 'terp.txt'), 'w')
  for corruption in (corruptions.keys() + g_c.corruptions.keys()):
    metrics.coco(*writer.files_json(corruption), corruption=corruption, f=coco_file)
    metrics.badger(*writer.files_xml(corruption), corruption=corruption, f=badger_file)
    metrics.terp(*writer.files_xml(corruption), corruption=corruption, f=terp_file)
  terp_file.close()
  badger_file.close()
  coco_file.close()


if __name__ == '__main__':
  main()
