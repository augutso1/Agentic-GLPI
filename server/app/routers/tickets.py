from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from .. import schemas, models, auth, ai
import datetime
from ..config import TicketStatus
from ..auth import admin_required

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
        owner = current_user
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

    print(current_user)

    ticket = models.Ticket.get_or_none(models.Ticket.id == ticket_id)

    if not ticket:        
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Ticket not found",
        )

    if current_user.role != "admin" and ticket.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Permission denied"
        )
    
    return ticket

@router.put("/{ticket_id}/assign", response_model=schemas.Tickets)
def assign_ticket(
    ticket_id: int,
    admin: models.User = Depends(auth.admin_required)
):
    
    ticket = models.Ticket.get_or_none(models.Ticket.id == ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.assigned_technician = admin
    ticket.updated_at = datetime.datetime.now()
    ticket.save()
    return ticket


@router.put("/{ticket_id}/status", response_model=schemas.Tickets)
def update_ticket_status(
    ticket_id: int,
    new_status: TicketStatus, 
    admin: models.User = Depends(auth.admin_required)
):
    """Updates a ticket's status."""
    ticket = models.Ticket.get_or_none(models.Ticket.id == ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = new_status
    ticket.updated_at = datetime.datetime.now()

    if new_status.lower() == "fechado":
        admin.tickets_handled += 1
        admin.save()
    
    ticket.save()
    return ticket