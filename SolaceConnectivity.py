import os
import platform
import sys
import time
import psutil
import logging
import uuid
import threading
from enum import Enum
from datetime import datetime
# Solace Python API modules
import solace
from solace.messaging.messaging_service import MessagingService, ReconnectionListener, ReconnectionAttemptListener, \
    ServiceInterruptionListener, RetryStrategy, ServiceEvent
from solace.messaging.resources.topic import Topic
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.publisher.direct_message_publisher import PublishFailureListener
from solace.messaging.receiver.persistent_message_receiver import PersistentMessageReceiver
from solace.messaging.publisher.outbound_message import OutboundMessageBuilder
from solace.messaging.resources.topic import Topic
from solace.messaging.receiver.message_receiver import MessageHandler
from solace.messaging.resources.queue import Queue



logger = logging.getLogger('DirectPublisher')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s P%(process)d T%(thread)d (%(threadName)-9s) [%(levelname)s] %(message)s', )



class PublisherErrorHandling(PublishFailureListener):
    def on_failed_publish(self, e: "FailedPublishEvent"):
        logger.error(f"on_failed_publish {e}")


class ServiceEventHandler(ReconnectionListener, ReconnectionAttemptListener, ServiceInterruptionListener):
    def on_reconnected(self, e: ServiceEvent):
        logger.error("\non_reconnected")
        logger.error(f"Error cause: {e.get_cause()}")
        logger.error(f"Message: {e.get_message()}")

    def on_reconnecting(self, e: "ServiceEvent"):
        logger.error("\non_reconnecting")
        logger.error(f"Error cause: {e.get_cause()}")
        logger.error(f"Message: {e.get_message()}")

    def on_service_interrupted(self, e: "ServiceEvent"):
        logger.error("\non_service_interrupted")
        logger.error(f"Error cause: {e.get_cause()}")
        logger.error(f"Message: {e.get_message()}")


class PublishingType(Enum):
    TOPIC_DIRECT = 1
    PERSISTENT = 2


class SubscribtionType(Enum):
    TOPIC_DIRECT = 1  #
    QUEUE_DURABLE_EXCLUSIEVE = 2
    QUEUE_DURABLE_NON_EXCLUSIEVE = 3
    QUEUE_NON_DURABLE_EXCLUSIEVE = 4


