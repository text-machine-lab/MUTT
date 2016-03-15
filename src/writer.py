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

def clean_text(sent):
    # remove goofy characters
    sent = sent.replace('&', 'and')
    for c in '<>\x12':
        sent = sent.replace(c, '')

    try:
        s = sent.decode('ascii', 'ignore')
    except UnicodeDecodeError, e:
        s_list = []
        for c in sent:
            try:
                s_list.append( c.decode('ascii', 'ignore') )
            except UnicodeDecodeError, e:
                continue
        s = ''.join(s_list)
    return s


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

def files_json(corruption):
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
  f_sent_a.write(json.dumps({'image_id':write_json.hash_id, 'caption':clean_text(entry[2])}))
  f_sent_b.write(json.dumps({'image_id':write_json.hash_id, 'caption':clean_text(entry[3])}))
  
  f_refs_5.write(write_json.comma)
  f_refs_10.write(write_json.comma)
  f_refs_20.write(write_json.comma)
  
  write_json.comma = ""
  for ref in refs[:5]:
    f_refs_5.write(write_json.comma)
    f_refs_5.write(json.dumps({'image_id':write_json.hash_id, 'id': write_json.hash_id, 'caption':clean_text(ref)}))
    
    close_json.ref_id_list[0].append({'id': write_json.hash_id})
    
    write_json.comma = ",\n"
  write_json.comma = ""
  for ref in refs[:10]:
    f_refs_10.write(write_json.comma)
    f_refs_10.write(json.dumps({'image_id':write_json.hash_id, 'id': write_json.hash_id, 'caption':clean_text(ref)}))
    
    close_json.ref_id_list[1].append({'id': write_json.hash_id})
    
    write_json.comma = ",\n"
  write_json.comma = ""
  for ref in refs[:20]:
    f_refs_20.write(write_json.comma)
    f_refs_20.write(json.dumps({'image_id':write_json.hash_id, 'id': write_json.hash_id, 'caption':clean_text(ref)}))
    
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

#
# xml 
#
def check_xml(corruption):
  """
    Checks to see if files have already been written.
  """
  return (os.path.isfile(os.path.join(TMP_DIR, corruption + '_a.xml'))   and \
          os.path.isfile(os.path.join(TMP_DIR, corruption + '_b.xml'))   and \
          os.path.isfile(os.path.join(TMP_DIR, corruption + '_r5.xml'))  and \
          os.path.isfile(os.path.join(TMP_DIR, corruption + '_r10.xml')) and \
          os.path.isfile(os.path.join(TMP_DIR, corruption + '_r20.xml')))

def files_xml(corruption):
  """
    Returns a list of the json files
  """
  return (os.path.join(TMP_DIR, corruption + '_a.xml'), 
          os.path.join(TMP_DIR, corruption + '_b.xml'),
          os.path.join(TMP_DIR, corruption + '_r5.xml'),
          os.path.join(TMP_DIR, corruption + '_r10.xml'),
          os.path.join(TMP_DIR, corruption + '_r20.xml'))



def init_xml(corruption):
  """
    Opens the json files for writting and writes initial data.
    Returns the file pointers.
  """
  f_sent_a  = open(os.path.join(TMP_DIR, corruption + '_a.xml'),   'w') 
  f_sent_b  = open(os.path.join(TMP_DIR, corruption + '_b.xml'),   'w')
  f_refs_5  = open(os.path.join(TMP_DIR, corruption + '_r5.xml'),  'w')
  f_refs_10 = open(os.path.join(TMP_DIR, corruption + '_r10.xml'), 'w')
  f_refs_20 = open(os.path.join(TMP_DIR, corruption + '_r20.xml'), 'w')

  f_sent_a.write('<?xml version="1.0" encoding="UTF-8"?>\n\
                  <mteval>\n\
                  <tstset setid="example_set" srclang="bar" trglang="baz" sysid="sample_system">\n\
                  <doc docid="doc1" genre="nw">\n\
                  <p>\n')
  f_sent_b.write('<?xml version="1.0" encoding="UTF-8"?>\n\
                  <mteval>\n\
                  <tstset setid="example_set" srclang="bar" trglang="baz" sysid="sample_system">\n\
                  <doc docid="doc1" genre="nw">\n\
                  <p>\n')
  f_refs_5.write('<?xml version="1.0" encoding="UTF-8"?>\n\
                  <mteval>\n')
  f_refs_10.write('<?xml version="1.0" encoding="UTF-8"?>\n\
                   <mteval>\n')
  f_refs_20.write('<?xml version="1.0" encoding="UTF-8"?>\n\
                   <mteval>\n')

  # psuedo-static variables for write_xml
  write_xml.refs = list()
  for i in range(20):
    write_xml.refs.append('<refset setid="example_set" srclang="bar" trglang="baz" refid="ref%d">\n\
                          <doc docid="doc1" genre="nw">\n\
                          <p>\n' % i)
  write_xml.hash_id = 1 


  return f_sent_a, f_sent_b, f_refs_5, f_refs_10, f_refs_20

def write_xml(files, entry, refs):
  """
    Writes to the xml files. (To meet nist, badger formatting requirements)
  """
  f_sent_a  = files[0]
  f_sent_b  = files[1]
  
  # Candidates
  f_sent_a.write('<seg id="%d"> %s </seg>\n' % (write_xml.hash_id, clean_text(entry[2])))
  f_sent_b.write('<seg id="%d"> %s </seg>\n' % (write_xml.hash_id, clean_text(entry[3])))

  for i, ref in enumerate(refs[:20]):
    write_xml.refs[i] += '<seg id="%d"> %s </seg>\n' % (write_xml.hash_id, clean_text(ref))

  write_xml.hash_id += 1

def close_xml(files):
  """
    Places closing tags and closes xml files.
  """
  f_sent_a  = files[0]
  f_sent_b  = files[1]
  f_refs_5  = files[2]
  f_refs_10 = files[3]
  f_refs_20 = files[4]

  # Close the reference braces
  for i in range(len(write_xml.refs[:20])):
    write_xml.refs[i] += '</p>\n</doc>\n</refset>\n' 

  # Write references for reference files
  for ref in write_xml.refs[:20]:
    f_refs_20.write(ref)
  for ref in write_xml.refs[:10]:
    f_refs_10.write(ref)
  for ref in write_xml.refs[:5]:
    f_refs_5.write(ref)

  # Placing closing tags on xml files
  f_sent_a.write('</p>\n</doc>\n</tstset>\n</mteval>\n')
  f_sent_b.write('</p>\n</doc>\n</tstset>\n</mteval>\n')
  f_refs_5.write('</mteval>\n')
  f_refs_10.write('</mteval>\n')
  f_refs_20.write('</mteval>\n')

  f_sent_a.close()
  f_sent_b.close()
  f_refs_5.close()
  f_refs_10.close()
  f_refs_20.close()
