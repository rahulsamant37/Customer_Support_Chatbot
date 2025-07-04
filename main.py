import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Annotated
from dotenv import load_dotenv

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from retriever.retrieval import Retriever
from utils.model_loader import ModelLoader
from prompt_library.prompt import PROMPT_TEMPLATES

import os
load_dotenv()

app = FastAPI()

# Allow CORS (optional for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


retriever_obj = Retriever()

model_loader = ModelLoader()

def invoke_chain(query: str):
    try:
        retriever = retriever_obj.load_retriever()
        
        # Test the retriever first to see if it finds any documents
        test_docs = retriever.invoke(query)
        print(f"Retriever found {len(test_docs)} documents for query: '{query}'")
        
        if len(test_docs) == 0:
            return "I'm sorry, I couldn't find any relevant product information for your query. Please try a different search term or make sure the product database has been populated."
        
        # Log the first document for debugging
        if test_docs:
            print(f"Sample document: {test_docs[0].page_content[:100]}...")
        
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATES["product_bot"])
        llm = model_loader.load_llm()
        
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        output = chain.invoke(query)
        return output
        
    except Exception as e:
        print(f"Error in invoke_chain: {str(e)}")
        return f"I'm experiencing technical difficulties. Error: {str(e)}"

@app.get("/")
async def main():
    """
    Main endpoint to check if the API is running.
    """
    return {"message": "Welcome to the Product Information Bot API. Use the /get endpoint to chat with the bot."}

@app.post("/get")
async def chat(msg: Annotated[str, Form(...,title="Message", description="User's message")]):
    """
    Handle chat messages.
    """
    result=invoke_chain(msg)
    print(f"Response: {result}")
    return {"response": result}

@app.get("/chat")
async def serve_frontend():
    """
    Serve the chat frontend.
    """
    return FileResponse("frontend/index.html")