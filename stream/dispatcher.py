#!/usr/bin/env python3
"""
FreshCart / Rapido Dispatcher
Publishes food-order/ride-request events to a RabbitMQ topic exchange.
Usage: python dispatcher.py
Env:   AMQP_URL  (default: amqp://guest:guest@localhost:5672/)
"""
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

import pika

EXCHANGE = "rapido-dispatch"
AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@localhost:5672/")

CITIES = ["bangalore", "chennai"]
ZONES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield"],
    "chennai": ["tnagar", "adyar", "velachery"],
}
TYPES = ["ride", "food"]


def main():
    params = pika.URLParameters(AMQP_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    print(f"[dispatcher] Connected. Publishing to exchange '{EXCHANGE}'")

    counter = 0
    try:
        while True:
            counter += 1
            city = random.choice(CITIES)
            zone = random.choice(ZONES[city])
            order_type = random.choice(TYPES)
            order_id = str(uuid.uuid4())[:8]
            ts = datetime.now(timezone.utc).isoformat()

            # Every 10th message is a "bad" message (missing zone field) for D3
            if counter % 10 == 0:
                body = {
                    "id": order_id,
                    "city": city,
                    # zone intentionally omitted
                    "type": order_type,
                    "ts": ts,
                    "_bad": True,
                }
                routing_key = f"{city}.MISSING.{order_type}"
                print(f"[dispatcher] BAD  msg #{counter}: routing_key={routing_key} body={body}")
            else:
                body = {
                    "id": order_id,
                    "city": city,
                    "zone": zone,
                    "type": order_type,
                    "ts": ts,
                }
                routing_key = f"{city}.{zone}.{order_type}"
                print(f"[dispatcher] GOOD msg #{counter}: routing_key={routing_key}")

            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(body),
                properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
            )
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[dispatcher] Stopped.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
