import os
import httpx 
import logging
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain.schema import Document

# Create FastAPI app instance
app = FastAPI()

folder_path = "Data"

logging.basicConfig(level=logging.INFO)

# Serve static files (CSS, JavaScript, etc.) from the "static" folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the model
model = OllamaLLM(model="llama3.2")

# Prompt Template for answering questions
prompt = ChatPromptTemplate.from_template(
    """
    You are a trauma-informed, emotionally intelligent digital parenting assistant designed to help caregivers better 
    understand and respond to their child's behavior in the context of trauma. 
    Use the context provided to give empathetic, personalized, and evidence-based guidance. 
    Your tone should be supportive, non-judgmental, and practical.

    Context:
    {context}

    Parent's Concern:
    {question}

    Instructions:
    - Identify any trauma-related patterns or emotional needs implied in the question.
    - Provide 2-3 trauma-aware parenting strategies that promote emotional safety, connection, and regulation.
    - If appropriate, recommend professional help or self-care suggestions for the parent.
    - Avoid diagnostic language or making assumptions; focus on understanding and support.
    - Use the persona selected by the user to tailor your response.
    - Only use and reference the info from the chunks of parenting guides to inform your response.
    - Include reflective prompts or questions to help the parent deepen their understanding of their parenting patterns.

    Answer:
    """
)

# Load and chunk parenting guides (from text files in the folder)
def load_and_chunk_folder(folder_path, chunk_size=1000, chunk_overlap=200):
    documents = [] # List to hold Document objects
    all_text = ""

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            print(f"Processing file: {filename}")
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
                text = file.read()
                all_text += text + "\n"  # Append the text to all_text with a newline
                documents.append(Document(page_content=text, metadata={"source": filename}))

    # Splitting the loaded text into chunks for processing
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(all_text)  # Split the concatenated text into chunks

    if not chunks:
        logging.error("No chunks were loaded from the folder.")
    return chunks

# Get response based on user query and context
def get_response(context, question):
    formatted_prompt = prompt.format(context=context, question=question)
    return model.invoke(formatted_prompt)

# Home endpoint: Serve HTML page
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r") as file:
        return HTMLResponse(file.read())

# Endpoint to get parenting advice based on a question and persona
@app.get("/ask")
async def ask_parenting_advice(question: str, persona: str):
    logging.info(f"Received question: {question}")
    logging.info(f"Selected persona: {persona}")
    
    if not question.strip():
        return {"error": "Question cannot be empty."}
    if persona not in ["friendly", "professional", "humorous"]:
        return {"error": f"Invalid persona: {persona}. Choose from 'friendly', 'professional', or 'humorous'."}
    
    folder_path = "Data"  # Your folder with parenting guide text files

    # Load and chunk the text content from parenting guides
    chunks = load_and_chunk_folder(folder_path)
    if not chunks:
        logging.error("No chunks were loaded from the folder.")
        return {"error": "No data available to generate a response."}
    
    context = "\n\n".join(chunks[:3])  # Using the first 3 chunks as context
    logging.info(f"Context: {context}")

    # Adjust the AI prompt based on the persona
    persona_prompts = {
        "friendly": "Answer in a warm and friendly tone.",
        "professional": "Provide a detailed and professional response.",
        "humorous": "Respond with a lighthearted and humorous tone.", 
    }.get(persona, "Answer in a neutral tone.")

    # Combine persona prompt with the context
    combined_context = f"{persona_prompts}\n\n{context}"
    logging.info(f"Combined context: {combined_context}")
    
    # Generate the response
    try:
        answer = get_response(combined_context, question)
        logging.info(f"Generated answer: {answer}")
        return {"answer": answer}
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return {"error": "Failed to generate a response."}