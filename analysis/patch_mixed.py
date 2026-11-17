# -*- coding: utf-8 -*-
import io, re
p = r"C:\Users\kukat\Desktop\USA\analysis\omml_segments.py"
s = io.open(p, encoding="utf-8").read()
start = s.index("def convert_mixed")
end = s.index("path = sys.argv[1]")
new_fn = '''def convert_mixed(p, text):
    cut = text.find(" Rectangular jets")
    if cut < 0:
        return False
    head = text[:cut]
    rest = text[cut:]
    parts = []
    segs = head.split("; ")
    for i, seg in enumerate(segs):
        last = (i == len(segs) - 1)
        if last and ", with " in seg:
            a, b = seg.split(", with ", 1)
            parts.append(("m", a.strip() + ","))
            parts.append(("t", " with "))
            parts.append(("m", b.strip()))
        elif seg.strip():
            parts.append(("m", seg.strip() + ("" if last else ";")))
        if not last:
            parts.append(("t", " "))
    parts.append(("t", rest))
    rebuild(p, parts)
    return True


'''
s = s[:start] + new_fn + s[end:]
io.open(p, "w", encoding="utf-8").write(s)
print("rewrote convert_mixed")
