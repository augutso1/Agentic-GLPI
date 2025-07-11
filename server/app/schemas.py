#Models for the HTTP requests and responses
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

#Users
class UserBase(BaseModel):
    login: str
    role: str

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
        from_attributes = True

#Userresponse
class UserResponse(BaseModel):
    id: int
    login: str
    role: str

    #Orm
    class Config:
        from_attributes = True

#Tickets
class TicketCreate(BaseModel):
    title: str
    description: str
    department: Optional[str] = None

class Tickets(BaseModel):
    id: int
    title: str
    description: str
    status: str = Field(default="Aberto")
    priority: str = Field(default="Média")
    category: Optional[str] = Field(default=None)
    department: Optional[str]
    created_at: datetime
    updated_at: datetime
    suggested_solution: Optional[str] = None
    owner_id: UserResponse
    assigned_technician_id: Optional[int] = None

    #Orm
    class Config:
        from_attributes = True

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
        from_attributes = True

class TokenData(BaseModel):
    id: Optional[int] = None
