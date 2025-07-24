"""
Сервис обработки уборки
Основная бизнес-логика для обработки сообщений машин и обновления статусов дворов
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from ..models.machine import Machine, MachineMessage
from ..models.yard import Yard, YardStatus


class CleaningService:
    """
    Сервис для обработки процесса уборки
    
    Отвечает за:
    - Обработку сообщений от машин
    - Обновление статусов дворов
    - Расчет времени работы и убранной площади
    - Логирование изменений
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Инициализация сервиса
        
        Args:
            logger: Логгер для записи событий
        """
        self.logger = logger
        self._message_count = 0
        self._error_count = 0
    
    def process_machine_update(
        self, 
        machine: Machine, 
        message: MachineMessage, 
        yards: Dict[int, Yard]
    ) -> Optional[Dict]:
        """
        Обработка обновления от машины
        
        Args:
            machine: Объект машины
            message: Сообщение от машины
            yards: Словарь дворов
            
        Returns:
            Информация об изменении статуса двора или None
        """
        self._message_count += 1
        
        try:
            # Логируем получение сообщения
            self.logger.debug(
                f"📨 Сообщение #{self._message_count} от машины {message.machine_id}: "
                f"координаты=({message.coordinates[0]}, {message.coordinates[1]}), "
                f"двор={message.yard_id}, время={message.timestamp}"
            )
            
            # Обновляем позицию машины
            changes = machine.update_position(message)
            
            # Логируем изменения позиции
            if changes['position_changed']:
                self.logger.debug(
                    f"🚚 Машина {machine.machine_id} изменила позицию: "
                    f"{message.coordinates}"
                )
            
            # Обрабатываем изменения дворов
            status_change = None
            
            if changes['yard_changed']:
                status_change = self._handle_yard_change(machine, changes, yards, message.timestamp)
            
            # Если машина работает в текущем дворе, обновляем статус
            elif (changes['work_time_added'] > 0 and 
                  machine.current_yard_id is not None and 
                  machine.current_yard_id in yards):
                
                yard = yards[machine.current_yard_id]
                old_status = yard.status
                new_status = yard.add_work_time(changes['work_time_added'])
                
                if new_status:
                    status_change = {
                        'yard_id': yard.yard_id,
                        'old_status': old_status,
                        'new_status': new_status,
                        'timestamp': message.timestamp.isoformat(),
                        'machine_id': machine.machine_id,
                        'work_time_added': changes['work_time_added']
                    }
                    
                    self.logger.info(
                        f"📊 Машина {machine.machine_id} работала {changes['work_time_added']:.1f}с "
                        f"во дворе {yard.yard_id}, убрано {yard.get_completion_percentage():.1f}%"
                    )
            
            return status_change
            
        except Exception as e:
            self._error_count += 1
            self.logger.error(
                f"❌ Ошибка обработки сообщения от машины {message.machine_id}: {e}"
            )
            return None
    
    def _handle_yard_change(
        self, 
        machine: Machine, 
        changes: dict, 
        yards: Dict[int, Yard], 
        timestamp: datetime
    ) -> Optional[Dict]:
        """
        Обработка изменения двора для машины
        
        Args:
            machine: Объект машины
            changes: Словарь с изменениями
            yards: Словарь дворов
            timestamp: Время изменения
            
        Returns:
            Информация об изменении статуса двора или None
        """
        status_change = None
        
        # Машина покинула двор
        if changes['left_yard'] is not None:
            left_yard_id = changes['left_yard']
            work_time = changes['work_time_added']
            
            self.logger.info(
                f"🚪 Машина {machine.machine_id} покинула двор {left_yard_id} "
                f"(работала {work_time:.1f}с)"
            )
            
            # Обновляем статус покинутого двора
            if left_yard_id in yards and work_time > 0:
                yard = yards[left_yard_id]
                old_status = yard.status
                new_status = yard.add_work_time(work_time)
                
                if new_status:
                    status_change = {
                        'yard_id': yard.yard_id,
                        'old_status': old_status,
                        'new_status': new_status,
                        'timestamp': timestamp.isoformat(),
                        'machine_id': machine.machine_id,
                        'work_time_added': work_time
                    }
        
        # Машина вошла в новый двор
        if changes['entered_yard'] is not None:
            entered_yard_id = changes['entered_yard']
            
            if entered_yard_id in yards:
                yard = yards[entered_yard_id]
                self.logger.info(
                    f"🏠 Машина {machine.machine_id} вошла во двор {entered_yard_id} "
                    f"(убрано {yard.get_completion_percentage():.1f}%)"
                )
            else:
                self.logger.warning(
                    f"⚠️ Машина {machine.machine_id} вошла в неизвестный двор {entered_yard_id}"
                )
        
        return status_change
    
    def calculate_yard_statistics(self, yards: Dict[int, Yard]) -> Dict:
        """
        Расчет статистики по дворам
        
        Args:
            yards: Словарь дворов
            
        Returns:
            Словарь со статистикой
        """
        if not yards:
            return {
                'total_yards': 0,
                'cleaned_yards': 0,
                'partially_cleaned_yards': 0,
                'average_completion': 0.0,
                'total_area': 0.0,
                'cleaned_area': 0.0
            }
        
        total_yards = len(yards)
        cleaned_yards = 0
        partially_cleaned_yards = 0
        total_area = 0.0
        cleaned_area = 0.0
        completion_sum = 0.0
        
        for yard in yards.values():
            info = yard.get_status_info()
            
            total_area += info['area']
            cleaned_area += info['cleaned_area']
            completion_sum += info['completion_percentage']
            
            if info['is_fully_cleaned']:
                cleaned_yards += 1
            elif info['completion_percentage'] > 0:
                partially_cleaned_yards += 1
        
        return {
            'total_yards': total_yards,
            'cleaned_yards': cleaned_yards,
            'partially_cleaned_yards': partially_cleaned_yards,
            'untouched_yards': total_yards - cleaned_yards - partially_cleaned_yards,
            'average_completion': completion_sum / total_yards if total_yards > 0 else 0.0,
            'total_area': total_area,
            'cleaned_area': cleaned_area,
            'cleaning_efficiency': (cleaned_area / total_area * 100) if total_area > 0 else 0.0
        }
    
    def calculate_machine_statistics(self, machines: Dict[int, Machine]) -> Dict:
        """
        Расчет статистики по машинам
        
        Args:
            machines: Словарь машин
            
        Returns:
            Словарь со статистикой
        """
        if not machines:
            return {
                'total_machines': 0,
                'active_machines': 0,
                'idle_machines': 0,
                'total_work_sessions': 0
            }
        
        total_machines = len(machines)
        active_machines = 0
        total_work_sessions = 0
        
        for machine in machines.values():
            status = machine.get_current_status()
            
            if status['is_active']:
                active_machines += 1
            
            total_work_sessions += status['total_yards_worked']
        
        return {
            'total_machines': total_machines,
            'active_machines': active_machines,
            'idle_machines': total_machines - active_machines,
            'total_work_sessions': total_work_sessions,
            'average_work_sessions': total_work_sessions / total_machines if total_machines > 0 else 0.0
        }
    
    def get_processing_statistics(self) -> Dict:
        """
        Получение статистики обработки сообщений
        
        Returns:
            Словарь со статистикой обработки
        """
        success_rate = ((self._message_count - self._error_count) / self._message_count * 100 
                       if self._message_count > 0 else 0.0)
        
        return {
            'total_messages_processed': self._message_count,
            'successful_messages': self._message_count - self._error_count,
            'failed_messages': self._error_count,
            'success_rate_percent': success_rate
        }
    
    def validate_yard_consistency(self, yards: Dict[int, Yard]) -> list:
        """
        Проверка консистентности данных дворов
        
        Args:
            yards: Словарь дворов
            
        Returns:
            Список найденных проблем
        """
        issues = []
        
        for yard in yards.values():
            info = yard.get_status_info()
            
            # Проверяем соответствие убранной площади и статуса
            expected_status = YardStatus.get_status_by_percentage(info['completion_percentage'])
            if info['current_status'] != expected_status:
                issues.append(
                    f"Двор {yard.yard_id}: несоответствие статуса "
                    f"({info['current_status'].value}% vs ожидаемый {expected_status.value}%)"
                )
            
            # Проверяем логичность убранной площади
            if info['cleaned_area'] > info['area']:
                issues.append(
                    f"Двор {yard.yard_id}: убранная площадь ({info['cleaned_area']:.1f}) "
                    f"превышает общую площадь ({info['area']:.1f})"
                )
            
            # Проверяем отрицательные значения
            if info['cleaned_area'] < 0 or info['total_work_time'] < 0:
                issues.append(
                    f"Двор {yard.yard_id}: отрицательные значения в данных"
                )
        
        return issues
    
    def __str__(self) -> str:
        """Строковое представление сервиса"""
        stats = self.get_processing_statistics()
        return (f"CleaningService: обработано {stats['total_messages_processed']} сообщений, "
                f"успешность {stats['success_rate_percent']:.1f}%")