import json 
import pprint
import re
import string
import words2num
from num2words import num2words
import pythonbible as bible
import sys
from os import listdir
from os.path import isfile, join
import time

ordinalBooks = []
ordinalBooks.append("samuel")
ordinalBooks.append("kings")
ordinalBooks.append("chronicles")
ordinalBooks.append("corinthians") 
ordinalBooks.append("thessalonians")
ordinalBooks.append("timothy")
ordinalBooks.append("peter")

ambiguousBooks = []
ambiguousBooks.append("numbers")
ambiguousBooks.append("job")
ambiguousBooks.append("songs")
ambiguousBooks.append("acts")

f = open('./lookupTable.json')
lookupTable = json.load(f)

encodingTable = {}
encodingTable['CHAPTER'] = 1
encodingTable['CHAPTERS'] = 2
encodingTable['BOOK'] = 3
encodingTable['BOOKS'] = 4
encodingTable['VERSE'] = 5
encodingTable['VERSES'] = 6
encodingTable['ORDINAL'] = 7
encodingTable['NUMBER'] = 8
encodingTable['THROUGH'] = 9
encodingTable['AND'] = 10
encodingTable['CVCOMBO'] = 11
encodingTable['NUMBERED_BOOK'] = 12
encodingTable['AMBIGUOUS_BOOK'] = 13

def process(text) :
    sentence = text.lower()
    #now lets replace the ordinals with numbers
    
    numberedJohnHit = False
    if 'first john' in sentence :
        numberedJohnHit = True
    elif 'second john' in sentence :
        numberedJohnHit = True
    elif 'third john' in sentence :
        numberedJohnHit = True
    elif '1st john' in sentence :
        numberedJohnHit = True
    elif '2nd john' in sentence :
        numberedJohnHit = True
    elif '3rd john' in sentence :
        numberedJohnHit = True

    sToks = sentence.replace('.', '').replace(',', '').split()

    outputToks = []
    outputToksTypes = []
    encodedToks = []

    for tok in sToks :
        tok = tok.lower()

        if tok in lookupTable :
            outputToks.append(str(lookupTable[tok][0]))
            
            if tok in ordinalBooks :
                outputToksTypes.append('NUMBERED_BOOK')
                encodedToks.append(encodingTable['NUMBERED_BOOK'])
            elif tok == 'john' and numberedJohnHit :
                outputToksTypes.append('NUMBERED_BOOK')
                encodedToks.append(encodingTable['NUMBERED_BOOK'])
            elif tok in ambiguousBooks :
                outputToksTypes.append('AMBIGUOUS_BOOK')
                encodedToks.append(encodingTable['AMBIGUOUS_BOOK'])
            else :
                outputToksTypes.append(lookupTable[tok][1])
                encodedToks.append(encodingTable[lookupTable[tok][1]])
        else :
            found = re.search("[1-9][0-9]{0,2}:[1-9][0-9]{0,2}", tok)

            if found :
                outputToks.append(tok)
                outputToksTypes.append('CVCOMBO')
                encodedToks.append(encodingTable['CVCOMBO'])
            else :
                outputToks.append(tok)
                outputToksTypes.append('_')
                encodedToks.append(0)

    return (' '.join(outputToks), ' '.join(outputToksTypes), encodedToks)

def find_pattern(sl, l):
    j = 0
    idx = 0

    if sl == l :
        return [(0, len(sl)-1), list(range(0, len(sl)))]
    
    if l == [] :
        return None

    idxs = []

    for val in l:
        if val == sl[j] :
            idxs.append(idx)
        idx+=1

    output = []
    
    #print(str(l) + " " + str(sl) + " " + str(idxs))

    for idx in idxs :
        i=0
        start = idx
        outputIndexes = []
        while i < len(sl) :
            if idx+i >= len(l) :
                break
            elif l[idx+i] == 0 :
                idx+=1
                continue
            elif sl[i] != l[idx+i] :
                break
            
            outputIndexes.append(idx+i)
            i+=1
        
        if i == len(sl) :
          output.append((start, idx+i-1))
          output.append(outputIndexes)  

    return output

