#!/usr/bin/python
# -*- coding=utf-8 -*-
#************************************************************************
# Verb Form Detector for Arabic Verb Forms I-X
#
# Description:
# Detects and identifies Arabic verb forms (I-X) based on morphological patterns
#
# Copyright (c) 2025, Enhanced Qutrub Project
#
#***********************************************************************/

"""
Arabic Verb Form Detector Module

This module provides functionality to detect which of the 10 standard Arabic verb forms
a given verb belongs to, based on its morphological pattern.

The 10 Arabic verb forms:
Form I (الفعل المجرد): فَعَلَ - Basic root form
Form II (فَعَّلَ): Intensive/causative
Form III (فَاعَلَ): Interactive/reciprocal
Form IV (أَفْعَلَ): Causative/declarative
Form V (تَفَعَّلَ): Reflexive/intensive of Form II
Form VI (تَفاعَلَ): Reflexive/reciprocal of Form III
Form VII (اِنْفَعَلَ): Passive/reflexive
Form VIII (اِفْتَعَلَ): Reflexive/participatory
Form IX (اِفْعَلَّ): Color/physical defects (rare)
Form X (اِسْتَفْعَلَ): Request/seeking action
"""

import re
import pyarabic.araby as araby
from pyarabic.araby import FATHA, DAMMA, KASRA, SHADDA, SUKUN, HAMZA, ALEF, \
    NOON, ALEF_WASLA, WAW, ALEF_HAMZA_ABOVE, ALEF_HAMZA_BELOW, ALEF_MADDA, \
    YEH_HAMZA, WAW_HAMZA, TATWEEL, SMALL_ALEF, SMALL_YEH, SMALL_WAW, YEH, \
    ALEF_MAKSURA

class VerbFormInfo:
    """Class to store information about an Arabic verb form"""

    def __init__(self, form_num, arabic_name, pattern, english_meaning, example):
        self.form_num = form_num
        self.arabic_name = arabic_name
        self.pattern = pattern
        self.english_meaning = english_meaning
        self.example = example

    def __str__(self):
        return f"Form {self.form_num}: {self.arabic_name} ({self.pattern})"

# Define the 10 Arabic verb forms
VERB_FORMS = {
    1: VerbFormInfo(1, "الفعل المجرد", "فَعَلَ", "Basic/Original", "كَتَبَ"),
    2: VerbFormInfo(2, "فَعَّلَ", "فَعَّلَ", "Intensive/Causative", "كَتَّبَ"),
    3: VerbFormInfo(3, "فَاعَلَ", "فَاعَلَ", "Interactive/Reciprocal", "كَاتَبَ"),
    4: VerbFormInfo(4, "أَفْعَلَ", "أَفْعَلَ", "Causative/Declarative", "أَكْتَبَ"),
    5: VerbFormInfo(5, "تَفَعَّلَ", "تَفَعَّلَ", "Reflexive of Form II", "تَكَتَّبَ"),
    6: VerbFormInfo(6, "تَفاعَلَ", "تَفاعَلَ", "Reciprocal of Form III", "تَكَاتَبَ"),
    7: VerbFormInfo(7, "اِنْفَعَلَ", "اِنْفَعَلَ", "Passive/Reflexive", "اِنْكَتَبَ"),
    8: VerbFormInfo(8, "اِفْتَعَلَ", "اِفْتَعَلَ", "Reflexive/Participatory", "اِكْتَتَبَ"),
    9: VerbFormInfo(9, "اِفْعَلَّ", "اِفْعَلَّ", "Color/Physical Defects", "اِشْوَدَّ"),
    10: VerbFormInfo(10, "اِسْتَفْعَلَ", "اِسْتَفْعَلَ", "Request/Seeking", "اِسْتَكْتَبَ")
}

