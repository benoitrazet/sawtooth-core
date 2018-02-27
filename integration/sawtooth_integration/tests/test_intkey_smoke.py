# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

# pylint: disable = attribute-defined-outside-init

import unittest
import logging
import operator  # used by verifier
# -- used by rest_api callers --
import urllib.request
import urllib.error
import json
from base64 import b64decode
from time import sleep

import cbor

from sawtooth_intkey.intkey_message_factory import IntkeyMessageFactory
from sawtooth_integration.tests.integration_tools import wait_for_rest_apis


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

WAIT = 20
INTKEY_PREFIX = '1cf126'

# Not associative commutative
NASSCOM= 'nasscom'

class TestIntkeySmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        wait_for_rest_apis(['rest-api-0:8008'])
        wait_for_rest_apis(['rest-api-1:8008'])
        wait_for_rest_apis(['rest-api-2:8008'])
        wait_for_rest_apis(['rest-api-3:8008'])
        wait_for_rest_apis(['rest-api-4:8008'])

    def test_intkey_smoke(self):
        '''
        After starting up a validator, intkey processor, and rest api,
        generate three batches of transactions: a batch of 'set' transactions
        (the "populate" batch), a batch of valid 'inc'/'dec' transactions,
        and a batch of invalid of invalid 'inc'/'dec' transactions (invalid
        because they target words not set by the populate batch).

        First, verify that the state is initially empty. Next, load the
        batches in the following order, verifying that the state is
        as it should be after each load:

        1. Send the batch of 'set' transactions, populating the state.
        2. Send the batch of valid transactions, altering the state.
        3. Send the batch of invalid transactions, leaving the state the same.
        4. Send the batch of valid transactions, again altering the state.
        5. Send the same batch of 'set' transactions from before.
           Because the state has already been populated, these transactions
           are invalid, and shouldn't affect the state.
        6. Send the batch of valid transactions, again altering the state.
        '''

        # self.verifier = IntkeyTestVerifier()

        # populate, valid_txns, invalid_txns = self.make_txn_batches()

        # self.verify_empty_state()

        # batches = (
        #     populate,
        #     valid_txns,
        #     invalid_txns,
        #     valid_txns,
        #     populate,
        #     valid_txns
        # )

        # how_many_updates = 0

        # for batch in batches:
        #     if batch == valid_txns:
        #         how_many_updates += 1
        #     self.post_and_verify(batch, how_many_updates)

        init_append()
        # send 25 append intkey transactions. The choice for picking the rest-api is arbitrary
        send_append('-0', 10)
        send_append('-1', 20)
        send_append('-2', 30)
        send_append('-3', 40)
        send_append('-4', 50)
        send_append('-0', 60)
        send_append('-1', 70)
        send_append('-2', 80)
        send_append('-4', 90)
        send_append('-3', 100)
        send_append('-3', 110)
        send_append('-0', 120)
        send_append('-2', 130)
        send_append('-2', 140)
        send_append('-0', 150)
        send_append('-1', 160)
        send_append('-1', 170)
        send_append('-1', 180)
        send_append('-2', 190)
        send_append('-2', 200)
        send_append('-4', 210)
        send_append('-3', 220)
        send_append('-4', 230)
        send_append('-1', 240)
        send_append('-3', 250)
        sleep(10)
        self.assertEqual(log_all_appends(), 1)

    # assertions

    def post_and_verify(self, batch, how_many_updates):
        batch = IntkeyMessageFactory().create_batch(batch)
        LOGGER.info('Posting batch')
        _post_batch(batch)
        self.verify_state_after_n_updates(how_many_updates)

    def verify_state_after_n_updates(self, num):
        LOGGER.debug('Verifying state after %s updates', num)
        expected_state = self.verifier.state_after_n_updates(num)
        actual_state = _get_data()
        LOGGER.info('Current state: %s', actual_state)
        self.assertEqual(
            expected_state,
            actual_state,
            'Updated state error')

    def verify_empty_state(self):
        LOGGER.debug('Verifying empty state')
        self.assertEqual(
            [],
            _get_state(),
            'Empty state error')

    # utilities

    def make_txn_batches(self):
        LOGGER.debug('Making txn batches')
        batches = self.verifier.make_txn_batches()
        return batches

