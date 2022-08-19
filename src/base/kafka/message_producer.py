from kafka import KafkaProducer


class MessageProducer:
    broker = ""

    def __init__(self, broker):
        self.broker = broker

    def produce_message(self, topic, key, message):
        producer = KafkaProducer(bootstrap_servers=self.broker)
        producer.send(topic=topic, value=message.encode(), key=key.encode())
