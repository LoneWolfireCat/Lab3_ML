import sqlite3

def init_database():
    conn = sqlite3.connect('knowledge_base.db')
    cursor = conn.cursor()

    # Таблица с нечеткими множествами
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fuzzy_sets (
        id INTEGER PRIMARY KEY,
        variable_name TEXT NOT NULL,
        set_name TEXT NOT NULL,
        a REAL, b REAL, c REAL, d REAL
    )
    ''')

    # Таблица правил
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rules (
        id INTEGER PRIMARY KEY,
        condition_smoke TEXT,
        condition_temp TEXT,
        condition_zone TEXT,
        action_sprinkler TEXT,
        action_alarm TEXT,
        action_evacuation TEXT,
        priority INTEGER
    )
    ''')

    # Очищаем таблицы
    cursor.execute("DELETE FROM fuzzy_sets")
    cursor.execute("DELETE FROM rules")

    # Нечеткие множества для системы пожаротушения
    smoke_sets = [
        ('smoke', 'none', 0, 0, 10, 20),
        ('smoke', 'low', 10, 20, 30, 40),
        ('smoke', 'medium', 30, 40, 60, 70),
        ('smoke', 'high', 60, 70, 100, 100)
    ]

    temp_sets = [
        ('temperature', 'normal', 0, 0, 30, 40),
        ('temperature', 'warm', 30, 40, 60, 70),
        ('temperature', 'hot', 60, 70, 100, 120),
        ('temperature', 'critical', 100, 120, 200, 200)
    ]

    zone_sets = [
        ('zone', 'safe', 0, 0, 1, 2),
        ('zone', 'risk', 1, 2, 3, 4),
        ('zone', 'danger', 3, 4, 5, 5)
    ]

    cursor.executemany('INSERT INTO fuzzy_sets VALUES (NULL, ?, ?, ?, ?, ?, ?)',
                       smoke_sets + temp_sets + zone_sets)

    # ДОПОЛНИТЕЛЬНЫЕ ПРАВИЛА ДЛЯ ТЕМПЕРАТУРЫ В ДИАПАЗОНЕ hot
    rules = [
        # smoke, temp, zone, sprinkler, alarm, evacuation, priority
        ('high', None, None, 'high', 'on', 'immediate', 10),
        (None, 'critical', None, 'high', 'on', 'immediate', 10),
        ('medium', 'hot', None, 'medium', 'on', 'prepare', 9),
        ('medium', None, 'danger', 'medium', 'on', 'prepare', 9),
        ('low', 'warm', 'risk', 'low', 'on', 'none', 8),
        ('low', None, 'risk', 'low', 'warning', 'none', 7),
        (None, 'warm', 'risk', 'low', 'warning', 'none', 7),

        # НОВЫЕ ПРАВИЛА ДЛЯ ТЕМПЕРАТУРЫ hot:
        (None, 'hot', 'danger', 'medium', 'on', 'prepare', 8),
        (None, 'hot', 'risk', 'low', 'on', 'none', 7),
        (None, 'hot', None, 'low', 'warning', 'none', 6),

        ('none', 'normal', 'safe', 'off', 'off', 'none', 5),
        (None, None, 'safe', 'off', 'off', 'none', 4),

        # ДОПОЛНИТЕЛЬНОЕ ПРАВИЛО ДЛЯ ОСТАТОЧНОЙ ТЕМПЕРАТУРЫ:
        ('none', 'warm', None, 'off', 'warning', 'none', 5),
    ]

    cursor.executemany('''
    INSERT INTO rules VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
    ''', rules)

    conn.commit()
    conn.close()
    print("База данных системы пожаротушения инициализирована!")

if __name__ == "__main__":
    init_database()