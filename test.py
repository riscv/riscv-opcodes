#!/usr/bin/env python3

import logging
import unittest
from unittest.mock import Mock, patch

from shared_utils import (
    InstrDict,
    check_arg_lut,
    check_overlapping_bits,
    extract_isa_type,
    find_extension_file,
    handle_arg_lut_mapping,
    initialize_encoding,
    is_rv_variant,
    overlaps,
    pad_to_equal_length,
    parse_instruction_line,
    process_enc_line,
    process_fixed_ranges,
    process_standard_instructions,
    same_base_isa,
    update_encoding_for_fixed_range,
    validate_bit_range,
)


class EncodingUtilsTest(unittest.TestCase):
    """Tests for basic encoding utilities"""

    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.disabled = True

    def test_initialize_encoding(self):
        """Test encoding initialization with different bit lengths"""
        self.assertEqual(initialize_encoding(32), ["-"] * 32)
        self.assertEqual(initialize_encoding(16), ["-"] * 16)
        self.assertEqual(initialize_encoding(), ["-"] * 32)  # default case

    def test_validate_bit_range(self):
        """Test bit range validation"""
        # Valid cases
        validate_bit_range(7, 3, 15, "test_instr")  # 15 fits in 5 bits
        validate_bit_range(31, 0, 0xFFFFFFFF, "test_instr")  # max 32-bit value

        # Invalid cases
        with self.assertRaises(SystemExit):
            validate_bit_range(3, 7, 1, "test_instr")  # msb < lsb
        with self.assertRaises(SystemExit):
            validate_bit_range(3, 0, 16, "test_instr")  # value too large for range

    def test_parse_instruction_line(self):
        """Test instruction line parsing"""
        name, remaining = parse_instruction_line("add.w r1, r2, r3")
        self.assertEqual(name, "add_w")
        self.assertEqual(remaining, "r1, r2, r3")

        name, remaining = parse_instruction_line("lui rd imm20 6..2=0x0D")
        self.assertEqual(name, "lui")
        self.assertEqual(remaining, "rd imm20 6..2=0x0D")


class BitManipulationTest(unittest.TestCase):
    """Tests for bit manipulation and checking functions"""

    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.disabled = True
        self.test_encoding = initialize_encoding()

    def test_check_overlapping_bits(self):
        """Test overlapping bits detection"""
        # Valid case - no overlap
        self.test_encoding[31 - 5] = "-"
        check_overlapping_bits(self.test_encoding, 5, "test_instr")

        # Invalid case - overlap
        self.test_encoding[31 - 5] = "1"
        with self.assertRaises(SystemExit):
            check_overlapping_bits(self.test_encoding, 5, "test_instr")

    def test_update_encoding_for_fixed_range(self):
        """Test encoding updates for fixed ranges"""
        encoding = initialize_encoding()
        update_encoding_for_fixed_range(encoding, 6, 2, 0x0D, "test_instr")

        # Check specific bits are set correctly
        self.assertEqual(encoding[31 - 6 : 31 - 1], ["0", "1", "1", "0", "1"])

    def test_process_fixed_ranges(self):
        """Test processing of fixed bit ranges"""
        encoding = initialize_encoding()
        remaining = "rd imm20 6..2=0x0D 1..0=3"

        result = process_fixed_ranges(remaining, encoding, "test_instr")
        self.assertNotIn("6..2=0x0D", result)
        self.assertNotIn("1..0=3", result)


class EncodingArgsTest(unittest.TestCase):
    """Tests for encoding arguments handling"""

    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.disabled = True

    @patch.dict("shared_utils.arg_lut", {"rd": (11, 7), "rs1": (19, 15)})
    def test_check_arg_lut(self):
        """Test argument lookup table checking"""
        encoding_args = initialize_encoding()
        args = ["rd", "rs1"]
        check_arg_lut(args, encoding_args, "test_instr")

        # Verify encoding_args has been updated correctly
        self.assertEqual(encoding_args[31 - 11 : 31 - 6], ["rd"] * 5)
        self.assertEqual(encoding_args[31 - 19 : 31 - 14], ["rs1"] * 5)

    @patch.dict("shared_utils.arg_lut", {"rs1": (19, 15)})
    def test_handle_arg_lut_mapping(self):
        """Test handling of argument mappings"""
        # Valid mapping
        result = handle_arg_lut_mapping("rs1=new_arg", "test_instr")
        self.assertEqual(result, "rs1=new_arg")

        # Invalid mapping
        with self.assertRaises(SystemExit):
            handle_arg_lut_mapping("invalid_arg=new_arg", "test_instr")


