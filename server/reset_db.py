#For possible changes on DB schemas
from app.database import db
from app.models import User, Ticket, TicketUpdate

print("Connecting to the database...")
db.connect()

print("Dropping tables...")
db.drop_tables([User, Ticket, TicketUpdate], safe=True, cascade=True)

print("Closing connection...")
db.close()

print("Database tables dropped successfully.")