"""
 
 
"""
class SolaceConnectivity():

    def __init__(self, sol_host, sol_vpn, sol_user, sol_psw, dbg=False):
        try:
            # self.logger = logger
            self.sol_host = sol_host
            self.sol_vpn = sol_vpn
            self.sol_user = sol_user
            self.service_handler = ServiceEventHandler()
            self.publishers = []
            self.receivers = []

            self.broker_props = {
                "solace.messaging.transport.host": os.environ.get('SOLACE_HOST') or sol_host,
                "solace.messaging.service.vpn-name": os.environ.get('SOLACE_VPN') or sol_vpn,
                "solace.messaging.authentication.scheme.basic.username": os.environ.get('SOLACE_USERNAME') or sol_user,
                "solace.messaging.authentication.scheme.basic.password": os.environ.get('SOLACE_PASSWORD') or sol_psw
            }
            self.service = MessagingService.builder() \
                .from_properties(self.broker_props) \
                .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(20, 3)) \
                .build()

            if dbg:
                self.service.set_core_messaging_log_level(level='DEBUG')
            else:
                logger.debug(f'Solace messaging package logging is off')

            self.service.add_reconnection_listener(self.service_handler)
            self.service.add_reconnection_attempt_listener(self.service_handler)
            self.service.add_service_interruption_listener(self.service_handler)
            self.service.connect()
            logger.debug(f'Solace service {self.service}')


            self.direct_rcv_builder = self.service.create_direct_message_receiver_builder()
            self.persistent_rcv_builder = self.service.create_persistent_message_receiver_builder()
            #on_back_pressure parameters should be added here if needed
            self.direct_pub_builder = self.service.create_direct_message_publisher_builder()
            self.persistent_pub_builder = self.service.create_persistent_message_publisher_builder()



            logger.debug(f'Builders created')
        except Exception as e:
            logger.error(f'Couldnt create Solace connection {e}')

    def is_server_connected(self):
        stat = self.service.is_connected
        logger.debug(
            f'Is Solace service {self.service} connected ? {stat}')
        return stat

    def disconnect_service(self):
        try:
            if self.service.is_connected:
                self.service.disconnect()
                logger.debug(f'Solace service {self.service} disconnected')
            else:
                logger.debug(f'Solace service {self.service} already disconnected')
        except Exception as e:
            logger.error(f'Failed to disconnect Solace service {self.service}')

    # to shutdown Solace connection gracefully and remove allocated resources
    def close_solace_connection(self):
        self.disconnect_service()
        for p in self.publishers:
            self.remove_publisher(p)
        for r in self.receivers:
            self.remove_receiver(r)

    def solace_connection_details(self):
        if self.service.is_connected:
            logger.info(
                f'Service connected to Solace message router using url: {self.sol_host}')
            logger.info(f'Solace message router VPN name: {self.sol_vpn}')
            logger.info(f'Client username: {self.sol_user}')
            logger.info(f'{len(self.publishers)} active publishers , {len(self.receivers)} active receivers')
        else:
            logger.info(f'Service is not connected')

    def create_publisher(self, mode, pub_err_lstnr):
        publisher = None
        try:
            if mode is TopicType.DIRECT:
                publisher = self.direct_pub_builder.build()
            elif mode is TopicType.PERSISTENT:
                publisher = self.persistent_pub_builder.build()
            publisher.set_publish_failure_listener(pub_err_lstnr)
            self.publishers.append(publisher)
            publisher.start()
            logger.debug(f'Publisher {mode} {publisher} created ')
        except Exception as e:
            logger.error(f'Failed to create publisher {e}')
        return publisher

    def create_direct_message_publisher(self, pub_err_lstnr):
        publisher = None
        try:
            publisher = self.direct_pub_builder.build()
            publisher.set_publish_failure_listener(pub_err_lstnr)
            self.publishers.append(publisher)
            publisher.start()
            logger.debug(f'Direct message publisher {publisher} started ')
        except Exception as e:
            logger.error(f'Failed to create direct message publisher {e}')
        return publisher

    def create_peristent_message_publisher(self, pub_err_lstnr):
        publisher = None
        try:
            publisher = self.persistent_pub_builder.build()
            publisher.set_publish_failure_listener(pub_err_lstnr)
            self.publishers.append(publisher)
            publisher.start()
            logger.debug(f'Persistent message publisher {publisher} created ')
        except Exception as e:
            logger.error(f'Failed to create persistent message publisher {e}')
        return publisher

    def is_publisher_ready(self, publisher):
        stat = publisher.is_ready()
        logger.debug(
            f'Is Publisher {publisher} ready ? {stat}')
        return stat

    def remove_publisher(self, publisher):
        try:
            self.publishers.remove(publisher)
            publisher.terminate()
            logger.debug(f'Publisher {publisher} terminated and  removed')
        except Exception as e:
            logger.error(f'Failed to terminate and remove publisher {e}')

    def remove_receiver(self, receiver):
        try:
            self.receivers.remove(receiver)
            receiver.terminate()
            logger.debug(f'Receiver {receiver} terminated and  removed')
        except Exception as e:
            logger.error(f'Failed to terminate and remove receiver {e}')

    # Direct topic receiver
    # Args:
    #   topics: list of topics names to subscribe to
    # Returns:
    #    receiver instance or None if failed to create
    def create_direct_message_receiver(self, topics: []):
        receiver = None
        try:
            topics_sub = []
            for t in topics:
                topics_sub.append(TopicSubscription.of(t))
            receiver = self.direct_rcv_builder.with_subscriptions(topics_sub).build()
            if receiver is not None:
                self.receivers.append(receiver)
                receiver.start()
                logger.debug(f'Direct message receiver {receiver} started')
        except Exception as e:
            logger.error(f'Failed to create Direct message type receiver for {topics} {e}')
        return receiver

    # Three types of Persistent receiver can be created (AUTO_ACK mode is used)
    # Args:
    #   mode: QUEUE_DURABLE_NON_EXCLUSIEVE, QUEUE_NON_DURABLE_EXCLUSIEVE, QUEUE_NON_DURABLE_EXCLUSIEVE
    #   end_point: Queue name
    # Returns:
    #    receiver instance or None if failed to create
    # Note:
    # Only durable endpoints may be provisioned.A non - durable endpoint is created when a Flow is bound to it.
    def create_persistent_message_receiver(self, mode: SubscribtionType, end_point: str, topics: [] = None):
        receiver = None
        try:
            if mode is SubscribtionType.QUEUE_DURABLE_EXCLUSIEVE:
                # More than one consumer can bind a flow to the queue, but only the first bound consumer receives messages.
                # If the processing consumer fails, the next bound consumer receives unprocessed messages and becomes
                # the active processing consumer. The queue persists whether there are consumers bound to the queue or not
                q = Queue.durable_exclusive_queue(end_point)
            elif mode is SubscribtionType.QUEUE_DURABLE_NON_EXCLUSIEVE:
                # Create a non-exclusive queue for load-balancing and fault tolerance to durable consumers, and more
                # than one consumer can bind to the queue. Messages are delivered in round-robin fashion for load-balancing.
                # If a consumer fails, it's unprocessed messages are forwarded to an active consumer. The queue persists
                # whether there are consumers bound to the queue or not.
                q = Queue.durable_non_exclusive_queue(end_point)
            elif mode is SubscribtionType.QUEUE_NON_DURABLE_EXCLUSIEVE:
                # Temporary queues follow the lifecycle of the client connection, and are useful
                # for ensuring message persistence while clients are online.
                # Create an exclusive temporary queue for non-durable consumers. More than one consumer can bind a flow to
                # the temporary queue, but only the first bound consumer receives messages.
                # If the processing consumer fails, the next bound consumer receives unprocessed messages and becomes
                # the active processing consumer. When there are no consumers connected to the queue, the queue doesn't persist.
                q = Queue.non_durable_exclusive_queue(end_point)
            else:
                q = None

            # prop receiver builder
            if q is not None:
                # adding AUTO_ACK
                bldr = self.persistent_rcv_builder.with_message_auto_acknowledgement()
                # topic subscribtions for tmp queues (QUEUE_NON_DURABLE_EXCLUSIEVE) adding
                if mode is SubscribtionType.QUEUE_NON_DURABLE_EXCLUSIEVE:
                    if topics is not None:
                        topics_sub = []
                        for t in topics:
                            topics_sub.append(TopicSubscription.of(t))
                        bldr = bldr.with_subscriptions(topics_sub)
                    else:
                        logger.error(
                            f'QUEUE_NON_DURABLE_EXCLUSIEVE mode requires list of topics as parameter')
                # create and start receiver
                receiver = bldr.build(q)
                if receiver is not None:
                    self.receivers.append(receiver)
                    receiver.start()
                    logger.debug(f'Persistent message receiver {receiver} started , {end_point} {mode}')
                else:
                    logger.error(f'Couldnt create receiver: {end_point} {mode}')
            else:
                    logger.error(f'Couldnt create queue: {end_point} {mode}')

        except Exception as e:
            logger.error(f'Failed to create message receiver: {mode } {end_point} {e}')

        return receiver

    @staticmethod
    def thread_info():
        logger.info(
            f'----- Threads ----------- Total({len(threading.enumerate())})/Active({threading.active_count()}) ----------')
        for t in threading.enumerate():
            logger.info({t})
        logger.info(f'-----------------------------------------------------------')


    @staticmethod
    def process_info(pid = None):
        def get_size(bytes, suffix="B"):
            factor = 1024
            for unit in ["", "K", "M", "G", "T", "P"]:
                if bytes < factor:
                    return f"{bytes:.2f}{unit}{suffix}"
                bytes /= factor
        if pid is None:
            pid = os.getpid()
        process = psutil.Process(pid)
        logger.info(f"============ Process ============")
        logger.info(f"User: {process.username()}")
        logger.info(f"Process Id: {process.pid}")
        logger.info(f"Process name: {process.name()}")
        logger.info(f"Create time: {datetime.fromtimestamp(process.create_time())}")
        logger.info(f"Process threads: {process.num_threads()}")
        logger.info(f"Process memory usage: {get_size(process.memory_full_info().uss)}")
        logger.info(f"CPU utilization: {process.cpu_percent()} %")

    @staticmethod
    def system_info(detailed=False):
        logger.info(f'OS: {platform.uname()}')
        logger.info(f'Python version: {platform.python_version()}')
        if detailed:
            def get_size(bytes, suffix="B"):
                factor = 1024
                for unit in ["", "K", "M", "G", "T", "P"]:
                    if bytes < factor:
                        return f"{bytes:.2f}{unit}{suffix}"
                    bytes /= factor
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            # and show them
            logger.info(f"============ CPU =============")
            logger.info(f"Physical cores: {psutil.cpu_count(logical=False)}")
            logger.info(f"Total cores: {psutil.cpu_count(logical=True)}")
            logger.info(f"CPU Usage Per Core:")
            for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
                logger.info(f"Core {i}: {percentage}%")
            logger.info(f"Total CPU Usage: {psutil.cpu_percent()}%")
            logger.info(f"=========== MEMORY =============")
            logger.info(f"Total: {get_size(mem.total)}")
            logger.info(f"Available: {get_size(mem.available)}")
            logger.info(f"Used: {get_size(mem.used)}")
            logger.info(f"Percentage: {mem.percent}%")
            logger.info(f"============= SWAP =============")
            logger.info(f"Total: {get_size(swap.total)}")
            logger.info(f"Free: {get_size(swap.free)}")
            logger.info(f"Used: {get_size(swap.used)}")
            logger.info(f"Percentage: {swap.percent}%")


    #convenience functions to create a message with the body and messageId
    def create_basic_message(self, seq_num, message_body, msg_Id=None):
        if msg_Id is None:
            msg_Id = uuid.uuid1()
        outbound_msg = self.service.message_builder() \
            .with_application_message_id(f'{msg_Id}') \
            .with_sequence_number(seq_num)\
            .build(message_body)
        return outbound_msg

    #instead of setting options an creating message again just supply msg body
    def reuse_basic_message(self, org_msg, seq_num, message_body, msg_Id=None):
        if msg_Id is None:
            msg_Id = uuid.uuid1()
        org_msg.solace_message.message_set_binary_attachment_string(f'{message_body}-M')
        org_msg.solace_message.set_message_application_message_id(f'{msg_Id}')
        org_msg.solace_message.set_message_sequence_number(seq_num)
        return org_msg

    #to check or to log details before sending them
    def get_message_details(self, msg, detailed=True):
        if detailed:
            logger.info(f"\n-------------------------------------\n" \
                  + f"{msg.solace_message.get_message_dump()}" \
                + "\n--------------------------------------\n")

        #logger.info(f"Msg seqNum: {msg.solace_message.get_message_sequence_number()}\
        #, msg Id: {msg.solace_message.get_message_id()}\
        #, app msg Id: {msg.solace_message.get_application_message_id()}\
        #, app msg Type: {msg.solace_message.get_application_message_type()}\
        #, correlationId: {msg.solace_message.message_get_correlation_id()}")
        #if detailed:
        #    logger.info(f"expiration: {msg.solace_message.get_expiration()}\
        #    , sender timestamp: {msg.solace_message.get_message_sender_timestamp()}\
        #    , priority: {msg.solace_message.get_message_priority()}\
        #    , priority: {msg.solace_message.get_delivery_mode()}")


    #use when basic message functionality is not enough
    # get message builder and add to it available chain options:
    # with_sequence_number() (int) The sequence number is carried in the message meta data.
    # with_application_message_id() (str) The application message identifier is carried in the message metadata
    # with_application_message_type() (str) The Application Message type is carried in the message meta data
    # with_priority() 0->9(int) The priority of the outbound message
    # with_expiration() timestamp(int) Sets message expiration time.
    # add any additional properties you need in metadata
    # with_property() Key(str) Value(str/int/bytearray)
    def get_msg_builder(self):
        return self.service.message_builder()



    #send message to topics specified in the list passed as parameter
    def send_message(self, publisher, msg, topics:[]):
        for dest in topics:
            logger.info(f'Sending message {msg.get_application_meessage_id()} to: {dest}')
            publisher.publish(destination=Topic.of(dest), message=msg)



