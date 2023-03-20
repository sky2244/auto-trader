import argparse
import configparser
import logging
import os
import sys
import time
import traceback
import warnings
from datetime import datetime

import pandas as pd

from candles import candles
from notify.line_notify import LineNotify
from output import debug_output
from runner import select_runner
from technic import select_technic
from trade_operator import Operator
from trader import bitflyer
from viewer import viewer

warnings.simplefilter('ignore', FutureWarning)

logging.basicConfig(filename='../runner.log', format='%(asctime)s %(message)s',
                    level=logging.INFO)

pd.options.display.float_format = '{:.2f}'.format


def main():
    try:
        print("Start trading")
        main_loop()
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        sys.exit()


def run(is_run_view, runner, sleep_second, debug):
    logging.debug('Init buy orders %s', runner.orders)
    if is_run_view:
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
    config = parse_config(args.config_file)

    market = config.get('Default/market', 'BTC_JPY')
    bitflyer.set_api_key_secret_file(
        market, os.path.join(os.environ['HOME'], '.bitflyer_token'))
    trade_operator = Operator(bitflyer, args.debug or args.debug_operation)

    algorithm_name = config.get('Algorithm/name', 'bb')
    algorithm = select_technic.get_algorithm(algorithm_name.lower())

    runner_name = config.get('Runner/name', 'scalping')
    runner = select_runner.get_runner(runner_name.lower())(
        trade_operator, args.debug, args.debug_operation,
        algorithm, send_line_message(args.debug))

    logging.debug(f'select algorithm is {algorithm.name}')

    viewer.set_runner(runner)
    is_run_view = (not args.debug) and config.getboolean('View/run', False)

    try:
        sleep_second = int(config.get('Default/sleep', 0))
        if args.debug:
            sleep_second = 0
        run(is_run_view, runner, sleep_second, args.debug)

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
    line_notify = LineNotify()

    def send_message(msg):
        logging.info(msg)
        output_log = '%s: %s' % (datetime.fromtimestamp(time.time()), msg)
        print(output_log)
        try:
            if not debug:
                line_notify.send(output_log)
        except Exception as e:
            print('notify error', e.message)
    return send_message


def parse_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def parse_arg():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--debug', default=False,
                        action='store_true', help='Run debug mode')
    parser.add_argument('--debug-operation', default=False,
                        action='store_true', help='Debug operation')
    parser.add_argument('--config-file', required=True,
                        help='select config file')

    return parser.parse_args()


if __name__ == '__main__':
    main()
