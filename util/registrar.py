from threading import Lock, Event

class Registrar:
    """Static class that provides the option to register threads and wait
    until all threads are de-registered (and therefor done) using
    wait_for_shutdown()"""
    registered_threads = []
    registered_thread_lock = Lock()

    shutdown_requested = False
    shutdown_requested_lock = Lock()

    shutdown_event = Event()
    Event.clear(shutdown_event)

    @classmethod
    def register_thread(cls, thread):
        cls.registered_thread_lock.acquire()
        cls.register_thread.append(thread)
        cls.registered_thread_lock.release()

    @classmethod
    def deregister_thread(cls, thread):
        cls.registered_thread_lock.acquire()
        cls.register_thread.remove(thread)
        length = len(cls.registered_threads)
        cls.registered_thread_lock.release()

        if length <= 0:
            Event.set(cls.shutdown_event)

    @classmethod
    def threads_registered(cls):
        cls.registered_thread_lock.acquire()
        length = len(cls.register_thread)
        cls.registered_thread_lock.release()
        return length

    @classmethod
    def wait_for_shutdown(cls):
        Event.wait(cls.shutdown_event)

    @classmethod
    def request_shutdown(cls):
        cls.shutdown_requested_lock.acquire()
        cls.shutdown_requested = True
        cls.shutdown_requested_lock.release()

    @classmethod
    def shutdown_requested(cls):
        cls.shutdown_requested_lock.acquire()
        # ! 'fun'-fact, apparently this does not return a reference and is
        # ! therefor 'safe'¯\_(ツ)_/¯
        shutdown_requested = cls.shutdown_requested
        cls.shutdown_requested_lock.release()
        return shutdown_requested
