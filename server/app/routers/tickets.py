from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .. import schemas, models, auth, ai

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)

@router.post("/", response_model=schemas.Tickets)
def create_ticket(
    ticket: schemas.TicketCreate,
    current_user: models.User = Depends(auth.get_current_user)
):
    new_ticket = models.Ticket.create(
        title = ticket.title,
        description = ticket.description,
        owner_id = current_user.id
    )

    analysis = ai.analyze_ticket(new_ticket.title, new_ticket.description)

    new_ticket.category = analysis.get("category")
    new_ticket.priority = analysis.get("priority")
    new_ticket.suggested_solution = analysis.get("suggested_solution")
    new_ticket.save()

    return new_ticket

@router.get("/", response_model=List[schemas.Tickets])
def get_tickets(current_user: models.User = Depends(auth.get_current_user)):
    return list(current_user.tickets)

@router.get("/{ticket_id}", response_model=schemas.Tickets)
def get_ticket(
    ticket_id: int,
    current_user: models.User = Depends(auth.get_current_user)):
    
    ticket = models.Ticket.get_or_none(models.Ticket.id == ticket_id)

    if not ticket or ticket.owner_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Ticket not found"
        )
    return ticket
