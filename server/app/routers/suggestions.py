from fastapi import APIRouter
from typing import List
from .. import ai, schemas

router = APIRouter(
    prefix="/suggestions",
    tags=["Suggestions"]
)

@router.get("/", response_model=List[schemas.KnowledgeBaseEntry])
def get_suggestions(q: str):
    return ai.get_solutions_suggestions(query=q)