"""
Сервис логирования
Настройка и конфигурация системы логирования для мониторинга уборочных машин
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """
    Форматтер с цветным выводом для консоли
    Добавляет цвета к различным уровням логирования
    """
    
    # Цветовые коды ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Голубой
        'INFO': '\033[32m',       # Зеленый
        'WARNING': '\033[33m',    # Желтый
        'ERROR': '\033[31m',      # Красный
        'CRITICAL': '\033[35m',   # Пурпурный
        'RESET': '\033[0m'        # Сброс цвета
    }
    
    def format(self, record):
        """
        Форматирование записи лога с добавлением цветов
        
        Args:
            record: Запись лога
            
        Returns:
            Отформатированная строка с цветами
        """
        # Сохраняем оригинальное сообщение
        original_msg = record.getMessage()
        
        # Добавляем цвет к уровню логирования
        level_color = self.COLORS.get(record.levelname, '')
        reset_color = self.COLORS['RESET']
        
        # Создаем цветной префикс уровня
        colored_level = f"{level_color}{record.levelname:8}{reset_color}"
        
        # Заменяем уровень в записи
        record.levelname = colored_level
        
        # Форматируем запись
        formatted = super().format(record)
        
        # Восстанавливаем оригинальные значения
        record.levelname = record.levelname.strip()
        
        return formatted


class CleaningSystemLogger:
    """
    Специализированный логгер для системы мониторинга уборочных машин
    Предоставляет дополнительные методы для логирования специфичных событий
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Инициализация системного логгера
        
        Args:
            logger: Базовый логгер
        """
        self.logger = logger
        self._start_time = datetime.now()
    
    def log_machine_event(self, machine_id: int, event: str, details: str = ""):
        """
        Логирование события машины
        
        Args:
            machine_id: ID машины
            event: Тип события
            details: Дополнительные детали
        """
        message = f"🚚 Машина {machine_id}: {event}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_yard_event(self, yard_id: int, event: str, details: str = ""):
        """
        Логирование события двора
        
        Args:
            yard_id: ID двора
            event: Тип события
            details: Дополнительные детали
        """
        message = f"🏠 Двор {yard_id}: {event}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def log_status_change(self, yard_id: int, old_status: int, new_status: int, machine_id: int):
        """
        Логирование изменения статуса двора
        
        Args:
            yard_id: ID двора
            old_status: Старый статус
            new_status: Новый статус
            machine_id: ID машины, вызвавшей изменение
        """
        self.logger.info(
            f"📊 Статус двора {yard_id} изменен: {old_status}% → {new_status}% "
            f"(машина {machine_id})"
        )
    
    def log_system_stats(self, stats: dict):
        """
        Логирование системной статистики
        
        Args:
            stats: Словарь со статистикой
        """
        self.logger.info("📈 Системная статистика:")
        for key, value in stats.items():
            if isinstance(value, float):
                self.logger.info(f"   {key}: {value:.2f}")
            else:
                self.logger.info(f"   {key}: {value}")
    
    def log_performance_metrics(self, messages_processed: int, processing_time: float):
        """
        Логирование метрик производительности
        
        Args:
            messages_processed: Количество обработанных сообщений
            processing_time: Время обработки в секундах
        """
        rate = messages_processed / processing_time if processing_time > 0 else 0
        self.logger.info(
            f"⚡ Производительность: {messages_processed} сообщений за {processing_time:.2f}с "
            f"({rate:.1f} сообщ/сек)"
        )
    
    def log_error_with_context(self, error: Exception, context: str):
        """
        Логирование ошибки с контекстом
        
        Args:
            error: Исключение
            context: Контекст возникновения ошибки
        """
        self.logger.error(f"❌ Ошибка в {context}: {type(error).__name__}: {error}")
    
    def get_uptime(self) -> str:
        """
        Получение времени работы системы
        
        Returns:
            Строка с временем работы
        """
        uptime = datetime.now() - self._start_time
        return str(uptime).split('.')[0]  # Убираем микросекунды


def setup_logging(debug_mode: bool = False, log_file: Optional[str] = None) -> CleaningSystemLogger:
    """
    Настройка системы логирования
    
    Args:
        debug_mode: Включить режим отладки
        log_file: Путь к файлу логов (опционально)
        
    Returns:
        Настроенный логгер системы
    """
    # Определяем уровень логирования
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # Создаем корневой логгер
    logger = logging.getLogger('cleaning_system')
    logger.setLevel(log_level)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Создаем директорию для логов
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"cleaning_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Форматы сообщений
    console_format = '%(asctime)s | %(levelname)s | %(message)s'
    file_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
    
    # Настройка консольного вывода
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if sys.stdout.isatty():  # Если вывод в терминал, используем цвета
        console_formatter = ColoredFormatter(console_format)
    else:  # Если вывод перенаправлен, не используем цвета
        console_formatter = logging.Formatter(console_format)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Настройка файлового вывода
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # В файл записываем все
    file_formatter = logging.Formatter(file_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Создаем специализированный логгер
    system_logger = CleaningSystemLogger(logger)
    
    # Логируем инициализацию
    logger.info(" Система логирования инициализирована")
    logger.info(f" Файл логов: {log_file}")
    logger.info(f" Режим отладки: {'включен' if debug_mode else 'выключен'}")
    
    return system_logger


def create_file_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Создание отдельного файлового логгера
    
    Args:
        name: Имя логгера
        log_file: Путь к файлу
        level: Уровень логирования
        
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Создаем директорию если нужно
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Настраиваем обработчик
    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setLevel(level)
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger


def log_system_info():
    """
    Логирование информации о системе
    """
    logger = logging.getLogger('cleaning_system')
    
    import platform
    import psutil
    
    logger.info("💻 Информация о системе:")
    logger.info(f"   Платформа: {platform.platform()}")
    logger.info(f"   Python: {platform.python_version()}")
    logger.info(f"   Процессор: {platform.processor()}")
    logger.info(f"   ОЗУ: {psutil.virtual_memory().total // (1024**3)} ГБ")
    logger.info(f"   Диск: {psutil.disk_usage('/').total // (1024**3)} ГБ")


def setup_debug_logging() -> CleaningSystemLogger:
    """
    Быстрая настройка логирования для отладки
    
    Returns:
        Логгер в режиме отладки
    """
    return setup_logging(debug_mode=True)


def setup_production_logging(log_dir: str = "logs") -> CleaningSystemLogger:
    """
    Настройка логирования для продакшена
    
    Args:
        log_dir: Директория для логов
        
    Returns:
        Логгер для продакшена
    """
    log_file = Path(log_dir) / f"production_{datetime.now().strftime('%Y%m%d')}.log"
    return setup_logging(debug_mode=False, log_file=str(log_file))