# rest_api calls

# Initialize the NASSCOM address in Inkey to 0
def init_append():
    triple = ('set', NASSCOM, 0)
    batch = IntkeyMessageFactory().create_batch([triple])
    LOGGER.info('Posting batch')
    _post_batch(batch)
    
# Send an `append` verb with a given value to a specific REST api
def send_append(api_nb, value):
    triple = ('append', NASSCOM, value)
    batch = IntkeyMessageFactory().create_batch([triple])
    LOGGER.info('Posting batch')
    _post_batch(batch, api_nb=api_nb)
    sleep(2)
    log_all_appends()
    sleep(2)

# Query each rest-api to find out the value associated with NASSCOM key on different validators
def log_all_appends():
    res0 = _get_data(api_nb='-0')
    res1 = _get_data(api_nb='-1')
    res2 = _get_data(api_nb='-2')
    res3 = _get_data(api_nb='-3')
    res4 = _get_data(api_nb='-4')
    r = [res0,res1,res2,res3,res4]
    LOGGER.info('\n V0 {} \n V1 {} \n V2 {}, \n V3 {}, \n V4 {}'.format(r[0], r[1], r[2], r[3], r[4]))
    LOGGER.info('The nasscom value for each validator should be the same')
    branches = set()
    for res in r:
        branches.add(res['nasscom'])
    LOGGER.info('There are {} different branches.'.format(len(branches)))
    return len(branches)
    
def _post_batch(batch, api_nb='-0'):
    headers = {'Content-Type': 'application/octet-stream'}
    response = _query_rest_api(
        '/batches',
        data=batch, headers=headers, expected_code=202, api_nb=api_nb)
    response = _submit_request('{}&wait={}'.format(response['link'], WAIT))
    return response


        

def _get_data(api_nb='-0'):
    state = _get_state(api_nb=api_nb)
    # state is a list of dictionaries: { data: ..., address: ... }
    dicts = [cbor.loads(b64decode(entry['data'])) for entry in state]
    data = {k: v for d in dicts for k, v in d.items()}  # merge dicts
    return data


def _get_state(api_nb='-0'):
    response = _query_rest_api('/state?address={}'.format(INTKEY_PREFIX), api_nb=api_nb)
    return response['data']


def _query_rest_api(suffix='', data=None, headers=None, expected_code=200, api_nb='-0'):
    if headers is None:
        headers = {}
    url = 'http://rest-api{}:8008'.format(api_nb) + suffix
    LOGGER.info('URL IS {}'.format(url))
    return _submit_request(urllib.request.Request(url, data, headers),
                           expected_code=expected_code)


def _submit_request(request, expected_code=200):
    conn = urllib.request.urlopen(request)
    assert expected_code == conn.getcode()

    response = conn.read().decode('utf-8')
    return json.loads(response)


# separate file?
class IntkeyTestVerifier:
    def __init__(self,
                 valid=('lark', 'thrush', 'jay', 'wren', 'finch'),
                 invalid=('cow', 'pig', 'sheep', 'goat', 'horse'),
                 verbs=('inc', 'inc', 'dec', 'inc', 'dec'),
                 incdec=(1, 2, 3, 5, 8),
                 initial=(415, 325, 538, 437, 651)):
        self.valid = valid
        self.invalid = invalid
        self.verbs = verbs
        self.incdec = incdec
        self.initial = initial
        self.sets = ['set' for _ in range(len(self.initial))]

    def make_txn_batches(self):
        populate = tuple(zip(self.sets, self.valid, self.initial))
        valid_txns = tuple(zip(self.verbs, self.valid, self.incdec))
        invalid_txns = tuple(zip(self.verbs, self.invalid, self.incdec))

        return populate, valid_txns, invalid_txns

    def state_after_n_updates(self, num):
        ops = {
            'inc': operator.add,
            'dec': operator.sub
        }

        expected_values = [
            ops[verb](init, (val * num))
            for verb, init, val
            in zip(self.verbs, self.initial, self.incdec)
        ]

        return {word: val for word, val in zip(self.valid, expected_values)}
