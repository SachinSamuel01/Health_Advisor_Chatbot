import json 
from pprint import pprint
import requests
import io
from PyPDF2 import PdfReader
import numpy as np
import os
from lib.vectordb import create_get_collection, splitting_of_text, chunks_to_collection, retrieve_content
from lib.llm import response

with open(r'./data/queries.json','r') as f:
    file_json= json.load(f)


try:
    unique_chart_id= set(os.listdir(r'./db'))
except:

    unique_chart_id= set()



def info_from_url(url):
    binary_text= requests.get(url).content

    io_object= io.BytesIO(binary_text)
    pdf_reader= PdfReader(io_object)

    pages= pdf_reader.pages
    text='\n'
    for i in range(len(pages)):
        page= pages[i]
        info= page.extract_text()
        text= text + info

    return text



all_data=[]

for sample in file_json:
    profile= sample['profile_context']  # dict
    query= sample['latest_query'] # list 3
    ideal_response= sample['ideal_response']
    chat_context= sample['chat_context']

    patient_profile= profile['patient_profile']
    program_name= profile['program_name']
    diet_chart= profile['diet_chart']
    diet_chart_url= profile['diet_chart_url']
    
    diet_chart_id= diet_chart['id']
    
    
    ticket_created= chat_context['ticket_created']
    ticket_id= chat_context['ticket_id']
    chat_history= chat_context['chat_history']
    
    
    text= info_from_url(diet_chart_url)
    diet_chart_id= str(diet_chart_id)
    collection= create_get_collection(diet_chart_id)
    
    if diet_chart_id not in unique_chart_id:
        chunks, ids= splitting_of_text(text)
        chunks_to_collection(ids, chunks, collection)
        
        unique_chart_id.add(diet_chart_id)
    
    try:
        if diet_chart['notes']!='':
            content= retrieve_content(collection, diet_chart['notes'])
        else: 
            content= retrieve_content(collection, diet_chart['hindi_notes'])

        content_docs=f'{content['documents'][0][-1]}\n'
    except:
        content_docs='\n'


    user_input='\n'
    
    for i in query:
        user_input= user_input+i['content']
        content= retrieve_content(collection, i['content'])
        content_docs= content_docs + content['documents'][0][-1]

    
    res= response(patient_profile, diet_chart['language'], diet_chart['notes'], diet_chart['hindi_notes'], content_docs, user_input)
    # print(res)
    # print()
    # print(ideal_response)
    
    data= {
    "ticket_id": ticket_id,
    "latest_query":user_input,
    "generated_response":res,
    "ideal_response":ideal_response 
    }

    all_data.append(data)
    
   


with open('output.json', 'w') as file:
        json.dump(all_data, file, indent=4)