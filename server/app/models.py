#Database Models, with type specification
import datetime
from peewee import (Model, CharField, TextField, DateTimeField, ForeignKeyField, IntegerField, AutoField)
from .database import db
from .config import TicketStatus

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = AutoField(primary_key=True)
    login = CharField(unique=True)
    password = CharField()
    role = CharField(default='user')
    created_at = DateTimeField(default=datetime.datetime.now)
    tickets_handled = IntegerField(default=0)

class Ticket(BaseModel):
    id =  AutoField(primary_key=True)
    title = CharField()
    description = TextField()
    status = CharField(default=TicketStatus.OPEN)
    priority = CharField(null=True)
    category = CharField(null=True)
    department = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    owner_id = ForeignKeyField(User, backref='tickets')
    assigned_technician = ForeignKeyField(User, backref='assigned_tickets', null=True)
    suggested_solution = TextField(null=True)

class TicketUpdate(BaseModel):
    id = AutoField(primary_key=True)
    comment = TextField()
    change_description = TextField(null=True)
    created_at= DateTimeField(default=datetime.datetime.now)
    ticket_id = ForeignKeyField(Ticket, backref='updates')
    author_id = ForeignKeyField(User, backref='updates_made')