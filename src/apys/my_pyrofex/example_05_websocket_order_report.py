# -*- coding: utf-8 -*-
# python -m apys.my_pyrofex.example_05_websocket_order_report
"""
    Sample Module.

    Example of market data using websocket API.

    The code show how to initialize the connection,
    subscribe to receive order reports for a valid and invalid account,
    and finally close the connection.

    Go to the official Documentation to check the API Responses.

    Steps:
    1-Initialize the environment
    2-Defines the handlers that will process the messages and exceptions.
    3-Initialize Websocket Connection with the handlers
    4-Subscribes to receive order report for the default account
    5-Subscribes to an invalid account
    6-Send an order to check that order_report_handler is called
    7-Wait 5 sec then close the connection
"""
import time
import inspect
import json
import os

import pyRofex

# 1-Initialize the environment
dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
json_path = dir_path + '/remarkets.json'
if os.path.isfile(json_path):
    with open(json_path) as json_file:
        data_json = json.load(json_file)
        pyRofex.initialize(
            user = data_json['user'],
            password = data_json['password'],
            account = data_json['account'],
            environment=pyRofex.Environment.REMARKET
        )
    json_file.close()


# 2-Defines the handlers that will process the messages and exceptions.
def order_report_handler(message):
    print("Order Report Message Received: {0}".format(message))


def error_handler(message):
    print("Error Message Received: {0}".format(message))


def exception_handler(e):
    print("Exception Occurred: {0}".format(e.msg))


# 3-Initialize Websocket Connection with the handlers
pyRofex.init_websocket_connection(order_report_handler=order_report_handler,
                                  error_handler=error_handler,
                                  exception_handler=exception_handler)


# 4-Subscribes to receive order report for the default account
pyRofex.order_report_subscription()


# 5-Subscribes to an invalid account
pyRofex.order_report_subscription(account="InvalidAccount")


# 6-Send an order to check that order_report_handler is called
pyRofex.send_order(ticker="DLR/ENE24",
                   side=pyRofex.Side.BUY,
                   size=10,
                   order_type=pyRofex.OrderType.MARKET)


# 7-Wait 5 sec then close the connection
time.sleep(1)
pyRofex.close_websocket_connection()