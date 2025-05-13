import os
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Create FastAPI app instance
app = FastAPI()

# Serve static files (CSS, JavaScript, etc.) from the "static" folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the model
model = OllamaLLM(model="llama3.2")

# Prompt Template for answering questions
prompt = ChatPromptTemplate.from_template(
    """
    Answer as if you are mentoring a parent with empathy, using insights from the context provided.
    You are a compassionate and knowledgeable parenting assistant.
    Use the following context to give thoughtful, evidence-based advice to a parent.
    
    Context:
    {context}

    Question:
    {question}

    Answer:
    """
)

# Load and chunk parenting guides (from text files in the folder)
def load_and_chunk_folder(folder_path, chunk_size=1000, chunk_overlap=200):
    all_text = ""

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                all_text += f"\n\n=== {filename} ===\n\n{content}"

    # Splitting the loaded text into chunks for processing
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(all_text)

# Get response based on user query and context
def get_response(context, question):
    formatted_prompt = prompt.format(context=context, question=question)
    return model.invoke(formatted_prompt)

# Home endpoint: Serve HTML page
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r") as file:
        return HTMLResponse(file.read())

# Endpoint to get parenting advice based on a question
@app.get("/ask")
async def ask_parenting_advice(question: str):
    folder_path = "parenting_guides"  # Your folder with parenting guide text files

    # Load and chunk the text content from parenting guides
    chunks = load_and_chunk_folder(folder_path)
    context = "\n\n".join(chunks[:3])  # Using the first 3 chunks as context

    # Get the model's response
    answer = get_response(context, question)
    return {"question": question, "answer": answer}
