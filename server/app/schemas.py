#Models for the HTTP requests and responses
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

#Users
class UserCreate(BaseModel):
    login: str
    password: str
    role: str = "user"

class User(BaseModel):
    id: int
    login: str
    role: str
    created_at: datetime

    #Orm
    class Config:
        orm_mode = True

#Tickets
class TicketCreate(BaseModel):
    title: str
    description: str

class Tickets(BaseModel):
    id: int
    title: str
    description: str
    status: str = Field(default="Aberto")
    priority: str = Field(default="Média")
    category: Optional[str] = Field(default=None)
    created_at: datetime
    owner_id: int = Field(default=None)

    #Orm
    class Config:
        orm_mode = True

#Updates
class TicketUpdateCreate(BaseModel):
    comment: str

class TicketUpdate(BaseModel):
    id: int
    comment: Optional[str] = Field(default=None)
    created_at: datetime
    ticket_id: int
    author_id: str
    
    #Orm
    class Config:
        orm_mode = True