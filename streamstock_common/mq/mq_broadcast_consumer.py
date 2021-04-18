from .mq_consumer import MQConsumer


class MQBroadcastConsumer(MQConsumer):
    def declare_callbacks(self):
        for callback_name, callback in self.callbacks.items():
            self.logger.debug('{}: declare exchange {}'.format(self.name, callback_name))
            self._channel.exchange_declare(exchange=callback_name, exchange_type='fanout')

            result = self._channel.queue_declare(queue='', exclusive=False, auto_delete=True)
            queue_name = result.method.queue
            self._channel.queue_bind(exchange=callback_name, queue=queue_name)

            self._channel.basic_consume(queue=queue_name,
                                        auto_ack=True,
                                        on_message_callback=callback)
