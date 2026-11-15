#!/usr/bin/env python3
"""
Rapido Driver Consumer
Subscribes to the rapido-dispatch topic exchange with a binding pattern.
Usage: python driver.py <NAME> <PATTERN>
Example: python driver.py Ravi "bangalore.koramangala.*"
Env:   AMQP_URL  (default: amqp://guest:guest@localhost:5672/)
"""
import json
import os
import sys
from datetime import datetime

import pika

EXCHANGE = "rapido-dispatch"
AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@localhost:5672/")


def main():
    if len(sys.argv) < 3:
        print("Usage: python driver.py <NAME> <PATTERN>")
        sys.exit(1)

    name = sys.argv[1]
    pattern = sys.argv[2]

    params = pika.URLParameters(AMQP_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare exchange
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    # Declare a queue named after the driver so multiple drivers can run simultaneously
    queue_name = f"driver.{name}"
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=pattern)

    print(f"[{name}] Listening on queue '{queue_name}' with pattern '{pattern}'")

    def callback(ch, method, properties, body):
        try:
            msg = json.loads(body)
        except json.JSONDecodeError:
            print(f"[{name}] REJECTED (invalid JSON)")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # D3: reject messages missing the 'zone' field
        if 'zone' not in msg:
            print(
                f"[{name}] REJECTED (missing zone) | id={msg.get('id')} | "
                f"routing_key={method.routing_key} | ts={msg.get('ts')}"
            )
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Good message — ACK
        ts_recv = datetime.now().strftime("%H:%M:%S")
        print(
            f"[{name}] ACK | id={msg['id']} | city={msg['city']} | "
            f"zone={msg['zone']} | type={msg['type']} | "
            f"routing_key={method.routing_key} | received_at={ts_recv}"
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n[{name}] Stopped.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
