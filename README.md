# 🚚 Система мониторинга уборочных машин / Cleaning Machine Monitoring System

[![Русский](https://img.shields.io/badge/Язык-Русский-blue)](#russian-version) [![English](https://img.shields.io/badge/Language-English-green)](#english-version)

---

## 📋 Technology Stack / Технологический стек

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-1.6+-60A5FA?style=for-the-badge&logo=poetry&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Threading](https://img.shields.io/badge/Threading-Multi--threaded-FF6B6B?style=for-the-badge&logo=processwire&logoColor=white)
![Queue](https://img.shields.io/badge/Queue-Real--time-4ECDC4?style=for-the-badge&logo=clockify&logoColor=white)
![Logging](https://img.shields.io/badge/Logging-Advanced-45B7D1?style=for-the-badge&logo=files&logoColor=white)

---

# 🚚 Система мониторинга уборочных машин (RU)
<a id="russian-version"></a>

Система для отслеживания работы уборочных машин и мониторинга процесса уборки дворов в **режиме реального времени** с симуляцией реальных условий передачи данных.

## 📋 Описание проекта

Данная система предназначена для обработки сообщений от специальных уборочных машин, оснащенных коммуникационными блоками. Система отслеживает координаты машин, время их работы во дворах и автоматически обновляет статусы уборки на основе убранной площади **с полной симуляцией реальных условий IoT-систем**.

### ✨ Основной функционал

#### 🚀 **Режимы работы**
- 📦 **Пакетная обработка** - традиционная обработка всех сообщений сразу
- ⚡ **Режим реального времени** - симуляция реальной передачи данных с:
  - Передачей сообщений ~1 раз в секунду
  - Потерей сообщений (6% по умолчанию)
  - Ошибками в координатах (1.5% сообщений)
  - Задержками передачи (до 2 секунд)
  - Многопоточной обработкой через очередь

#### 🔄 **Система передачи данных**
- 📡 **Реалистичная симуляция передачи** с интервалами ~1 секунда
- 📉 **Потеря сообщений** - небольшая часть сообщений не доходит
- ⚠️ **Ошибки координат** - единичные ошибки GPS (смещение, шум, перестановка)
- ⏱️ **Задержки доставки** - реалистичные задержки передачи
- 🔀 **Многопоточность** - реальная работа с очередью сообщений

#### 📊 **Мониторинг и аналитика**
- 🔄 **Итеративная обработка сообщений** из очереди в реальном времени
- 📍 **Отслеживание координат** и перемещений машин с уникальными маршрутами
- ⏱️ **Расчет времени работы** во дворах с учетом всех заездов
- 📈 **Автоматическое обновление статусов** уборки (0%, 20%, 40%, 60%, 80%, 100%)
- 🏠 **Управление справочником дворов** с площадью и скоростью уборки
- 📊 **Живой мониторинг** - статистика каждые 5 обработанных сообщений
- 📄 **Генерация отчетов** в текстовом формате

### 🎯 Особенности реализации

- ✅ **Соответствие техническому заданию**: Точная реализация всех требований
- 🔄 **Режим реального времени**: Передача "примерно 1 раз в секунду" 
- 📉 **Потери данных**: "доставка сообщений не гарантирована"
- ⚠️ **Ошибки измерений**: "единичные ошибки в определении координат"
- 🔀 **Очередь сообщений**: "итеративно, имитируя работу с очередью"
- ➕ **Суммирование времени**: от разных машин и заездов
- 🛡️ **Обработка ошибок**: валидация данных с детальным логированием
- 🐛 **Режим отладки**: подробное логирование для разработки

## 🛠️ Технологический стек

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Язык программирования** | Python | 3.11+ |
| **Управление зависимостями** | Poetry | 1.6.1 |
| **Контейнеризация** | Docker & Docker Compose | - |
| **Архитектура** | Модульная с разделением слоев | - |
| **Многопоточность** | Threading + Queue | Standard Library |
| **Логирование** | Стандартная библиотека logging | - |
| **Типизация** | Type hints | - |

### 📦 Основные зависимости

- `threading` - для многопоточной обработки
- `queue` - для реальной работы с очередью сообщений  
- `psutil` - для системной информации
- `dataclasses` - для моделей данных
- `pathlib` - для работы с файловой системой
- `json` - для обработки JSON сообщений

## 📁 Структура проекта

```
cleaning-machine-monitoring/
├── 📂 src/                          # Исходный код приложения
│   ├── 📂 models/                   # Модели данных
│   │   ├── machine.py              # Модель машины и сообщений
│   │   ├── yard.py                 # Модель двора и статусов
│   │   └── __init__.py
│   ├── 📂 services/                 # Бизнес-логика
│   │   ├── cleaning_service.py     # Сервис обработки уборки
│   │   ├── logging_service.py      # Сервис логирования
│   │   └── __init__.py
│   ├── 📂 utils/                    # Утилиты
│   │   ├── file_handler.py         # Обработка файлов
│   │   ├── data_generator.py       # Генератор тестовых данных с реалистичными интервалами
│   │   └── __init__.py
│   └── __init__.py
├── 📂 data/                         # Входные данные
│   ├── yards.txt                   # Справочник дворов
│   ├── machine_messages.json       # Сообщения от машин (с реалистичными временными метками)
│   └── generation_metadata.json    # Метаданные генерации
├── 📂 output/                       # Выходные файлы
│   ├── yard_status_changes.txt     # Изменения статусов дворов
│   ├── final_machine_positions.txt # Финальные позиции машин
│   └── summary_report.txt          # Сводный отчет
├── 📂 logs/                         # Файлы логов
├── 📄 main.py                      # **ОБНОВЛЕН** - Главный модуль с поддержкой реального времени
├── 📄 run.py                       # Скрипт быстрого запуска
├── 📄 Dockerfile                   # Конфигурация Docker
├── 📄 docker-compose.yml           # **ОБНОВЛЕН** - Конфигурация с режимом реального времени
├── 📄 pyproject.toml               # Конфигурация Poetry
└── 📄 README.md                    # **ОБНОВЛЕН** - Документация проекта
```

## 🚀 Запуск проекта

### 📋 Предварительные требования

- Python 3.11+
- Poetry (для управления зависимостями)
- Docker и Docker Compose (для контейнеризации)

### 🔧 Установка зависимостей

```bash
# Клонирование репозитория
git clone <repository-url>
cd cleaning-machine-monitoring

# Установка зависимостей через Poetry
poetry install

# Активация виртуального окружения
poetry shell
```

### 🎲 Генерация тестовых данных

```bash
# Генерация тестовых данных с реалистичными временными метками
python -m src.utils.data_generator

# Или через Poetry
poetry run python -m src.utils.data_generator

# С настройками длительности
python -m src.utils.data_generator --duration 30
```

### 💻 Ручной запуск

#### 📦 **Пакетный режим (оригинальный)**
```bash
# Базовый запуск - все сообщения обрабатываются мгновенно
python main.py

# С отладкой
python main.py --debug
```

#### ⚡ **Режим реального времени**
```bash
# Режим реального времени с симуляцией передачи
python main.py --debug --realtime

# С настройкой скорости (15x быстрее для демонстрации)
python main.py --debug --realtime --speed 15.0

# Реальная скорость (1 секунда = 1 секунда)
python main.py --debug --realtime --speed 1.0
```

#### 🔧 Параметры командной строки

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--debug` | Режим отладки с подробным логированием | `False` |
| `--realtime` | 🚀 **Режим реального времени с симуляцией передачи** | `False` |
| `--speed` | ⚡ **Множитель скорости для режима реального времени** | `1.0` |
| `--yards` | Путь к файлу справочника дворов | `data/yards.txt` |
| `--messages` | Путь к файлу сообщений машин | `data/machine_messages.json` |
| `--output` | Директория для выходных файлов | `output` |

### 🐳 Запуск в Docker

#### 📦 **Пакетный режим**
```bash
# Традиционная пакетная обработка
docker-compose up cleaning-monitor
```

#### ⚡ **Режим реального времени**
```bash
# 🚀 НОВЫЙ режим реального времени (рекомендуется)
docker-compose up cleaning-monitor-realtime

# Запуск в фоновом режиме
docker-compose up -d cleaning-monitor-realtime

# Просмотр логов в реальном времени
docker-compose logs -f cleaning-monitor-realtime
```

#### 🛠️ **Режим разработки**
```bash
# Интерактивный режим для разработки
docker-compose --profile dev up cleaning-monitor-dev

# Остановка всех контейнеров
docker-compose down
```

### 📊 Результаты работы

После выполнения в директории `output/` будут созданы:

1. **`yard_status_changes.txt`** - История изменений статусов дворов
2. **`final_machine_positions.txt`** - Финальные позиции всех машин  
3. **`summary_report.txt`** - Подробный сводный отчет с указанием режима работы

Логи работы системы сохраняются в директории `logs/`.

## 📈 Пример вывода режима реального времени

```
📡 Начало симуляции передачи 51 сообщений
⚙️ Параметры: интервал=1.00с, потери=6.0%, ошибки=1.5%
📉 Сообщение #6 от машины 1 потеряно при передаче
⏱️ Сообщение #8 задержано на 1.4с
⚠️ Сообщение #25 содержит ошибку координат
🚚 Новая машина зарегистрирована: ID=1
📊 Обработано: 5 сообщений | Скорость: 0.6 сообщ/сек | Активных машин: 1/5
🎯 Изменение статуса двора 7: YardStatus.PERCENT_0 -> YardStatus.PERCENT_100
📊 Обработано: 10 сообщений | Скорость: 0.5 сообщ/сек | Активных машин: 3/5
...
📡 Передача завершена. Потеряно: 4/51
📈 СТАТИСТИКА ПЕРЕДАЧИ СООБЩЕНИЙ:
   Сгенерировано: 51
   Доставлено: 47
   Потеряно: 4
   Задержано: 26
   С ошибками: 2
   Надежность доставки: 92.2%
   Ошибки в данных: 4.3%
✅ Обработано 47 сообщений в режиме реального времени
```

## 🆚 Сравнение режимов работы

| Характеристика | Пакетный режим | Режим реального времени |
|----------------|----------------|------------------------|
| **Обработка сообщений** | Мгновенная | ~1 секунда интервалы |
| **Потеря сообщений** | 0% | 6% (настраивается) |
| **Ошибки координат** | Нет | 1.5% сообщений |
| **Многопоточность** | Нет | ✅ Да (Queue + Threading) |
| **Мониторинг в реальном времени** | Только финальный результат | ✅ Живые обновления |
| **Симуляция IoT** | Нет | ✅ Полная симуляция |
| **Соответствие ТЗ** | Функциональное | ✅ **Полное соответствие** |

---

# 🚚 Cleaning Machine Monitoring System (EN)
<a id="english-version"></a>

A system for tracking cleaning machines and monitoring yard cleaning processes in **real-time** with realistic IoT data transmission simulation.

## 📋 Project Description

This system is designed to process messages from specialized cleaning machines equipped with communication units. The system tracks machine coordinates, their working time in yards, and automatically updates cleaning statuses based on cleaned area **with full simulation of real IoT system conditions**.

### ✨ Key Features

#### 🚀 **Operation Modes**
- 📦 **Batch Processing** - traditional processing of all messages at once
- ⚡ **Real-time Mode** - realistic data transmission simulation with:
  - Message transmission ~1 time per second
  - Message loss (6% by default)
  - Coordinate errors (1.5% of messages)
  - Transmission delays (up to 2 seconds)
  - Multi-threaded processing via queue

#### 🔄 **Data Transmission System**
- 📡 **Realistic transmission simulation** with ~1 second intervals
- 📉 **Message loss** - some messages don't reach the system
- ⚠️ **Coordinate errors** - individual GPS errors (offset, noise, swap)
- ⏱️ **Delivery delays** - realistic transmission delays
- 🔀 **Multi-threading** - real queue-based message processing

#### 📊 **Monitoring and Analytics**
- 🔄 **Iterative message processing** from queue in real-time
- 📍 **Coordinate tracking** and machine movement with unique routes
- ⏱️ **Work time calculation** in yards accounting for all visits
- 📈 **Automatic status updates** for cleaning progress (0%, 20%, 40%, 60%, 80%, 100%)
- 🏠 **Yard directory management** with area and cleaning speed data
- 📊 **Live monitoring** - statistics every 5 processed messages
- 📄 **Report generation** in text format

### 🎯 Implementation Features

- ✅ **Technical specification compliance**: Exact implementation of all requirements
- 🔄 **Real-time mode**: Transmission "approximately 1 time per second"
- 📉 **Data loss**: "message delivery is not guaranteed"
- ⚠️ **Measurement errors**: "individual errors in coordinate determination"
- 🔀 **Message queue**: "iteratively, simulating queue operation"
- ➕ **Time accumulation**: from different machines and visits
- 🛡️ **Error handling**: data validation with detailed logging
- 🐛 **Debug mode**: verbose logging for development

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Programming Language** | Python | 3.11+ |
| **Dependency Management** | Poetry | 1.6.1 |
| **Containerization** | Docker & Docker Compose | - |
| **Architecture** | Modular with layer separation | - |
| **Multi-threading** | Threading + Queue | Standard Library |
| **Logging** | Standard logging library | - |
| **Type Hints** | Type annotations | - |

### 📦 Main Dependencies

- `threading` - for multi-threaded processing
- `queue` - for real queue-based message processing
- `psutil` - for system information
- `dataclasses` - for data models
- `pathlib` - for filesystem operations
- `json` - for JSON message processing

## 📁 Project Structure

```
cleaning-machine-monitoring/
├── 📂 src/                          # Application source code
│   ├── 📂 models/                   # Data models
│   │   ├── machine.py              # Machine and message models
│   │   ├── yard.py                 # Yard and status models
│   │   └── __init__.py
│   ├── 📂 services/                 # Business logic
│   │   ├── cleaning_service.py     # Cleaning processing service
│   │   ├── logging_service.py      # Logging service
│   │   └── __init__.py
│   ├── 📂 utils/                    # Utilities
│   │   ├── file_handler.py         # File processing
│   │   ├── data_generator.py       # Test data generator with realistic timing
│   │   └── __init__.py
│   └── __init__.py
├── 📂 data/                         # Input data
│   ├── yards.txt                   # Yard directory
│   ├── machine_messages.json       # Machine messages (with realistic timestamps)
│   └── generation_metadata.json    # Generation metadata
├── 📂 output/                       # Output files
│   ├── yard_status_changes.txt     # Yard status changes
│   ├── final_machine_positions.txt # Final machine positions
│   └── summary_report.txt          # Summary report
├── 📂 logs/                         # Log files
├── 📄 main.py                      # **UPDATED** - Main module with real-time support
├── 📄 run.py                       # Quick start script
├── 📄 Dockerfile                   # Docker configuration
├── 📄 docker-compose.yml           # **UPDATED** - Configuration with real-time mode
├── 📄 pyproject.toml               # Poetry configuration
└── 📄 README.md                    # **UPDATED** - Project documentation
```

## 🚀 Running the Project

### 📋 Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker and Docker Compose (for containerization)

### 🔧 Installation

```bash
# Clone repository
git clone <repository-url>
cd cleaning-machine-monitoring

# Install dependencies via Poetry
poetry install

# Activate virtual environment
poetry shell
```

### 🎲 Generate Test Data

```bash
# Generate test data with realistic timestamps
python -m src.utils.data_generator

# Or via Poetry
poetry run python -m src.utils.data_generator

# With duration settings
python -m src.utils.data_generator --duration 30
```

### 💻 Manual Execution

#### 📦 **Batch Mode (Original)**
```bash
# Basic run - all messages processed instantly
python main.py

# With debugging
python main.py --debug
```

#### ⚡ **Real-time Mode**
```bash
# Real-time mode with transmission simulation
python main.py --debug --realtime

# With speed adjustment (15x faster for demo)
python main.py --debug --realtime --speed 15.0

# Real speed (1 second = 1 second)
python main.py --debug --realtime --speed 1.0
```

#### 🔧 Command Line Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--debug` | Debug mode with verbose logging | `False` |
| `--realtime` | 🚀 **Real-time mode with transmission simulation** | `False` |
| `--speed` | ⚡ **Speed multiplier for real-time mode** | `1.0` |
| `--yards` | Path to yard directory file | `data/yards.txt` |
| `--messages` | Path to machine messages file | `data/machine_messages.json` |
| `--output` | Output directory | `output` |

### 🐳 Docker Execution

#### 📦 **Batch Mode**
```bash
# Traditional batch processing
docker-compose up cleaning-monitor
```

#### ⚡ **Real-time Mode**
```bash
# 🚀 NEW real-time mode (recommended)
docker-compose up cleaning-monitor-realtime

# Background run
docker-compose up -d cleaning-monitor-realtime

# View real-time logs
docker-compose logs -f cleaning-monitor-realtime
```

#### 🛠️ **Development Mode**
```bash
# Interactive mode for development
docker-compose --profile dev up cleaning-monitor-dev

# Stop all containers
docker-compose down
```

### 📊 Results

After execution, the following files will be created in the `output/` directory:

1. **`yard_status_changes.txt`** - History of yard status changes
2. **`final_machine_positions.txt`** - Final positions of all machines
3. **`summary_report.txt`** - Detailed summary report with operation mode indication

System logs are saved in the `logs/` directory.

## 📈 Real-time Mode Output Example

```
📡 Starting transmission simulation of 51 messages
⚙️ Parameters: interval=1.00s, loss=6.0%, errors=1.5%
📉 Message #6 from machine 1 lost during transmission
⏱️ Message #8 delayed by 1.4s
⚠️ Message #25 contains coordinate error
🚚 New machine registered: ID=1
📊 Processed: 5 messages | Speed: 0.6 msg/sec | Active machines: 1/5
🎯 Yard 7 status change: YardStatus.PERCENT_0 -> YardStatus.PERCENT_100
📊 Processed: 10 messages | Speed: 0.5 msg/sec | Active machines: 3/5
...
📡 Transmission completed. Lost: 4/51
📈 TRANSMISSION STATISTICS:
   Generated: 51
   Delivered: 47
   Lost: 4
   Delayed: 26
   With errors: 2
   Delivery reliability: 92.2%
   Data errors: 4.3%
✅ Processed 47 messages in real-time mode
```

## 🆚 Operation Mode Comparison

| Characteristic | Batch Mode | Real-time Mode |
|----------------|------------|----------------|
| **Message Processing** | Instant | ~1 second intervals |
| **Message Loss** | 0% | 6% (configurable) |
| **Coordinate Errors** | None | 1.5% of messages |
| **Multi-threading** | No | ✅ Yes (Queue + Threading) |
| **Real-time Monitoring** | Final result only | ✅ Live updates |
| **IoT Simulation** | No | ✅ Full simulation |
| **Specification Compliance** | Functional | ✅ **Complete compliance** |

---

## 🎉 Key Achievements

- ✅ **Complete technical specification compliance**
- 🔄 **Real IoT system simulation**
- 🔀 **Multi-threaded queue-based processing**
- 📊 **Live monitoring capabilities** 
- 🛡️ **Robust error handling**
- 🐳 **Full Docker containerization**
- 📈 **Comprehensive logging and reporting**

## 📞 Support

For questions or issues, please check the logs in the `logs/` directory or examine the detailed output in debug mode.