"""                                                                              
 Text-Machine Lab: MUT  

 File Name :                                                                  
                                                                              
 Creation Date : 12-02-2016
                                                                              
 Created By : Willie Boag                                               
                                                                              
 Purpose : Reads from the sick dataset and creates a list of entries. 
           Where each entry is a dictionary of attributes. 
"""

import os

SICK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sick', 'SICK.txt')

def read_sick_file(filename):
    data = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        labels = lines[0].strip().split('\t')
        for line in lines[1:]:
            entry_items = {}
            for entry,label in zip(line.strip().split('\t'),labels):
                entry_items[label] = entry
            rel_score = 'relatedness_score'
            entry_items[rel_score] = float(entry_items[rel_score])
            data.append(entry_items)
    return data


# READ THE DATA
sick = read_sick_file(SICK_FILE)

def main():

    # Rank data
    #ranked = sorted(sick, key=lambda e:e['relatedness_score'])
    ranked = sick
    for entry in ranked:
        print 'A:           ', entry['sentence_A']
        print 'A_orig:      ', entry['sentence_A_original']
        print 'A_data:      ', entry['sentence_A_dataset']
        print
        print 'B:           ', entry['sentence_B']
        print 'B_orig:      ', entry['sentence_B_original']
        print 'B_data:      ', entry['sentence_B_dataset']
        print
        print 'score:       ', entry['relatedness_score']
        print 'Entrailment: ', entry['entailment_label']
        print '\n\n'



if __name__ == '__main__':
    main()

