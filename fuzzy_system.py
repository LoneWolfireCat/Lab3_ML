import sqlite3
import numpy as np
from typing import Dict, List, Tuple

class FuzzyInferenceSystem:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.sprinkler_map = {'off': 0, 'low': 0.33, 'medium': 0.66, 'high': 1.0}
        self.alarm_map = {'off': 0, 'warning': 0.5, 'on': 1.0}
        self.evacuation_map = {'none': 0, 'prepare': 0.5, 'immediate': 1.0}

    def trapezoid_mf(self, x: float, a: float, b: float, c: float, d: float) -> float:
        """Трапециевидная функция принадлежности"""
        if x < a:
            return 0.0
        elif a <= x < b:
            if b == a:
                return 1.0
            return (x - a) / (b - a)
        elif b <= x <= c:
            return 1.0
        elif c < x <= d:
            if d == c:
                return 1.0
            return (d - x) / (d - c)
        else:
            return 0.0

    def fuzzify(self, value: float, variable: str) -> Dict[str, float]:
        """Фаззификация"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT set_name, a, b, c, d FROM fuzzy_sets 
        WHERE variable_name = ?
        ''', (variable,))

        result = {}
        for set_name, a, b, c, d in cursor.fetchall():
            membership = self.trapezoid_mf(value, a, b, c, d)
            if membership > 0:
                result[set_name] = membership

        conn.close()
        return result

    def infer(self, smoke: float, temperature: float, zone: float) -> Dict[str, float]:
        """Нечеткий вывод для системы пожаротушения"""
        # Фаззификация
        smoke_fuzzy = self.fuzzify(smoke, 'smoke')
        temp_fuzzy = self.fuzzify(temperature, 'temperature')
        zone_fuzzy = self.fuzzify(zone, 'zone')

        print("🎯 ФАЗЗИФИКАЦИЯ:")
        print(f"   Дым {smoke}% → {smoke_fuzzy}")
        print(f"   Температура {temperature}°C → {temp_fuzzy}")
        print(f"   Зона риска {zone} → {zone_fuzzy}")

        # Получение правил из БД
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rules ORDER BY priority DESC')
        rules = cursor.fetchall()
        conn.close()

        # Агрегация и активация правил
        sprinkler_output = {}
        alarm_output = {}
        evacuation_output = {}

        print("\n📋 ПРОВЕРКА ПРАВИЛ:")

        for rule in rules:
            (rule_id, cond_smoke, cond_temp, cond_zone,
             act_sprinkler, act_alarm, act_evacuation, priority) = rule

            # Вычисляем степень истинности условия
            truth_level = 1.0

            if cond_smoke:
                smoke_truth = smoke_fuzzy.get(cond_smoke, 0)
                truth_level = min(truth_level, smoke_truth)
            if cond_temp:
                temp_truth = temp_fuzzy.get(cond_temp, 0)
                truth_level = min(truth_level, temp_truth)
            if cond_zone:
                zone_truth = zone_fuzzy.get(cond_zone, 0)
                truth_level = min(truth_level, zone_truth)

            # Формируем читаемое условие
            condition_parts = []
            if cond_smoke:
                condition_parts.append(f"smoke={cond_smoke}")
            if cond_temp:
                condition_parts.append(f"temp={cond_temp}")
            if cond_zone:
                condition_parts.append(f"zone={cond_zone}")
            condition_str = " И ".join(condition_parts) if condition_parts else "ВСЕГДА"

            status = "✅ СРАБОТАЛО" if truth_level > 0 else "❌ НЕ СРАБОТАЛО"
            print(f"   Правило {rule_id}: ЕСЛИ {condition_str}")
            print(f"        Приоритет: {priority}, Истинность: {truth_level:.2f} → {status}")

            if truth_level > 0:
                # Активация заключений
                if act_sprinkler:
                    current_value = sprinkler_output.get(act_sprinkler, 0)
                    sprinkler_output[act_sprinkler] = max(current_value, truth_level)

                if act_alarm:
                    current_value = alarm_output.get(act_alarm, 0)
                    alarm_output[act_alarm] = max(current_value, truth_level)

                if act_evacuation:
                    current_value = evacuation_output.get(act_evacuation, 0)
                    evacuation_output[act_evacuation] = max(current_value, truth_level)

        print(f"\n🎛 АКТИВИРОВАННЫЕ ДЕЙСТВИЯ:")
        print(f"   Спринклер: {sprinkler_output}")
        print(f"   Сигнализация: {alarm_output}")
        print(f"   Эвакуация: {evacuation_output}")

        # Дефаззификация
        sprinkler_result = self.defuzzify_sprinkler(sprinkler_output)
        alarm_result = self.defuzzify_alarm(alarm_output)
        evacuation_result = self.defuzzify_evacuation(evacuation_output)

        return {
            'sprinkler': sprinkler_result,
            'alarm': alarm_result,
            'evacuation': evacuation_result
        }

    def defuzzify_sprinkler(self, fuzzy_output: Dict[str, float]) -> float:
        """Дефаззификация для спринклера"""
        if not fuzzy_output:
            print("   Спринклер: нет активированных правил → ВЫКЛ")
            return 0.0

        numerator = 0.0
        denominator = 0.0

        for term, membership in fuzzy_output.items():
            membership_val = float(membership)
            crisp_value = self.sprinkler_map[term]
            numerator += crisp_value * membership_val
            denominator += membership_val

        result = numerator / denominator if denominator != 0 else 0.0
        print(f"   Спринклер: {fuzzy_output} → интенсивность {result:.2f}")
        return result

    def defuzzify_alarm(self, fuzzy_output: Dict[str, float]) -> float:
        """Дефаззификация для сигнализации"""
        if not fuzzy_output:
            print("   Сигнализация: нет активированных правил → ВЫКЛ")
            return 0.0

        numerator = 0.0
        denominator = 0.0

        for term, membership in fuzzy_output.items():
            membership_val = float(membership)
            crisp_value = self.alarm_map[term]
            numerator += crisp_value * membership_val
            denominator += membership_val

        result = numerator / denominator if denominator != 0 else 0.0
        status = "ВЫКЛ" if result < 0.25 else "ПРЕДУПРЕЖДЕНИЕ" if result < 0.75 else "ВКЛ"
        print(f"   Сигнализация: {fuzzy_output} → {status} ({result:.2f})")
        return result

    def defuzzify_evacuation(self, fuzzy_output: Dict[str, float]) -> float:
        """Дефаззификация для эвакуации"""
        if not fuzzy_output:
            print("   Эвакуация: нет активированных правил → НЕТ")
            return 0.0

        numerator = 0.0
        denominator = 0.0

        for term, membership in fuzzy_output.items():
            membership_val = float(membership)
            crisp_value = self.evacuation_map[term]
            numerator += crisp_value * membership_val
            denominator += membership_val

        result = numerator / denominator if denominator != 0 else 0.0
        status = "НЕТ" if result < 0.25 else "ПОДГОТОВКА" if result < 0.75 else "НЕМЕДЛЕННО"
        print(f"   Эвакуация: {fuzzy_output} → {status} ({result:.2f})")
        return result