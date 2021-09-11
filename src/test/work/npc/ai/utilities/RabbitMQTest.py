import unittest

import javaobj.v2 as javaobj
import pika

from work.npc.ai.utilities import Utilities
from work.npc.ai.utilities.StreamReceiver import StreamReceiver
from work.npc.ai.utilities.StreamSender import StreamSender


class RabbitMQTest(unittest.TestCase):
    def test_something(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='hello')

        #
        # channel.basic_publish(exchange='',
        #                       routing_key='hello',
        #                       body='Hello World!'.encode("utf-8"))
        # print(" [x] Sent 'Hello World!'")

        def callback(ch, method, properties, body):
            stuff = javaobj.loads(body)
            # print(" [x] Received %s, app=%s, users=%s" % (
            #         stuff.content.value,
            #         stuff.app.value,
            #         ",".join([u.value for u in list(stuff.userIds)])
            #     ))
            print(" [x] Received a=%d, b=%s" % (
                stuff.a,
                stuff.b
            ))
            # sys.stdout.flush()

        queueName = "hello"
        # queueName = "event.trans.ai.queue"

        channel.basic_consume(queue=queueName,
                              auto_ack=True,
                              on_message_callback=callback)

        channel.start_consuming()

        self.assertEqual(True, False)

    def test_sending(self):
        sender = StreamSender.of("amqp://localhost?queue=hello&format=json")

        sender.send("abc")

    def test_receiving(self):
        def callback(data):
            print(" [x] Received %s", data)

        receiver = StreamReceiver.of("amqp://localhost?queue=hello&format=json", callback)

        receiver.receiving()

        self.assertEqual(True, False)

    def test_receivingJava(self):
        def callback(data):
            print("got it")
            print(f" [x] Received {data}")
            Utilities.printObject(data)

        receiver = StreamReceiver.of("amqp://localhost?queue=hello&format=javaobj", callback)

        receiver.receiving()

        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
