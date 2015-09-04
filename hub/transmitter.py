import logging
import time

import requests

from . import common, database


logging.basicConfig(level=logging.INFO)


def transmit(db, xbee_id):
    for row in db.get_unrelayed_temperatures():
        id, cell_id, temperature, sleep_period, timestamp = row
        cell_id = common.hexlify(cell_id)
        data = dict(hub=xbee_id, cell=cell_id, temp=temperature, sp=sleep_period, time=timestamp)
        logging.info(data)
        response = requests.post('http://relay.heatseeknyc.com/temperatures', data)
        if response.status_code == 200: db.set_relayed_temperature(id)
        else: logging.error('bad response: %s', response)
        time.sleep(1)

@common.main
def main():
    with database.Database() as db:
        logging.info('connected to database.')

        while True:
            xbee_id = db.get_xbee_id()
            if xbee_id: break
            logging.warn('waiting for xbee id to appear in db...')
            time.sleep(1)
        xbee_id = common.hexlify(xbee_id)

        while True:
            transmit(db, xbee_id)
            time.sleep(1)
