import subprocess
import time
import os
import csv
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

def run_master(num_workers=3):
    """Menjalankan master.py sebagai subprocess dan mengambil output waktu."""
    try:
        result = subprocess.run(
            ["python3", "src/master.py", str(num_workers), "--benchmark"], 
            capture_output=True, text=True, check=True
        )
        output_lines = result.stdout.strip().split('\n')
        for line in reversed(output_lines):
            try:
                return float(line.strip())
            except ValueError:
                continue
        return 0.0
    except Exception as e:
        print(f"   [Error] Gagal menjalankan master dengan {num_workers} worker: {e}")
        return 0.0

def generate_benchmark():
    output_dir = "hasil_benchmark"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 65)
    print("📊 BENCHMARK KINERJA KLASTER gRPC (MASTER-WORKER)")
    print("=" * 65)

    # --- TAHAP 1: SPEEDUP (1 WORKER VS 3 WORKER) ---
    print("\n[1/2] Menganalisis Speedup & Efisiensi Klaster...")
    
    print("   ⏳ Menjalankan komputasi base (1 Worker)...")
    t1 = run_master(1)
    print(f"      └─ Waktu Selesai: {t1:.2f} detik")
    
    print("   ⏳ Menjalankan komputasi klaster (3 Worker)...")
    t3 = run_master(3)
    print(f"      └─ Waktu Selesai: {t3:.2f} detik")
    
    speedup = (t1 / t3) if t3 > 0 else 0.0
    efficiency = (speedup / 3) * 100 if speedup > 0 else 0.0
    print(f"   ✨ Hasil: Speedup = {speedup:.2f}x | Efisiensi = {efficiency:.1f}%")

    # --- TAHAP 2: LOAD TESTING (1, 5, 20 CLIENT) ---
    print("\n[2/2] Melakukan Load Testing Konkurensi Sistem...")
    clients_list = [1, 5, 20]
    results_data = []

    for clients in clients_list:
        print(f"   ⏳ Menguji tingkat beban: {clients} Client konkuren...")
        start_load = time.time()
        times = []
        
        with ThreadPoolExecutor(max_workers=clients) as executor:
            futures = [executor.submit(run_master, 3) for _ in range(clients)]
            for fut in futures:
                times.append(fut.result())
                
        total_duration = time.time() - start_load
        valid_times = [t for t in times if t > 0]
        avg_latency = (sum(valid_times) / len(valid_times)) if valid_times else 0.0
        throughput = clients / total_duration if total_duration > 0 else 0.0
        
        print(f"      └─ Selesai | Total Waktu: {total_duration:.2f}s | Latensi: {avg_latency:.2f}s | Throughput: {throughput:.2f} req/s")
        
        results_data.append({
            "clients": clients,
            "waktu_total": total_duration,
            "latensi": avg_latency,
            "throughput": throughput
        })

    # --- LAPORAN TABEL KONSOL ---
    print("\n" + "=" * 65)
    print("📈 RINGKASAN EVALUASI PERFORMA SISTEM")
    print("=" * 65)
    print(f" • Waktu Eksekusi 1 Worker (Base)  : {t1:.2f} detik")
    print(f" • Waktu Eksekusi 3 Worker (Klaster): {t3:.2f} detik")
    print(f" • Faktor Speedup (S)              : {speedup:.2f}x")
    print(f" • Efisiensi Paralel (E)           : {efficiency:.2f}%")
    print("-" * 65)
    print(f"{'Konkurensi':<12} | {'Waktu Total (s)':<16} | {'Latensi Rata-rata (s)':<22} | {'Throughput (req/s)':<18}")
    print("-" * 65)
    for row in results_data:
        print(f"{row['clients']} Client{' '*(5-len(str(row['clients'])))} | "
              f"{row['waktu_total']:<16.2f} | "
              f"{row['latensi']:<22.2f} | "
              f"{row['throughput']:<18.2f}")
    print("=" * 65)

    # --- EKSPOR CSV ---
    csv_path = os.path.join(output_dir, "tabel_benchmark.csv")
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Jumlah Client", "Waktu Total (s)", "Latensi Rata-rata (s)", "Throughput (req/s)", "Speedup", "Efisiensi (%)"])
        for row in results_data:
            writer.writerow([row["clients"], round(row["waktu_total"], 2), round(row["latensi"], 2), round(row["throughput"], 2), round(speedup, 2), round(efficiency, 2)])

    # --- GENERATE GRAFIK MATPLOTLIB ---
    print("\n🎨 Menyimpan laporan visualisasi grafik...")
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axs = plt.subplots(1, 3, figsize=(17, 5.5))
    
    bars = axs[0].bar(['1 Worker', '3 Workers (Klaster)'], [t1, t3], color=['#d9534f', '#5cb85c'], width=0.45)
    axs[0].set_title('Analisis Peningkatan Kinerja (Speedup)', fontsize=11, fontweight='bold', pad=12)
    axs[0].set_ylabel('Waktu Eksekusi (detik)', fontsize=10)
    axs[0].grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        h = bar.get_height()
        axs[0].annotate(f'{h:.2f}s', xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontweight='bold', fontsize=9)

    x_clients = [str(r['clients']) for r in results_data]
    y_latensi = [r['latensi'] for r in results_data]
    y_throughput = [r['throughput'] for r in results_data]

    axs[1].plot(x_clients, y_latensi, marker='o', linestyle='-', color='#f0ad4e', linewidth=2.5, markersize=8)
    axs[1].set_title('Latensi Rata-rata vs Beban Client', fontsize=11, fontweight='bold', pad=12)
    axs[1].set_xlabel('Jumlah Client Konkuren', fontsize=10)
    axs[1].set_ylabel('Latensi (detik)', fontsize=10)
    axs[1].grid(True, linestyle='--', alpha=0.7)
    for i, txt in enumerate(y_latensi):
        axs[1].annotate(f'{txt:.2f}s', (x_clients[i], y_latensi[i]), xytext=(0, 8), textcoords="offset points", ha='center', fontsize=9, fontweight='bold')

    axs[2].plot(x_clients, y_throughput, marker='s', linestyle='-', color='#0275d8', linewidth=2.5, markersize=8)
    axs[2].set_title('Throughput Sistem vs Beban Client', fontsize=11, fontweight='bold', pad=12)
    axs[2].set_xlabel('Jumlah Client Konkuren', fontsize=10)
    axs[2].set_ylabel('Throughput (request/detik)', fontsize=10)
    axs[2].grid(True, linestyle='--', alpha=0.7)
    for i, txt in enumerate(y_throughput):
        axs[2].annotate(f'{txt:.2f} req/s', (x_clients[i], y_throughput[i]), xytext=(0, 8), textcoords="offset points", ha='center', fontsize=9, fontweight='bold')

    plt.suptitle('LAPORAN EVALUASI PERFORMA ARSITEKTUR MASTER-WORKER gRPC', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    grafik_path = os.path.join(output_dir, "grafik_benchmark.png")
    plt.savefig(grafik_path, dpi=300, bbox_inches='tight')
    plt.close()

    print("=" * 65)
    print("✅ BENCHMARK SELESAI DENGAN SUKSES!")
    print(f"   📁 Data CSV   : {csv_path}")
    print(f"   📈 Grafik PNG : {grafik_path}")
    print("=" * 65)

if __name__ == '__main__':
    generate_benchmark()