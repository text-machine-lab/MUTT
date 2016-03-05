"""                                                                              
 Text-Machine Lab: MUTT 

 File Name : writer.py
                                                                              
 Creation Date : 02-03-2016
                                                                              
 Created By : Renan Campos                                               
                                                                              
 Purpose : This module writes the test data in various formats so that
           it can be properly consumed by particular metrics.

"""
import os

TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')

#
# JSON (for coco-captions)
#
import json

def check_json(corruption):
  """
    Checks to see if files have already been written.
  """
  return (os.path.isfile(os.path.join(TMP_DIR, corruption + '_a.json'))   and \
          os.path.isfile(os.path.join(TMP_DIR, corruption + '_b.json'))   and \
          os.path.isfile(os.path.join(TMP_DIR, corruption + '_r5.json'))  and \
          os.path.isfile(os.path.join(TMP_DIR, corruption + '_r10.json')) and \
          os.path.isfile(os.path.join(TMP_DIR, corruption + '_r20.json')))

def files_json():
  """
    Returns a list of the json files
  """
  return (os.path.join(TMP_DIR, corruption + '_a.json'), 
          os.path.join(TMP_DIR, corruption + '_b.json'),
          os.path.join(TMP_DIR, corruption + '_r5.json'),
          os.path.join(TMP_DIR, corruption + '_r10.json'),
          os.path.join(TMP_DIR, corruption + '_r20.json'))



def init_json(corruption):
  """
    Opens the json files for writting and writes initial data.
    Returns the file pointers.
  """
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

  # psuedo-static variables for write_json 
  close_json.ref_id_list = [list(), list(), list()]
  write_json.hash_id     = 0
  write_json.comma       = ""

  return f_sent_a, f_sent_b, f_refs_5, f_refs_10, f_refs_20

def write_json(files, entry, refs):
  """
    Writes to the json files. (To meet coco-caption formatting requirements)
  """
  f_sent_a  = files[0]
  f_sent_b  = files[1]
  f_refs_5  = files[2]
  f_refs_10 = files[3]
  f_refs_20 = files[4]

  f_sent_a.write(write_json.comma)
  f_sent_b.write(write_json.comma)

  # Entry indices
  # dataset                 0
  # original sentence       1
  # sentence A              2
  # sentence B (corruption) 3
  # score                   4
  f_sent_a.write(json.dumps({'image_id':write_json.hash_id, 'caption':unicode(entry[2], errors='ignore')}))
  f_sent_b.write(json.dumps({'image_id':write_json.hash_id, 'caption':unicode(entry[3], errors='ignore')}))
  
  f_refs_5.write(write_json.comma)
  f_refs_10.write(write_json.comma)
  f_refs_20.write(write_json.comma)
  
  write_json.comma = ""
  for ref in refs[:5]:
    f_refs_5.write(write_json.comma)
    f_refs_5.write(json.dumps({'image_id':write_json.hash_id, 'id': write_json.hash_id, 'caption':unicode(ref, errors='ignore')}))
    
    close_json.ref_id_list[0].append({'id': write_json.hash_id})
    
    write_json.comma = ",\n"
  write_json.comma = ""
  for ref in refs[:10]:
    f_refs_10.write(write_json.comma)
    f_refs_10.write(json.dumps({'image_id':write_json.hash_id, 'id': write_json.hash_id, 'caption':unicode(ref, errors='ignore')}))
    
    close_json.ref_id_list[1].append({'id': write_json.hash_id})
    
    write_json.comma = ",\n"
  write_json.comma = ""
  for ref in refs[:20]:
    f_refs_20.write(write_json.comma)
    f_refs_20.write(json.dumps({'image_id':write_json.hash_id, 'id': write_json.hash_id, 'caption':unicode(ref, errors='ignore')}))
    
    close_json.ref_id_list[2].append({'id': write_json.hash_id})
    
    write_json.comma = ",\n"
  write_json.comma = ",\n"
  write_json.hash_id += 1

def close_json(files):
  """
    Places final brackets and closes the json files.
  """
  f_sent_a  = files[0]
  f_sent_b  = files[1]
  f_refs_5  = files[2]
  f_refs_10 = files[3]
  f_refs_20 = files[4]
 
  f_sent_a.write(']')
  f_sent_b.write(']')
  f_refs_5.write( '], \"images\":' + json.dumps(close_json.ref_id_list[0]) + '}')
  f_refs_10.write('], \"images\":' + json.dumps(close_json.ref_id_list[1]) + '}')
  f_refs_20.write('], \"images\":' + json.dumps(close_json.ref_id_list[2]) + '}')

  f_sent_a.close()
  f_sent_b.close()
  f_refs_5.close()
  f_refs_10.close()
  f_refs_20.close()

