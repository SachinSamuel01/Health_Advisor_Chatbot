from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate

from lib.def_prompt import prompt_temp, prompt_inst

import os
from dotenv import load_dotenv
load_dotenv()

key= os.getenv('google_llm_key')






llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.2,
    top_p=0.7,
    max_retries=6,
    api_key=key
)


prompt= PromptTemplate.from_template(prompt_temp)
parser= StrOutputParser()

chain= prompt | llm | parser

def response(profile, lang, notes, hindi_notes, content, user_input):
    
    res= chain.invoke(
        {
        'inst': prompt_inst,
        'profile': profile,
        'lang': lang,   
        'notes': notes,
        'hindi_notes': hindi_notes,
        'content': content,
        'user_input': user_input
        }
    )
    return res
