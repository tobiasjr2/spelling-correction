"""
Language Model class.
Create and read the corpus with the language model file.

Statistical techniques for text correction:
    * N-gram with similarity.
    * Peter Norvig's method.
    * Symspell method.
"""

import os
import re
import string

from ngram import NGram
from spellchecker import SpellChecker
from symspellpy.symspellpy import SymSpell


class LanguageModel():

    def __init__(self, mode, source, N=2):
        self.autocorrect = getattr(self, f"_{mode}")
        self.source = source
        self.N = N

    def create_corpus(self, sentences):
        """Create corpus file"""

        matches = " ¶ ".join(sentences).translate(str.maketrans("", "", string.punctuation))
        matches = re.compile(r'[^\S\n]+', re.UNICODE).sub(" ", matches.strip())
        matches = "\n".join(matches.strip().split(" ¶ "))

        return matches.lower()

    def read_corpus(self, corpus_path):
        """Read corpus file to the autocorrect tool"""

        self.corpus_path = corpus_path
        self.dictionary_path = os.path.join(os.path.dirname(corpus_path), "dictionary.txt")
        self.corpus = " ".join(open(corpus_path).read().splitlines()).lower()

    def _kaldi(self, sentences):
        """
        Kaldi Speech Recognition Toolkit with SRI Language Modeling Toolkit.

        ** Important Note **
        You'll need to do all by yourself:

        1. Compile Kaldi with SRILM and OpenBLAS.
        2. Create these files:
            a. `chars.lst`
            b. `conf_mats.ark`
            c. `ground_truth.lst`
            d. `ID_test.lst`
            e. `ID_train.lst`
        3. Put kaldi folder in the project `lib` folder: ``src/tool/lib/kaldi``
        4. Put the files in the project `output` folder: ``output/<DATASET>/kaldi``

        More information (maybe help) in ``src/tool/lib/kaldi-srilm-script.sh``.

        References:
            D. Povey, A. Ghoshal, G. Boulianne, L. Burget, O. Glembek, N. Goel, M. Hannemann,
            P. Motlicek, Y. Qian, P. Schwarz, J. Silovsky, G. Stem- mer and K. Vesely.
            The Kaldi speech recognition toolkit, 2011.
            Workshop on Automatic Speech Recognition and Understanding.
            URL: http://github.com/kaldi-asr/kaldi

            Andreas Stolcke.
            SRILM - An Extensible Language Modeling Toolkit, 2002.
            Proceedings of the 7th International Conference on Spoken Language Processing (ICSLP).
            URL: http://www.speech.sri.com/projects/srilm/
        """

        print("kaldi")

    def _similarity(self, sentences):
        """
        N-gram with similarity.

        The NGram class extends the Python ‘set’ class with efficient fuzzy search for members by
        means of an N-gram similarity measure.

        Reference:
            Vacláv Chvátal and David Sankoff.
            Longest common subsequences of two random sequences, 1975.
            Journal of Applied Probability,

            Python module: ngram (https://pypi.org/project/ngram/)
        """

        ngram = NGram(self.corpus.split(), key=lambda x:x.lower(), N=self.N)
        predicts = []

        if not isinstance(sentences, list):
            sentences = [sentences]

        for i in range(len(sentences)):
            splitted = []

            for x in sentences[i].split():
                sugg = ngram.find(x) if x not in string.punctuation else None
                splitted.append(sugg if sugg else x)

            predicts.append(" ".join(splitted))

        return predicts

    def _norvig(self, sentences):
        """
        It uses a Levenshtein Distance algorithm to find permutations within an edit distance of 2
        from the original word. It then compares all permutations (insertions, deletions, replacements,
        and transpositions) to known words in a word frequency list.
        Those words that are found more often in the frequency list are more likely the correct results.

        Reference:
            Stuart J. Russell and Peter Norvig.
            Artificial intelligence - a modern approach: the intelligent agent book, 1995.
            Prentice Hall series in artificial intelligence.
            URL: http://norvig.com/spell-correct.html

            Python module: pyspellchecker (https://pypi.org/project/pyspellchecker/)
        """

        norvig = SpellChecker(distance=self.N)
        norvig.word_frequency.load_words(self.corpus.split())
        predicts = []

        if not isinstance(sentences, list):
            sentences = [sentences]

        for i in range(len(sentences)):
            splitted = []

            for x in sentences[i].split():
                sugg = norvig.correction(x) if x not in string.punctuation else None
                splitted.append(sugg if sugg else x)

            predicts.append(" ".join(splitted))

        return predicts

    def _symspell(self, sentences):
        """
        SymSpell tool to text correction through Symmetric Delete spelling algorithm.

        Reference:
            Author: Wolf Garbe <wolf.garbe@faroo.com>
            Description: https://medium.com/@wolfgarbe/1000x-faster-spelling-correction-algorithm-2012-8701fcd87a5f
            URL: https://github.com/wolfgarbe/symspell

            Python module: symspellpy (https://github.com/mammothb/symspellpy)
        """

        symspell = SymSpell(max_dictionary_edit_distance=self.N)
        symspell.create_dictionary(self.corpus_path)

        with open(self.dictionary_path, "w") as f:
            for key, count in symspell.words.items():
                f.write(f"{key} {count}\n")

        symspell.load_dictionary(self.dictionary_path, term_index=0, count_index=1)
        predicts = []

        if not isinstance(sentences, list):
            sentences = [sentences]

        for i in range(len(sentences)):
            splitted = []

            for x in sentences[i].split():
                sugg = symspell.lookup(x, verbosity=0, max_edit_distance=self.N,
                                       transfer_casing=True) if x not in string.punctuation else None
                splitted.append(sugg[0].term if sugg else x)

            predicts.append(" ".join(splitted))

        return predicts
