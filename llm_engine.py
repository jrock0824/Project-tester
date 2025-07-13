# llm_engine.py

import os
import logging
from langchain_ollama.llms import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

model = OllamaLLM(model="llama3.2")
folder_path = "Data"
logging.basicConfig(level=logging.INFO)

ALLOWED_KEYWORDS = [
    "parent", "parenting", "child", "children", "trauma", "discipline", "emotion",
    "resilience", "behavior", "coparenting", "communication", "support", "routine",
    "ADHD", "stimulant", "substance", "abuse", "relapse", "therapy", "hospitalization",
    "mental", "health", "self-esteem", "emotional", "regulation", "adversity",
    "risk", "co-occurring", "treatment", "recovery", "awareness", "intervention",
    "relational", "cycle", "transmission", "generational", "stress", "supportive",
    "prevention", "vulnerability", "gender", "psychiatric", "trauma-informed",
    "curriculum", "education", "tools", "recognition", "coping", "mentorship",
    "healing", "identity", "forgiveness", "growth", "dialogue", "transparency",
    "fatherhood", "masculinity", "empathy", "nurture", "safety", "attachment",
    "boundaries", "modeling", "role model", "guidance", "cultural", "nonviolent",
    "whupping", "corporal", "co-regulation", "security", "trust", "spiritual",
    "emotional repression", "self-awareness", "expression", "development", "ACE",
    "adversities", "neglect", "abandonment", "emotional intelligence", "systemic",
    "environment", "racism", "community", "representation", "protection",
    "anxiety", "depression", "psychological", "social coping", "identity formation",
    "charged language", "reflective", "firmness", "grounding", "trauma history"
]

#prompt engineering
prompt_template = ChatPromptTemplate.from_template("""
You are a trauma-informed, emotionally intelligent digital parenting assistant designed to help caregivers better 
understand and respond to their child's behavior in the context of trauma. 
Use the context provided to give empathetic, personalized, and evidence-based guidance. 
Your tone should be supportive, non-judgmental, and practical.

### Persona Tone Instruction:
{tone}

### Context:
{context}

### Parent's Concern:
{question}

### Instructions:
- Identify any trauma-related patterns or emotional needs implied in the question.
- Provide 2-3 trauma-aware parenting strategies that promote emotional safety, connection, and regulation.
- If appropriate, recommend professional help or self-care suggestions for the parent.
- Avoid diagnostic language or making assumptions; focus on understanding and support.
- Use the persona selected by the user to tailor your response.
- You must only refer to the specific parenting strategies and trauma patterns included in the given context. Do not generate advice outside of what is present in the context.
- **Format the entire response using Markdown syntax** (e.g., `**bold**`, `### headings`, `- bullet points`) for readability.
- Use short paragraphs, whitespace, and clear section titles for aesthetic clarity.
- Include reflective prompts or questions to help the parent deepen their understanding of their parenting patterns.

### Answer:
""")

def is_on_topic(question: str) -> float:
    """Return a basic 'relevance score' between -1 and 1."""
    matches = sum(1 for kw in ALLOWED_KEYWORDS if kw in question.lower())
    score = matches / len(ALLOWED_KEYWORDS)
    return round((score * 2) - 1, 2)  # Map 0-1 → -1 to 1

def retrieve_relevant_chunks(query, k=3):
    try:
        embedding_function = OllamaEmbeddings(model="nomic-embed-text")
        vectorstore = Chroma(
            persist_directory="chroma_store",
            embedding_function=embedding_function
        )
        docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)
        return [doc.page_content for doc, score in docs_and_scores]
    except Exception as e:
        logging.error(f"Failed to retrieve embeddings: {e}")
        return ["Sorry, I couldn’t retrieve context for that right now."]


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

def process_question(question: str, persona: str) -> str:
    score = is_on_topic(question)
    logging.info(f"Relevance Score: {score}")
    if score < -1:
        return "Please ask a question related to parenting or trauma. I'm here to help with those topics."

    persona_tones = {
        "friendly": "Speak warmly and with encouragement.",
        "professional": "Speak formally and provide structured guidance.",
        "humorous": "Use a light and witty tone, while still being helpful.",
    }
    tone = persona_tones.get(persona, "")

    context_chunks = retrieve_relevant_chunks(question, k=3)
    context = "\n\n".join(context_chunks)
    final_context = f"{tone}\n\n{context}"
    formatted_prompt = prompt_template.format(context=final_context, question=question, tone=tone)
    return model.invoke(formatted_prompt)

