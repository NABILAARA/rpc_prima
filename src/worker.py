import grpc
import sys
from concurrent import futures
import prime_pb2
import prime_pb2_grpc

def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

class PrimeServicer(prime_pb2_grpc.PrimeServiceServicer):
    def CheckHealth(self, request, context):
        return prime_pb2.StatusResponse(is_alive=True, message="OK")

    def FindPrimes(self, request, context):
        for num in range(request.start_num, request.end_num + 1):
            if is_prime(num):
                yield prime_pb2.PrimeResult(prime_number=num)

    def GetMetrics(self, request, context):
        return prime_pb2.StatusResponse(is_alive=True, message="Normal")

    def AbortTask(self, request, context):
        return prime_pb2.Empty()

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    prime_pb2_grpc.add_PrimeServiceServicer_to_server(PrimeServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    print(f"[WORKER] Berjalan di port {port}...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else "50051"
    serve(port)