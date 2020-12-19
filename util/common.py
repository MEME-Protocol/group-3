from logging import DEBUG, Formatter, StreamHandler, getLogger
from struct import Struct

"""Represents a u32 value"""
json_size_struct = Struct("I")


def create_logger(logger_name):
    log = getLogger(logger_name)
    log.setLevel(DEBUG)
    log_handler = StreamHandler()
    log_handler.setFormatter(
        Formatter("%(asctime)s [%(filename)s] [%(threadName)s] %(message)s"))
    log.addHandler(log_handler)
    return log
