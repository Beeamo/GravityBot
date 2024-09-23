import time
from queue import Queue
from threading import Lock, Thread

class RoleRateLimiter:
    def __init__(self, limit, window_size):
        self.limit = limit
        self.window_size = window_size
        self.requests = []
        self.queue = Queue()
        self.lock = Lock()
        self.timer_thread = Thread(target=self.timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def check_request(self):
        self.queue.put(time.time())
        self.queue.join()  # Wait until the queue is empty
        with self.lock:
            # Remove expired requests
            current_time = time.time()
            self.requests = [req for req in self.requests if current_time - req <= self.window_size]
            
            # Check if the number of requests exceeds the limit
            if len(self.requests) >= self.limit:
                # Calculate the time until the next retry
                next_retry_time = self.requests[0] + self.window_size
                retry_duration = max(0, next_retry_time - current_time)
                return retry_duration
            
            # Add the current request to the list
            self.requests.append(current_time)
            return 0  # No retry needed

    def timer(self):
        while True:
            time.sleep(self.window_size / 10)
            with self.lock:
                current_time = time.time()
                self.requests = [req for req in self.requests if current_time - req <= self.window_size]
                while not self.queue.empty():  # Consume items from the queue
                    self.queue.get()
                    self.queue.task_done()

# Singleton pattern to ensure there's only one instance of RateLimiter
rate_limiter_instance = None

def get_rate_limiter(limit=1, window_size=1):
    global rate_limiter_instance
    if rate_limiter_instance is None:
        rate_limiter_instance = RoleRateLimiter(limit, window_size)
    return rate_limiter_instance
