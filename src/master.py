import grpc
import time
import random
import sys
import threading
import prime_pb2
import prime_pb2_grpc
from concurrent.futures import ThreadPoolExecutor

MAX_NUM = 10_000_000  # Rentang pencarian 1 hingga 10 Juta
CHUNK_SIZE = 500_000  
ALL_WORKERS = ['localhost:50051', 'localhost:50052', 'localhost:50053']

global_primes = []
lock = threading.Lock()
completed_chunks = 0
total_chunks_count = 0

def process_chunk(start, end, chunk_id, active_workers, is_benchmark):
    global completed_chunks
    
    if not is_benchmark:
        print(f"🔄 [CHUNK {chunk_id+1}/{total_chunks_count}] Memproses rentang {start:,} s.d {end:,}...")

    for attempt in range(3):
        target_worker = random.choice(active_workers)
        try:
            with grpc.insecure_channel(target_worker) as channel:
                stub = prime_pb2_grpc.PrimeServiceStub(channel)
                # Cek kesehatan worker sebelum kirim tugas
                stub.CheckHealth(prime_pb2.Empty(), timeout=2)
                
                req = prime_pb2.TaskRequest(request_id=f"TASK_{chunk_id}_{attempt}", start_num=start, end_num=end)
                response_stream = stub.FindPrimes(req, timeout=60)
                
                local_results = [res.prime_number for res in response_stream]
                with lock:
                    global_primes.extend(local_results)
                    completed_chunks += 1
                    
                if not is_benchmark:
                    print(f"✅ [CHUNK {chunk_id+1}] Selesai oleh worker {target_worker} | Ditemukan {len(local_results):,} prima (Progress: {completed_chunks}/{total_chunks_count})")
                return True
        except grpc.RpcError:
            if not is_benchmark:
                print(f"⚠️ [CHUNK {chunk_id+1}] Gagal di {target_worker} (Percobaan {attempt+1}/3), mencoba ulang...")
            time.sleep(0.5)
            
    if not is_benchmark:
        print(f"❌ [CHUNK {chunk_id+1}] Gagal total setelah 3 percobaan!")
    return False

def main():
    global total_chunks_count, completed_chunks
    is_benchmark = "--benchmark" in sys.argv
    
    num_workers = len(ALL_WORKERS)
    for arg in sys.argv:
        if arg.isdigit():
            num_workers = int(arg)
            
    active_workers = ALL_WORKERS[:num_workers]
    
    # Buat pembagian chunk
    chunks = [(i, min(i + CHUNK_SIZE - 1, MAX_NUM)) for i in range(1, MAX_NUM + 1, CHUNK_SIZE)]
    total_chunks_count = len(chunks)
    completed_chunks = 0
    
    if not is_benchmark:
        print("=" * 60)
        print(f"🚀 MEMULAI DISTRIBUSI TUGAS PENCARI PRIMA (1 s.d 10 Juta)")
        print(f"   Jumlah Worker Aktif : {len(active_workers)} node ({active_workers})")
        print(f"   Total Chunk         : {total_chunks_count} bagian (@ {CHUNK_SIZE:,} angka)")
        print("=" * 60)
    
    start_time = time.time()
    
    # Jalankan eksekusi paralel dengan ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(active_workers)) as executor:
        futures = []
        for idx, (start, end) in enumerate(chunks):
            futures.append(executor.submit(process_chunk, start, end, idx, active_workers, is_benchmark))
        for f in futures:
            f.result()
            
    total_time = time.time() - start_time
    
    if is_benchmark:
        # Format khusus untuk dibaca otomatis oleh benchmark.py
        print(f"{total_time:.4f}")
    else:
        print("=" * 60)
        print(f"🎉 KOMPUTASI SELESAI DENGAN SUKSES!")
        print(f" • Total Bilangan Prima Ditemukan : {len(global_primes):,}")
        print(f" • Waktu Eksekusi Total           : {total_time:.2f} detik")
        print("=" * 60)

if __name__ == '__main__':
    main()