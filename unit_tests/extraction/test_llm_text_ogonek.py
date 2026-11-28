"""The text for the AI models has the same Polish letters as the text of the language checks.

LaTeX with the default font encoding draws "ą" and "ę" as a letter and a separate ogonek, and PyMuPDF returns them
as "˛a" / "˛e", often splitting the word in front of the ogonek.
"""
import unittest

from analysis.extraction.helper_llm.extraction_json_llm import parse_text_block


def _parsed_words(words):
    """One line of a PDF block, given as the words PyMuPDF returns for it; the texts of the parsed spans."""
    boxes = [(10.0 + 50 * i, 100.0, 55.0 + 50 * i, 112.0) for i in range(len(words))]
    line_box = (10.0, 100.0, boxes[-1][2], 112.0)
    raw_span = {"text": " ".join(words), "bbox": line_box, "size": 12.0, "font": "SFRM1200", "color": 0, "flags": 0}
    raw_block = {"number": 0, "bbox": line_box, "lines": [{"spans": [raw_span], "bbox": line_box, "wmode": 0}]}
    word_list = [(*box, word, 0, 0, i) for i, (box, word) in enumerate(zip(boxes, words))]
    block, _, _ = parse_text_block(raw_block, word_list, 595.0, {"left": 10.0, "right": 10.0}, None, 0, [], False)
    return [span.text for line in block.lines for span in line.spans]


class LlmTextOgonekTest(unittest.TestCase):
    def test_ogonek_inside_a_word(self):
        self.assertEqual(_parsed_words(["sprz˛etowych", "wst˛epne", "s˛a"]), ["sprzętowych", "wstępne", "są"])

    def test_capital_letters(self):
        self.assertEqual(_parsed_words(["PI˛EĆ", "S˛AD"]), ["PIĘĆ", "SĄD"])

    def test_word_split_in_front_of_the_ogonek_is_joined(self):
        self.assertEqual(_parsed_words(["istniej", "˛acych", "rozwi", "˛aza´n"]), ["istniejących", "rozwiązań"])

    def test_other_latex_letters_still_work(self):
        self.assertEqual(_parsed_words(["´swiat", "˙zółw"]), ["świat", "żółw"])

    def test_separate_words_stay_separate(self):
        self.assertEqual(_parsed_words(["analiza", "danych"]), ["analiza", "danych"])


if __name__ == "__main__":
    unittest.main()
