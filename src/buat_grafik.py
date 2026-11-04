
import os
import csv
import matplotlib.pyplot as plt

# Lokasi file
csv_path = "hasil_benchmark/tabel_benchmark.csv"
output_path = "hasil_benchmark/grafik_benchmark.png"

# Data hasil pengujian speedup sebelumnya
t1 = 259.18
t3 = 182.75

# Membaca data CSV
results_data = []

with open(csv_path, mode="r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        results_data.append({
            "clients": int(row["Jumlah Client"]),
            "waktu_total": float(row["Waktu Total (s)"]),
            "latensi": float(row["Latensi Rata-rata (s)"]),
            "throughput": float(row["Jumlah Client"]) /
                          float(row["Waktu Total (s)"])
        })

# Menghitung speedup dan efisiensi
speedup = t1 / t3
efficiency = (speedup / 3) * 100

# Menyiapkan data grafik
x_clients = [str(r["clients"]) for r in results_data]
x_pos = list(range(len(x_clients)))

y_latensi = [r["latensi"] for r in results_data]
y_throughput = [r["throughput"] for r in results_data]

# Pengaturan tampilan
plt.style.use("default")
fig, axs = plt.subplots(1, 3, figsize=(18, 6))

# =====================================
# GRAFIK 1: PERBANDINGAN WAKTU EKSEKUSI
# =====================================

labels = ["1 Worker", "3 Workers"]
waktu = [t1, t3]

bars = axs[0].bar(
    labels,
    waktu,
    color=["#d9534f", "#5cb85c"],
    width=0.5
)

axs[0].set_title(
    "Perbandingan Waktu Eksekusi",
    fontsize=11,
    fontweight="bold"
)

axs[0].set_ylabel("Waktu Eksekusi (detik)")
axs[0].grid(axis="y", linestyle="--", alpha=0.5)

for bar in bars:
    height = bar.get_height()

    axs[0].annotate(
        f"{height:.2f}s",
        (bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        fontweight="bold"
    )

axs[0].text(
    0.5, 0.88,
    f"Speedup: {speedup:.2f}x\nEfisiensi: {efficiency:.2f}%",
    transform=axs[0].transAxes,
    ha="center",
    fontsize=10,
    fontweight="bold",
    bbox=dict(
        facecolor="white",
        edgecolor="gray",
        alpha=0.9
    )
)

# =====================================
# GRAFIK 2: LATENSI
# =====================================

axs[1].plot(
    x_pos,
    y_latensi,
    marker="o",
    color="#f0ad4e",
    linewidth=2.5,
    markersize=8
)

axs[1].set_title(
    "Latensi Rata-rata vs Beban Client",
    fontsize=11,
    fontweight="bold"
)

axs[1].set_xlabel("Jumlah Client Konkuren")
axs[1].set_ylabel("Latensi (detik)")
axs[1].set_xticks(x_pos)
axs[1].set_xticklabels(x_clients)
axs[1].grid(True, linestyle="--", alpha=0.5)

for i, value in enumerate(y_latensi):
    axs[1].annotate(
        f"{value:.2f}s",
        (x_pos[i], value),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold"
    )

# =====================================
# GRAFIK 3: THROUGHPUT
# =====================================

axs[2].plot(
    x_pos,
    y_throughput,
    marker="s",
    color="#0275d8",
    linewidth=2.5,
    markersize=8
)

axs[2].set_title(
    "Throughput Sistem vs Beban Client",
    fontsize=11,
    fontweight="bold"
)

axs[2].set_xlabel("Jumlah Client Konkuren")
axs[2].set_ylabel("Throughput (request/detik)")
axs[2].set_xticks(x_pos)
axs[2].set_xticklabels(x_clients)
axs[2].grid(True, linestyle="--", alpha=0.5)

for i, value in enumerate(y_throughput):
    axs[2].annotate(
        f"{value:.4f}",
        (x_pos[i], value),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold"
    )

# =====================================
# MENYIMPAN GRAFIK
# =====================================

plt.suptitle(
    "LAPORAN EVALUASI PERFORMA ARSITEKTUR MASTER-WORKER gRPC",
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout()

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("=" * 55)
print("GRAFIK BENCHMARK BERHASIL DIPERBARUI")
print("=" * 55)
print(f"Speedup    : {speedup:.2f}x")
print(f"Efisiensi  : {efficiency:.2f}%")
print(f"File grafik: {output_path}")
print("=" * 55)
