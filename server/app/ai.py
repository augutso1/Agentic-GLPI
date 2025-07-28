import os
import json
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
from . import prompts

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini: {e}")

retrieval_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def get_knowledge_base() -> list:
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
    if not knowledge_base:
        return ""

    query_embedding = retrieval_model.encode(ticket_description, convert_to_tensor=True)

    cosine_scores = util.cos_sim(query_embedding, problem_embeddings)

    best_match_index = cosine_scores.argmax()
    
    if cosine_scores[0][best_match_index] > 0.5:
        return knowledge_base[best_match_index]["solution"]
    else:
        return ""

def get_solutions_suggestions(query: str, top_k: int = 3) -> list:
    if not knowledge_base or not query.strip():
        return []
    
    query_embedding = retrieval_model.encode(query, convert_to_tensor=True)

    cosine_scores = util.cos_sim(query_embedding, problem_embeddings)

    top_results  = cosine_scores[0].topk(top_k)

    suggestions = []

    for score, idx in zip(top_results.values, top_results.indices):
            suggestions.append(knowledge_base[idx])

    return suggestions

def analyze_ticket(title: str, description: str) -> dict:

    relevant_solution_context = find_relevant_solutions(description)

    system_prompt = prompts.SYSTEM_PROMPT

    generation_config = {"response_mime_type": "application/json"}
    model = genai.GenerativeModel("gemini-2.5-pro", generation_config=generation_config, system_instruction = system_prompt)

    priorities = ["Baixa", "Média", "Alta", "Urgente"]

    categories = ["Hardware", "Software", "Segurança", "Rede", "Outro"]

    user_prompt = prompts.USER_PROMPT_TEMPLATE.format(
        categories=categories,
        priorities=priorities,
        context_solution=relevant_solution_context,
        title=title,
        description=description,
    )

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