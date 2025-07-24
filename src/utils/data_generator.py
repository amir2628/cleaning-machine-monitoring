"""
Генератор тестовых данных
Создание справочника дворов и сообщений от машин для тестирования системы
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class TestDataGenerator:
    """
    Генератор тестовых данных для системы мониторинга уборочных машин
    
    Создает реалистичные данные с учетом требований задачи:
    - Минимум 10 дворов, 80% должны быть подвергнуты уборке
    - Минимум 5 машин, минимум 5 сообщений на машину
    - 80% сообщений попадают во дворы
    - Реалистичные временные интервалы ~1 секунда между сообщениями
    """
    
    def __init__(self, seed: int = 42):
        """
        Инициализация генератора
        
        Args:
            seed: Сид для воспроизводимости результатов
        """
        random.seed(seed)
        self.yards: List[Dict] = []
        self.machines: List[int] = []
        self.messages: List[Dict] = []
        
        # Конфигурация генерации
        self.config = {
            'min_yards': 10,
            'max_yards': 15,
            'min_machines': 5,
            'max_machines': 8,
            'messages_per_machine': (12, 20),  # Увеличено для лучшего покрытия дворов
            'yard_area_range': (100, 1000),
            'cleaning_speed_range': (0.5, 3.0),
            'coordinate_range': (-100, 100),
            'simulation_duration_minutes': 60,  # Увеличено до 60 минут для большего количества сообщений
            'yard_coverage_percent': 80,
            'message_in_yard_percent': 80,
            'base_message_interval': 1.0,  # Базовый интервал в секундах
            'interval_variance': 0.2,  # Уменьшена вариативность до ±20%
        }
    
    def generate_all_data(self, output_dir: str = "data") -> bool:
        """
        Генерация всех тестовых данных
        
        Args:
            output_dir: Директория для сохранения файлов
            
        Returns:
            True если генерация успешна
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            print(" Генерация тестовых данных...")
            
            # Генерируем дворы
            self._generate_yards()
            print(f" Сгенерировано {len(self.yards)} дворов")
            
            # Генерируем машины
            self._generate_machines()
            print(f" Сгенерировано {len(self.machines)} машин")
            
            # Генерируем сообщения с реалистичными временными метками
            self._generate_realistic_messages()
            print(f" Сгенерировано {len(self.messages)} сообщений")
            
            # Сохраняем данные
            self._save_yards(output_path / "yards.txt")
            self._save_messages(output_path / "machine_messages.json")
            self._save_metadata(output_path / "generation_metadata.json")
            
            print(f" Данные сохранены в директории {output_dir}")
            self._print_statistics()
            
            return True
            
        except Exception as e:
            print(f" Ошибка генерации данных: {e}")
            return False
    
    def _generate_yards(self):
        """Генерация дворов"""
        num_yards = random.randint(self.config['min_yards'], self.config['max_yards'])
        
        for yard_id in range(1, num_yards + 1):
            area = random.uniform(*self.config['yard_area_range'])
            cleaning_speed = random.uniform(*self.config['cleaning_speed_range'])
            
            # Округляем для удобства
            area = round(area, 1)
            cleaning_speed = round(cleaning_speed, 2)
            
            self.yards.append({
                'yard_id': yard_id,
                'area': area,
                'cleaning_speed': cleaning_speed
            })
    
    def _generate_machines(self):
        """Генерация списка машин"""
        num_machines = random.randint(self.config['min_machines'], self.config['max_machines'])
        self.machines = list(range(1, num_machines + 1))
    
    def _generate_realistic_messages(self):
        """
        Генерация сообщений с реалистичными временными интервалами
        """
        # Определяем дворы, которые будут убираться (80% от общего количества)
        yards_to_clean = self._select_yards_for_cleaning()
        
        # Начальное время - текущее время минус длительность симуляции
        start_time = datetime.now() - timedelta(minutes=self.config['simulation_duration_minutes'])
        
        # Сначала генерируем сообщения для каждой машины (минимум 5)
        all_messages = []
        
        for machine_id in self.machines:
            # Генерируем минимум сообщений для этой машины
            messages_for_machine = random.randint(*self.config['messages_per_machine'])
            machine_messages = []
            
            current_time = start_time + timedelta(minutes=random.uniform(0, 5))  # Небольшой сдвиг для каждой машины
            
            for msg_idx in range(messages_for_machine):
                # Определяем, должно ли сообщение быть во дворе (80% вероятность)
                should_be_in_yard = random.random() < (self.config['message_in_yard_percent'] / 100)
                
                if should_be_in_yard and yards_to_clean:
                    # Сообщение во дворе
                    yard_id = random.choice(yards_to_clean)
                    position = self._get_yard_position_with_variance(yard_id, machine_id)
                else:
                    # Сообщение вне дворов
                    yard_id = None
                    position = self._random_position_with_machine_variance(machine_id)
                
                # Создаем сообщение
                message = {
                    'machine_id': machine_id,
                    'timestamp': current_time.isoformat(),
                    'x': round(position[0], 2),
                    'y': round(position[1], 2),
                    'yard_id': yard_id
                }
                
                machine_messages.append(message)
                
                # Добавляем реалистичный интервал (небольшие вариации для каждой машины)
                interval = self._get_realistic_interval() + random.uniform(-0.2, 0.2)
                current_time += timedelta(seconds=max(0.5, interval))
            
            all_messages.extend(machine_messages)
        
        # Сортируем все сообщения по времени
        all_messages.sort(key=lambda x: x['timestamp'])
        
        # Корректируем временные метки для реалистичных интервалов
        self.messages = self._normalize_message_intervals(all_messages)
        
        # Проверяем и исправляем покрытие дворов
        self._validate_and_fix_yard_coverage()
        
        # Проверяем и исправляем распределение сообщений по дворам
        self._validate_and_fix_message_distribution()
        
        # Добавляем небольшую потерю сообщений на уровне генерации
        self._add_generation_losses()
    
    def _normalize_message_intervals(self, messages: List[Dict]) -> List[Dict]:
        """
        Нормализация интервалов между сообщениями для достижения ~1 секунды
        """
        if len(messages) <= 1:
            return messages
        
        # Создаем новый список с нормализованными временными метками
        normalized_messages = []
        start_time = datetime.fromisoformat(messages[0]['timestamp'])
        
        for i, message in enumerate(messages):
            if i == 0:
                # Первое сообщение остается как есть
                normalized_messages.append(message.copy())
            else:
                # Вычисляем новое время с правильным интервалом
                interval = self._get_realistic_interval()
                new_time = start_time + timedelta(seconds=i * interval)
                
                new_message = message.copy()
                new_message['timestamp'] = new_time.isoformat()
                normalized_messages.append(new_message)
        
        return normalized_messages
    
    def _get_realistic_interval(self) -> float:
        """
        Генерация реалистичного интервала между сообщениями (~1 секунда с небольшими вариациями)
        """
        base_interval = self.config['base_message_interval']
        variance = self.config['interval_variance']
        
        # Используем нормальное распределение с ограничениями
        interval = random.normalvariate(base_interval, base_interval * variance)
        
        # Ограничиваем интервал разумными пределами (0.7-1.5 секунды)
        return max(0.7, min(1.5, interval))
    
    def _get_yard_position_with_variance(self, yard_id: int, machine_id: int) -> Tuple[float, float]:
        """
        Получение позиции во дворе с вариациями для разных машин
        """
        base_position = self._get_yard_position(yard_id)
        
        # Добавляем уникальные вариации для каждой машины
        machine_seed = hash((yard_id, machine_id)) % 10000
        random.seed(machine_seed)
        
        # Небольшие вариации в пределах двора
        x_offset = random.uniform(-8, 8)
        y_offset = random.uniform(-8, 8)
        
        # Восстанавливаем общий сид
        random.seed(42)
        
        return (base_position[0] + x_offset, base_position[1] + y_offset)
    
    def _random_position_with_machine_variance(self, machine_id: int) -> Tuple[float, float]:
        """
        Генерация случайной позиции с учетом машины
        """
        # Создаем уникальную позицию для каждой машины
        machine_seed = hash(machine_id) % 10000
        random.seed(machine_seed)
        
        x = random.uniform(*self.config['coordinate_range'])
        y = random.uniform(*self.config['coordinate_range'])
        
        # Добавляем небольшую случайность
        x += random.uniform(-15, 15)
        y += random.uniform(-15, 15)
        
        # Восстанавливаем общий сид
        random.seed(42)
        
        return (x, y)
    
    def _validate_and_fix_message_distribution(self):
        """
        Проверка и исправление распределения сообщений (80% во дворах)
        """
        messages_in_yards = sum(1 for msg in self.messages if msg['yard_id'] is not None)
        current_percentage = (messages_in_yards / len(self.messages) * 100) if self.messages else 0
        
        target_percentage = self.config['message_in_yard_percent']
        
        if current_percentage < target_percentage:
            print(f" Сообщений во дворах {current_percentage:.1f}% < {target_percentage}%, исправляем...")
            
            # Находим сообщения вне дворов
            messages_outside = [i for i, msg in enumerate(self.messages) if msg['yard_id'] is None]
            
            if messages_outside:
                # Сколько сообщений нужно переместить во дворы
                target_in_yards = int(len(self.messages) * target_percentage / 100)
                messages_to_move = target_in_yards - messages_in_yards
                messages_to_move = min(messages_to_move, len(messages_outside))
                
                # Выбираем случайные сообщения для перемещения
                indices_to_move = random.sample(messages_outside, messages_to_move)
                yards_to_clean = self._select_yards_for_cleaning()
                
                for idx in indices_to_move:
                    # Перемещаем сообщение во двор
                    yard_id = random.choice(yards_to_clean)
                    machine_id = self.messages[idx]['machine_id']
                    new_position = self._get_yard_position_with_variance(yard_id, machine_id)
                    
                    self.messages[idx]['yard_id'] = yard_id
                    self.messages[idx]['x'] = round(new_position[0], 2)
                    self.messages[idx]['y'] = round(new_position[1], 2)
                
                print(f" Перемещено {messages_to_move} сообщений во дворы")
    
    def _select_yards_for_cleaning(self) -> List[int]:
        """
        Выбор дворов для уборки (80% от общего количества)
        
        Returns:
            Список ID дворов для уборки
        """
        total_yards = len(self.yards)
        num_to_clean = max(1, int(total_yards * self.config['yard_coverage_percent'] / 100))
        
        yard_ids = [yard['yard_id'] for yard in self.yards]
        return random.sample(yard_ids, num_to_clean)
    
    def _validate_and_fix_yard_coverage(self):
        """
        Проверка и исправление покрытия дворов до достижения 80%
        """
        yards_mentioned = set(msg['yard_id'] for msg in self.messages if msg['yard_id'] is not None)
        current_coverage = len(yards_mentioned) / len(self.yards) * 100 if self.yards else 0
        
        if current_coverage < 80:
            print(f" Покрытие дворов {current_coverage:.1f}% < 80%, добавляем сообщения...")
            
            # Находим дворы, которые не посещались
            all_yard_ids = [yard['yard_id'] for yard in self.yards]
            unvisited_yards = [y_id for y_id in all_yard_ids if y_id not in yards_mentioned]
            
            # Сколько дворов нужно добавить для достижения 80%
            target_yards_count = int(len(self.yards) * 0.8)
            yards_to_add = target_yards_count - len(yards_mentioned)
            
            if yards_to_add > 0 and unvisited_yards:
                # Выбираем случайные непосещенные дворы
                yards_to_visit = random.sample(
                    unvisited_yards, 
                    min(yards_to_add, len(unvisited_yards))
                )
                
                # Добавляем сообщения для этих дворов с реалистичными временными метками
                for yard_id in yards_to_visit:
                    # Выбираем случайную машину
                    machine_id = random.choice(self.machines)
                    
                    # Создаем 2-3 сообщения для этого двора
                    num_messages = random.randint(2, 3)
                    
                    # Вставляем сообщения в случайные места временной линии
                    for i in range(num_messages):
                        # Выбираем случайное время из существующих сообщений
                        if self.messages:
                            random_msg = random.choice(self.messages)
                            base_time = datetime.fromisoformat(random_msg['timestamp'])
                            # Добавляем небольшое смещение
                            time_offset = random.uniform(-300, 300)  # ±5 минут
                            new_time = base_time + timedelta(seconds=time_offset)
                        else:
                            new_time = datetime.now() - timedelta(minutes=30)
                        
                        yard_position = self._get_yard_position_with_variance(yard_id, machine_id)
                        
                        message = {
                            'machine_id': machine_id,
                            'timestamp': new_time.isoformat(),
                            'x': round(yard_position[0], 2),
                            'y': round(yard_position[1], 2),
                            'yard_id': yard_id
                        }
                        self.messages.append(message)
                
                # Пересортируем сообщения по времени
                self.messages.sort(key=lambda x: x['timestamp'])
                print(f" Добавлено сообщений для {len(yards_to_visit)} дворов")
    
    def _random_position(self) -> Tuple[float, float]:
        """Генерация случайной позиции"""
        x = random.uniform(*self.config['coordinate_range'])
        y = random.uniform(*self.config['coordinate_range'])
        return (x, y)
    
    def _get_yard_position(self, yard_id: int) -> Tuple[float, float]:
        """
        Получение позиции двора
        
        Args:
            yard_id: ID двора
            
        Returns:
            Координаты двора
        """
        # Генерируем фиксированные координаты для каждого двора
        # Используем yard_id как сид для воспроизводимости
        random.seed(yard_id * 1000)
        x = random.uniform(*self.config['coordinate_range'])
        y = random.uniform(*self.config['coordinate_range'])
        
        # Восстанавливаем общий сид
        random.seed(42)
        
        return (x, y)
    
    def _add_generation_losses(self):
        """Симуляция потерь сообщений на уровне генерации (дополнительно к потерям при передаче)"""
        # Удаляем случайные сообщения для имитации потерь на уровне генерации данных
        loss_rate = 0.02  # Уменьшили до 2% потерь при генерации
        num_to_remove = int(len(self.messages) * loss_rate)
        
        if num_to_remove > 0:
            indices_to_remove = random.sample(range(len(self.messages)), num_to_remove)
            # Удаляем в обратном порядке, чтобы не нарушить индексы
            for index in sorted(indices_to_remove, reverse=True):
                del self.messages[index]
    
    def _save_yards(self, file_path: Path):
        """Сохранение справочника дворов"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Справочник дворов\n")
            f.write("# Формат: yard_id,area,cleaning_speed\n")
            
            for yard in self.yards:
                f.write(f"{yard['yard_id']},{yard['area']},{yard['cleaning_speed']}\n")
    
    def _save_messages(self, file_path: Path):
        """Сохранение сообщений от машин"""
        data = {
            'metadata': {
                'total_messages': len(self.messages),
                'machines_count': len(self.machines),
                'generation_time': datetime.now().isoformat(),
                'simulation_duration_minutes': self.config['simulation_duration_minutes'],
                'base_message_interval_seconds': self.config['base_message_interval'],
                'timing_mode': 'realistic_intervals'
            },
            'messages': self.messages
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_metadata(self, file_path: Path):
        """Сохранение метаданных генерации"""
        # Анализ временных интервалов
        intervals = []
        if len(self.messages) > 1:
            for i in range(1, len(self.messages)):
                prev_time = datetime.fromisoformat(self.messages[i-1]['timestamp'])
                curr_time = datetime.fromisoformat(self.messages[i]['timestamp'])
                interval = (curr_time - prev_time).total_seconds()
                intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        # Статистика по сообщениям во дворах
        messages_in_yards = sum(1 for msg in self.messages if msg['yard_id'] is not None)
        yard_coverage_actual = messages_in_yards / len(self.messages) * 100 if self.messages else 0
        
        # Статистика по убираемым дворам
        yards_mentioned = set(msg['yard_id'] for msg in self.messages if msg['yard_id'] is not None)
        yard_usage_actual = len(yards_mentioned) / len(self.yards) * 100 if self.yards else 0
        
        metadata = {
            'generation_config': self.config,
            'generated_data': {
                'yards_count': len(self.yards),
                'machines_count': len(self.machines),
                'messages_count': len(self.messages),
                'messages_per_machine': len(self.messages) // len(self.machines) if self.machines else 0
            },
            'timing_analysis': {
                'target_interval_seconds': self.config['base_message_interval'],
                'actual_average_interval_seconds': round(avg_interval, 2),
                'total_intervals_analyzed': len(intervals),
                'realistic_timing_achieved': 0.7 <= avg_interval <= 1.5
            },
            'statistics': {
                'messages_in_yards_percent': round(yard_coverage_actual, 1),
                'yards_used_percent': round(yard_usage_actual, 1),
                'yards_used_count': len(yards_mentioned),
                'yards_total_count': len(self.yards)
            },
            'requirements_check': {
                'min_10_yards': len(self.yards) >= 10,
                'min_5_machines': len(self.machines) >= 5,
                'min_5_messages_per_machine': all(
                    sum(1 for msg in self.messages if msg['machine_id'] == m_id) >= 5 
                    for m_id in self.machines
                ),
                '80_percent_yards_cleaned': yard_usage_actual >= 80,
                '80_percent_messages_in_yards': yard_coverage_actual >= 80,
                'realistic_timing': 0.7 <= avg_interval <= 1.5
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _print_statistics(self):
        """Вывод статистики генерации"""
        print("\n📊 СТАТИСТИКА ГЕНЕРАЦИИ:")
        print(f"   Дворов: {len(self.yards)}")
        print(f"   Машин: {len(self.machines)}")
        print(f"   Сообщений: {len(self.messages)}")
        
        # Анализ временных интервалов
        if len(self.messages) > 1:
            intervals = []
            for i in range(1, len(self.messages)):
                prev_time = datetime.fromisoformat(self.messages[i-1]['timestamp'])
                curr_time = datetime.fromisoformat(self.messages[i]['timestamp'])
                interval = (curr_time - prev_time).total_seconds()
                intervals.append(interval)
            
            avg_interval = sum(intervals) / len(intervals)
            print(f"   Средний интервал: {avg_interval:.2f}с (цель: {self.config['base_message_interval']}с)")
        
        # Проверяем требования
        messages_in_yards = sum(1 for msg in self.messages if msg['yard_id'] is not None)
        yard_coverage = messages_in_yards / len(self.messages) * 100 if self.messages else 0
        
        yards_mentioned = set(msg['yard_id'] for msg in self.messages if msg['yard_id'] is not None)
        yard_usage = len(yards_mentioned) / len(self.yards) * 100 if self.yards else 0
        
        print(f"   Сообщений во дворах: {messages_in_yards} ({yard_coverage:.1f}%)")
        print(f"   Дворов использовано: {len(yards_mentioned)} из {len(self.yards)} ({yard_usage:.1f}%)")
        
        # Анализ сообщений по машинам
        messages_per_machine = {}
        for message in self.messages:
            machine_id = message['machine_id']
            messages_per_machine[machine_id] = messages_per_machine.get(machine_id, 0) + 1
        
        if messages_per_machine:
            min_messages = min(messages_per_machine.values())
            max_messages = max(messages_per_machine.values())
            avg_messages = sum(messages_per_machine.values()) / len(messages_per_machine)
            print(f"   Сообщений на машину: мин={min_messages}, макс={max_messages}, сред={avg_messages:.1f}")
        else:
            min_messages = 0
        
        # Проверка соответствия требованиям
        print("\n ПРОВЕРКА ТРЕБОВАНИЙ:")
        print(f"   ≥10 дворов: {'' if len(self.yards) >= 10 else ''} ({len(self.yards)})")
        print(f"   ≥5 машин: {'' if len(self.machines) >= 5 else ''} ({len(self.machines)})")
        print(f"   ≥5 сообщений/машину: {'' if min_messages >= 5 else ''} (мин: {min_messages})")
        print(f"   80% дворов убирается: {'' if yard_usage >= 80 else ''} ({yard_usage:.1f}%)")
        print(f"   80% сообщений во дворах: {'' if yard_coverage >= 80 else ''} ({yard_coverage:.1f}%)")
        
        # Проверка реалистичности временных интервалов
        if len(self.messages) > 1:
            realistic_timing = 0.7 <= avg_interval <= 1.5
            print(f"   Реалистичные интервалы: {'' if realistic_timing else ''} ({avg_interval:.2f}с)")


def generate_test_data():
    """Функция для запуска генерации тестовых данных"""
    generator = TestDataGenerator()
    return generator.generate_all_data()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Генератор тестовых данных')
    parser.add_argument('--output', '-o', default='data', help='Директория для выходных файлов')
    parser.add_argument('--seed', '-s', type=int, default=42, help='Сид для генератора случайных чисел')
    parser.add_argument('--duration', '-d', type=int, default=60, help='Длительность симуляции (минуты)')
    
    args = parser.parse_args()
    
    generator = TestDataGenerator(seed=args.seed)
    generator.config['simulation_duration_minutes'] = args.duration
    success = generator.generate_all_data(args.output)
    
    if success:
        print(" Генерация тестовых данных завершена успешно!")
        exit(0)
    else:
        print(" Ошибка при генерации тестовых данных!")
        exit(1)