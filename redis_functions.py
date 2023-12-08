from redis import Redis
import os


redis = Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"],
)


def save_usage(cb):
    usage = redis.get("Profi_usage")
    usage = float(usage) + cb.total_cost if usage else cb.total_cost
    redis.set("Profi_usage", usage)


def set_user(name, user_id):
    redis.set(name, user_id, ex=86400)


def get_user(name):
    return redis.get(name)
