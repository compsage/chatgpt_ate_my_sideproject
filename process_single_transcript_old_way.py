import sys
import pprint
import json
import extract_verses2
import math

filename = sys.argv[1]

with open(filename, 'r') as file:
    json_data = json.load(file)

video_id = filename.split('_')[1].split('.')[0]

outputList = []
verses = []
for row in json_data :
    #print(row['text'])
    processedSent = extract_verses2.process(row['text'])

    validVerse = False

    #print(processedSent)
    if processedSent :
        verse = extract_verses2.extract_verse(processedSent)
    
    if verse :
        dataDict = {}
        dataDict['verse'] = verse[0]
        dataDict['originalSentence'] = row['text']
        dataDict['start'] = row['start']
        dataDict['duration'] =  row['duration']
        dataDict['link'] = "https://youtu.be/" + video_id + "?t=" + str(math.floor(dataDict['start'])) 
        
        outputList.append(dataDict)

        if verse[0] not in verses :
            verses.append(verse[0])

#pprint.pprint(outputList)
verses.sort()
pprint.pprint(verses)
