#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for Arabic Verb Forms Detection and Display

This module contains unit tests for the new verb forms functionality
added to the qutrub library.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import libqutrub.verb_form_detector
import libqutrub.conjugator
from libqutrub import verb_const


class TestVerbFormDetector(unittest.TestCase):
    """Test cases for verb form detection"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = libqutrub.verb_form_detector.VerbFormDetector()

    def test_form_i_detection(self):
        """Test detection of Form I verbs (فَعَلَ)"""
        # Test with properly vocalized Form I
        verb = u"كَتَبَ"
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertEqual(form_num, 1)
        self.assertGreater(confidence, 0.8)

    def test_form_ii_detection(self):
        """Test detection of Form II verbs (فَعَّلَ)"""
        verb = u"كَتَّبَ"  # Note: this doesn't follow standard pattern but should be detected
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertEqual(form_num, 2)

    def test_form_iii_detection(self):
        """Test detection of Form III verbs (فَاعَلَ)"""
        verb = u"كَاتَبَ"
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertEqual(form_num, 3)

    def test_form_iv_detection(self):
        """Test detection of Form IV verbs (أَفْعَلَ)"""
        verb = u"أَكْتَبَ"
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertEqual(form_num, 4)

    def test_form_v_detection(self):
        """Test detection of Form V verbs (تَفَعَّلَ)"""
        verb = u"تَكَتَّبَ"
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertEqual(form_num, 5)

    def test_form_vi_detection(self):
        """Test detection of Form VI verbs (تَفاعَلَ)"""
        verb = u"تَكَاتَبَ"
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertEqual(form_num, 6)

    def test_form_vii_detection(self):
        """Test detection of Form VII verbs (اِنْفَعَلَ)"""
        verb = u"اِنْكَتَبَ"
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertEqual(form_num, 7)

    def test_form_viii_detection(self):
        """Test detection of Form VIII verbs (اِفْتَعَلَ)"""
        verb = u"اِكْتَتَبَ"  # Should be detected as Form VIII
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertEqual(form_num, 8)

    def test_form_x_detection(self):
        """Test detection of Form X verbs (اِسْتَفْعَلَ)"""
        verb = u"اِسْتَكْتَبَ"
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertEqual(form_num, 10)

    def test_unvocalized_verb(self):
        """Test handling of unvocalized verbs"""
        verb = u"كتب"  # Unvocalized
        form_num, confidence = self.detector.detect_form_pattern(verb)
        self.assertIsNone(form_num)  # Should return None for unvocalized

    def test_form_generation(self):
        """Test generation of form variants"""
        verb = u"كَتَبَ"

        # Test generation for Form II
        variants = self.detector.generate_form_variants(verb, verb_const.FORM_II)
        self.assertTrue(len(variants) > 0)
        self.assertIn('كَتَّبَ', variants[0])  # Should contain II form

        # Test generation for Form IV
        variants = self.detector.generate_form_variants(verb, verb_const.FORM_IV)
        self.assertTrue(len(variants) > 0)
        self.assertIn('أَكْتَبَ', variants[0])  # Should contain IV form

    def test_constants(self):
        """Test verb form constants"""
        # Check that all forms 1-10 are defined
        for i in range(1, 11):
            self.assertIn(i, verb_const.VERB_FORMS_ORDER)
            self.assertIn(i, verb_const.VERB_FORM_NAMES)
            self.assertIn(i, verb_const.VERB_FORM_ENGLISH_MEANINGS)
            self.assertIn(i, verb_const.VERB_FORM_EXAMPLES)


class TestVerbFormsTable(unittest.TestCase):
    """Test cases for verb forms table generation"""

    def test_form_table_generation(self):
        """Test ASCII table generation"""
        detector = libqutrub.verb_form_detector.get_detector()

        # Test with verb data
        verb_data = {
            1: u"كَتَبَ",
            2: u"كَتَّبَ",
            3: u"كَاتَبَ",
            4: u"أَكْتَبَ"
        }

        table = detector.create_ascii_table(u"كَتَبَ", verb_data)
        self.assertIsInstance(table, str)
        self.assertIn('Form', table)
        self.assertIn('Arabic Name', table)
        self.assertIn('Conjugated Verb', table)
        self.assertIn('كَتَبَ', table)  # Should contain the input verb

    def test_form_table_empty_data(self):
        """Test table generation with no data"""
        detector = libqutrub.verb_form_detector.get_detector()
        table = detector.create_ascii_table(u"كَتَبَ", {})
        self.assertIn('N/A', table)

    def test_form_table_with_filter(self):
        """Test table generation with form filter"""
        detector = libqutrub.verb_form_detector.get_detector()
        table = detector.create_ascii_table(u"كَتَبَ", {1: u"كَتَبَ"})
        self.assertIn('كَتَبَ', table)
        self.assertNotIn('Form II', table)  # Should not contain other forms


class TestConjugatorWithForms(unittest.TestCase):
    """Test cases for conjugator with form filtering"""

    def test_form_table_display_format(self):
        """Test FORM_TABLE display format"""
        result = libqutrub.conjugator.conjugate(
            verb=u"كَتَبَ",
            future_type=u"ضمة",
            display_format="FORM_TABLE"
        )
        self.assertIsInstance(result, str)
        self.assertIn('Form', result)
        self.assertIn('Arabic Name', result)
        self.assertIn('Conjugated Verb', result)

    def test_form_filter_validation(self):
        """Test form filtering"""
        # This should work - same form
        result = libqutrub.conjugator.conjugate(
            verb=u"كَتَبَ",
            future_type=u"ضمة",
            form_filter=1
        )
        self.assertIsInstance(result, str)

        # This should fail - different form
        result = libqutrub.conjugator.conjugate(
            verb=u"كَتَبَ",
            future_type=u"ضمة",
            form_filter=2
        )
        self.assertIn('Error:', result)
        self.assertIn('not Form 2', result)

    def test_form_filter_with_form_iv_verb(self):
        """Test form filtering with Form IV verb"""
        result = libqutrub.conjugator.conjugate(
            verb=u"أَكْتَبَ",
            future_type=u"فَتْحة",
            form_filter=4
        )
        self.assertIsInstance(result, str)
        self.assertNotIn('Error:', result)


def run_verb_forms_tests():
    """Run all verb forms related tests"""
    # Create test suite
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTest(unittest.makeSuite(TestVerbFormDetector))
    suite.addTest(unittest.makeSuite(TestVerbFormsTable))
    suite.addTest(unittest.makeSuite(TestConjugatorWithForms))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return whether all tests passed
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running verb forms tests...")
    success = run_verb_forms_tests()

    if success:
        print("All verb forms tests passed! ✓")
        sys.exit(0)
    else:
        print("Some verb forms tests failed! ✗")
        sys.exit(1)