patternMap= {}
patternMap['BOOK CHAPTER NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]]
patternMap['AMBIGUOUS_BOOK CHAPTER NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]]
patternMap['ORDINAL NUMBERED_BOOK CHAPTER NUMBER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[3]]
patternMap['BOOK CVCOMBO'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[1]]
patternMap['AMBIGUOUS_BOOK CVCOMBO'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[1]]
patternMap['BOOK NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[1]]
patternMap['ORDINAL NUMBERED_BOOK NUMBER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[2]]
patternMap['ORDINAL NUMBERED_BOOK CVCOMBO'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[2]]
patternMap['NUMBER NUMBERED_BOOK CVCOMBO'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[2]]
patternMap['BOOK CHAPTER NUMBER VERSE NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]] + ":" + sent[idx[4]]
patternMap['AMBIGUOUS_BOOK CHAPTER NUMBER VERSE NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]] + ":" + sent[idx[4]]
patternMap['ORDINAL NUMBERED_BOOK CHAPTER NUMBER VERSE NUMBER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[3]] + ":" + sent[idx[5]]
patternMap['ORDINAL CHAPTER BOOK VERSE NUMBER'] = lambda sent, idx: sent[idx[2]].capitalize() + " " + sent[idx[0]] + ":" + sent[idx[4]]
patternMap['ORDINAL VERSE ORDINAL CHAPTER BOOK'] = lambda sent, idx: sent[idx[4]].capitalize() + " " + sent[idx[2]] + ":" + sent[idx[0]]
#patternMap['BOOK CHAPTERS NUMBER THROUGH NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]] + "-" + sent[idx[4]]
patternMap['ORDINAL NUMBERED_BOOK CHAPTERS NUMBER THROUGH NUMBER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[3]] #+ "-" + sent[idx[5]]
patternMap['BOOK CHAPTER NUMBER VERSES NUMBER THROUGH NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]] + ":" + sent[idx[4]] #+ "-" + sent[idx[6]]
patternMap['AMBIGUOUS_BOOK CHAPTER NUMBER VERSES NUMBER THROUGH NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]] + ":" + sent[idx[4]] #+ "-" + sent[idx[6]]
patternMap['ORDINAL NUMBERED_BOOK CHAPTER NUMBER VERSES NUMBER THROUGH NUMBER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[3]] + ":" + sent[idx[5]] #+ "-" + sent[idx[7]]
#patternMap['BOOK CHAPTER NUMBER VERSE NUMBER AND NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]] + ":" + sent[idx[4]] + "," + sent[idx[6]]
#patternMap['ORDINAL BOOK CHAPTER NUMBER VERSE NUMBER AND NUMBER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[3]] + ":" + sent[idx[5]] + "," + sent[idx[7]]
patternMap['BOOK CHAPTER NUMBER VERSES NUMBER AND NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]] + ":" + sent[idx[4]] + "," + sent[idx[6]]
patternMap['AMBIGUOUS_BOOK CHAPTER NUMBER VERSES NUMBER AND NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[2]] + ":" + sent[idx[4]] + "," + sent[idx[6]]
#patternMap['ORDINAL NUMBERED_BOOK CHAPTER NUMBER VERSES NUMBER AND NUMBER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[3]] + ":" + sent[idx[5]] + "," + sent[idx[7]]
patternMap['BOOK NUMBER NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[1]] + ":" + sent[idx[2]]
patternMap['ORDINAL NUMBERED_BOOK NUMBER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[2]]
patternMap['ORDINAL NUMBERED_BOOK NUMBER NUMBER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[2]] + ":" + sent[idx[3]]
patternMap['BOOK ORDINAL CHAPTER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[1]]
patternMap['AMBIGUOUS_BOOK ORDINAL CHAPTER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[1]]
patternMap['ORDINAL NUMBERED_BOOK ORDINAL CHAPTER'] = lambda sent, idx: sent[idx[0]] + " " + sent[idx[1]].capitalize() + " " + sent[idx[2]]
patternMap['BOOK NUMBER VERSE NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[1]] + ":" + sent[idx[3]]
patternMap['AMBIGUOUS_BOOK NUMBER VERSE NUMBER'] = lambda sent, idx: sent[idx[0]].capitalize() + " " + sent[idx[1]] + ":" + sent[idx[3]]

patterns = {}
for pattern in patternMap.keys() :
    vals = []
    toks = pattern.split(' ')
    for tok in toks :
        vals.append(encodingTable[tok])
    
    patterns[pattern] = vals

def gimmie_verse(val) :
    #print(val)
    if not val :
        return None

    sent = val[0].split(' ')
    idx = val[2][1]
    return patternMap[val[1]](sent, idx)

def extract_verse(processedSent) :
    if not processedSent :
        return None
    
    output = ()
    for key in patterns.keys() :
        val = find_pattern(patterns[key], processedSent[2])
        if val :
            maxVal = 0  
            if len(patterns[key]) > maxVal :
                maxVal = len(patterns[key])
                output = (processedSent[0], key, val)
                
    verse = gimmie_verse(output)
    
    if verse :
        validVerse = False
        verse_text = ''

        try :
            #print(verse)
            references = bible.get_references(verse)  
            verse_ids = bible.convert_reference_to_verse_ids(references[0])
            

            #for verseid in verse_ids :
            #    verse_text += bible.get_verse_text(verseid, version=bible.Version.KING_JAMES)

            verse_text = bible.get_verse_text(verse_ids[0], version=bible.Version.KING_JAMES)
        
            verse = (verse, verse_text, references[0])
            validVerse = True
        except Exception:
            print(verse + " invalid")
            verse = None

        return verse
    else :
        return None

def run_tests():
    #Run Test
    f3 = open('./test.json')
    test_sents = json.load(f3)

    accum = 0

    for sent in test_sents:
        start = int(round(time.time() * 1000))
        processedSent = process(sent[0])
        print(str(sent) + ' -> ' + processedSent[0] + ' -> ' + processedSent[1] + ' -> ' + str(processedSent[2]))
        #print (address + " " + sent[1])
        #assert address[0].lower() == sent[1].lower(), "Verse Mismatch: " + address[0] + " " + sent[1]
        verse = extract_verse(processedSent)
        if verse :
            print(sent[1].lower() + " +++ " + verse[0].lower())
            assert sent[1].lower() == verse[0].lower(), "Verse Mismatch: " + sent[1] + " <==> " + verse[0]
        end = int(round(time.time() * 1000))
        accum += (end - start)

    print('All Tests Passed. ' + str(accum/len(test_sents)) + " avg processing time per line.")
    
