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

TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')

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
    comma =""

    for entry in entries: 
      
      cluster, refs = gather_references(entry[1], entry[0])

      # We only want entries with 20+ references
      if len(refs) >= 20:
        f_sent_a.write(comma)
        f_sent_b.write(comma)
        f_sent_a.write(json.dumps({'image_id':hash(cluster), 'caption':entry[2]}))
        f_sent_b.write(json.dumps({'image_id':hash(cluster), 'caption':entry[3]}))
        comma = ""
        for ref in refs[:5]:
          f_refs_5.write(comma)
          #f_refs_5.write(json.dumps({'image_id':hash(cluster), 'id': ref_id_count[0], 'caption':ref}))
          f_refs_5.write(json.dumps({'image_id':hash(cluster), 'id': hash(cluster), 'caption':ref}))
          
          ref_id_list[0].append({'id': hash(cluster)})
          #ref_id_list[0].append({'id': ref_id_count[0]})
          #ref_id_count[0] += 1
          
          comma = ","
        comma = ""
        for ref in refs[:10]:
          f_refs_10.write(comma)
          #f_refs_10.write(json.dumps({'image_id':hash(cluster), 'id': ref_id_count[1], 'caption':ref}))
          f_refs_10.write(json.dumps({'image_id':hash(cluster), 'id': hash(cluster), 'caption':ref}))
          
          ref_id_list[1].append({'id': hash(cluster)})
          #ref_id_list[1].append({'id': ref_id_count[1]})
          #ref_id_count[1] += 1
          
          comma = ","
        comma = ""
        for ref in refs[:20]:
          f_refs_20.write(comma)
         #f_refs_20.write(json.dumps({'image_id':hash(cluster), 'id': ref_id_count[2], 'caption':ref}))
          f_refs_20.write(json.dumps({'image_id':hash(cluster), 'id': hash(cluster), 'caption':ref}))
          
          ref_id_list[2].append({'id': hash(cluster)})
          #ref_id_list[2].append({'id': ref_id_count[2]})
          #ref_id_count[2] += 1
          
          comma = ","
        comma = ","
 
        break
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

if __name__ == '__main__':
  main()
