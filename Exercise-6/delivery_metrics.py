
from prometheus_client import start_http_server, Summary, Gauge
import random
import time

# Define delivery metrics
total_deliveries = Gauge(
    "total_deliveries", "Total number of deliveries"
)
pending_deliveries = Gauge(
    "pending_deliveries", "Number of pending deliveries"
)
on_the_way_deliveries = Gauge(
    "on_the_way_deliveries", "Number of deliveries on the way"
)
average_delivery_time = Summary(
    "average_delivery_time", "Delivery time in seconds"
)

def simulate_delivery():
    pending = random.randint(10, 20)
    on_the_way = random.randint(5, 20)
    delivered = random.randint(30, 70)
    avg_time = random.uniform(15, 45)

    total = pending + on_the_way + delivered

    print(f"Total deliveries: {total}")
    print(f"Pending deliveries: {pending}")
    print(f"On-the-way deliveries: {on_the_way}")
    print(f"Delivery time: {avg_time:.2f} seconds")
    print("-" * 35)

    total_deliveries.set(total)
    pending_deliveries.set(pending)
    on_the_way_deliveries.set(on_the_way)
    average_delivery_time.observe(avg_time)

if __name__ == "__main__":
    print("Starting metrics server on port 8000...")
    start_http_server(8000, addr="0.0.0.0")

    while True:
        simulate_delivery()
        time.sleep(1)
