from enum import Enum

class TicketStatus(str, Enum):
    OPEN = "Aberto"
    IN_PROGRESS = "Em Andamento"
    SCHEDULED = "Agendado"
    CLOSED = "Fechado"