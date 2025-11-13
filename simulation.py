import numpy as np
from fuzzy_system import FuzzyInferenceSystem
from visualization import SimulationVisualizer

def get_user_input():
    """Интерактивный ввод начальных условий"""
    print("🎛 НАСТРОЙКА НАЧАЛЬНЫХ УСЛОВИЙ СИСТЕМЫ ПОЖАРОТУШЕНИЯ")
    print("=" * 50)

    while True:
        try:
            smoke = float(input("🚬 Введите уровень задымленности (0-100%): "))
            if 0 <= smoke <= 100:
                break
            else:
                print("❌ Ошибка: уровень дыма должен быть от 0 до 100%")
        except ValueError:
            print("❌ Ошибка: введите число")

    while True:
        try:
            temperature = float(input("🌡 Введите температуру (0-200°C): "))
            if 0 <= temperature <= 200:
                break
            else:
                print("❌ Ошибка: температура должна быть от 0 до 200°C")
        except ValueError:
            print("❌ Ошибка: введите число")

    while True:
        try:
            zone = float(input("🏢 Введите уровень риска зоны (0-5): "))
            if 0 <= zone <= 5:
                break
            else:
                print("❌ Ошибка: уровень риска должен быть от 0 до 5")
        except ValueError:
            print("❌ Ошибка: введите число")

    return smoke, temperature, zone

def is_safe_zone(smoke: float, temperature: float, zone: float) -> bool:
    """Проверка, находятся ли значения в безопасной зоне"""
    smoke_safe = smoke <= 20
    temp_safe = temperature <= 40
    zone_safe = zone <= 1
    return smoke_safe and temp_safe and zone_safe

class FireSuppressionSimulator:
    def __init__(self):
        self.fis = FuzzyInferenceSystem('knowledge_base.db')
        self.visualizer = SimulationVisualizer()

        # Интерактивный ввод начальных условий
        self.smoke, self.temperature, self.zone = get_user_input()

        # Внешние условия (имитация)
        self.external_smoke = 0.0
        self.external_temp = 25.0

        self.step = 0
        self.safe_steps_count = 0

        print("\n" + "=" * 60)
        print("🚒 СИМУЛЯТОР СИСТЕМЫ ПОЖАРОТУШЕНИЯ ЗАПУЩЕН!")
        print(f"📊 НАЧАЛЬНЫЕ УСЛОВИЯ: Дым={self.smoke}%, Температура={self.temperature}°C, Зона={self.zone}")

        if is_safe_zone(self.smoke, self.temperature, self.zone):
            print("🎉 Начальные условия БЕЗОПАСНЫ! Система мониторинга активна.")
        else:
            print("🚨 ОБНАРУЖЕНА ПОТЕНЦИАЛЬНАЯ ОПАСНОСТЬ! Активация системы пожаротушения...")
        print("=" * 60)

    def update_environment(self):
        """Имитация изменения условий"""
        # Имитация возможного развития пожара
        self.external_smoke = max(0, min(100, self.external_smoke + np.random.normal(0, 2)))
        self.external_temp = max(0, min(200, self.external_temp + np.random.normal(0, 1)))

    def apply_control_actions(self, sprinkler: float, alarm: float, evacuation: float):
        """Улучшенная физическая модель с естественным охлаждением"""

        # БАЗОВОЕ ВОЗДЕЙСТВИЕ СПРИНКЛЕРА (усиленное)
        smoke_reduction = sprinkler * 30  # увеличено с 25
        temp_reduction = sprinkler * 40  # увеличено с 35

        # ЭКСПОНЕНЦИАЛЬНОЕ ОХЛАЖДЕНИЕ при высоких температурах
        if self.temperature > 80:
            extra_cooling = (self.temperature - 80) * 0.4 * sprinkler
            temp_reduction += extra_cooling

        # ЕСТЕСТВЕННОЕ ОХЛАЖДЕНИЕ (даже без спринклера)
        natural_cooling = max(0, (self.external_temp - self.temperature) * 0.15)
        temp_reduction += natural_cooling

        # ОБНОВЛЕНИЕ СОСТОЯНИЯ
        self.smoke = max(0, min(100, self.smoke - smoke_reduction + self.external_smoke * 0.05))
        self.temperature = max(0, min(200, self.temperature - temp_reduction + self.external_temp * 0.02))

        # БОЛЕЕ БЫСТРОЕ СНИЖЕНИЕ УРОВНЯ РИСКА ЗОНЫ
        if sprinkler > 0.5 or self.temperature > 60:
            risk_increase = 0.02
        else:
            risk_increase = -0.15  # быстрое снижение риска

        self.zone = max(0, min(5, self.zone + risk_increase))

    def run(self, steps=20):
        """Запуск симуляции"""
        print("\n📈 ЗАПУСК СИМУЛЯЦИИ...")
        print("   Графики будут обновляться в реальном времени!")
        input("   Нажмите Enter чтобы продолжить...")

        step = 0
        actual_steps = 0

        while actual_steps < steps and step < steps * 2:
            step += 1

            if is_safe_zone(self.smoke, self.temperature, self.zone):
                self.safe_steps_count += 1
                print(f"\n✅ ШАГ {step}: БЕЗОПАСНАЯ СИТУАЦИЯ")
                print(f"   Дым: {self.smoke:.1f}%, Температура: {self.temperature:.1f}°C, Зона: {self.zone:.1f}")
                print("   Система мониторинга активна")
                print("-" * 40)

                self.visualizer.update(step, self.smoke, self.temperature, self.zone, 0, 0, 0)
                continue

            actual_steps += 1
            self.step = step

            print(f"\n🎯 ШАГ {step} (активный шаг {actual_steps}):")
            print("-" * 40)

            self.update_environment()
            print(f"🌍 Внешние условия: дым={self.external_smoke:.1f}%, темп={self.external_temp:.1f}°C")

            print(f"🏢 Состояние: дым={self.smoke:.1f}%, темп={self.temperature:.1f}°C, зона={self.zone:.1f}")
            actions = self.fis.infer(self.smoke, self.temperature, self.zone)
            sprinkler = actions['sprinkler']
            alarm = actions['alarm']
            evacuation = actions['evacuation']

            print(f"🎛 УПРАВЛЕНИЕ: спринклер={sprinkler:.2f}, сигнализация={alarm:.2f}, эвакуация={evacuation:.2f}")

            self.visualizer.update(step, self.smoke, self.temperature, self.zone, sprinkler, alarm, evacuation)
            self.apply_control_actions(sprinkler, alarm, evacuation)

        # Статистика
        print("\n" + "=" * 60)
        print("✅ СИМУЛЯЦИЯ ЗАВЕРШЕНА!")
        print(f"📊 СТАТИСТИКА:")
        print(f"   Всего шагов симуляции: {step}")
        print(f"   Активных шагов пожаротушения: {actual_steps}")
        print(f"   Шагов в безопасной зоне: {self.safe_steps_count}")
        print(f"   Финальное состояние: дым={self.smoke:.1f}%, темп={self.temperature:.1f}°C, зона={self.zone:.1f}")

        if is_safe_zone(self.smoke, self.temperature, self.zone):
            print("🎉 ОПАСНОСТЬ ЛИКВИДИРОВАНА! Система работает нормально.")
        else:
            print("⚠️  ТРЕБУЕТСЯ ВМЕШАТЕЛЬСТВО! Ситуация не полностью под контролем.")

        print("   Закройте окно с графиками чтобы выйти...")
        print("=" * 60)

        self.visualizer.show_final()

if __name__ == "__main__":
    simulator = FireSuppressionSimulator()
    simulator.run(steps=15)