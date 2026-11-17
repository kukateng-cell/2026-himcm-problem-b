# -*- coding: utf-8 -*-
"""Compare original vs rebuilt paragraph text (math excluded) for edited paragraphs."""
import sys, re
from docx import Document

orig = Document(sys.argv[1]).paragraphs
new = Document(sys.argv[2]).paragraphs
IDX = [25, 27, 28, 29, 47, 48, 50, 54, 57, 59, 60, 62, 65, 66, 67, 68, 83, 137]

def norm(t):
    return re.sub(r"\s+", " ", t).strip()

for i in IDX:
    a = norm(orig[i].text)
    j = i + 1 if i > 51 else i
    b = norm(new[j].text)
    if a != b:
        # find first diff
        k = 0
        while k < min(len(a), len(b)) and a[k] == b[k]:
            k += 1
        print("P%03d DIFF at %d\n  old: %r\n  new: %r" % (i, k, a[max(0, k-40):k+80], b[max(0, k-40):k+80]))
    else:
        print("P%03d ok (%d chars)" % (i, len(a)))
# prose paragraph added after 51
print("P052 prose:", norm(new[52].text)[:80], "...")
