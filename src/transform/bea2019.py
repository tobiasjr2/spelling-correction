"""Transform BEA2019 dataset"""

import os
from data import preproc, m2


class Transform():

    def __init__(self, source, charset, max_text_length):
        self.m2_file = os.path.join(source, "m2")
        self.charset = charset
        self.max_text_length = max_text_length
        self.partitions = dict()

    def build(self):
        m2_list = next(os.walk(self.m2_file))[2]
        lines = []

        for m2_file in m2_list:
            f = os.path.join(self.m2_file, m2_file)
            lines += m2.read_raw(f)

        lines = list(set(lines))
        lines = preproc.normalize_text(lines, charset=self.charset, limit=self.max_text_length)

        total = len(lines)
        train_i = int(total * 0.8)
        valid_i = train_i + int((total - train_i) / 2)

        self.partitions["train"] = lines[:train_i]
        self.partitions["valid"] = lines[train_i:valid_i]
        self.partitions["test"] = lines[valid_i:]