"""
Утилиты для работы с файлами
Обработка входных и выходных файлов системы мониторинга
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional


class FileHandler:
    """
    Класс для обработки файловых операций
    
    Обеспечивает загрузку и сохранение данных в различных форматах,
    валидацию входных данных и обработку ошибок
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Инициализация обработчика файлов
        
        Args:
            logger: Логгер для записи событий
        """
        self.logger = logger
    
    def load_yard_directory(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Загрузка справочника дворов из текстового файла
        
        Ожидаемый формат файла (разделитель - запятая):
        yard_id,area,cleaning_speed
        
        Args:
            file_path: Путь к файлу справочника
            
        Returns:
            Список словарей с информацией о дворах
            
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если данные некорректны
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл справочника дворов не найден: {file_path}")
        
        self.logger.debug(f" Чтение справочника дворов из {file_path}")
        
        yards = []
        line_number = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line_number += 1
                    line = line.strip()
                    
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        # Парсим строку
                        parts = [part.strip() for part in line.split(',')]
                        
                        if len(parts) != 3:
                            raise ValueError(
                                f"Ожидается 3 поля, получено {len(parts)}: {line}"
                            )
                        
                        yard_data = {
                            'yard_id': int(parts[0]),
                            'area': float(parts[1]),
                            'cleaning_speed': float(parts[2])
                        }
                        
                        # Валидация данных
                        self._validate_yard_data(yard_data)
                        yards.append(yard_data)
                        
                    except (ValueError, IndexError) as e:
                        self.logger.warning(
                            f" Ошибка в строке {line_number}: {e}"
                        )
                        continue
        
        except Exception as e:
            self.logger.error(f" Ошибка чтения файла {file_path}: {e}")
            raise
        
        if not yards:
            raise ValueError("Не удалось загрузить ни одного двора из файла")
        
        self.logger.info(f" Загружено {len(yards)} дворов из справочника")
        return yards
    
    def load_machine_messages(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Загрузка сообщений от машин из JSON файла
        
        Args:
            file_path: Путь к JSON файлу с сообщениями
            
        Returns:
            Список сообщений от машин
            
        Raises:
            FileNotFoundError: Если файл не найден
            json.JSONDecodeError: Если файл содержит некорректный JSON
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл сообщений не найден: {file_path}")
        
        self.logger.debug(f" Чтение сообщений машин из {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Проверяем формат данных
            if isinstance(data, dict) and 'messages' in data:
                messages = data['messages']
            elif isinstance(data, list):
                messages = data
            else:
                raise ValueError("Неожиданный формат JSON файла")
            
            # Валидируем каждое сообщение
            valid_messages = []
            for i, message in enumerate(messages):
                try:
                    self._validate_message_data(message)
                    valid_messages.append(message)
                except ValueError as e:
                    self.logger.warning(f" Некорректное сообщение #{i + 1}: {e}")
                    continue
            
            if not valid_messages:
                raise ValueError("Не найдено ни одного корректного сообщения")
            
            self.logger.info(
                f" Загружено {len(valid_messages)} сообщений "
                f"(пропущено {len(messages) - len(valid_messages)})"
            )
            
            return valid_messages
            
        except json.JSONDecodeError as e:
            self.logger.error(f" Ошибка парсинга JSON: {e}")
            raise
        except Exception as e:
            self.logger.error(f" Ошибка чтения файла {file_path}: {e}")
            raise
    
    def save_yard_status_changes(self, status_changes: List[Dict], output_file: str):
        """
        Сохранение изменений статусов дворов в файл
        
        Args:
            status_changes: Список изменений статусов
            output_file: Путь к выходному файлу
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.debug(f" Сохранение изменений статусов в {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write("# Изменения статусов дворов\n")
                file.write("# Формат: ID_двора,Статус,Время_изменения\n\n")
                
                if not status_changes:
                    file.write("# Изменений статусов не зафиксировано\n")
                    return
                
                for change in status_changes:
                    file.write(
                        f"{change['yard_id']},"
                        f"{change['new_status'].value}%,"
                        f"{change['timestamp']}\n"
                    )
            
            self.logger.info(f" Сохранено {len(status_changes)} изменений статусов")
            
        except Exception as e:
            self.logger.error(f" Ошибка сохранения изменений статусов: {e}")
            raise
    
    def save_machine_positions(self, machines: Dict, output_file: str):
        """
        Сохранение финальных позиций машин в файл
        
        Args:
            machines: Словарь машин
            output_file: Путь к выходному файлу
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.debug(f" Сохранение позиций машин в {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write("# Финальные позиции машин\n")
                file.write("# Формат: ID_машины,X,Y,ID_двора\n\n")
                
                for machine in machines.values():
                    yard_id = machine.current_yard_id if machine.current_yard_id else ""
                    file.write(
                        f"{machine.machine_id},"
                        f"{machine.current_coordinates[0]},"
                        f"{machine.current_coordinates[1]},"
                        f"{yard_id}\n"
                    )
            
            self.logger.info(f" Сохранены позиции {len(machines)} машин")
            
        except Exception as e:
            self.logger.error(f" Ошибка сохранения позиций машин: {e}")
            raise
    
    def create_summary_report(self, machines: Dict, yards: Dict, 
                            status_changes: List, output_file: str):
        """
        Создание сводного отчета
        
        Args:
            machines: Словарь машин
            yards: Словарь дворов
            status_changes: Список изменений статусов
            output_file: Путь к файлу отчета
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.debug(f" Создание сводного отчета в {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                self._write_report_header(file)
                self._write_general_statistics(file, machines, yards, status_changes)
                self._write_yard_details(file, yards)
                self._write_machine_details(file, machines)
                self._write_status_changes_summary(file, status_changes)
            
            self.logger.info(" Сводный отчет создан")
            
        except Exception as e:
            self.logger.error(f" Ошибка создания отчета: {e}")
            raise
    
    def _validate_yard_data(self, yard_data: Dict[str, Any]):
        """
        Валидация данных двора
        
        Args:
            yard_data: Данные двора для валидации
            
        Raises:
            ValueError: Если данные некорректны
        """
        required_fields = ['yard_id', 'area', 'cleaning_speed']
        
        for field in required_fields:
            if field not in yard_data:
                raise ValueError(f"Отсутствует обязательное поле: {field}")
        
        if yard_data['yard_id'] <= 0:
            raise ValueError("ID двора должен быть положительным числом")
        
        if yard_data['area'] <= 0:
            raise ValueError("Площадь двора должна быть положительным числом")
        
        if yard_data['cleaning_speed'] <= 0:
            raise ValueError("Скорость уборки должна быть положительным числом")
    
    def _validate_message_data(self, message: Dict[str, Any]):
        """
        Валидация данных сообщения от машины
        
        Args:
            message: Данные сообщения для валидации
            
        Raises:
            ValueError: Если данные некорректны
        """
        required_fields = ['machine_id', 'timestamp', 'x', 'y']
        
        for field in required_fields:
            if field not in message:
                raise ValueError(f"Отсутствует обязательное поле: {field}")
        
        if not isinstance(message['machine_id'], int) or message['machine_id'] <= 0:
            raise ValueError("machine_id должен быть положительным целым числом")
        
        if not isinstance(message['x'], (int, float)):
            raise ValueError("Координата x должна быть числом")
        
        if not isinstance(message['y'], (int, float)):
            raise ValueError("Координата y должна быть числом")
        
        # Проверяем формат времени
        if not isinstance(message['timestamp'], str):
            raise ValueError("timestamp должен быть строкой")
        
        # Проверяем yard_id если он есть
        if 'yard_id' in message and message['yard_id'] is not None:
            if not isinstance(message['yard_id'], int) or message['yard_id'] <= 0:
                raise ValueError("yard_id должен быть положительным целым числом или null")
    
    def _write_report_header(self, file):
        """Запись заголовка отчета"""
        from datetime import datetime
        
        file.write("=" * 60 + "\n")
        file.write("СВОДНЫЙ ОТЧЕТ СИСТЕМЫ МОНИТОРИНГА УБОРОЧНЫХ МАШИН\n")
        file.write("=" * 60 + "\n")
        file.write(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    def _write_general_statistics(self, file, machines, yards, status_changes):
        """Запись общей статистики"""
        file.write("ОБЩАЯ СТАТИСТИКА\n")
        file.write("-" * 20 + "\n")
        file.write(f"Общее количество машин: {len(machines)}\n")
        file.write(f"Общее количество дворов: {len(yards)}\n")
        file.write(f"Изменений статусов: {len(status_changes)}\n")
        
        # Статистика по машинам
        active_machines = sum(1 for m in machines.values() if m.current_yard_id is not None)
        file.write(f"Активных машин: {active_machines}\n")
        file.write(f"Простаивающих машин: {len(machines) - active_machines}\n")
        
        # Статистика по дворам
        cleaned_yards = sum(1 for y in yards.values() if y.is_fully_cleaned())
        partially_cleaned = sum(1 for y in yards.values() 
                              if y.get_completion_percentage() > 0 and not y.is_fully_cleaned())
        untouched = len(yards) - cleaned_yards - partially_cleaned
        
        file.write(f"Полностью убранных дворов: {cleaned_yards}\n")
        file.write(f"Частично убранных дворов: {partially_cleaned}\n")
        file.write(f"Нетронутых дворов: {untouched}\n\n")
    
    def _write_yard_details(self, file, yards):
        """Запись детальной информации по дворам"""
        file.write("ДЕТАЛИ ПО ДВОРАМ\n")
        file.write("-" * 20 + "\n")
        
        for yard in sorted(yards.values(), key=lambda y: y.yard_id):
            progress = yard.get_completion_percentage()
            file.write(
                f"Двор {yard.yard_id:3d}: {progress:5.1f}% убрано "
                f"({yard.cleaned_area:6.1f}/{yard.area:6.1f} м²), "
                f"статус: {yard.status.value:3d}%, "
                f"время работы: {yard.total_work_time:6.1f}с\n"
            )
        file.write("\n")
    
    def _write_machine_details(self, file, machines):
        """Запись детальной информации по машинам"""
        file.write("ДЕТАЛИ ПО МАШИНАМ\n")
        file.write("-" * 20 + "\n")
        
        for machine in sorted(machines.values(), key=lambda m: m.machine_id):
            status_info = machine.get_current_status()
            location = f"двор {machine.current_yard_id}" if machine.current_yard_id else "вне дворов"
            coords = f"({machine.current_coordinates[0]}, {machine.current_coordinates[1]})"
            
            file.write(
                f"Машина {machine.machine_id:3d}: {location:15s} "
                f"в координатах {coords:15s}, "
                f"работала в {status_info['total_yards_worked']} дворах\n"
            )
        file.write("\n")
    
    def _write_status_changes_summary(self, file, status_changes):
        """Запись сводки изменений статусов"""
        file.write("ИЗМЕНЕНИЯ СТАТУСОВ\n")
        file.write("-" * 20 + "\n")
        
        if not status_changes:
            file.write("Изменений статусов не зафиксировано\n")
            return
        
        # Группируем изменения по дворам
        changes_by_yard = {}
        for change in status_changes:
            yard_id = change['yard_id']
            if yard_id not in changes_by_yard:
                changes_by_yard[yard_id] = []
            changes_by_yard[yard_id].append(change)
        
        for yard_id in sorted(changes_by_yard.keys()):
            changes = changes_by_yard[yard_id]
            file.write(f"Двор {yard_id}: {len(changes)} изменений статуса\n")
            
            for change in changes:
                file.write(
                    f"  {change['old_status'].value}% → {change['new_status'].value}% "
                    f"в {change['timestamp'][:19]} (машина {change['machine_id']})\n"
                )
        file.write("\n")
    
    def backup_file(self, file_path: str, backup_suffix: str = ".backup") -> Optional[str]:
        """
        Создание резервной копии файла
        
        Args:
            file_path: Путь к файлу
            backup_suffix: Суффикс для резервной копии
            
        Returns:
            Путь к резервной копии или None в случае ошибки
        """
        try:
            original_path = Path(file_path)
            if not original_path.exists():
                return None
            
            backup_path = original_path.with_suffix(original_path.suffix + backup_suffix)
            
            import shutil
            shutil.copy2(original_path, backup_path)
            
            self.logger.debug(f" Создана резервная копия: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.warning(f" Не удалось создать резервную копию {file_path}: {e}")
            return None