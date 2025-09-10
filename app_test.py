import RPi.GPIO as GPIO
import time
import csv
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt


# --- Настройка пинов ---
TRIG = 16
ECHO = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)


def get_distance():
    """Функция измерения расстояния с HC-SR04"""
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start = time.time()
    stop = time.time()

    while GPIO.input(ECHO) == 0:
        start = time.time()

    while GPIO.input(ECHO) == 1:
        stop = time.time()

    elapsed = stop - start
    distance = (elapsed * 34300) / 2  # скорость звука 34300 см/с
    return round(distance, 2)


def ask_parameters():
    """Окно для ввода параметров (время и имя файла)"""
    dialog = tk.Toplevel(root)
    dialog.title("Параметры эксперимента")

    tk.Label(dialog, text="Время эксперимента (сек):").grid(row=0, column=0, padx=5, pady=5)
    duration_entry = tk.Entry(dialog)
    duration_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(dialog, text="Имя CSV файла:").grid(row=1, column=0, padx=5, pady=5)
    filename_entry = tk.Entry(dialog)
    filename_entry.insert(0, "data.csv")  # значение по умолчанию
    filename_entry.grid(row=1, column=1, padx=5, pady=5)

    def submit():
        duration = duration_entry.get()
        filename = filename_entry.get()
        if not duration.isdigit():
            messagebox.showerror("Ошибка", "Введите число секунд!")
            return
        if not filename.endswith(".csv"):
            filename += ".csv"
        dialog.destroy()
        start_measurement(int(duration), filename)

    tk.Button(dialog,  text="OK", command=submit).grid(row=2, column=0, columnspan=2, pady=10)
    dialog.grab_set()  # блокируем главное окно, пока не закроем это


def start_measurement(duration, filename):
    """Сбор данных за n секунд"""
    try:
        button.pack_forget()  # убираем кнопку

        data = []
        start_time = time.time()

        while (time.time() - start_time) < duration:
            dist = get_distance()
            elapsed_time = round(time.time() - start_time, 3)  # секунды с начала
            data.append([elapsed_time, dist])
            time.sleep(0.1)  # опрос 10 Гц

        # сохраняем CSV
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Время (сек)", "Расстояние (см)"])
            writer.writerows(data)

        # строим график
        times = [row[0] for row in data]
        distances = [row[1] for row in data]

        fig, ax = plt.subplots()
        ax.plot(times, distances, marker="o")
        ax.set_title("Расстояние от времени")
        ax.set_xlabel("Время (сек)")
        ax.set_ylabel("Расстояние (см)")
        plt.tight_layout()

        def on_close(event):
            button.pack(pady=20, padx=20)  # вернуть кнопку после закрытия графика

        fig.canvas.mpl_connect("close_event", on_close)
        plt.show()

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


# --- GUI ---
root = tk.Tk()
root.title("HC-SR04 Logger")

button = tk.Button(root, text="Начать измерение", command=ask_parameters, font=("Arial", 14))
button.pack(pady=20, padx=20)

root.mainloop()

# очистка GPIO при выходе
GPIO.cleanup()
