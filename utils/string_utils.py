def phase_convert(string):
    result = string.replace("IV", "4").replace("III", "3").replace("II", "2").replace("I", "1")
    return result.strip()


