# -*- coding: utf-8 -*-
import io
p = r"analysis/apply_math.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("def convert_spans(p, explicit=()):",
              "def convert_spans(p, explicit=(), size=None):")
s = s.replace("        p._p.append(parse_xml(omml.omath(latex)))",
              "        p._p.append(parse_xml(omml.omath(latex, size=size)))")
s = s.replace('''        cell = doc.tables[ti].rows[ri].cells[ci]
        mathdoc.rebuild(cell.paragraphs[0], parts)''',
              '''        cell = doc.tables[ti].rows[ri].cells[ci]
        mathdoc.rebuild(cell.paragraphs[0], parts, size=16)
        mathdoc.relax_line(cell.paragraphs[0])''')
s = s.replace('''        cell = doc.tables[1].rows[row_i].cells[0]
        mathdoc.rebuild(cell.paragraphs[0], [(M, latex)])''',
              '''        cell = doc.tables[1].rows[row_i].cells[0]
        mathdoc.rebuild(cell.paragraphs[0], [(M, latex)], size=16)
        mathdoc.relax_line(cell.paragraphs[0])''')
s = s.replace('''                    if p._p.find(qn("m:oMath")) is not None:
                        continue
                    convert_spans(p)''',
              '''                    if p._p.find(qn("m:oMath")) is not None:
                        continue
                    if convert_spans(p, (), size=16):
                        mathdoc.relax_line(p)''')
io.open(p, "w", encoding="utf-8").write(s)
print("patched", s.count("size=16"))
