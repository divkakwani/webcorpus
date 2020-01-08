
import pika
import json


URL = 'amqp://qqxmvctd:n0zXmr7gNYGv-Rj9pkBty8ZFEUfH7bP7'\
      '@orangutan.rmq.cloudamqp.com/qqxmvctd'
param = pika.connection.URLParameters(URL)
connection = pika.BlockingConnection(param)
channel = connection.channel()
channel.exchange_declare(exchange='crawler-events', exchange_type='fanout', durable=True)


class RemoteChannel:
    """
    Each spider creates its own spider controller by passing the spider name.
    Internally, the events are published/consumed using a rabbitmq message
    broker.

    publish
    ========
    The events are published in the `crawler-events` exchange. The exchange
    has type fanout, which means any number of consumers can attach a queue
    to this exchange and listen to all the crawl events. The consumer
    is generally an instance of webcorpus-dashboard

    consume
    =======
    control commands are published in the `crawler-commands` exchange, which
    has type direct. To listen to the commands, one needs to create a queue
    and bind it to that exchange.

    """

    def __init__(self, iden):
        self.iden = iden

    def send_event(self, event):
        global channel
        try:
            dump = json.dumps(event)
            channel.basic_publish(exchange='crawler-events',
                                  routing_key=self.iden, body=dump)
        except:
            pass

