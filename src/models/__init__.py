"""
Модели данных системы мониторинга
Содержит классы для представления машин, дворов и связанных сущностей
"""

from .machine import Machine, MachineMessage
from .yard import Yard, YardStatus

__all__ = [
    'Machine',
    'MachineMessage', 
    'Yard',
    'YardStatus'
]