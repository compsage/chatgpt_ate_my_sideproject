import openai
import json
import sys
import os

#JSON Transcript
filename = sys.argv[1]
video_id = filename.split('_')[1].split('.')[0]

with open(filename, 'r') as file:
    json_data = json.load(file)

openai.organization = os.environ['OPENAI_ORGANIZATION']
openai.api_key = os.environ['OPENAI_API_KEY']

# Set up the model and prompt
model_engine = "text-davinci-003"
prompt_template = '''
You are a sermon annotator that understands all the versions of the Bible.  You know when a verse has been directly mentioned by a preacher or has been paraphrased by the preacher.  Your job is to analyze transcripts of sermons and for each line that references a Bible verse or Bible chapter, whether directly or paraphrase, create an output list of dictionaries for each verse found. 

Some examples are:
- "Let's turn to the sixteenth verse of the third chapter in the book of John" = John 3:16
- "Open your Bibles to the Gospel of John the third chapter, sixteenth verse" = John 3:16
- "Turn to John three verse sixteen" = John 3:16

Make sure that all the json returned uses double quotes for strings and key names.
and that the json is well formed meaning all dicts have open and close curly braces and the list is opened and closed with brackets.
Given the following transcript below in json format, identify the dictionaries where the 'text' references a Bible verse. 

Add the following key/values to the dictionaries that have a bible verse in the 'text':
verse - which contains the address of the verse or chapter
mention_type - which denotes whether the verse was a direct mention or paraphrase
verse_text - which is the actual verse text in the NLT versions
youtube_link - which takes the video_id provided and builds the direct youtube like to the start of the verse with the video_id.  Start of the video should be the floor function of the start value so that it is an integer and not a float.  The t value in the link must reference an integer version of the start value.

Remove all dictionaries from the list that do not contain a Bible verse.

Execute the following instructions with the specified json from video_id {video_id} :

{input_json}

Return a the list of dictionaries of verses you found with the additional key/values in each dict.  Do not generate
code.  Return a property formatted json list that terminates each dict with a curly brace and every list with a bracket.  Ensure the json is properly formatted.  The response should be a list of dictionaries. 
'''

transcript_chunks = [json_data[i:i+50] for i in range(0, len(json_data), 50)]

verses = []
for chunk in transcript_chunks :
    prompt = prompt_template.format(video_id=video_id, input_json=json.dumps(chunk))
  
    # Generate a response
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.1,
    )

    response = completion.choices[0].text
    print(response)
    try:
        verses.extend(json.loads(response))
    except json.JSONDecodeError as e:
        print("Error decoding JSON produced by LLM:", str(e))
    
with open('./chatgpt_parse_' + video_id + '.json', "w") as file:
    json.dump(verses, file, indent=4)