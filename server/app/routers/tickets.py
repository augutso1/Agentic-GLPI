from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from .. import schemas, models, auth, ai
import datetime
from ..config import TicketStatus

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
    assignment_data: schemas.TicketAssignment,
    _: models.User = Depends(auth.admin_required)
):
    
    ticket = models.Ticket.get_or_none(models.Ticket.id == ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    technician_to_assign = models.User.get_or_none(models.User.id == assignment_data.
    technician_id)

    if not technician_to_assign or technician_to_assign.role.strip().lower() != 'admin':
        raise HTTPException(status_code=404, detail="Technician not found or user is not an admin")

    ticket.assigned_technician = technician_to_assign
    ticket.updated_at = datetime.datetime.now()
    ticket.save()
    return ticket


@router.put("/{ticket_id}/status", response_model=schemas.Tickets)
def update_ticket_status(
    ticket_id: int,
    new_status: TicketStatus, 
    admin: models.User = Depends(auth.admin_required)
):
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

@router.get("/admin/all", response_model=List[schemas.Tickets])
def get_all_tickets_admin(admin: models.User = Depends(auth.admin_required)):
    return list(models.Ticket.select())

@router.get("/admin/{ticket_id}", response_model=schemas.Tickets)
def get_single_ticket_admin(
    ticket_id: int,
    admin: models.User = Depends(auth.admin_required)
):
    ticket = models.Ticket.get_or_none(models.Ticket.id == ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/admin/{ticket_id}", response_model=schemas.Tickets)
def update_ticket_admin(
        ticket_id: int,
        update_data: schemas.TicketUpdateAdmin,
        admin: models.User = Depends(auth.admin_required)
):

    ticket = models.Ticket.get_or_none(models.Ticket.id == ticket_id)
    if not ticket:
        raise HTTPException(
            status_code = 404,
            detail="Ticket not found"
        )
    
    if update_data.description is not None:
        ticket.description = update_data.description
    if update_data.status is not None:
        ticket.status = update_data.status.value
    if update_data.assigned_technician is not None:
        technician = models.User.get_or_none(models.User.id == update_data.assigned_technician)
        if not technician or technician.role.strip().lower() != 'admin':
            raise HTTPException(
                status_code = 404,
                detail = "Technician to assign not found or is not an admin"
            )
        ticket.assigned_technician = technician
    if update_data.comment:
        models.TicketUpdate.create(
            comment=update_data.comment,
            author_id=admin.id,
            ticket_id=ticket.id
        )

    ticket.updated_at = datetime.datetime.now()
    ticket.save()

    return ticket

@router.get("/admin/technicians", response_model=List[schemas.User])
def get_all_technicians(admin: models.User = Depends(auth.admin_required)):
    return list(models.User.select().where(models.User.role == 'admin'))