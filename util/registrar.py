from threading import Event, Lock

from util.common import create_logger
from model.server.tcp_outgoing import TcpOutgoing, AddedUser, RemovedUser


class Registrar:
    """Static class that provides the option to register threads and wait
    until all threads are de-registered (and therefor done) using
    wait_for_shutdown()"""

    log = create_logger("Registrar")
    outgoing_actor = TcpOutgoing()
    outgoing_actor.start()

    registered_threads = 0
    overall_counter = 0
    registered_thread_lock = Lock()

    shutdown_requested_flag = False
    shutdown_requested_lock = Lock()

    registered_users = []
    registered_users_lock = Lock()

    shutdown_event = Event()
    Event.clear(shutdown_event)

    @classmethod
    def broadcast_message(cls, broadcast):
        cls.outgoing_actor.tell(broadcast)

    @classmethod
    def register_user(cls, user, connection):
        ret = None
        cls.registered_users_lock.acquire()
        if user not in cls.registered_users:
            cls.log.info(f"User ({user}) successfully registered")
            cls.outgoing_actor.tell(AddedUser(user, connection, cls.registered_users))
            cls.registered_users.append(user)
            ret = user
        else:
            cls.log.info(f"User ({user}) is already registered")
        cls.registered_users_lock.release()
        return ret

    @classmethod
    def deregister_user(cls, user, connection):
        cls.registered_users_lock.acquire()
        if user in cls.registered_users:
            cls.log.info(f"Successfully unregistered user {user}")
            cls.outgoing_actor.tell(RemovedUser(user, connection))
            cls.registered_users.remove(user)
        else:
            cls.log.info(f"Could not unregistered user {user} - not registered")
        cls.registered_users_lock.release()

    @classmethod
    def retrieve_user(cls, name):
        cls.registered_users_lock.acquire()
        user = [user for user in cls.registered_users if user.nickname == name][0]
        cls.registered_users_lock.release()
        return user

    @classmethod
    def register_thread(cls):
        cls.registered_thread_lock.acquire()
        cls.registered_threads += 1
        cls.overall_counter += 1
        thread = cls.overall_counter
        cls.registered_thread_lock.release()
        return thread

    @classmethod
    def deregister_thread(cls):
        cls.registered_thread_lock.acquire()
        cls.registered_threads -= 1
        length = cls.registered_threads
        cls.registered_thread_lock.release()

        if length <= 0:
            Event.set(cls.shutdown_event)

    @classmethod
    def threads_registered(cls):
        cls.registered_thread_lock.acquire()
        length = cls.registered_threads
        cls.registered_thread_lock.release()
        return length

    @classmethod
    def wait_for_shutdown(cls):
        if cls.threads_registered() > 0:
            Event.wait(cls.shutdown_event, 30)

    @classmethod
    def request_shutdown(cls):
        cls.shutdown_requested_lock.acquire()
        cls.shutdown_requested_flag = True
        cls.shutdown_requested_lock.release()

    @classmethod
    def shutdown_requested(cls):
        cls.shutdown_requested_lock.acquire()
        shutdown_requested = cls.shutdown_requested_flag
        cls.shutdown_requested_lock.release()
        return shutdown_requested
