import os
import json
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini: {e}")

retrieval_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def get_knowledge_base() -> list:
    """Parses the knowledge base file into a list of problem/solution dicts."""
    try:
        with open("app/knowledge_base.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        entries = []
        for block in content.strip().split("\n\n"):
            if "Problema:" in block and "Solução:" in block:
                problem = block.split("Problema:")[1].split("Solução:")[0].strip()
                solution = block.split("Solução:")[1].strip()
                entries.append({"problem": problem, "solution": solution})
        return entries
    except FileNotFoundError:
        return []

knowledge_base = get_knowledge_base()
problem_embeddings = retrieval_model.encode([entry["problem"] for entry in knowledge_base], convert_to_tensor=True)


def find_relevant_solutions(ticket_description: str) -> str:
    """Finds the most relevant solution using semantic search."""
    if not knowledge_base:
        return ""

    query_embedding = retrieval_model.encode(ticket_description, convert_to_tensor=True)

    cosine_scores = util.cos_sim(query_embedding, problem_embeddings)

    best_match_index = cosine_scores.argmax()
    
    if cosine_scores[0][best_match_index] > 0.5:
        return knowledge_base[best_match_index]["solution"]
    else:
        return ""


def analyze_ticket(title: str, description: str) -> dict:

    """
    Analyzes ticket text to determine category, priority, and a suggested solution.
    """
    relevant_solution_context = find_relevant_solutions(description)

    system_prompt = """
    You are a helpful IT support assistant. 
    When you are given a user's problem and a potential solution from a knowledge base, 
    your goal is to provide a clear, step-by-step guide for the user to follow.
    Your entire response must be a single JSON object.
    """

    generation_config = {"response_mime_type": "application/json"}
    model = genai.GenerativeModel("gemini-2.5-pro", generation_config=generation_config,
                                  system_instruction = system_prompt)

    priorities = ["Baixa", "Média", "Alta", "Urgente"]

    categories = ["Hardware", "Software", "Segurança", "Rede", "Outro"]

    user_prompt = f"""
    Analyze the support ticket below. Your response MUST be a single JSON object containing three keys: "category", "priority", and "suggested_solution".

    - Your most important task is to analyze the "Context Solution". It may contain several methods. 
    - Based on the user's "Ticket Description", identify the *single most relevant step or method* from the context and use only that for the "suggested_solution".
    - For example, if the user mentions an IP address, only explain the TCP/IP method, not the others.

    - "category" must be one of: {categories}.
    - "priority" must be one of: {priorities}.
    - "suggested_solution" must be a helpful response. If the provided "Context Solution" is relevant, adapt it. Otherwise, create a new one.

    Context Solution: "{relevant_solution_context}"

    Ticket Title: "{title}"
    Ticket Description: "{description}"
    """

    try:
        response = model.generate_content(user_prompt)
        result = json.loads(response.text)
        return {
            "category": result["category"],
            "priority": result["priority"],
            "suggested_solution": result["suggested_solution"]
        }
    except Exception as e:
        print(f"AI analysis failed: {e}")
        return {
            "category": None,
            "priority": None,
            "suggested_solution": "AI analysis failed. Please classify manually."
        }

#TODO externalize the user and system prompts for better comprehension and distinction between code and prompt