"""
monitor.py — Моніторинг CPU та Memory під час стрес-тесту.

Запускається паралельно зі стрес-тестом:
    python tests/k6/monitor.py --output results/metrics.csv

Зупинка: Ctrl+C
"""
import time
import csv
import argparse
import os
import sys
from datetime import datetime

try:
    import psutil
except ImportError:
    print("Встановіть psutil: pip install psutil")
    sys.exit(1)


def find_flask_process():
    """Знаходить PID Flask-процесу."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'run.py' in cmdline or 'flask' in cmdline.lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None


def monitor(output_path, interval=1.0):
    """Збирає метрики CPU/Memory кожен interval секунд."""
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    flask_proc = find_flask_process()
    if flask_proc:
        print(f"Flask процес знайдено: PID {flask_proc.pid}")
    else:
        print("Flask процес не знайдено — моніторинг системи загалом")

    print(f"Запис метрик у: {output_path}")
    print("Натисніть Ctrl+C для зупинки\n")

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'timestamp', 'elapsed_s',
            'system_cpu_%', 'system_mem_%', 'system_mem_mb',
            'flask_cpu_%', 'flask_mem_mb', 'flask_threads'
        ])

        start = time.time()
        try:
            while True:
                now = time.time()
                elapsed = round(now - start, 1)
                ts = datetime.now().strftime('%H:%M:%S')

                # Системні метрики
                sys_cpu = psutil.cpu_percent(interval=None)
                sys_mem = psutil.virtual_memory()

                # Flask-специфічні метрики
                flask_cpu = flask_mem = flask_threads = 0
                if flask_proc:
                    try:
                        flask_proc.cpu_percent(interval=None)
                        flask_cpu    = round(flask_proc.cpu_percent(interval=0.1), 1)
                        flask_mem    = round(flask_proc.memory_info().rss / 1024 / 1024, 1)
                        flask_threads = flask_proc.num_threads()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        flask_proc = find_flask_process()

                row = [
                    ts, elapsed,
                    sys_cpu,
                    round(sys_mem.percent, 1),
                    round(sys_mem.used / 1024 / 1024, 1),
                    flask_cpu, flask_mem, flask_threads
                ]
                writer.writerow(row)
                f.flush()

                print(
                    f"\r[{ts}] +{elapsed:.0f}s | "
                    f"SYS CPU: {sys_cpu:5.1f}% | "
                    f"MEM: {sys_mem.percent:4.1f}% ({sys_mem.used//1024//1024}MB) | "
                    f"Flask CPU: {flask_cpu:5.1f}% MEM: {flask_mem:.0f}MB",
                    end='', flush=True
                )
                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\nМоніторинг завершено. Записано у {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',   default='results/metrics.csv')
    parser.add_argument('--interval', type=float, default=1.0)
    args = parser.parse_args()
    monitor(args.output, args.interval)
