"""
Система мониторинга уборочных машин
Основной модуль для обработки сообщений от машин и отслеживания статуса уборки дворов
"""

import json
import logging
import random
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from queue import Queue

from src.models.machine import Machine, MachineMessage
from src.models.yard import Yard, YardStatus
from src.services.cleaning_service import CleaningService
from src.services.logging_service import setup_logging
from src.utils.file_handler import FileHandler


class MessageTransmissionSimulator:
    """
    Симулятор передачи сообщений с характеристиками реальной системы:
    - Передача ~1 раз в секунду
    - Потеря сообщений (5-8%)
    - Ошибки в координатах (1-2%)
    - Задержки в доставке
    """
    
    def __init__(self, 
                 message_interval: float = 1.0,
                 loss_rate: float = 0.06,
                 coordinate_error_rate: float = 0.015,
                 max_delay: float = 2.0):
        """
        Args:
            message_interval: Интервал между сообщениями (секунды)
            loss_rate: Процент потерянных сообщений (0.06 = 6%)
            coordinate_error_rate: Процент сообщений с ошибками координат
            max_delay: Максимальная задержка доставки (секунды)
        """
        self.message_interval = message_interval
        self.loss_rate = loss_rate
        self.coordinate_error_rate = coordinate_error_rate
        self.max_delay = max_delay
        
        # Статистика
        self.total_generated = 0
        self.total_lost = 0
        self.total_delayed = 0
        self.total_with_errors = 0
        self.logger = logging.getLogger('cleaning_system')
    
    def simulate_transmission(self, messages: List[Dict], message_queue: Queue, 
                            processing_speed: float = 1.0):
        """
        Симуляция передачи сообщений в реальном времени
        
        Args:
            messages: Список исходных сообщений
            message_queue: Очередь для передачи сообщений
            processing_speed: Множитель скорости (1.0 = реальное время)
        """
        self.logger.info(f"📡 Начало симуляции передачи {len(messages)} сообщений")
        self.logger.info(f"⚙️ Параметры: интервал={self.message_interval/processing_speed:.2f}с, "
                        f"потери={self.loss_rate*100:.1f}%, ошибки={self.coordinate_error_rate*100:.1f}%")
        
        for i, message in enumerate(messages):
            self.total_generated += 1
            
            # Симуляция потери сообщения
            if random.random() < self.loss_rate:
                self.total_lost += 1
                self.logger.debug(f"📉 Сообщение #{i+1} от машины {message['machine_id']} потеряно при передаче")
                # Ждем интервал даже для потерянного сообщения
                time.sleep(random.uniform(0.5, self.message_interval) / processing_speed)
                continue
            
            # Симуляция задержки передачи
            transmission_delay = random.uniform(0, self.max_delay)
            if transmission_delay > 0.8:
                self.total_delayed += 1
                self.logger.debug(f"⏱️ Сообщение #{i+1} задержано на {transmission_delay:.1f}с")
            
            # Создаем копию сообщения для модификации
            processed_message = message.copy()
            
            # Симуляция ошибок в координатах
            if random.random() < self.coordinate_error_rate:
                self.total_with_errors += 1
                processed_message = self._add_coordinate_error(processed_message)
                self.logger.debug(f" Сообщение #{i+1} содержит ошибку координат")
            
            # Добавляем реальную задержку передачи
            time.sleep(transmission_delay / processing_speed)
            
            # Помещаем сообщение в очередь
            message_queue.put(processed_message)
            
            # Интервал между сообщениями (с небольшой случайностью)
            actual_interval = random.uniform(
                self.message_interval * 0.8, 
                self.message_interval * 1.2
            )
            time.sleep(actual_interval / processing_speed)
        
        # Сигнал окончания передачи
        message_queue.put(None)
        self.logger.info(f"📡 Передача завершена. Потеряно: {self.total_lost}/{self.total_generated}")
    
    def _add_coordinate_error(self, message: Dict) -> Dict:
        """
        Добавление ошибки в координаты сообщения
        """
        # Разные типы ошибок
        error_type = random.choice(['offset', 'noise', 'swap', 'scale'])
        
        x, y = message['x'], message['y']
        
        if error_type == 'offset':
            # Случайное смещение
            offset_x = random.uniform(-8, 8)
            offset_y = random.uniform(-8, 8)
            message['x'] = round(x + offset_x, 2)
            message['y'] = round(y + offset_y, 2)
            
        elif error_type == 'noise':
            # Добавление шума
            noise_x = random.uniform(-4, 4)
            noise_y = random.uniform(-4, 4)
            message['x'] = round(x + noise_x, 2)
            message['y'] = round(y + noise_y, 2)
            
        elif error_type == 'swap':
            # Перестановка координат
            message['x'] = round(y, 2)
            message['y'] = round(x, 2)
            
        elif error_type == 'scale':
            # Неправильное масштабирование
            scale = random.uniform(0.85, 1.15)
            message['x'] = round(x * scale, 2)
            message['y'] = round(y * scale, 2)
        
        return message
    
    def get_transmission_stats(self) -> Dict:
        """Получение статистики передачи"""
        delivered = self.total_generated - self.total_lost
        return {
            'total_generated': self.total_generated,
            'total_delivered': delivered,
            'total_lost': self.total_lost,
            'total_delayed': self.total_delayed,
            'total_with_errors': self.total_with_errors,
            'delivery_rate': (delivered / self.total_generated * 100) if self.total_generated > 0 else 0,
            'error_rate': (self.total_with_errors / delivered * 100) if delivered > 0 else 0
        }