class ISAHandlingTest(unittest.TestCase):
    """Tests for ISA type handling and validation"""

    def test_extract_isa_type(self):
        """Test ISA type extraction"""
        self.assertEqual(extract_isa_type("rv32_i"), "rv32")
        self.assertEqual(extract_isa_type("rv64_m"), "rv64")
        self.assertEqual(extract_isa_type("rv_c"), "rv")

    def test_is_rv_variant(self):
        """Test RV variant checking"""
        self.assertTrue(is_rv_variant("rv32", "rv"))
        self.assertTrue(is_rv_variant("rv", "rv64"))
        self.assertFalse(is_rv_variant("rv32", "rv64"))

    def test_same_base_isa(self):
        """Test base ISA comparison"""
        self.assertTrue(same_base_isa("rv32_i", ["rv32_m", "rv32_a"]))
        self.assertTrue(same_base_isa("rv_i", ["rv32_i", "rv64_i"]))
        self.assertFalse(same_base_isa("rv32_i", ["rv64_m"]))


class StringManipulationTest(unittest.TestCase):
    """Tests for string manipulation utilities"""

    def test_pad_to_equal_length(self):
        """Test string padding"""
        str1, str2 = pad_to_equal_length("101", "1101")
        self.assertEqual(len(str1), len(str2))
        self.assertEqual(str1, "-101")
        self.assertEqual(str2, "1101")

    def test_overlaps(self):
        """Test string overlap checking"""
        self.assertTrue(overlaps("1-1", "101"))
        self.assertTrue(overlaps("---", "101"))
        self.assertFalse(overlaps("111", "101"))


class InstructionProcessingTest(unittest.TestCase):
    """Tests for instruction processing and validation"""

    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.disabled = True
        # Create a patch for arg_lut
        self.arg_lut_patcher = patch.dict(
            "shared_utils.arg_lut", {"rd": (11, 7), "imm20": (31, 12)}
        )
        self.arg_lut_patcher.start()

    def tearDown(self):
        self.arg_lut_patcher.stop()

    @patch("shared_utils.fixed_ranges")
    @patch("shared_utils.single_fixed")
    def test_process_enc_line(self, mock_single_fixed: Mock, mock_fixed_ranges: Mock):
        """Test processing of encoding lines"""
        # Setup mock return values
        mock_fixed_ranges.findall.return_value = [(6, 2, "0x0D")]
        mock_fixed_ranges.sub.return_value = "rd imm20"
        mock_single_fixed.findall.return_value = []
        mock_single_fixed.sub.return_value = "rd imm20"

        # Create a mock for split() that returns the expected list
        mock_split = Mock(return_value=["rd", "imm20"])
        mock_single_fixed.sub.return_value = Mock(split=mock_split)

        name, data = process_enc_line("lui rd imm20 6..2=0x0D", "rv_i")

        self.assertEqual(name, "lui")
        self.assertEqual(data["extension"], ["rv_i"])
        self.assertIn("rd", data["variable_fields"])
        self.assertIn("imm20", data["variable_fields"])

    @patch("os.path.exists")
    @patch("shared_utils.logging.error")
    def test_find_extension_file(self, mock_logging: Mock, mock_exists: Mock):
        """Test extension file finding"""
        # Test successful case - file exists in main directory
        mock_exists.side_effect = [True, False]
        result = find_extension_file("rv32i", "/path/to/opcodes")
        self.assertEqual(result, "/path/to/opcodes/rv32i")

        # Test successful case - file exists in unratified directory
        mock_exists.side_effect = [False, True]
        result = find_extension_file("rv32i", "/path/to/opcodes")
        self.assertEqual(result, "/path/to/opcodes/unratified/rv32i")

        # Test failure case - file doesn't exist anywhere
        mock_exists.side_effect = [False, False]
        with self.assertRaises(SystemExit):
            find_extension_file("rv32i", "/path/to/opcodes")
        mock_logging.assert_called_with("Extension rv32i not found.")

    def test_process_standard_instructions(self):
        """Test processing of standard instructions"""
        lines = [
            "add rd rs1 rs2 31..25=0 14..12=0 6..2=0x0C 1..0=3",
            "sub rd rs1 rs2 31..25=0x20 14..12=0 6..2=0x0C 1..0=3",
            "$pseudo add_pseudo rd rs1 rs2",  # Should be skipped
            "$import rv32i::mul",  # Should be skipped
        ]

        instr_dict: InstrDict = {}
        file_name = "rv32i"

        with patch("shared_utils.process_enc_line") as mock_process_enc:
            # Setup mock return values
            mock_process_enc.side_effect = [
                ("add", {"extension": ["rv32i"], "encoding": "encoding1"}),
                ("sub", {"extension": ["rv32i"], "encoding": "encoding2"}),
            ]

            process_standard_instructions(lines, instr_dict, file_name)

            # Verify process_enc_line was called twice (skipping pseudo and import)
            self.assertEqual(mock_process_enc.call_count, 2)

            # Verify the instruction dictionary was updated correctly
            self.assertEqual(len(instr_dict), 2)
            self.assertIn("add", instr_dict)
            self.assertIn("sub", instr_dict)


if __name__ == "__main__":
    unittest.main()