#----------------------------------- Custom code ----------------------------------


#Handling received messges:
class MessageHandlerExample(MessageHandler):
    def on_message(self, message: 'InboundMessage'):

        #message dump returned by C code details
        print(f"\n-------------------------------------\n" \
              + f"{message.solace_message.get_message_dump()}" \
              + "\n--------------------------------------\n")

        # To get message payload use this one with default encoding utf-8
        print(f"Payload: {message.get_payload_as_bytes().decode()}")

        #These are hit amnd miss, some contain details most don't
        print("\n" + f"Message sender time: {message.get_sender_timestamp()} \n")
        print("\n" + f"Message payload details: {message.solace_message.message.get_payload_details()} \n")
        print("\n" + f"Message seqNum: {message.get_sequence_number()} \n")
        print("\n" + f"Message expiration: {message.get_expiration()} \n")
        priority = message.get_priority()
        if priority == SOLCLIENT_NOT_SET_PRIORITY_VALUE:
            print("\n" + f"Message priority: {priority} \n")
        print("\n" + f"Message correlationId: {message.get_correlation_id()} \n")
        print("\n" + f"Message applicationType: {message.get_application_message_type()} \n")
        print("\n" + f"Message payload as string: {message.get_payload_as_string()}\n")
        print("\n" + f"Message payload as bytes: {str}\n")
        print("\n" + f"Message properties: {message.get_properties()}\n")
        #standard conversion doesnt work with "sender timestamp" returned int for some reasons ???
        print("\n" + f"Message sender timestamp: {datetime.fromtimestamp(message.get_sender_timestamp())}\n")
        print("\n" + f"Message timestamp: {datetime.fromtimestamp(message.get_time_stamp())}\n")




