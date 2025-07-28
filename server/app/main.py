from fastapi import FastAPI
from .database import db
from .models import User, Ticket, TicketUpdate
from . import models
from .routers import users, auth, tickets, suggestions
import logging
from fastapi.middleware.cors import CORSMiddleware



logging.getLogger('passlib').setLevel(logging.ERROR)

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(suggestions.router)

@app.on_event("startup")
def startup():
    db.connect()
    db.create_tables([User, Ticket, TicketUpdate])

@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()

#Main app endpoint
@app.get("/")
def read_root():
    return{"message":"Root"}