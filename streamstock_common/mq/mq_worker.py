import pika
import time
import logging


class MQWorker:
    def __init__(self, connection_params, name='MQWorker'):
        self.logger = logging.getLogger(__name__)
        self.connection_params = connection_params
        self._connection = None
        self._channel = None
        self.name = name

    def connect(self):
        self.reconnect()

    def reconnect(self):
        while True:
            try:
                self._reconnect()
                break
            except Exception as err:
                self._handle_error(err)
                self.logger.info('{}: Try to reconnect in 5 sec'.format(self.name))
                time.sleep(5)

    def _reconnect(self):
        self.logger.info('{}: Try to create MQ connection'.format(self.name))
        self._create_connection()
        self.logger.info('{}: MQ connection created'.format(self.name))

        self.logger.info('{}: Try to create MQ channel'.format(self.name))
        self._create_channel()
        self.logger.info('{}: MQ channel created '.format(self.name))

    def _create_connection(self):
        self._connection = pika.BlockingConnection(self.connection_params)

    def _create_channel(self):
        self._channel = self._connection.channel()

    def _handle_error(self, err, name=None):
        if name is None:
            name = self.name

        if hasattr(err, 'message'):
            self.logger.error('{}: {}'.format(name, err.message))
        else:
            self.logger.error('{}: {}'.format(name, repr(err)))

        self.logger.exception(err)