def main():
    logger.info(f'Test main')

    #Default Docker Solace contaner setup
    sol_user = "default"
    sol_host = "localhost"
    sol_vpn = "default"
    sol_psw = ""

    try:
        #Start here
        c = SolaceConnectivity(sol_host, sol_vpn, sol_user, sol_psw, dbg=False)

        #---------------------------------------
        #TO CHECK SYSTEM IF NEEDED
        #---------------------------------------
        #SolaceConnection.system_info()
        #SolaceConnection.process_info()
        #SolaceConnection.thread_info()



        # SOLACE MESSAGES PUBLISHERs
        #----------------------------------------
        # DIRECT
        #----------------------------------------
        dir_pub = c.create_direct_message_publisher(PublisherErrorHandling)

        #----------------------------------------
        #
        #----------------------------------------

        #SPECIAL NOTE:
        # if create_basic_message() functionality is not enough
        # create message as follows:
        #msg = c.get_msg_builder()\
        #    .with_application_message_id(f'{msg_Id}') \
        #    .with_property("application Id", "samples") \
        #    .build(message_body)
        # Available options to pass additional details about msg in metadata
        # with_sequence_number() (int) The sequence number
        # with_application_message_id() (str) The application message identifier
        # with_application_message_type() (str) The Application Message type
        # with_priority() 0->9(int) The priority of the outbound message
        # with_expiration() timestamp(int) Sets message expiration time
        # Also you you can include additional properties you need in metadata
        # with_property() Key(str) Value(str/int/bytearray)

        seq = 1
        msg = c.create_basic_message(seq,"www")
        #send the same message to a number of topics
        for dest in ["try-me/python/Test", "try-me/control/Test2"]:
            logger.info(f'Sending message {c.get_message_details(msg)} to: {dest}')
        dir_pub.publish(destination=Topic.of(dest), message=msg)



        while True:
            seq+=1
            c.reuse_basic_message(msg, seq, f'test {seq}')
            for dest in ["try-me/python/Test", "try-me/control/Test2"]:
                logger.info(f'Sending message {c.get_message_details(msg)} to: {dest}')
            dir_pub.publish(destination=Topic.of(dest), message=msg)
            c.thread_info()
            time.sleep(15)





        # SOLACE MESSAGES RECEIVERs
        #----------------------------------------
        # DIRECT
        # No matter what DM you specify when publish to topics "aa" and "bb"
        # list of topics to get direct messages from
        #----------------------------------------
        #rcv0 = c.create_direct_message_receiver(["aa", "bb"])
        #rcv0.receive_async(MessageHandlerExample())
        #------------------------------------------
        # "queueTest"  QUEUE_DURABLE_EXCLUSIEVE
        # durable exclusieve queue which has 2 topics mapped to it  "Test1" and "Test2":
        # When publish to "queueTest" destination Queue, DM can be "DIRECT" or "PERSISTENT"
        # When publish to test topic say "Test1" : destination set to "Test1" DM also can be "DIRECT" or "PERSISTENT"
        # if mode "PERSISTENT", "queueTest" gets it as "PERSISTENT"
        # if mode "DIRECT",  "queueTest" gets it as  "DIRECT"
        #----------------------------------------
        #rcv1 = c.create_persistent_message_receiver(SubscribtionType.QUEUE_DURABLE_EXCLUSIEVE\
        #                                                    ,"queueTest"\
        #                                                    ,["fg", "67"])
        #rcv1.receive_async(MessageHandlerExample())
        #------------------------------------------
        #"queueTest2"  QUEUE_DURABLE_NON_EXCLUSIEVE
        # durable, non-exclusieve queue which has 2 topics provisoned "Test1" and "Test2":
        # same logic as above
        #------------------------------------------
        #rcv2 = c.create_persistent_message_receiver(SubscribtionType.QUEUE_DURABLE_NON_EXCLUSIEVE\
        #                                            ,"queueTest2"\
        #                                            ,["abcde", "12345"])
        #rcv2.receive_async(MessageHandlerExample())
        #
        #---------------------------------------
        # "queueTest3" QUEUE_NON_DURABLE_EXCLUSIEVE
        # Temporary queue, getting created when
        # receiver is built
        # rcv3 = c.create_persistent_message_receiver(SubscribtionType.QUEUE_NON_DURABLE_EXCLUSIEVE\
        #                                            ,"queueTest3"\
        #                                            ,["aa", "bb"])
        #rcv3.receive_async(MessageHandlerExample())
        #---------------------------------------
        #ICOMING MESSAGES PROCESSING
        #Just looping



        #while True:
        #    c.thread_info()
        #    time.sleep(15)

    except Exception as e:
        logger.error(f'Exception: {e}')
    finally:
        c.close_solace_connection()
        logger.error(f'Disconnecting, shutting down service')


if __name__ == '__main__':
    main()
