"""
Простой скрипт запуска системы мониторинга уборочных машин
"""

import subprocess
import sys
from pathlib import Path

def create_directories():
    """Создание необходимых директорий"""
    directories = ['data', 'output', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print(" Директории созданы")

def generate_data():
    """Генерация тестовых данных"""
    print(" Генерация тестовых данных...")
    try:
        subprocess.run([sys.executable, "-m", "src.utils.data_generator"], check=True)
        print(" Тестовые данные сгенерированы")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Ошибка генерации данных: {e}")
        return False

def run_system():
    """Запуск системы мониторинга"""
    print(" Запуск системы мониторинга...")
    try:
        subprocess.run([sys.executable, "main.py", "--debug"], check=True)
        print(" Система выполнена успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Ошибка выполнения: {e}")
        return False

def main():
    print(" Система мониторинга уборочных машин")
    print("=" * 40)
    
    # Создание директорий
    create_directories()
    
    # Генерация данных
    if not generate_data():
        return 1
    
    # Запуск системы
    if not run_system():
        return 1
    
    print("\n Выполнение завершено!")
    print("📂 Результаты в директории: output/")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())