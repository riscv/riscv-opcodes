#!/usr/bin/env python3

from parse import *
import logging
import unittest

class EncodingLineTest(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger()
        logger.disabled = True

    def assertError(self, string):
        self.assertRaises(SystemExit, process_enc_line, string, 'rv_i')

    def test_lui(self):
        name, data = process_enc_line('lui     rd imm20 6..2=0x0D 1=1 0=1', 'rv_i')
        self.assertEqual(name, 'lui')
        self.assertEqual(data['extension'], ['rv_i'])
        self.assertEqual(data['match'], '0x37')
        self.assertEqual(data['mask'], '0x7f')

    def test_overlapping(self):
        self.assertError('jol rd jimm20 6..2=0x00 3..0=7')
        self.assertError('jol rd jimm20 6..2=0x00 3=1')
        self.assertError('jol rd jimm20 6..2=0x00 10=1')
        self.assertError('jol rd jimm20 6..2=0x00 31..10=1')

    def test_invalid_order(self):
        self.assertError('jol 2..6=0x1b')

    def test_illegal_value(self):
        self.assertError('jol rd jimm20 2..0=10')
        self.assertError('jol rd jimm20 2..0=0xB')

    def test_overlapping_field(self):
        self.assertError('jol rd rs1 jimm20 6..2=0x1b 1..0=3')

    def test_illegal_field(self):
        self.assertError('jol rd jimm128 2..0=3')
