

```markdown
# Proyek Mini RPC: Sistem Terdistribusi Master-Worker (Pencarian Bilangan Prima)

Mata Kuliah: **Komputasi Paralel dan Terdistribusi**  
Studi Kasus 2: Komputasi Terdistribusi (Master-Worker) menggunakan gRPC[cite: 13]

---

## 📋 1. Deskripsi Proyek
Proyek ini mengimplementasikan sistem komputasi terdistribusi dengan arsitektur **Master-Worker** menggunakan kerangka kerja **gRPC** dan **Protocol Buffers** (IDL)[cite: 13, 14]. Sistem bertugas mencari seluruh bilangan prima dalam rentang **1 hingga 10.000.000**[cite: 13]. 

Beban komputasi yang berat (*CPU-bound*) dipecah oleh node **Master** ke dalam beberapa *chunk* data dan didistribusikan secara paralel ke 3 kontainer **Worker** yang berjalan secara terisolasi di atas **Docker**.

### Fitur Utama:
1. **gRPC & Protocol Buffers:** Menggunakan komunikasi biner efisien berbasis HTTP/2 dengan mendefinisikan 4 metode RPC (termasuk *Server Streaming*)[cite: 13, 14].
2. **Concurrency & Thread Safety:** Sisi *Master* menggunakan `ThreadPoolExecutor` untuk pengiriman tugas paralel, serta dilindungi `threading.Lock()` untuk mencegah *race condition* saat menulis hasil ke memori global[cite: 13, 14].
3. **Toleransi Kegagalan (*Fault Tolerance*):** Dilengkapi mekanisme *Timeout* dan *Retry* (hingga 3 kali percobaan) dengan jaminan operasi idempoten menggunakan `request_id`[cite: 13, 14].
4. **Automated Benchmarking:** Dilengkapi skrip otomatis untuk menghitung nilai ***Speedup*** ($Waktu_1 / Waktu_N$) serta uji beban (*Load Testing*) untuk **1, 5, dan 20 client** bersamaan[cite: 13, 14].

---

## 🗂️ 2. Struktur Direktori Proyek
```text
rpc_prima/
│
├── proto/
│   └── prime.proto          # Kontrak layanan IDL gRPC
│
├── src/
│   ├── master.py            # Logika utama client/master (Concurrency & Fault Tolerance)
│   ├── worker.py            # Logika server pencari prima (gRPC Servicer)
│   └── benchmark.py         # Skrip otomatis pengujian kinerja (Speedup & Load Test)
│
├── hasil_benchmark/         # Folder hasil keluaran otomatis
│   ├── tabel_benchmark.csv  # Tabel data metrik kinerja
│   └── grafik_benchmark.png # Visualisasi grafik (Speedup, Latensi, Throughput)
│
├── venv/                    # Python Virtual Environment
├── requirements.txt         # Daftar pustaka dependensi
├── Dockerfile               # Konfigurasi container image worker
├── .gitignore               # Konfigurasi file yang diabaikan Git
└── README.md                # Dokumentasi proyek

```

---

## ⚙️ 3. Persiapan & Instalasi Lingkungan

Pastikan Anda menggunakan sistem operasi Linux (atau WSL) dan telah menginstal **Python 3.10+** serta **Docker Engine**.

1. **Buat dan Aktifkan Virtual Environment:**
```bash
python3 -m venv venv
source venv/bin/activate

```


2. **Instal Pustaka Dependensi:**
```bash
pip install -r requirements.txt

```


3. **Generate Stub gRPC (Protocol Buffers):**
Kompilasi file `.proto` agar menghasilkan file stubs `_pb2.py` dan `_pb2_grpc.py` di dalam folder `src/`:
```bash
python3 -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src proto/prime.proto

```



---

## 🐳 4. Menjalankan Server (Docker Containers)

Sistem berjalan di atas **3 kontainer Docker berbeda** (memenuhi syarat minimal 2+ container/mesin) untuk mensimulasikan lingkungan terdistribusi.

Anda bisa menggunakan salah satu cara berikut:

* **Opsi A: Menggunakan Docker Compose (Direkomendasikan)**
```bash
sudo docker compose up --build -d

```


* **Opsi B: Menjalankan Manual Satu Per Satu**
```bash
sudo docker build -t worker-prima .
sudo docker run -d --name worker1 -p 50051:50051 worker-prima python3 src/worker.py 50051
sudo docker run -d --name worker2 -p 50052:50051 worker-prima python3 src/worker.py 50051
sudo docker run -d --name worker3 -p 50053:50051 worker-prima python3 src/worker.py 50051

```


*(Pastikan kontainer aktif dengan mengetik `sudo docker ps`)*.

---

## 🚀 5. Cara Menjalankan Program & Pengujian Kinerja

* **Menjalankan Komputasi Utama (Master):**
Untuk menjalankan proses pencarian prima dari 1 sampai 10.000.000 secara normal:
```bash
python3 src/master.py

```


* **Menjalankan Pengujian Kinerja Otomatis (Benchmark):**
Untuk mengeksekusi pengujian *Speedup* (1 Worker vs 3 Worker) serta pengujian beban *throughput* dan latensi (1, 5, dan 20 client bersamaan):


```bash
python3 src/benchmark.py

```


> **Catatan:** Setelah skrip ini selesai, tabel hasil pengujian akan tercetak di terminal, dan file laporan berupa tabel CSV serta grafik PNG beresolusi tinggi akan tersimpan otomatis di dalam folder `hasil_benchmark/`.



---

## 👥 6. Anggota Kelompok & Pembagian Tugas

| Nama | NIM | Peran & Kontribusi Utama |
| --- | --- | --- |
| **Ismatul Ilmi & Nabila Rohmatul Aulia** | 247006111137 & 247006111143 | Implementasi *Master-Worker*, Logika Konkurensi (`ThreadPoolExecutor`),Integrasi gRPC, Desain Kontrak `.proto`, Mekanisme *Fault Tolerance* (*Retry & Timeout*), Dokumentasi, Konfigurasi Kontainer Docker, Skrip Pengujian *Benchmark*, dan Analisis Kinerja |

```
