def phase_convert(string):
    result = string.replace("IV", "4").replace("III", "3").replace("II", "2").replace("I", "1")
    return result.strip()


def check_words_in_string(string, words, case_ignore=False):
    for word in words:
        if case_ignore:
            if word.lower() in string.lower():
                return True
        else:
            if word in string:
                return True
    return False


