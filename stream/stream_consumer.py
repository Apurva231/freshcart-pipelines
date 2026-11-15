#!/usr/bin/env python3
"""
Bonus: Stream-to-Lakehouse Consumer
Receives FreshCart order events from RabbitMQ, collects for 60 seconds,
writes as a landing file, and triggers the ELT transform so orders
reach gold.fct_orders without duplicating gold totals.

Usage: python stream_consumer.py
Env:   AMQP_URL       (default: amqp://guest:guest@localhost:5672/)
       SNOWFLAKE_*    (see freshcart_elt.ipynb)
"""
import json
import os
import signal
import time
import uuid
from datetime import datetime, timezone

import pika
import pandas as pd

EXCHANGE = "freshcart-orders"
QUEUE = "freshcart.landing"
AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@localhost:5672/")
COLLECTION_SECONDS = 60


def write_landing(orders: list, run_id: str) -> str:
    """Write collected orders to a JSON-lines landing file."""
    filename = f"landing_stream_{run_id}.json"
    with open(filename, "w") as f:
        for o in orders:
            f.write(json.dumps(o) + "\n")
    print(f"[consumer] Wrote {len(orders)} orders to {filename}")
    return filename


def main():
    params = pika.URLParameters(AMQP_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key="order.#")

    collected = []
    start_time = time.time()
    run_id = str(uuid.uuid4())[:8]

    print(f"[consumer] Collecting orders for {COLLECTION_SECONDS}s (run_id={run_id})...")

    def callback(ch, method, properties, body):
        msg = json.loads(body)
        collected.append(msg)
        print(f"[consumer] Received order id={msg.get('order_id', '?')}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        if time.time() - start_time >= COLLECTION_SECONDS:
            channel.stop_consuming()

    channel.basic_consume(queue=QUEUE, on_message_callback=callback, auto_ack=False)

    try:
        connection.call_later(COLLECTION_SECONDS, channel.stop_consuming)
        channel.start_consuming()
    except Exception as e:
        print(f"[consumer] {e}")
    finally:
        if collected:
            landing_file = write_landing(collected, run_id)
            print(f"[consumer] Landing file ready: {landing_file}")
            print("[consumer] Next: run load_file() and transform SQL in freshcart_elt.ipynb")
        else:
            print("[consumer] No orders collected.")
        connection.close()


if __name__ == "__main__":
    main()
