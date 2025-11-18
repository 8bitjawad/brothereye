import time
import multiprocessing

def burn():
    while True:
        x = 999999 ** 5

if __name__ == "__main__":
    workers = multiprocessing.cpu_count()  # max stress
    procs = []

    print(f"🔥 Spawning {workers} CPU burners...")
    for _ in range(workers):
        p = multiprocessing.Process(target=burn)
        p.start()
        procs.append(p)

    time.sleep(60)  # run for 1 minute
    print("🛑 Stopping load...")

    for p in procs:
        p.terminate()
        p.join()

    print("✔ Stress test finished.")
