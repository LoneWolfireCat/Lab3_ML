import matplotlib.pyplot as plt
import numpy as np

class SimulationVisualizer:
    def __init__(self):
        self.steps = []
        self.smoke_levels = []
        self.temperatures = []
        self.zones = []
        self.sprinklers = []
        self.alarms = []
        self.ventilations = []

        plt.ion()
        self.fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(15, 8))
        self.fig.suptitle('СИСТЕМА ПОЖАРОТУШЕНИЯ С ВЕНТИЛЯЦИЕЙ', fontsize=14, fontweight='bold')

    def update(self, step, smoke, temperature, zone, sprinkler, alarm, ventilation):
        """Обновление данных для графика"""
        self.steps.append(step)
        self.smoke_levels.append(smoke)
        self.temperatures.append(temperature)
        self.zones.append(zone)
        self.sprinklers.append(sprinkler)
        self.alarms.append(alarm)
        self.ventilations.append(ventilation)

        self._plot_all()

    def _plot_all(self):
        """Отрисовка всех графиков"""
        for ax in self.fig.axes:
            ax.clear()

        # График задымленности
        ax1 = self.fig.axes[0]
        ax1.plot(self.steps, self.smoke_levels, color='gray', marker='o', linestyle='-', linewidth=2, markersize=4)
        ax1.set_title('УРОВЕНЬ ЗАДЫМЛЕННОСТИ')
        ax1.set_ylabel('Дым (%)')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=20, color='red', linestyle='--', alpha=0.7, label='Порог опасности')
        ax1.legend()

        # График температуры
        ax2 = self.fig.axes[1]
        ax2.plot(self.steps, self.temperatures, color='red', marker='o', linestyle='-', linewidth=2, markersize=4)
        ax2.set_title('ТЕМПЕРАТУРА')
        ax2.set_ylabel('Температура (°C)')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=40, color='red', linestyle='--', alpha=0.7, label='Порог опасности')
        ax2.legend()

        # График зоны риска
        ax3 = self.fig.axes[2]
        ax3.plot(self.steps, self.zones, color='orange', marker='o', linestyle='-', linewidth=2, markersize=4)
        ax3.set_title('УРОВЕНЬ РИСКА ЗОНЫ')
        ax3.set_ylabel('Уровень риска')
        ax3.set_ylim(0, 5.5)
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=2, color='red', linestyle='--', alpha=0.7, label='Порог опасности')
        ax3.legend()

        # График спринклера
        ax4 = self.fig.axes[3]
        ax4.plot(self.steps, self.sprinklers, color='blue', marker='o', linestyle='-', linewidth=2, markersize=4)
        ax4.set_title('ИНТЕНСИВНОСТЬ СПРИНКЛЕРА')
        ax4.set_ylabel('Интенсивность (0-1)')
        ax4.set_xlabel('Шаг симуляции')
        ax4.set_ylim(-0.1, 1.1)
        ax4.grid(True, alpha=0.3)

        # График сигнализации
        ax5 = self.fig.axes[4]
        ax5.plot(self.steps, self.alarms, color='yellow', marker='o', linestyle='-', linewidth=2, markersize=4)
        ax5.set_title('СИГНАЛИЗАЦИЯ')
        ax5.set_ylabel('Уровень (0-1)')
        ax5.set_xlabel('Шаг симуляции')
        ax5.set_ylim(-0.1, 1.1)
        ax5.grid(True, alpha=0.3)

        # График вентиляции
        ax6 = self.fig.axes[5]
        ax6.plot(self.steps, self.ventilations, color='green', marker='o', linestyle='-', linewidth=2, markersize=4)
        ax6.set_title('СИСТЕМА ВЕНТИЛЯЦИИ')
        ax6.set_ylabel('Интенсивность (0-1)')
        ax6.set_xlabel('Шаг симуляции')
        ax6.set_ylim(-0.1, 1.1)
        ax6.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.draw()
        plt.pause(0.1)

    def show_final(self):
        """Показать финальный график"""
        plt.ioff()
        plt.show()