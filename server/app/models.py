#DatabasemModels, with type specification
import datetime
from peewee import (Model, CharField, TextField, DateTimeField, ForeignKeyField, IntegerField)
from .database import db

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = IntegerField(primary_key=True)
    login = CharField(unique=True)
    password = CharField()
    role = CharField(default='user')
    created_at = DateTimeField(default=datetime.datetime.now)

class Ticket(BaseModel):
    id =  IntegerField(primary_key=True)
    title = CharField()
    description = TextField()
    status = CharField(default='Aberto')
    priority = CharField(default='Média')
    category = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    owner_id = ForeignKeyField(User, backref='tickets')

class TicketUpdate(BaseModel):
    id = IntegerField(primary_key=True)
    comment = TextField()
    created_at= DateTimeField(default=datetime.datetime.now)
    ticket_id = ForeignKeyField(Ticket, backref='updates')
    author_id = ForeignKeyField(User, backref='updates')