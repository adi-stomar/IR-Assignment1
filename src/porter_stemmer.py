"""
Pure-Python implementation of the Porter stemming algorithm

"""

VOWELS = set("aeiou")


class PorterStemmer:

    def _is_consonant(self, word, i):
        c = word[i]
        if c in VOWELS:
            return False
        if c == "y":
            if i == 0:
                return True
            return not self._is_consonant(word, i - 1)
        return True

    def _cv_string(self, word):
        return "".join("c" if self._is_consonant(word, i) else "v" for i in range(len(word)))

    def _measure(self, stem):
        # m = number of "vc" occurrences in the consonant/vowel form of stem
        cv = self._cv_string(stem)
        return cv.count("vc")

    def _contains_vowel(self, stem):
        return any(not self._is_consonant(stem, i) for i in range(len(stem)))

    def _ends_double_consonant(self, word):
        if len(word) < 2:
            return False
        return word[-1] == word[-2] and self._is_consonant(word, len(word) - 1)

    def _ends_cvc(self, word):
        if len(word) < 3:
            return False
        return (
            self._is_consonant(word, len(word) - 3)
            and not self._is_consonant(word, len(word) - 2)
            and self._is_consonant(word, len(word) - 1)
            and word[-1] not in ("w", "x", "y")
        )

    def _apply_suffix(self, word, endings):
        """endings: list of (suffix, replacement, condition_fn) tried in order.
        condition_fn receives the stem left after removing suffix and returns bool."""
        for suffix, replacement, condition in endings:
            if suffix == "" or word.endswith(suffix):
                stem = word[: len(word) - len(suffix)] if suffix else word
                if condition(stem):
                    return stem + replacement
        return word

    def _step1a(self, word):
        return self._apply_suffix(word, [
            ("sses", "ss", lambda s: True),
            ("ies", "i", lambda s: True),
            ("ss", "ss", lambda s: True),
            ("s", "", lambda s: True),
            ("", "", lambda s: True),
        ])

    def _step1b(self, word):
        if word.endswith("eed"):
            stem = word[:-3]
            if self._measure(stem) > 0:
                return stem + "ee"
            return word

        applied = False
        stem = None
        if word.endswith("ed") and self._contains_vowel(word[:-2]):
            stem = word[:-2]
            applied = True
        elif word.endswith("ing") and self._contains_vowel(word[:-3]):
            stem = word[:-3]
            applied = True

        if not applied:
            return word

        if stem.endswith(("at", "bl", "iz")):
            return stem + "e"
        if self._ends_double_consonant(stem) and stem[-1] not in ("l", "s", "z"):
            return stem[:-1]
        if self._measure(stem) == 1 and self._ends_cvc(stem):
            return stem + "e"
        return stem

    def _step1c(self, word):
        if word.endswith("y") and len(word) > 1 and self._contains_vowel(word[:-1]):
            return word[:-1] + "i"
        return word

    def _step2(self, word):
        mapping = [
            ("ational", "ate"), ("tional", "tion"), ("enci", "ence"), ("anci", "ance"),
            ("izer", "ize"), ("abli", "able"), ("alli", "al"), ("entli", "ent"),
            ("eli", "e"), ("ousli", "ous"), ("ization", "ize"), ("ation", "ate"),
            ("ator", "ate"), ("alism", "al"), ("iveness", "ive"), ("fulness", "ful"),
            ("ousness", "ous"), ("aliti", "al"), ("iviti", "ive"), ("biliti", "ble"),
            ("logi", "log"),
        ]
        for suffix, replacement in mapping:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                if self._measure(stem) > 0:
                    return stem + replacement
                return word
        return word

    def _step3(self, word):
        mapping = [
            ("icate", "ic"), ("ative", ""), ("alize", "al"), ("iciti", "ic"),
            ("ical", "ic"), ("ful", ""), ("ness", ""),
        ]
        for suffix, replacement in mapping:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                if self._measure(stem) > 0:
                    return stem + replacement
                return word
        return word

    def _step4(self, word):
        suffixes = [
            "al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement",
            "ment", "ent", "ion", "ou", "ism", "ate", "iti", "ous", "ive", "ize",
        ]
        for suffix in suffixes:
            if word.endswith(suffix):
                stem = word[: -len(suffix)]
                if suffix == "ion":
                    if stem and stem[-1] in ("s", "t") and self._measure(stem) > 1:
                        return stem
                    return word
                if self._measure(stem) > 1:
                    return stem
                return word
        return word

    def _step5a(self, word):
        if word.endswith("e"):
            stem = word[:-1]
            m = self._measure(stem)
            if m > 1:
                return stem
            if m == 1 and not self._ends_cvc(stem):
                return stem
        return word

    def _step5b(self, word):
        if self._measure(word) > 1 and self._ends_double_consonant(word) and word.endswith("l"):
            return word[:-1]
        return word

    def stem(self, word):
        word = word.lower()
        if len(word) <= 2:
            return word
        word = self._step1a(word)
        word = self._step1b(word)
        word = self._step1c(word)
        word = self._step2(word)
        word = self._step3(word)
        word = self._step4(word)
        word = self._step5a(word)
        word = self._step5b(word)
        return word


if __name__ == "__main__":
    stemmer = PorterStemmer()
    tests = ["caresses", "ponies", "ties", "caress", "cats", "feed", "agreed",
             "plastered", "bled", "motoring", "sing", "conflated", "troubled",
             "sized", "hopping", "tanned", "falling", "hissing", "fizzed",
             "failing", "filing", "happy", "sky", "relational", "conditional",
             "rational", "valenci", "hesitanci", "digitizer", "conformabli",
             "radicalli", "differentli", "vileli", "analogousli", "vietnamization",
             "predication", "operator", "feudalism", "decisiveness", "hopefulness",
             "callousness", "formaliti", "sensitiviti", "sensibiliti", "triplicate",
             "formative", "formalize", "electriciti", "electrical", "hopeful",
             "goodness", "revival", "allowance", "inference", "airliner",
             "gyroscopic", "adjustable", "defensible", "irritant", "replacement",
             "adjustment", "dependent", "adoption", "homologou", "communism",
             "activate", "angulariti", "homologous", "effective", "bowdlerize",
             "probate", "rate", "cease", "controll", "roll"]
    for t in tests:
        print(t, "->", stemmer.stem(t))
