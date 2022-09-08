from candles import candles
from viewer import viewer
from trader import bitflyer
from trade_operator import Operator
from technic import select_technic
from runner import select_runner
from output import debug_output
from notify.line_notify import LineNotify

from datetime import datetime

import argparse
import logging
import os
import pandas as pd
import sys
import time
import traceback
import warnings

warnings.simplefilter('ignore', FutureWarning)

logging.basicConfig(filename='../runner.log', format='%(asctime)s %(message)s',
                    level=logging.DEBUG)

pd.options.display.float_format = '{:.2f}'.format

DEBUG = True
OPERATE_DEBUG = True


def main():
    try:
        print("Start trading")
        main_loop()
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        sys.exit()


def run(runner, sleep_second, debug):
    logging.debug('Init buy orders %s', runner.orders)
    if not debug:
        viewer.run()

    count = 0

    while True:
        count += 1
        runner.auto_trade()

        if debug and candles.is_finished_candles():
            break

        time.sleep(sleep_second)


def main_loop():
    args = parse_arg()
    is_debug = args.debug or args.debug_operation

    logging.debug(f'select algorithm is {args.algorithm}')
    bitflyer.set_api_key_secret_file(
        os.path.join(os.environ['HOME'], '.bitflyer_token'))
    trade_operator = Operator(bitflyer, is_debug)
    algorithm = select_technic.get_algorithm(args.algorithm)
    runner = select_runner.get_runner(args.runner)(
        trade_operator, is_debug, algorithm, send_line_message(args.debug))
    viewer.set_runner(runner)

    try:
        sleep_second = args.sleep
        if args.debug:
            sleep_second = 0
        run(runner, sleep_second, args.debug)

    except Exception as e:
        print(traceback.format_exc())
        LineNotify().send(traceback.format_exc())
        raise e
    finally:
        runner.close()
        buy_order = runner.orders
        if args.debug:
            debug_output(runner.COMPLETE_ORDER, buy_order)


def send_line_message(debug):
    def send_message(msg):
        logging.debug(msg)
        output_log = '%s: %s' % (datetime.fromtimestamp(time.time()), msg)
        print(output_log)
        if not debug:
            line_notify = LineNotify()
            line_notify.send(output_log)
    return send_message


def parse_arg():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--algorithm', default='BB',
                        help='select trade algorithm')
    parser.add_argument('--runner', default='buy_steps', help='select runner')
    parser.add_argument('--sleep', default=30, help='trader run span(seconds)')
    parser.add_argument('--debug', default=False, help='Run debug mode')
    parser.add_argument('--debug-operation', default=False,
                        help='Debug operation')

    return parser.parse_args()


if __name__ == '__main__':
    main()
