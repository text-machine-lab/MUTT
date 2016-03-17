"""
 Text-Machine Lab: MUTT

 File Name : generate_corruptions.py

 Creation Date : 16-03-2016

 Created By : Willie Boag
              Renan Campos

 Purpose : Generates the fluency disruption corruptions.

"""

import read_data

from pattern.en import parse
from nltk.tokenize import word_tokenize
import random
import re

import writer

#
# Helpers
#

def clean_text(sent):
    try:
        safe = sent.encode('ascii', 'ignore')
    except UnicodeDecodeError, e:
        safe_list = []
        for c in sent:
            try:
                safe_list.append( c.encode('ascii', 'ignore') )
            except UnicodeDecodeError, e:
                pass
        safe = ''.join(safe_list)
    return safe



def tokenize(sent):
    return word_tokenize(clean_text(sent))



def corrupt_remove_prep(sent):
    # parse
    P = parse(sent)
    parsed = sum(P.split(), [])

    # chunk
    new = []
    for word in parsed:
        chunktag = word[3]
        if chunktag != 'B-PNP':
            new.append(word[0])

    corr = ' '.join(new)

    if sorted(tokenize(sent)) == sorted(tokenize(corr)):
        return None

    return corr




def corrupt_double_PP(sent):
    # parse
    P = parse(sent)
    parsed = sum(P.split(), [])

    # chunk
    chunks = []
    chunk = []
    tags = []
    for word in parsed:
        chunktag = word[3]
        if chunktag == 'B-PNP':
            if chunk:
                chunks.append(chunk)
                tags.append('PNP')
            chunk = [word[0]]

        elif chunktag == 'I-PNP':
            chunk.append(word[0])

        else:
            if chunk:
                chunks.append(chunk)
                tags.append('PNP')
                chunk = []
            chunks.append([word[0]])
            tags.append('O')

    # if last tag was 'I', then flush it from buffer
    if parsed[-1][3] in ['B-PNP', 'I-PNP']:
        chunks.append(chunk)
        tags.append('PNP')

    assert len(chunks) == len(tags)

    # build sentence with doubled PP
    new = []
    for chunk,tag in zip(chunks,tags):
        new.append(chunk)

        # again?
        if tag == 'PNP':
            new.append(chunk)

    flat = sum(new,[])
    corr = ' '.join(flat)

    if sorted(tokenize(sent)) == sorted(tokenize(corr)):
        return None

    return corr



def corrupt_swap_chunks(sent):
    # parse
    P = parse(sent)
    parsed = sum(P.split(), [])

    # end-of-sentence  punctuation
    is_period      = False
    is_question    = False
    is_exclamation = False
    if parsed[-1][0] in ['.','?','!']:
        last_chunk = parsed[-1]
        parsed     = parsed[:-1]

        if   last_chunk[0] == '.':
            is_period = True
        elif last_chunk[0] == '?':
            is_question = True
        elif last_chunk[0] == '!':
            is_exclamation = True

    # SPECIAL CASE: over-aggressive parsing

    # chunk
    chunks = []
    chunk = []
    for i,word in enumerate(parsed):
        chunktag = word[2]
        if chunktag[0] == 'B':
            if i:
                chunks.append(chunk)
            chunk = [word[0]]

        elif chunktag[0] == 'I':
            chunk.append(word[0])

        elif chunktag[0] == 'O':
            if i:
                chunks.append(chunk)
                chunk = []
            chunks.append([word[0]])

        else:
            print '\n\t', sent,
            print '\n\tERROR: unknown chunktag   ', word
            exit()

    # if last tag was 'I', then flush it from buffer
    if parsed[-1][2][0] in ['B', 'I']:
        chunks.append(chunk)

    # cannot shuffle it if its just a single chunk
    if len(chunks) == 1:
        return None

    # shuffle the chunks
    original = list(chunks)
    while chunks == original:
        random.shuffle(chunks)

    # add the punctuation, if need be (dont want it getting shuffled into middle)
    if is_period:
        chunks.append(['.'])
    elif is_question:
        chunks.append(['?'])
    elif is_exclamation:
        chunks.append(['!'])

    # re-assemble
    corr = ' '.join(sum(chunks, []))

    # sanity check
    if sorted(tokenize(sent)) != sorted(tokenize(corr)):
        return None

    return corr






#
# Main interface - welcome to hell.
#

corruptions = {
               'remove_prep':corrupt_remove_prep,
               'double_PP':corrupt_double_PP,
               'swap_chunks':corrupt_swap_chunks
              }

