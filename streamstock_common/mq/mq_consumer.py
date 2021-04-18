from .mq_worker import MQWorker
from pika.exceptions import AMQPError, ChannelClosedByClient
import pika
import json
import time


class MQConsumer(MQWorker):
    def __init__(self, mq_host, mq_port, name):
        connection_params = pika.ConnectionParameters(host=mq_host,
                                                      port=mq_port,
                                                      heartbeat=600,
                                                      blocked_connection_timeout=300)

        super().__init__(connection_params, name)
        self.callbacks = {}

    def start_infinity_consuming(self):
        self.logger.debug('{}: Infinity consuming has started'.format(self.name))
        while True:
            try:
                self.connect()
                self.declare_callbacks()

                self.logger.debug('{}: Start consuming'.format(self.name))
                self._channel.start_consuming()
                self.logger.debug('{}: Consuming was ended'.format(self.name))

                self.close_channel_and_connection()
                self.logger.debug('{}: Channel and connection are closed'.format(self.name))
                break
            except ChannelClosedByClient:
                self.logger.debug('{}: Consuming was stopped and ended'.format(self.name))
                break
            except AMQPError as err:
                self._handle_error(err)
                time.sleep(5)
                continue

    def stop_consuming(self):
        self.logger.debug('{}: Stop consuming'.format(self.name))
        self._channel.stop_consuming()

    def close_channel_and_connection(self):
        self._channel.close()
        self._connection.close()

    @property
    def is_closed(self):
        return self._channel.is_closed

    def declare_callbacks(self):
        for callback_name, callback in self.callbacks.items():
            self.logger.debug('{}: declare queue {}'.format(self.name, callback_name))
            self._channel.queue_declare(callback_name)
            self._channel.basic_consume(queue=callback_name,
                                        auto_ack=True,
                                        on_message_callback=callback)

    def add_callback(self, fun, fun_name):
        def callback_decorator(ch, method, properties, body):
            body = json.loads(body)
            self.logger.debug('{}: received "{}"'.format(self.name, str(body)))
            return fun(body)

        self.callbacks[fun_name] = callback_decorator
