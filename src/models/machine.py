"""
Модели данных для уборочных машин
Содержит классы для представления машин и их сообщений
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass
class MachineMessage:
    """
    Сообщение от уборочной машины
    
    Представляет данные, передаваемые машиной в систему мониторинга
    """
    machine_id: int  # Идентификатор машины
    timestamp: datetime  # Время отправки сообщения
    coordinates: Tuple[float, float]  # Координаты машины (x, y)
    yard_id: Optional[int] = None  # ID двора или None если машина вне дворов
    
    def __post_init__(self):
        """Валидация данных после инициализации"""
        if self.machine_id <= 0:
            raise ValueError("ID машины должен быть положительным числом")
        
        if len(self.coordinates) != 2:
            raise ValueError("Координаты должны содержать два значения (x, y)")
        
        if self.yard_id is not None and self.yard_id <= 0:
            raise ValueError("ID двора должен быть положительным числом")


class Machine:
    """
    Класс представляющий уборочную машину
    
    Отслеживает текущее состояние машины, включая:
    - Текущие координаты
    - Время последнего обновления
    - Двор, в котором находится машина
    - Историю работы во дворах
    """
    
    def __init__(self, machine_id: int):
        """
        Инициализация машины
        
        Args:
            machine_id: Уникальный идентификатор машины
        """
        if machine_id <= 0:
            raise ValueError("ID машины должен быть положительным числом")
        
        self.machine_id = machine_id
        self.current_coordinates: Tuple[float, float] = (0.0, 0.0)
        self.last_update: Optional[datetime] = None
        self.current_yard_id: Optional[int] = None
        self.previous_yard_id: Optional[int] = None
        
        # История работы во дворах: {yard_id: общее_время_работы}
        self.yard_work_history: dict[int, float] = {}
        
        # Время входа в текущий двор (для расчета времени работы)
        self._yard_entry_time: Optional[datetime] = None
    
    def update_position(self, message: MachineMessage) -> dict:
        """
        Обновление позиции машины на основе полученного сообщения
        
        Args:
            message: Сообщение от машины с новыми данными
            
        Returns:
            Словарь с информацией об изменениях
        """
        changes = {
            'position_changed': False,
            'yard_changed': False,
            'entered_yard': None,
            'left_yard': None,
            'work_time_added': 0.0
        }
        
        # Проверяем изменение позиции
        old_coordinates = self.current_coordinates
        self.current_coordinates = message.coordinates
        
        if old_coordinates != message.coordinates:
            changes['position_changed'] = True
        
        # Обрабатываем изменение двора
        if self.current_yard_id != message.yard_id:
            changes['yard_changed'] = True
            
            # Если машина покидает двор, записываем время работы
            if self.current_yard_id is not None and self._yard_entry_time is not None:
                work_time = self._calculate_work_time(self.last_update, message.timestamp)
                if work_time > 0:
                    self._add_work_time(self.current_yard_id, work_time)
                    changes['work_time_added'] = work_time
                    changes['left_yard'] = self.current_yard_id
            
            # Обновляем информацию о дворе
            self.previous_yard_id = self.current_yard_id
            self.current_yard_id = message.yard_id
            
            # Если машина входит в новый двор
            if message.yard_id is not None:
                self._yard_entry_time = message.timestamp
                changes['entered_yard'] = message.yard_id
            else:
                self._yard_entry_time = None
        
        # Если машина остается в том же дворе, обновляем время работы
        elif (self.current_yard_id is not None and 
              self.last_update is not None and 
              self._yard_entry_time is not None):
            
            work_time = self._calculate_work_time(self.last_update, message.timestamp)
            if work_time > 0:
                self._add_work_time(self.current_yard_id, work_time)
                changes['work_time_added'] = work_time
        
        self.last_update = message.timestamp
        return changes
    
    def get_total_work_time_in_yard(self, yard_id: int) -> float:
        """
        Получение общего времени работы машины в указанном дворе
        
        Args:
            yard_id: Идентификатор двора
            
        Returns:
            Общее время работы в секундах
        """
        return self.yard_work_history.get(yard_id, 0.0)
    
    def _calculate_work_time(self, start_time: datetime, end_time: datetime) -> float:
        """
        Расчет времени работы между двумя моментами времени
        
        Args:
            start_time: Время начала
            end_time: Время окончания
            
        Returns:
            Время работы в секундах
        """
        if start_time is None or end_time is None:
            return 0.0
        
        time_diff = end_time - start_time
        seconds = time_diff.total_seconds()
        
        # Игнорируем отрицательные значения и слишком большие промежутки
        # (которые могут указывать на ошибки в данных)
        if seconds < 0 or seconds > 3600:  # Более часа между сообщениями
            return 0.0
        
        return seconds
    
    def _add_work_time(self, yard_id: int, work_time: float):
        """
        Добавление времени работы для указанного двора
        
        Args:
            yard_id: Идентификатор двора
            work_time: Время работы в секундах
        """
        if yard_id not in self.yard_work_history:
            self.yard_work_history[yard_id] = 0.0
        
        self.yard_work_history[yard_id] += work_time
    
    def get_current_status(self) -> dict:
        """
        Получение текущего статуса машины
        
        Returns:
            Словарь с информацией о текущем состоянии
        """
        return {
            'machine_id': self.machine_id,
            'coordinates': self.current_coordinates,
            'current_yard': self.current_yard_id,
            'last_update': self.last_update,
            'total_yards_worked': len(self.yard_work_history),
            'is_active': self.current_yard_id is not None
        }
    
    def __str__(self) -> str:
        """Строковое представление машины"""
        yard_info = f"двор {self.current_yard_id}" if self.current_yard_id else "вне дворов"
        return f"Машина {self.machine_id} в координатах {self.current_coordinates}, {yard_info}"
    
    def __repr__(self) -> str:
        """Техническое представление машины"""
        return (f"Machine(id={self.machine_id}, "
                f"coords={self.current_coordinates}, "
                f"yard={self.current_yard_id})")