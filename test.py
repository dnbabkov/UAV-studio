#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import statistics

TRIG = 16   # BCM нумерация
ECHO = 20

SPEED_OF_SOUND = 343.0  # м/с при 20°C
MAX_DISTANCE_M = 4.0    # макс. измерение для HC-SR04 ~4м
TIMEOUT_S = (2 * MAX_DISTANCE_M) / SPEED_OF_SOUND  # туда-обратно

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ECHO, GPIO.IN)
    time.sleep(0.05)  # дать датчику стабилизироваться

def pulse_distance():
    # Послать импульс ~10 мкс
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(10e-6)
    GPIO.output(TRIG, GPIO.LOW)

    # Ждём фронт ECHO с таймаутом
    start_time = time.perf_counter()
    while GPIO.input(ECHO) == 0:
        if (time.perf_counter() - start_time) > TIMEOUT_S:
            return None
    pulse_start = time.perf_counter()

    # Ждём спад ECHO с таймаутом
    while GPIO.input(ECHO) == 1:
        if (time.perf_counter() - pulse_start) > TIMEOUT_S:
            return None
    pulse_end = time.perf_counter()

    pulse_len = pulse_end - pulse_start  # сек
    # Расстояние = (время * скорость звука) / 2
    distance_m = (pulse_len * SPEED_OF_SOUND) / 2.0
    return distance_m

def measure(n=5, pause=0.06):
    readings = []
    for _ in range(n):
        d = pulse_distance()
        if d is not None:
            readings.append(d)
        time.sleep(pause)  # HC-SR04 рекомендует >60 мс между триггерами
    if not readings:
        return None
    # Медиана — устойчивее к выбросам
    return statistics.median(readings)

def main():
    setup()
    try:
        while True:
            d = measure()
            if d is None:
                print("Нет эха/таймаут")
            else:
                print(f"{d*100:.1f} см")
            time.sleep(0.3)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