def check_generated():
  for corruption in corruptions.keys():
    # The corruptions already exist
    if not writer.check_json(corruption) or not writer.check_xml(corruption):
      return False
  return True

def init_generate_corruptions():
  """
    Returns a list of json and xml files
  """
  files = dict()
  for corruption in corruptions.keys():
    files[corruption] = [writer.init_json(corruption), writer.init_xml(corruption)]

  return files

ref_id_list = {
               'remove_prep':[list(),list(),list()],
               'double_PP':[list(),list(),list()],
               'swap_chunks':[list(),list(),list()]
          }
hash_id = {
               'remove_prep':0,
               'double_PP':0,
               'swap_chunks':0
          }
comma = {
               'remove_prep':"",
               'double_PP':"",
               'swap_chunks':""
          }

xref_id_list = {
               'remove_prep':list(),
               'double_PP':list(),
               'swap_chunks':list(),
          }
for corr in corruptions.keys():
  for i in range(20):
    xref_id_list[corr].append('<refset setid="example_set" srclang="bar" trglang="baz" refid="ref%d">\n\
                        <doc docid="doc1" genre="nw">\n\
                          <p>\n' % i)
xhash_id = {
               'remove_prep':1,
               'double_PP':1,
               'swap_chunks':1
          }

count = 0
def generate_corruptions(gen_files, e, refs):
  """
    Writes the corruption to the appropriate files
  """
  global ref_id_list
  global hash_id
  global comma

  global xref_id_list
  global xhash_id

  global count

  if count == 500:
    return
  count += 1
  old_json = (writer.close_json.ref_id_list,
         writer.write_json.hash_id,
         writer.write_json.comma)

  old_xml = (writer.write_xml.refs, writer.write_xml.hash_id)

  entry = list(e)
  for corr, func in corruptions.items():
    entry[3] = func(entry[2])
    if not entry[3]:
      continue

    writer.close_json.ref_id_list = ref_id_list[corr]
    writer.write_json.hash_id = hash_id[corr]
    writer.write_json.comma = comma[corr]

    writer.write_json(gen_files[corr][0], entry, refs)

    hash_id[corr] = writer.write_json.hash_id
    comma[corr] = writer.write_json.comma

    writer.write_xml.refs = xref_id_list[corr]
    writer.write_xml.hash_id = xhash_id[corr]

    writer.write_xml(gen_files[corr][1], entry, refs)

    xhash_id[corr] = writer.write_xml.hash_id

  writer.close_json.ref_id_list, writer.write_json.hash_id, writer.write_json.comma = old_json

  writer.write_xml.refs, writer.write_xml.hash_id = old_xml


def close_generated_files(files):
  """
    Closes the generated files.
  """
  global xref_id_list
  global ref_id_list

  old = writer.close_json.ref_id_list
  xold = writer.write_xml.refs
  for corr in corruptions.keys():

    writer.close_json.ref_id_list = ref_id_list[corr]
    writer.close_json(files[corr][0])

    writer.write_xml.refs = xref_id_list[corr]
    writer.close_xml(files[corr][1])

  global hash_id
  global comma
  ref_id_list = {
                 'remove_prep':[list(),list(),list()],
                 'double_PP':[list(),list(),list()],
                 'swap_chunks':[list(),list(),list()]
            }
  hash_id = {
                 'remove_prep':0,
                 'double_PP':0,
                 'swap_chunks':0
            }
  comma = {
                 'remove_prep':"",
                 'double_PP':"",
                 'swap_chunks':""
            }

  global xhash_id

  xref_id_list = {
                 'remove_prep':list(),
                 'double_PP':list(),
                 'swap_chunks':list(),
            }
  xhash_id = {
                 'remove_prep':1,
                 'double_PP':1,
                 'swap_chunks':1
            }
  writer.close_json.ref_id_list = old
  writer.write_xml.refs         = xold

def main():

    #f_corr = corrupt_swap_chunks
    #f_corr = corrupt_double_PP
    f_corr = corrupt_remove_prep

    #single_run = True
    single_run = False

    if single_run:

        sentences = read_data.flickr.values()[0]
        s = sentences[0]
        s = 'a child on a scooter moving down the sidewalk .'
        print s
        print f_corr(s)

    else:
        sentences = []
        sentences += sum(read_data.flickr.values(), [])
        #print read_data.msr

        #sentences = ['a fluffy dog carries a stick through snow .']

        for s in sentences:
            pass
            c = f_corr(s)
            if c != None:
                #if len(s) != len(c):
                #    print s
                #    print c
                #    print
                #    exit()
                print s
                print c
                print
                #assert len(s) == len(c)







if __name__ == '__main__':
    main()





