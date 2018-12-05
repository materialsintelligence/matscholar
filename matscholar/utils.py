def parse_word_expression(expr):
    """
    Parses a word expression such as "thermoelectric - PbTe + LiFePO4" into positive and negative words
    :param expr: a string expression, with " +" and " -" strings separating the words in the expression.
    :return: Returns a tuple of lists (positive, negative)
    """
    last_word, i, is_positive = "", 0, True
    positive, negative = [], []
    while i < len(expr):
        if expr[i:i+2] != " +" and expr[i:i+2] != " -":
            last_word += expr[i]
        else:
            positive.append(last_word.strip()) if is_positive else negative.append(last_word.strip())
            is_positive, last_word, i = expr[i:i+2] == " +", "", i + 1
        i += 1
    if last_word.strip():
        positive.append(last_word.strip()) if is_positive else negative.append(last_word.strip())
    return positive, negative
