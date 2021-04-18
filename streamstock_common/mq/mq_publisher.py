from .mq_worker import MQWorker
from pika.exceptions import AMQPError
import pika
import json


class MQPublisher(MQWorker):
    def __init__(self, mq_host, mq_port, name):
        connection_params = pika.ConnectionParameters(host=mq_host,
                                                      port=mq_port,
                                                      heartbeat=600,
                                                      blocked_connection_timeout=300)
        super().__init__(connection_params, name)

    def publish(self, queue_name, body=None, count_of_trying=2):
        if self._channel is None:
            self.connect()

        json_body = json.dumps(body)

        while count_of_trying > 0:
            status = self._basic_publish(queue_name, json_body)

            if status is False:
                self.reconnect()
                count_of_trying -= 1
            else:
                count_of_trying = 0

    def close(self):
        self.logger.info('{}: Cancel channel and close connection'.format(self.name))
        self._channel.cancel()
        self._connection.close()

    def _basic_publish(self, queue_name, json_body):
        try:
            self.logger.info('{} publishes in {}: {}'.format(self.name, queue_name, str(json_body)))
            self._channel.basic_publish(exchange='',
                                        routing_key=queue_name,
                                        body=json_body)
        except AMQPError as err:
            self.logger.error('{}: {}'.format(self.name, repr(err)))
            return False
        else:
            return True


class MQPublisherSingleton(MQPublisher):
    _instances = {}

    @staticmethod
    def get_instance(mq_host, mq_port, name) -> MQPublisher:
        if name in MQPublisherSingleton._instances:
            return MQPublisherSingleton._instances[name]
        else:
            mq_publisher = MQPublisherSingleton(mq_host, mq_port, name)
            MQPublisherSingleton._instances[name] = mq_publisher
            return mq_publisher
