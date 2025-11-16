import re


def pluralize(word):
    """
    Pluralize an English word using regular expressions.
    Handles most common cases but not all irregular plurals.
    """
    if not word:
        return word

    word = word.lower()

    # Irregular plurals
    irregulars = {
        "man": "men",
        "woman": "women",
        "child": "children",
        "tooth": "teeth",
        "foot": "feet",
        "mouse": "mice",
        "goose": "geese",
        "person": "people",
        "ox": "oxen",
        "deer": "deer",
        "sheep": "sheep",
        "fish": "fish",
        "moose": "moose",
    }

    if word in irregulars:
        return irregulars[word]

    if re.search(r"[^aeiou]y$", word):
        return re.sub(r"y$", "ies", word)

    if re.search(r"[^aeiou]o$", word):
        exceptions = ["photo", "piano", "halo", "solo"]

        if word in exceptions:
            return word + "s"

        return word + "es"

    if re.search(r"fe?$", word):
        return re.sub(r"fe?$", "ves", word)

    if re.search(r"us$", word):
        return re.sub(r"us$", "i", word)

    if re.search(r"is$", word):
        return re.sub(r"is$", "es", word)

    if re.search(r"(ss|sh|ch|[sxz])$", word):
        return word + "es"

    return word + "s"
