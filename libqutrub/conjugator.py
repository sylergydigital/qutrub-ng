#************************************************************************
# $Id: mosaref_main.py, v 0.7 2009/06/02 01:10:00 Taha Zerrouki $
#
# ------------
# Description:
# ------------
#  Copyright (c) 2009, Arabtechies, Arabeyes Taha Zerrouki
#
#  This file is used by the web interface to execute verb conjugation
#
# -----------------
# Revision Details:    (Updated by Revision Control System)
# -----------------
#  $Date: 2009/06/02 01:10:00 $
#  $Author: Taha Zerrouki $
#  $Revision: 0.7 $
#  $Source: arabtechies.sourceforge.net
#
#***********************************************************************/
"""
Just a wraper for mosaref_main
The main function to call qutrub conjugation from other programs.
"""
#
import libqutrub.mosaref_main
from . import verb_form_detector
from . import verb_const
# rename the function
def conjugate(word, future_type, alltense = True, past = False, future = False,
passive = False, imperative = False, future_moode = False, confirmed = False,
 transitive = False, display_format = "HTML", form_filter = None):
    """
    The main function to conjugate verbs.
    You must specify all parameters.
    Can be used as an example to call the conjugation class.
    @param word: the givern verb. the given word must be vocalized,
    if it's 3 letters length only, else, the verb can be unvocalized,
     but the Shadda must be given, it' considered as letter.
    @type word: unicode.
    @param future_type: For Triliteral verbs,
    you must give the mark of Ain in the future,
    كة عين الفعل في المضارع. it's given as a name of haraka (فتحة، ضمة، كسرة).
    @type future_type: unicode(فتحة، ضمة، كسرة).
    @param alltense: conjugate in all arabic tenses.
    @type alltense: Boolean, default(True)
    @param past: conjugate in past tense ألماضي
    @type past: Boolean, default(False)
    @param future: conjugate in arabic present and future tenses المضارع
    @type future: Boolean, default(False)
    @param passive: conjugate in passive voice  المبني للمجهول
    @type passive: Boolean, default(False)
    @param imperative: conjugate in imperative tense الأمر
    @type imperative: Boolean, default(False)
    @param future_moode: conjugate in future moode tenses المضارع المنصوب والمجزوم
    @type future_moode: Boolean, default(False)
    @param confirmed: conjugate in confirmed cases tense المؤكّد
    @type confirmed: Boolean, default(False)
    @param transitive: verb transitivity التعدي واللزوم
    @type transitive: Boolean, default(False)
    @param display_format: Choose the display format:
        - 'TEXT':
        - 'HTML':
        - 'HTMLColoredDiacritics':
        - 'DICT':
        - 'CSV':
        - 'GUI':
        - 'TABLE':
        - 'XML':
        - 'TeX':
        - 'ROWS':
        - 'FORM_TABLE': (new) Show all 10 verb forms
    @type display_format: string, default("HTML")
    @param form_filter: Filter for specific verb form (1-10), None for all
    @type form_filter: int or None
    @return: The conjugation result
    @rtype: According to display_format.
    """
    # Handle special FORM_TABLE display format and form filtering
    if display_format.upper() == "FORM_TABLE":
        return create_verb_forms_table(word, form_filter, transitive)
    elif form_filter is not None:
        # If form filter is specified but not using FORM_TABLE format,
        # we need to check if the current verb matches the form
        detected_form, confidence = verb_form_detector.detect_verb_form(word)
        if detected_form != form_filter:
            return f"Error: Verb '{word}' is Form {detected_form}, not Form {form_filter}"

    # Regular conjugation
    return libqutrub.mosaref_main.do_sarf(word, future_type, alltense, past , future ,
passive , imperative , future_moode , confirmed ,
 transitive , display_format)


def create_verb_forms_table(word, form_filter=None, transitive=False):
    """
    Create a table showing all 10 Arabic verb forms for a given verb

    @param word: The base verb (root form - Form I)
    @type word: unicode
    @param form_filter: Specific form to show (1-10), None for all
    @type form_filter: int or None
    @param transitive: Whether the verb is transitive
    @type transitive: Boolean
    @return: Formatted table of verb forms
    @rtype: string
    """
    if not word:
        return "No verb provided"

    # Get detector instance
    detector = verb_form_detector.get_detector()

    # Generate forms data dictionary
    forms_data = {}

    # Always include the input verb
    current_form, _ = detector.detect_form_pattern(word)
    if current_form:
        forms_data[current_form] = word

    # Generate variants for all other forms if we have a 3-letter root
    import pyarabic.araby as araby
    stripped_word = araby.strip_vocalization(word)
    if len(stripped_word) == 3:
        for form_num in verb_const.VERB_FORMS_ORDER:
            if form_num != current_form:
                variants = detector.generate_form_variants(word, form_num)
                if variants:
                    forms_data[form_num] = variants[0]  # Take first variant

    # Apply form filter if specified
    if form_filter:
        if form_filter in forms_data:
            filtered_data = {form_filter: forms_data[form_filter]}
        else:
            return f"Form {form_filter} not available for verb '{word}'"
    else:
        filtered_data = forms_data

    # Create ASCII table
    return detector.create_ascii_table(word, filtered_data)


#~ conjugate = do_sarfco