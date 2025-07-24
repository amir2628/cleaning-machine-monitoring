"""
Модели данных для дворов
Содержит классы для представления дворов и их статусов уборки
"""

from enum import Enum
from typing import Optional


class YardStatus(Enum):
    """
    Статусы уборки двора
    
    Определяет возможные уровни завершенности уборки
    """
    PERCENT_0 = 0
    PERCENT_20 = 20
    PERCENT_40 = 40
    PERCENT_60 = 60
    PERCENT_80 = 80
    PERCENT_100 = 100
    
    @classmethod
    def get_status_by_percentage(cls, percentage: float) -> 'YardStatus':
        """
        Определение статуса по проценту убранной площади
        
        Args:
            percentage: Процент убранной площади (0-100)
            
        Returns:
            Соответствующий статус уборки
        """
        if percentage >= 100:
            return cls.PERCENT_100
        elif percentage >= 80:
            return cls.PERCENT_80
        elif percentage >= 60:
            return cls.PERCENT_60
        elif percentage >= 40:
            return cls.PERCENT_40
        elif percentage >= 20:
            return cls.PERCENT_20
        else:
            return cls.PERCENT_0
    
    def get_next_status(self) -> Optional['YardStatus']:
        """
        Получение следующего статуса в порядке возрастания
        
        Returns:
            Следующий статус или None если это максимальный статус
        """
        statuses = [
            YardStatus.PERCENT_0,
            YardStatus.PERCENT_20,
            YardStatus.PERCENT_40,
            YardStatus.PERCENT_60,
            YardStatus.PERCENT_80,
            YardStatus.PERCENT_100
        ]
        
        try:
            current_index = statuses.index(self)
            if current_index < len(statuses) - 1:
                return statuses[current_index + 1]
        except ValueError:
            pass
        
        return None


class Yard:
    """
    Класс представляющий двор для уборки
    
    Отслеживает:
    - Параметры двора (площадь, скорость уборки)
    - Текущий статус уборки
    - Убранную площадь
    - Общее время работы машин во дворе
    """
    
    def __init__(self, yard_id: int, area: float, cleaning_speed: float):
        """
        Инициализация двора
        
        Args:
            yard_id: Уникальный идентификатор двора
            area: Площадь двора в квадратных метрах
            cleaning_speed: Скорость уборки (м²/сек)
        """
        if yard_id <= 0:
            raise ValueError("ID двора должен быть положительным числом")
        
        if area <= 0:
            raise ValueError("Площадь двора должна быть положительным числом")
        
        if cleaning_speed <= 0:
            raise ValueError("Скорость уборки должна быть положительным числом")
        
        self.yard_id = yard_id
        self.area = area
        self.cleaning_speed = cleaning_speed
        
        # Состояние уборки
        self.status = YardStatus.PERCENT_0
        self.cleaned_area = 0.0
        self.total_work_time = 0.0
        
        # История изменений статуса
        self.status_history = [YardStatus.PERCENT_0]
    
    def add_work_time(self, work_time: float) -> Optional[YardStatus]:
        """
        Добавление времени работы и обновление статуса уборки
        
        Args:
            work_time: Время работы в секундах
            
        Returns:
            Новый статус если произошло изменение, иначе None
        """
        if work_time <= 0:
            return None
        
        # Обновляем общее время работы
        self.total_work_time += work_time
        
        # Рассчитываем убранную площадь
        cleaned_by_this_work = work_time * self.cleaning_speed
        self.cleaned_area += cleaned_by_this_work
        
        # Ограничиваем убранную площадь максимальной площадью двора
        if self.cleaned_area > self.area:
            self.cleaned_area = self.area
        
        # Определяем новый статус
        percentage = self.get_completion_percentage()
        new_status = YardStatus.get_status_by_percentage(percentage)
        
        # Проверяем, изменился ли статус
        if new_status != self.status:
            old_status = self.status
            self.status = new_status
            self.status_history.append(new_status)
            return new_status
        
        return None
    
    def get_completion_percentage(self) -> float:
        """
        Расчет процента выполнения уборки
        
        Returns:
            Процент убранной площади (0-100)
        """
        if self.area <= 0:
            return 0.0
        
        percentage = (self.cleaned_area / self.area) * 100
        return min(percentage, 100.0)  # Ограничиваем максимумом 100%
    
    def get_remaining_area(self) -> float:
        """
        Получение оставшейся для уборки площади
        
        Returns:
            Площадь в квадратных метрах
        """
        return max(0.0, self.area - self.cleaned_area)
    
    def get_estimated_completion_time(self) -> float:
        """
        Оценка времени до завершения уборки при текущей скорости
        
        Returns:
            Время в секундах до полной уборки
        """
        remaining_area = self.get_remaining_area()
        if remaining_area <= 0 or self.cleaning_speed <= 0:
            return 0.0
        
        return remaining_area / self.cleaning_speed
    
    def is_fully_cleaned(self) -> bool:
        """
        Проверка, полностью ли убран двор
        
        Returns:
            True если двор убран на 100%
        """
        return self.status == YardStatus.PERCENT_100
    
    def get_status_info(self) -> dict:
        """
        Получение подробной информации о статусе двора
        
        Returns:
            Словарь с информацией о состоянии уборки
        """
        return {
            'yard_id': self.yard_id,
            'area': self.area,
            'cleaning_speed': self.cleaning_speed,
            'current_status': self.status,
            'completion_percentage': self.get_completion_percentage(),
            'cleaned_area': self.cleaned_area,
            'remaining_area': self.get_remaining_area(),
            'total_work_time': self.total_work_time,
            'is_fully_cleaned': self.is_fully_cleaned(),
            'estimated_completion_time': self.get_estimated_completion_time(),
            'status_changes_count': len(self.status_history) - 1
        }
    
    def reset_cleaning_progress(self):
        """
        Сброс прогресса уборки (для тестирования или пересчета)
        """
        self.cleaned_area = 0.0
        self.total_work_time = 0.0
        self.status = YardStatus.PERCENT_0
        self.status_history = [YardStatus.PERCENT_0]
    
    def __str__(self) -> str:
        """Строковое представление двора"""
        percentage = self.get_completion_percentage()
        return (f"Двор {self.yard_id}: {percentage:.1f}% убрано "
                f"({self.cleaned_area:.1f}/{self.area:.1f} м²), "
                f"статус: {self.status.value}%")
    
    def __repr__(self) -> str:
        """Техническое представление двора"""
        return (f"Yard(id={self.yard_id}, "
                f"area={self.area}, "
                f"speed={self.cleaning_speed}, "
                f"status={self.status})")