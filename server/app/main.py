from fastapi import FastAPI
from .database import db
from .models import User, Ticket, TicketUpdate

app = FastAPI()

#Main app endpoint
@app.get("/")
def read_root():
    return{"message":"Root"}

db.connect()
db.create_tables([User, Ticket, TicketUpdate])
db.close()