class VerbFormDetector:
    """Detects Arabic verb forms based on morphological patterns"""

    def __init__(self):
        self.verb_forms = VERB_FORMS

    def is_vocalized(self, verb):
        """Check if a verb has vocalization (diacritics)"""
        return any(char in [FATHA, DAMMA, KASRA, SHADDA, SUKUN] for char in verb)

    def normalize_verb(self, verb):
        """Normalize verb for pattern matching by removing some diacritics"""
        if not self.is_vocalized(verb):
            return verb

        # Convert some variations for pattern matching
        normalized = verb
        # Handle ALEF variations
        normalized = re.sub(r'[' + ALEF + ALEF_HAMZA_ABOVE + ALEF_HAMZA_BELOW + ALEF_MADDA + ']', ALEF, normalized)
        # Handle YEH variations at end
        normalized = re.sub(r'[' + YEH + ALEF_MAKSURA + ']$', YEH, normalized)

        return normalized

    def detect_form_pattern(self, verb):
        """
        Detect verb form based on vocalization and pattern
        Returns the form number and confidence
        """
        if not verb:
            return None, 0

        if not self.is_vocalized(verb):
            # For unvocalized verbs, we can't reliably determine the form
            return None, 0

        normalized = self.normalize_verb(verb)
        length = len(araby.strip_vocalization(normalized))

        # Form detection logic based on patterns and vocalization
        patterns = [
            # Form II: فَعَّلَ (doubled middle consonant with shadda)
            {
                'form': 2,
                'pattern': r'^.' + SHADDA + '.',
                'condition': lambda v: SHADDA in v[1:-1] and not v.startswith(ALEF + FATHA) and not v.startswith('ت') and not v.startswith('ا')
            },

            # Form III: فَاعَلَ (long vowel fatHa after first consonant)
            {
                'form': 3,
                'condition': lambda v: len(araby.strip_vocalization(v)) >= 4 and
                                     (('ا' in v[1:3] and FATHA in v[1:3]) or
                                      ('َا' in v[1:3] or 'اَ' in v[1:3]))
            },

            # Form IV: أَفْعَلَ (starts with alef fatHa)
            {
                'form': 4,
                'condition': lambda v: v.startswith(ALEF + FATHA) and len(araby.strip_vocalization(v)) >= 4
            },

            # Form V: تَفَعَّلَ (starts with ta fatHa, has shadda)
            {
                'form': 5,
                'condition': lambda v: v.startswith('ت' + FATHA) and SHADDA in v[2:-1] and len(araby.strip_vocalization(v)) >= 5
            },

            # Form VI: تَفاعَلَ (starts with ta fatHa, has alif after)
            {
                'form': 6,
                'condition': lambda v: v.startswith('ت' + FATHA) and ('ا' in v[2:4] or FATHA + ALEF in v[2:4]) and len(araby.strip_vocalization(v)) >= 5
            },

            # Form VII: اِنْفَعَلَ (starts with alef wasla + kasra)
            {
                'form': 7,
                'condition': lambda v: (v.startswith('ا' + KASRA + 'ن') or
                                      v.startswith(ALEF_WASLA + KASRA + 'ن')) and len(araby.strip_vocalization(v)) >= 5
            },

            # Form VIII: اِفْتَعَلَ (starts with alef wasla + kasra + feh)
            {
                'form': 8,
                'condition': lambda v: (v.startswith('ا' + KASRA + 'ف') or
                                      v.startswith(ALEF_WASLA + KASRA + 'ف')) and len(araby.strip_vocalization(v)) >= 5
            },

            # Form IX: اِفْعَلَّ (starts with alef wasla + kasra + shadda at end)
            {
                'form': 9,
                'condition': lambda v: ((v.startswith('ا' + KASRA) or v.startswith(ALEF_WASLA + KASRA)) and
                                      v.endswith(SHADDA) and len(araby.strip_vocalization(v)) >= 5)
            },

            # Form X: اِسْتَفْعَلَ (starts with alef wasla + kasra + seen + ta)
            {
                'form': 10,
                'condition': lambda v: ((v.startswith('ا' + KASRA + 'س') or v.startswith(ALEF_WASLA + KASRA + 'س')) and
                                      'ت' in v[2:5]) and len(araby.strip_vocalization(v)) >= 6
            },

            # Form I: فَعَلَ (basic triliteral - no special patterns)
            {
                'form': 1,
                'condition': lambda v: length == 3 and FATHA in v and SHADDA not in v and not v.startswith(ALEF + FATHA) and not v.startswith('ت')
            }
        ]

        # Check each pattern
        for pattern_info in patterns:
            try:
                if pattern_info['condition'](normalized):
                    return pattern_info['form'], 0.9
            except:
                continue

        return None, 0

    def generate_form_variants(self, root_verb, form_num):
        """
        Generate possible variants of a verb in a specific form
        This is used when the exact vocalization is unknown
        """
        if not root_verb:
            return []

        root = araby.strip_vocalization(root_verb)
        if len(root) < 3:
            return []

        variants = []

        # Extract root letters (assuming 3-letter root for simplicity)
        if len(root) == 3:
            f1, f2, f3 = root[0], root[1], root[2]

            if form_num == 1:
                variants = [
                    f1 + FATHA + f2 + FATHA + f3,
                    f1 + FATHA + f2 + DAMMA + f3,
                    f1 + FATHA + f2 + KASRA + f3
                ]
            elif form_num == 2:
                variants = [
                    f1 + FATHA + f2 + SHADDA + FATHA + f3,
                    f1 + FATHA + f2 + SHADDA + ALEF + f3
                ]
            elif form_num == 3:
                variants = [
                    f1 + FATHA + ALEF + f2 + FATHA + f3,
                ]
            elif form_num == 4:
                variants = [
                    ALEF + FATHA + f1 + SUKUN + f2 + FATHA + f3 + ALEF,
                    ALEF + FATHA + f1 + SUKUN + f2 + FATHA + f3
                ]
            elif form_num == 5:
                variants = [
                    'ت' + FATHA + f1 + FATHA + f2 + SHADDA + FATHA + f3 + ALEF,
                    'ت' + FATHA + f1 + FATHA + f2 + SHADDA + FATHA + f3
                ]
            elif form_num == 6:
                variants = [
                    'ت' + FATHA + f1 + ALEF + f2 + FATHA + f3 + ALEF,
                    'ت' + FATHA + f1 + ALEF + f2 + FATHA + f3
                ]
            elif form_num == 7:
                variants = [
                    ALEF_WASLA + KASRA + 'ن' + SUKUN + f1 + FATHA + f2 + FATHA + f3 + ALEF,
                    ALEF_WASLA + KASRA + 'ن' + SUKUN + f1 + FATHA + f2 + FATHA + f3
                ]
            elif form_num == 8:
                variants = [
                    ALEF_WASLA + KASRA + 'ف' + SUKUN + f1 + FATHA + f2 + FATHA + f3 + ALEF,
                    ALEF_WASLA + KASRA + 'ف' + SUKUN + f1 + FATHA + f2 + FATHA + f3
                ]
            elif form_num == 10:
                variants = [
                    ALEF_WASLA + KASRA + 'س' + SUKUN + 'ت' + FATHA + f1 + SUKUN + f2 + FATHA + f3 + ALEF,
                    ALEF_WASLA + KASRA + 'س' + SUKUN + 'ت' + FATHA + f1 + SUKUN + f2 + FATHA + f3
                ]

        return [v for v in variants if v and len(v.strip()) > 0]

    def get_all_forms_info(self):
        """Return information about all verb forms"""
        return self.verb_forms.copy()

    def get_form_info(self, form_num):
        """Get information about a specific verb form"""
        return self.verb_forms.get(form_num)

    def create_ascii_table(self, base_verb, forms_data=None):
        """
        Create an ASCII table showing all 10 verb forms for a given base verb
        forms_data: dictionary of {form_num: actual_verb} for known forms
        """
        if not forms_data:
            forms_data = {}

        # Detect current form if provided
        current_form, confidence = self.detect_form_pattern(base_verb) if base_verb else (None, 0)

        table_lines = []
        table_lines.append("+-----+----------------------+----------------------+--------------------+")
        table_lines.append("|Form | Arabic Name          | Conjugated Verb      | Meaning            |")
        table_lines.append("+-----+----------------------+----------------------+--------------------+")

        for form_num in range(1, 11):
            form_info = self.verb_forms[form_num]

            # Get actual conjugated verb if available
            conjugated_verb = forms_data.get(form_num, "Generated" if base_verb else "N/A")
            if conjugated_verb == "Generated" and base_verb:
                # Try to generate this form
                variants = self.generate_form_variants(base_verb, form_num)
                if variants:
                    conjugated_verb = variants[0]  # Take first variant

            # Mark current form with *
            form_marker = f"{form_num}*" if form_num == current_form else str(form_num)

            line = f"| {form_marker:<3} | {form_info.arabic_name:<20} | {conjugated_verb:<20} | {form_info.english_meaning:<18} |"
            table_lines.append(line)

        table_lines.append("+-----+----------------------+----------------------+--------------------+")

        if current_form:
            form_info = self.verb_forms[current_form]
            table_lines.append(f"\nDetected: {base_verb} is Form {current_form} ({form_info.arabic_name})")
            table_lines.append(f"Confidence: {confidence:.1%}")

        return "\n".join(table_lines)

# Global detector instance
_detector = None

def get_detector():
    """Get or create the global detector instance"""
    global _detector
    if _detector is None:
        _detector = VerbFormDetector()
    return _detector

def detect_verb_form(verb):
    """Convenience function to detect verb form"""
    detector = get_detector()
    return detector.detect_form_pattern(verb)

def get_verb_forms_info():
    """Convenience function to get all verb forms information"""
    detector = get_detector()
    return detector.get_all_forms_info()

def create_verb_forms_table(base_verb, forms_data=None):
    """Convenience function to create ASCII table of verb forms"""
    detector = get_detector()
    return detector.create_ascii_table(base_verb, forms_data)