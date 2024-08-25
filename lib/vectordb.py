import chromadb
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer 
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.config import Settings
import os
from dotenv import load_dotenv
load_dotenv()

key= os.getenv('google_llm_key')



embeddings_func  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=key)

if os.path.exists(r'./db') is False:
    os.mkdir(r'./db')

client = chromadb.PersistentClient(path="./db")

tokenizer= Tokenizer.from_pretrained('bert-base-uncased')


def create_get_collection(diet_chart_id):
    collection= client.get_or_create_collection(name= diet_chart_id, metadata={"hnsw:space": "cosine",'folder':diet_chart_id}, embedding_function= embeddings_func)
    return collection



def splitting_of_text(text):
    max_token= 100
    splitter = TextSplitter.from_huggingface_tokenizer(tokenizer, max_token)
    chunks = splitter.chunks(text)
    ids=[]
    for i in range(len(chunks)):
        ids.append(f'id{i}')
    return chunks, ids


def chunks_to_collection(ids, chunks, collection):
    collection.add(
        documents= chunks,
        ids= ids
    )
    
def retrieve_content(collection, user_input):
    content= collection.query(
        query_texts= [user_input],
        n_results=10
    )
    return content
