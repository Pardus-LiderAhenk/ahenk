from kafka import KafkaConsumer, consumer
from base.scope import Scope
import json
import threading


class MessageConsumer(threading.Thread):
    #broker: object = ""
    #topic = ""
    #group_id = ""
    #logger = None
    #consumer = None

    def __init__(self, broker, topic, group_id):
        threading.Thread.__init__(self)
        scope = Scope.get_instance()
        self.event_manger = scope.get_event_manager()
        self.logger = scope.get_logger()
        self.broker = broker
        self.topic = topic
        self.group_id = group_id
        self.consumer = KafkaConsumer(bootstrap_servers=self.broker,
                                      group_id='python-my-group',
                                      # consumer_timeout_ms = 60000,
                                      auto_offset_reset='earliest',
                                      enable_auto_commit=False,
                                      value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                                      )

    def run(self):
        self.consumer.subscribe(self.topic)
        print("consumer is listening....")
        try:
            for message in self.consumer:
                #print("received message = ", message.value['hostname'])
                print("received message = ", message)
                try:
                    message_type = message.value['type']
                    self.logger.debug("Get message type: " + str(message_type))

                    if message_type == "EXECUTE_POLICY":
                        self.logger.info('---------->Received message: {0}'.format(str(message)))

                    if message_type == "EXECUTE_TASK":
                        task = json.loads(str(message.value['task']))
                        # plugin_name = task['plugin']['name']
                        parameter_map = task['parameterMap']
                        use_file_transfer = message.value['fileServerConf']
                        is_password = False
                        for key, value in parameter_map.items():
                            if "password" in key.lower():
                                parameter_map[key] = "********"
                                task['parameterMap'] = parameter_map
                                message.value['task'] = task
                                is_password = True
                        if use_file_transfer != None:
                            # message['fileServerConf'] = "*******"
                            file_server_conf = message.value['fileServerConf']
                            file_server_param = file_server_conf['parameterMap']
                            for key, value in file_server_param.items():
                                if "password" in key.lower():
                                    file_server_param[key] = "********"
                                    file_server_conf['parameterMap'] = file_server_param
                                    # message['fileServerConf']['parameterMap'] = file_server_param
                                    message.value['fileServerConf'] = file_server_conf
                            is_password = True
                        if is_password:
                            self.logger.info('---------->Received message: {0}'.format(str(message)))
                        else:
                            self.logger.info('---------->Received message: {0}'.format(str(message)))
                    ss = json.dumps(message.value)
                    #ttt = eval(str(message.value))
                    self.event_manger.fireEvent(message_type, ss)
                    self.logger.debug('Fired event is: {0}'.format(message_type))
                except Exception as e:
                    self.logger.error(
                        'A problem occurred while keeping message. Error Message: {0}'.format(str(e)))
                # committing message manually after reading from the topic
                self.consumer.commit()
        except KeyboardInterrupt:
            print("Aborted by user...")
        finally:
            self.consumer.close()


'''
from kafka import KafkaConsumer, consumer
import json


class MessageConsumer():
    broker: object = ""
    topic = ""
    group_id = ""
    logger = None

    def __init__(self, broker, topic, group_id):
        self.broker = broker
        self.topic = topic
        self.group_id = group_id

    def listen(self):
        consumer=KafkaConsumer(bootstrap_servers=self.broker,
                                 group_id='python-my-group',
                                 #consumer_timeout_ms = 60000,
                                 auto_offset_reset='earliest',
                                 enable_auto_commit=False,
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                                 )

        consumer.subscribe(self.topic)
        print("consumer is listening....")
        try:
            for message in consumer:
                print("received message = ", message.value['hostname'])
                #committing message manually after reading from the topic
                consumer.commit()
        except KeyboardInterrupt:
            print("Aborted by user...")
        finally:
            consumer.close()
'''