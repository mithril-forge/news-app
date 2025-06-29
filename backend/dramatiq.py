import dramatiq
from dramatiq.brokers.redis import RedisBroker

# Simple Redis broker setup
redis_broker = RedisBroker(url="redis://localhost:6379")
dramatiq.set_broker(redis_broker)

# Example task - replace with your own
@dramatiq.actor
def send_email(email: str, message: str):
    """Simple email task"""
    print(f"Sending email to {email}: {message}")
    # Add your email logic here

@dramatiq.actor
def process_data(data: str):
    """Simple data processing task"""
    print(f"Processing: {data}")
    # Add your processing logic here

# Add more tasks here...