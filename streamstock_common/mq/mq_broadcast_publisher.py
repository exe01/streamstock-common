from .mq_publisher import MQPublisher
from pika.exceptions import AMQPError
import json


class MQBroadcastPublisher(MQPublisher):
    def publish(self, exchange_name, body=None, count_of_trying=2):
        if self._channel is None:
            self.connect()

        json_body = json.dumps(body)

        while count_of_trying > 0:
            status = self._broadcast_publish(exchange_name, json_body)

            if status is False:
                self.reconnect()
                count_of_trying -= 1
            else:
                count_of_trying = 0

    def _broadcast_publish(self, exchange_name, json_body):
        try:
            self.logger.info('{} publishes in exchange {}: {}'.format(self.name, exchange_name, str(json_body)))

            self._channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
            self._channel.basic_publish(exchange=exchange_name,
                                        routing_key='',
                                        body=json_body)
        except AMQPError as err:
            self.logger.error('{}: {}'.format(self.name, repr(err)))
            return False
        else:
            return True
