#!/usr/bin/env python3

from unittest.mock import patch, mock_open
from parse import *
import logging
import unittest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EncodingLineTest(unittest.TestCase):
    """Test case for encoding line processing."""
    
    def setUp(self):
        """Set up the test environment."""
        logger.info("Starting a new EncodingLineTest...")
        logger.disabled = True

    def tearDown(self):
        """Clean up after tests."""
        logger.info("EncodingLineTest completed.")

    def assertError(self, string):
        """Assert that processing the given string raises a SystemExit error."""
        logger.info(f"Testing error assertion for: {string}")
        self.assertRaises(SystemExit, process_enc_line, string, 'rv_i')

    def test_lui(self):
        """Test the 'lui' instruction encoding."""
        logger.info("Testing 'test_lui'...")
        name, data = process_enc_line('lui     rd imm20 6..2=0x0D 1=1 0=1', 'rv_i')
        self.assertEqual(name, 'lui')
        self.assertEqual(data['extension'], ['rv_i'])
        self.assertEqual(data['match'], '0x37')
        self.assertEqual(data['mask'], '0x7f')

    def test_overlapping(self):
        """Test overlapping fields in instructions."""
        logger.info("Testing 'test_overlapping'...")
        self.assertError('jol rd jimm20 6..2=0x00 3..0=7')
        self.assertError('jol rd jimm20 6..2=0x00 3=1')
        self.assertError('jol rd jimm20 6..2=0x00 10=1')
        self.assertError('jol rd jimm20 6..2=0x00 31..10=1')

    def test_invalid_order(self):
        """Test invalid order of fields in instructions."""
        logger.info("Testing 'test_invalid_order'...")
        self.assertError('jol 2..6=0x1b')

    def test_illegal_value(self):
        """Test illegal values in instruction fields."""
        logger.info("Testing 'test_illegal_value'...")
        self.assertError('jol rd jimm20 2..0=10')
        self.assertError('jol rd jimm20 2..0=0xB')

    def test_overlapping_field(self):
        """Test overlapping fields in instructions."""
        logger.info("Testing 'test_overlapping_field'...")
        self.assertError('jol rd rs1 jimm20 6..2=0x1b 1..0=3')

    def test_illegal_field(self):
        """Test illegal fields in instructions."""
        logger.info("Testing 'test_illegal_field'...")
        self.assertError('jol rd jimm128 2..0=3')

class TestCreateInstDict(unittest.TestCase):
    """Test case for creating instruction dictionary."""
    
    def setUp(self):
        """Set up the test environment for instruction dictionary tests."""
        logger.info("Starting a new TestCreateInstDict...")

    def tearDown(self):
        """Clean up after tests."""
        logger.info("TestCreateInstDict completed.")

    @patch('builtins.open', new_callable=mock_open, read_data='mock instruction data')
    @patch('glob.glob', return_value=['mock_file.rv32_i'])
    @patch('parse.process_enc_line')  # Replace 'your_module' with the actual module name
    def test_create_inst_dict(self, mock_process_enc_line, mock_glob, mock_open):
        """Test the creation of an instruction dictionary."""
        logger.info("Testing 'create_inst_dict' function...")
        
        # Mock the return value of process_enc_line
        mock_process_enc_line.return_value = ('mock_instruction', {
            'variables': ['arg1', 'arg2'],
            'encoding': '00000000000000000000000000000000',
            'extension': ['mock_file.rv32_i'],
            'match': '0x0',
            'mask': '0xFFFFFFFF'
        })

        # Call the function with test parameters
        result = create_inst_dict(['_i'], include_pseudo=False)

        # Assertions to check if the result is as expected
        self.assertIn('mock_instruction', result)
        self.assertEqual(result['mock_instruction']['variables'], ['arg1', 'arg2'])
        self.assertEqual(result['mock_instruction']['encoding'], '00000000000000000000000000000000')
        self.assertEqual(result['mock_instruction']['extension'], ['mock_file.rv32_i'])
        self.assertEqual(result['mock_instruction']['match'], '0x0')
        self.assertEqual(result['mock_instruction']['mask'], '0xFFFFFFFF')

if __name__ == "__main__":
    unittest.main()
