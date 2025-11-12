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
        - 'FORM_TABLE': Show all 10 verb forms (simple)
        - 'COMPREHENSIVE_TABLE': Complete table with all conjugations and nouns
    @type display_format: string, default("HTML")
    @param form_filter: Filter for specific verb form (1-10), None for all
    @type form_filter: int or None
    @return: The conjugation result
    @rtype: According to display_format.
    """
    # Handle special FORM_TABLE display format and form filtering
    if display_format.upper() == "FORM_TABLE":
        return create_verb_forms_table(word, form_filter, transitive)
    elif display_format.upper() == "COMPREHENSIVE_TABLE":
        return create_comprehensive_forms_table(word, future_type, transitive)
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
    # Some pyarabic builds expose strip_harakat, others only strip_tashkeel.
    strip_fn = getattr(araby, "strip_harakat", None)
    if strip_fn is None:
        strip_fn = getattr(araby, "strip_tashkeel", None)
    if strip_fn is None:
        strip_fn = getattr(araby, "strip_diacritics", None)
    if strip_fn is None:
        # Fall back to the identity function; downstream code will still work
        # but we log a hint for future maintainers.
        def strip_fn(text):
            return text
    stripped_word = strip_fn(word)
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


def create_comprehensive_forms_table(word, future_type="ضمة", transitive=False):
    """
    Create comprehensive table showing all 10 forms with complete conjugations
    and derived nouns - matching "The Ten Measures" format
    
    @param word: The base verb (root form - Form I)
    @type word: unicode
    @param future_type: Future type marking
    @type future_type: unicode
    @param transitive: Whether the verb is transitive
    @type transitive: Boolean
    @return: Formatted comprehensive table
    @rtype: string
    """
    from . import conjugatedisplay
    
    # Create display object
    display = conjugatedisplay.ConjugateDisplay(word)
    
    # Generate the comprehensive table
    return display.display_comprehensive_forms_table(word, future_type)


def get_comprehensive_forms_data(word, future_type="ضمة", transitive=False):
    """
    Get structured data for all 10 verb forms with complete conjugations
    Returns a list of dictionaries, one for each form
    
    @param word: The base verb (root form - Form I)
    @type word: unicode
    @param future_type: Future type marking
    @type future_type: unicode
    @param transitive: Whether the verb is transitive
    @type transitive: Boolean
    @return: List of dictionaries with conjugation data for each form
    @rtype: list
    """
    from . import verb_form_detector
    from . import mosaref_main
    import pyarabic.araby as araby
    
    form_definitions = [
        (1, "I", "فَعَلَ", "REGULAR"),
        (2, "II", "فَعَّلَ", "CAUSATIVE/INTENSIVE OR DENOMINATIVE"),
        (3, "III", "فَاعَلَ", "RECIPROCAL"),
        (4, "IV", "أَفْعَلَ", "CAUSATIVE"),
        (5, "V", "تَفَعَّلَ", "REFLEXIVE OF II"),
        (6, "VI", "تَفَاعَلَ", "REFLEXIVE OF III"),
        (7, "VII", "اِنْفَعَلَ", "PASSIVE OF I"),
        (8, "VIII", "اِفْتَعَلَ", "REFLEXIVE OF I"),
        (9, "IX", "اِفْعَلَّ", "COLORS DEFECTS"),
        (10, "X", "اِسْتَفْعَلَ", "CAUSATIVE REFLEXIVE")
    ]
    
    # Get detector and generate actual verb forms
    detector = verb_form_detector.get_detector()
    current_form, _ = detector.detect_form_pattern(word)
    
    # Strip vocalization for root extraction
    strip_fn = getattr(araby, "strip_harakat", None)
    if strip_fn is None:
        strip_fn = getattr(araby, "strip_tashkeel", None)
    if strip_fn is None:
        strip_fn = getattr(araby, "strip_diacritics", None)
    if strip_fn is None:
        def strip_fn(text):
            return text
    stripped_word = strip_fn(word)
    
    forms_data = []
    
    for form_num, roman, pattern, meaning in form_definitions:
        # Get actual verb form for this form number
        verb_form = None
        if form_num == current_form:
            verb_form = word
        elif len(stripped_word) == 3:
            variants = detector.generate_form_variants(word, form_num)
            if variants:
                verb_form = variants[0]
        
        form_data = {
            "Form": str(form_num),
            "Roman": roman,
            "Pattern": pattern,
            "Meaning": meaning
        }
        
        if verb_form:
            try:
                # Conjugate the verb to get actual forms
                result = mosaref_main.do_sarf(verb_form, future_type, alltense=True,
                                               transitive=False, display_format="DICT")
                
                if result and hasattr(result, 'text') and hasattr(result, 'tab_conjug'):
                    # DEBUG: Log available keys (only for first form)
                    if form_num == 1:
                        import sys
                        print(f"\n=== DEBUG: Available keys in result ===", file=sys.stderr)
                        print(f"text keys: {list(result.text.keys())[:10]}", file=sys.stderr)
                        print(f"tab_conjug keys: {list(result.tab_conjug.keys())}", file=sys.stderr)
                        if result.tab_conjug:
                            first_tense = list(result.tab_conjug.keys())[0]
                            print(f"Pronouns in '{first_tense}': {list(result.tab_conjug[first_tense].keys())}", file=sys.stderr)
                        print(f"======================================\n", file=sys.stderr)
                    
                    # Extract noun derivatives
                    form_data["Noun_Place_Time"] = result.text.get("اسم المكان", "—")
                    form_data["Passive_Participle"] = result.text.get("اسم المفعول", "—")
                    form_data["Active_Participle"] = result.text.get("اسم الفاعل", "—")
                    form_data["Masdar"] = result.text.get("المصدر", "—")
                    
                    # Get verb conjugations (3rd person masculine singular where applicable)
                    # Use correct tense keys from verb_const
                    form_data["Passive_Perfect"] = result.tab_conjug.get("الماضي المجهول", {}).get("هو", "—")
                    form_data["Passive_Imperfect"] = result.tab_conjug.get("المضارع المجهول", {}).get("هو", "—")
                    form_data["Imperative"] = result.tab_conjug.get("الأمر", {}).get("أنت", "—")
                    form_data["Active_Imperfect"] = result.tab_conjug.get("المضارع المعلوم", {}).get("هو", "—")
                    form_data["Active_Perfect"] = result.tab_conjug.get("الماضي المعلوم", {}).get("هو", verb_form)
                else:
                    # Fallback if structure is different
                    form_data["Noun_Place_Time"] = "—"
                    form_data["Passive_Participle"] = "—"
                    form_data["Active_Participle"] = "—"
                    form_data["Masdar"] = "—"
                    form_data["Passive_Perfect"] = "—"
                    form_data["Passive_Imperfect"] = "—"
                    form_data["Imperative"] = "—"
                    form_data["Active_Imperfect"] = "—"
                    form_data["Active_Perfect"] = verb_form
            except Exception as e:
                # Fallback on error
                form_data["Noun_Place_Time"] = "—"
                form_data["Passive_Participle"] = "—"
                form_data["Active_Participle"] = "—"
                form_data["Masdar"] = "—"
                form_data["Passive_Perfect"] = "—"
                form_data["Passive_Imperfect"] = "—"
                form_data["Imperative"] = "—"
                form_data["Active_Imperfect"] = "—"
                form_data["Active_Perfect"] = verb_form if verb_form else pattern
        else:
            # No verb generated for this form
            form_data["Noun_Place_Time"] = "—"
            form_data["Passive_Participle"] = "—"
            form_data["Active_Participle"] = "—"
            form_data["Masdar"] = "—"
            form_data["Passive_Perfect"] = "—"
            form_data["Passive_Imperfect"] = "—"
            form_data["Imperative"] = "—"
            form_data["Active_Imperfect"] = "—"
            form_data["Active_Perfect"] = "—"
        
        forms_data.append(form_data)
    
    return forms_data


#~ conjugate = do_sarfco