class CleaningMonitoringSystem:
    """
    Главный класс системы мониторинга уборочных машин
    
    Отвечает за координацию всех компонентов системы:
    - Загрузку справочника дворов
    - Обработку сообщений от машин в реальном времени
    - Отслеживание статусов уборки
    - Вывод результатов
    """
    
    def __init__(self, debug_mode: bool = False, realtime_mode: bool = False, 
                 processing_speed: float = 1.0):
        """
        Инициализация системы мониторинга
        
        Args:
            debug_mode: Режим отладки для подробного логирования
            realtime_mode: Режим реального времени с симуляцией передачи
            processing_speed: Множитель скорости обработки
        """
        # Получаем системный логгер (он возвращает CleaningSystemLogger)
        system_logger = setup_logging(debug_mode)
        # Извлекаем обычный logger из системного логгера
        self.logger = system_logger.logger
        
        self.cleaning_service = CleaningService(self.logger)
        self.file_handler = FileHandler(self.logger)
        self.machines: Dict[int, Machine] = {}
        self.yards: Dict[int, Yard] = {}
        self.status_changes: List[Dict] = []
        
        # Настройки режима работы
        self.realtime_mode = realtime_mode
        self.processing_speed = processing_speed
        
        # Для режима реального времени
        self.message_queue = Queue()
        self.processing_active = False
        self.processed_messages = 0
        self.start_time = None
        
        mode_text = "реального времени" if realtime_mode else "пакетной обработки"
        self.logger.info(f" Система мониторинга уборочных машин запущена в режиме {mode_text}")
    
    def load_yard_directory(self, yard_file_path: str) -> bool:
        """
        Загрузка справочника дворов из файла
        
        Args:
            yard_file_path: Путь к файлу со справочником дворов
            
        Returns:
            True если загрузка успешна, False в противном случае
        """
        try:
            self.logger.info(f" Загрузка справочника дворов из {yard_file_path}")
            
            yard_data = self.file_handler.load_yard_directory(yard_file_path)
            
            for yard_info in yard_data:
                yard = Yard(
                    yard_id=yard_info['yard_id'],
                    area=yard_info['area'],
                    cleaning_speed=yard_info['cleaning_speed']
                )
                self.yards[yard.yard_id] = yard
                
                self.logger.debug(
                    f"Двор загружен: ID={yard.yard_id}, "
                    f"Площадь={yard.area}м², "
                    f"Скорость={yard.cleaning_speed}м²/сек"
                )
            
            self.logger.info(f" Загружено {len(self.yards)} дворов")
            return True
            
        except Exception as e:
            self.logger.error(f" Ошибка загрузки справочника дворов: {e}")
            return False
    
    def process_machine_messages(self, messages_file_path: str) -> bool:
        """
        Обработка сообщений от машин
        
        Args:
            messages_file_path: Путь к файлу с сообщениями от машин
            
        Returns:
            True если обработка успешна, False в противном случае
        """
        try:
            self.logger.info(f"📨 Начало обработки сообщений из {messages_file_path}")
            
            messages = self.file_handler.load_machine_messages(messages_file_path)
            
            # Сортируем сообщения по времени для корректной обработки
            messages.sort(key=lambda x: x['timestamp'])
            
            if self.realtime_mode:
                return self._process_messages_realtime(messages)
            else:
                return self._process_messages_batch(messages)
            
        except Exception as e:
            self.logger.error(f" Ошибка обработки сообщений: {e}")
            return False
    
    def _process_messages_batch(self, messages: List[Dict]) -> bool:
        """Пакетная обработка сообщений (оригинальный режим)"""
        processed_count = 0
        for message_data in messages:
            if self._process_single_message(message_data):
                processed_count += 1
        
        self.logger.info(f" Обработано {processed_count} из {len(messages)} сообщений")
        return True
    
    def _process_messages_realtime(self, messages: List[Dict]) -> bool:
        """Обработка сообщений в режиме реального времени"""
        # Создаем симулятор передачи
        simulator = MessageTransmissionSimulator(
            message_interval=1.0,
            loss_rate=0.06,  # 6% потерь
            coordinate_error_rate=0.015,  # 1.5% ошибок
            max_delay=2.0
        )
        
        # Запускаем обработчик сообщений в отдельном потоке
        self.processing_active = True
        self.start_time = datetime.now()
        
        processor_thread = threading.Thread(
            target=self._message_processor_worker,
            daemon=True
        )
        processor_thread.start()
        
        # Запускаем симуляцию передачи сообщений
        simulator.simulate_transmission(messages, self.message_queue, self.processing_speed)
        
        # Ждем завершения обработки всех сообщений
        self.message_queue.join()
        self.processing_active = False
        
        # Выводим статистику передачи
        transmission_stats = simulator.get_transmission_stats()
        self._print_transmission_stats(transmission_stats)
        
        self.logger.info(f" Обработано {self.processed_messages} сообщений в режиме реального времени")
        return True
    
    def _message_processor_worker(self):
        """Обработчик сообщений в отдельном потоке (имитация работы с очередью)"""
        progress_counter = 0
        
        while self.processing_active:
            try:
                # Получаем сообщение из очереди
                message = self.message_queue.get(timeout=1.0)
                
                # Проверяем сигнал окончания
                if message is None:
                    self.message_queue.task_done()
                    break
                
                # Обрабатываем сообщение
                if self._process_single_message(message):
                    self.processed_messages += 1
                    progress_counter += 1
                    
                    # Выводим прогресс каждые 5 сообщений
                    if progress_counter % 5 == 0:
                        self._print_progress()
                
                # Отмечаем задачу как выполненную
                self.message_queue.task_done()
                
            except:
                # Таймаут или другая ошибка - продолжаем
                continue
    
    def _print_progress(self):
        """Вывод прогресса обработки в реальном времени"""
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = self.processed_messages / elapsed if elapsed > 0 else 0
            
            active_machines = sum(1 for m in self.machines.values() if m.current_yard_id)
            
            self.logger.info(f"📊 Обработано: {self.processed_messages} сообщений | "
                           f"Скорость: {rate:.1f} сообщ/сек | "
                           f"Активных машин: {active_machines}/{len(self.machines)}")
    
    def _print_transmission_stats(self, stats: Dict):
        """Вывод статистики передачи"""
        self.logger.info(" СТАТИСТИКА ПЕРЕДАЧИ СООБЩЕНИЙ:")
        self.logger.info(f"   Сгенерировано: {stats['total_generated']}")
        self.logger.info(f"   Доставлено: {stats['total_delivered']}")
        self.logger.info(f"   Потеряно: {stats['total_lost']}")
        self.logger.info(f"   Задержано: {stats['total_delayed']}")
        self.logger.info(f"   С ошибками: {stats['total_with_errors']}")
        self.logger.info(f"   Надежность доставки: {stats['delivery_rate']:.1f}%")
        self.logger.info(f"   Ошибки в данных: {stats['error_rate']:.1f}%")
    
    def _process_single_message(self, message_data: Dict) -> bool:
        """
        Обработка одного сообщения от машины
        
        Args:
            message_data: Данные сообщения
            
        Returns:
            True если сообщение обработано успешно
        """
        try:
            # Создаем объект сообщения
            message = MachineMessage(
                machine_id=message_data['machine_id'],
                timestamp=datetime.fromisoformat(message_data['timestamp']),
                coordinates=(message_data['x'], message_data['y']),
                yard_id=message_data.get('yard_id')
            )
            
            # Получаем или создаем машину
            if message.machine_id not in self.machines:
                self.machines[message.machine_id] = Machine(message.machine_id)
                self.logger.debug(f"🚚 Новая машина зарегистрирована: ID={message.machine_id}")
            
            machine = self.machines[message.machine_id]
            
            # Обновляем состояние машины и проверяем изменения статуса дворов
            status_change = self.cleaning_service.process_machine_update(
                machine, message, self.yards
            )
            
            if status_change:
                self.status_changes.append(status_change)
                self.logger.info(
                    f"🎯 Изменение статуса двора {status_change['yard_id']}: "
                    f"{status_change['old_status']} -> {status_change['new_status']}"
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f" Ошибка обработки сообщения: {e}")
            return False
    
    def generate_output_files(self, output_dir: str = "output") -> bool:
        """
        Генерация выходных файлов с результатами
        
        Args:
            output_dir: Директория для сохранения файлов
            
        Returns:
            True если файлы созданы успешно
        """
        try:
            self.logger.info(f" Создание выходных файлов в директории {output_dir}")
            
            Path(output_dir).mkdir(exist_ok=True)
            
            # Файл с изменениями статусов дворов
            yard_status_file = Path(output_dir) / "yard_status_changes.txt"
            self._write_yard_status_changes(yard_status_file)
            
            # Файл с финальными позициями машин
            machine_positions_file = Path(output_dir) / "final_machine_positions.txt"
            self._write_final_machine_positions(machine_positions_file)
            
            # Сводный отчет
            summary_file = Path(output_dir) / "summary_report.txt"
            self._write_summary_report(summary_file)
            
            self.logger.info(" Выходные файлы созданы успешно")
            return True
            
        except Exception as e:
            self.logger.error(f" Ошибка создания выходных файлов: {e}")
            return False
    
    def _write_yard_status_changes(self, file_path: Path):
        """Запись изменений статусов дворов в файл"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Изменения статусов дворов\n")
            f.write("# Формат: ID_двора,Статус,Время_изменения\n\n")
            
            if not self.status_changes:
                f.write("# Изменений статусов не зафиксировано\n")
                return
            
            for change in self.status_changes:
                f.write(
                    f"{change['yard_id']},"
                    f"{change['new_status'].value}%,"
                    f"{change['timestamp']}\n"
                )
    
    def _write_final_machine_positions(self, file_path: Path):
        """Запись финальных позиций машин в файл"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Финальные позиции машин\n")
            f.write("# Формат: ID_машины,X,Y,ID_двора\n\n")
            
            for machine in self.machines.values():
                yard_id = machine.current_yard_id if machine.current_yard_id else ""
                f.write(
                    f"{machine.machine_id},"
                    f"{machine.current_coordinates[0]},"
                    f"{machine.current_coordinates[1]},"
                    f"{yard_id}\n"
                )
    
    def _write_summary_report(self, file_path: Path):
        """Создание сводного отчета"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=== СВОДНЫЙ ОТЧЕТ СИСТЕМЫ МОНИТОРИНГА ===\n\n")
            
            f.write(f"Общее количество машин: {len(self.machines)}\n")
            f.write(f"Общее количество дворов: {len(self.yards)}\n")
            f.write(f"Изменений статусов: {len(self.status_changes)}\n")
            
            if self.realtime_mode:
                f.write(f"Режим работы: Реальное время (скорость x{self.processing_speed})\n")
                f.write(f"Обработано сообщений: {self.processed_messages}\n")
            else:
                f.write("Режим работы: Пакетная обработка\n")
            
            f.write("\n=== СТАТИСТИКА ПО ДВОРАМ ===\n")
            for yard in self.yards.values():
                progress = (yard.cleaned_area / yard.area * 100) if yard.area > 0 else 0
                f.write(
                    f"Двор {yard.yard_id}: {progress:.1f}% убрано "
                    f"(статус: {yard.status.value}%)\n"
                )
            
            f.write("\n=== АКТИВНЫЕ МАШИНЫ ===\n")
            for machine in self.machines.values():
                status = f"во дворе {machine.current_yard_id}" if machine.current_yard_id else "вне дворов"
                f.write(f"Машина {machine.machine_id}: {status}\n")


def main():
    """Главная функция программы"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Система мониторинга уборочных машин')
    parser.add_argument('--debug', action='store_true', help='Режим отладки')
    parser.add_argument('--realtime', action='store_true', help='Режим реального времени с симуляцией передачи')
    parser.add_argument('--speed', type=float, default=1.0, help='Множитель скорости для режима реального времени')
    parser.add_argument('--yards', default='data/yards.txt', help='Файл справочника дворов')
    parser.add_argument('--messages', default='data/machine_messages.json', help='Файл сообщений машин')
    parser.add_argument('--output', default='output', help='Директория для выходных файлов')
    
    args = parser.parse_args()
    
    # Инициализация системы
    system = CleaningMonitoringSystem(
        debug_mode=args.debug, 
        realtime_mode=args.realtime,
        processing_speed=args.speed
    )
    
    # Загрузка справочника дворов
    if not system.load_yard_directory(args.yards):
        print(" Ошибка загрузки справочника дворов")
        return 1
    
    # Обработка сообщений от машин
    if not system.process_machine_messages(args.messages):
        print(" Ошибка обработки сообщений от машин")
        return 1
    
    # Генерация выходных файлов
    if not system.generate_output_files(args.output):
        print(" Ошибка создания выходных файлов")
        return 1
    
    mode_text = "в режиме реального времени" if args.realtime else "в пакетном режиме"
    print(f" Обработка завершена успешно {mode_text}!")
    return 0


if __name__ == "__main__":
    exit(main())