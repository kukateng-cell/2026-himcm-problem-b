# -*- coding: utf-8 -*-
"""LaTeX-subset -> OMML (Office Math) builder for Word equations."""
import re
from xml.sax.saxutils import escape

OMML_OPEN = (
    '<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
)
OMML_CLOSE = "</m:oMath>"

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ",
    "sigma": "σ", "tau": "τ", "phi": "φ", "varphi": "φ", "chi": "χ",
    "psi": "ψ", "omega": "ω", "Delta": "Δ", "Gamma": "Γ", "Theta": "Θ",
    "Lambda": "Λ", "Sigma": "Σ", "Phi": "Φ", "Omega": "Ω", "Pi": "Π",
}
OPS = {
    "cdot": "·", "times": "×", "approx": "≈", "le": "≤", "leq": "≤",
    "ge": "≥", "geq": "≥", "ne": "≠", "neq": "≠", "pm": "±", "mp": "∓",
    "sim": "∼", "infty": "∞", "div": "÷", "ast": "∗", "circ": "∘",
    "to": "→", "rightarrow": "→", "propto": "∝",
}
FUNCS = {"min", "max", "clamp", "exp", "ln", "log", "sin", "cos", "tan",
         "sqrt", "arg", "lim", "sup", "inf"}


def esc(t):
    return escape(t)


class _P:
    def __init__(self, s):
        self.s = s
        self.i = 0

    def eof(self):
        return self.i >= len(self.s)

    def peek(self, n=1):
        return self.s[self.i:self.i + n]

    def take(self, n=1):
        out = self.s[self.i:self.i + n]
        self.i += n
        return out

    def skip_ws(self):
        while self.i < len(self.s) and self.s[self.i] in " \t\r\n":
            self.i += 1


def run(text, upright=False):
    if not text:
        return ""
    rpr = '<m:rPr><m:sty m:val="p"/></m:rPr>' if upright else ""
    return '<m:r>%s<m:t xml:space="preserve">%s</m:t></m:r>' % (rpr, esc(text))


def frac(num, den):
    return "<m:f><m:fPr><m:type m:val=\"bar\"/></m:fPr><m:num>%s</m:num><m:den>%s</m:den></m:f>" % (num, den)


def sqrt(body, deg=None):
    if deg:
        return ("<m:rad><m:radPr><m:degHide m:val=\"0\"/></m:radPr>"
                "<m:deg>%s</m:deg><m:e>%s</m:e></m:rad>" % (deg, body))
    return ("<m:rad><m:radPr><m:degHide m:val=\"1\"/></m:radPr>"
            "<m:deg/><m:e>%s</m:e></m:rad>" % body)


def delim(body, beg="(", end=")"):
    return ("<m:d><m:dPr><m:begChr m:val=\"%s\"/><m:endChr m:val=\"%s\"/>"
            "<m:grow m:val=\"1\"/></m:dPr><m:e>%s</m:e></m:d>" % (esc(beg), esc(end), body))


def sub(base, s):
    return "<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>" % (base, s)


def sup(base, s):
    return "<m:sSup><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>" % (base, s)


def subsup(base, sb, sp):
    return ("<m:sSubSup><m:e>%s</m:e><m:sub>%s</m:sub><m:sup>%s</m:sup></m:sSubSup>"
            % (base, sb, sp))


def parse_group(p, stop=None, stop_right=False):
    """Parse until a closing brace (if stop='}') or end; return xml."""
    out = []
    buf = []

    def flush():
        if buf:
            out.append(run("".join(buf)))
            buf.clear()

    while not p.eof():
        if stop is not None and p.peek() == stop:
            flush()
            return "".join(out)
        if stop_right and p.s.startswith("\\right", p.i):
            flush()
            return "".join(out)
        c = p.peek()
        if p.s.startswith("\\left", p.i):
            flush()
            p.i += 5
            p.skip_ws()
            beg = p.take()
            body = parse_group(p, None, stop_right=True)
            # consume \right
            if p.s.startswith("\\right", p.i):
                p.i += 6
                p.skip_ws()
                end = p.take()
            else:
                end = "."
            out.append(delim(body, "" if beg == "." else beg, "" if end == "." else end))
            continue
        if c == "\\":
            flush()
            item, is_atom = parse_command(p)
            if item is None:
                continue
            out.append(item)
        elif c == "{":
            flush()
            p.take()
            inner = parse_group(p, "}")
            p.take()  # }
            out.append(inner)
        elif c == "}":
            flush()
            p.take()
            out.append(run("}"))
        elif c in "^_":
            flush()
            # script applies to the last atom
            p.take()
            script = parse_script_arg(p)
            base = out.pop() if out else ""
            if c == "^":
                out.append(sup(base, script))
            else:
                out.append(sub(base, script))
        elif c in " \t\r\n":
            p.take()
            continue
        else:
            buf.append(p.take())
    flush()
    return "".join(out)


def parse_script_arg(p):
    p.skip_ws()
    if p.eof():
        return ""
    c = p.peek()
    if c == "{":
        p.take()
        inner = parse_group(p, "}")
        p.take()
        return inner
    if c == "\\":
        item, _ = parse_command(p)
        return item or ""
    return run(p.take())


def _brace_arg(p):
    p.skip_ws()
    if p.peek() != "{":
        # single token
        return parse_script_arg(p)
    p.take()
    inner = parse_group(p, "}")
    p.take()
    return inner


def _brace_raw(p):
    """Return raw text inside braces (no math parsing)."""
    p.skip_ws()
    if p.peek() != "{":
        c = p.take()
        return c
    p.take()
    start = p.i
    depth = 1
    while not p.eof():
        c = p.take()
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return p.s[start:p.i - 1]
    return p.s[start:]


def parse_command(p):
    p.take()  # backslash
    m = re.match(r"[A-Za-z]+", p.s[p.i:])
    if not m:
        c = p.take()
        if c in (";", ",", " ", ":", "\\"):
            return run(" "), True
        if c == "!":
            return None, False
        return run(c), True
    name = m.group(0)
    p.i += len(name)
    if name in ("frac", "dfrac", "tfrac"):
        num = _brace_arg(p)
        den = _brace_arg(p)
        return frac(num, den), True
    if name == "sqrt":
        if p.peek() == "[":
            p.take()
            j = p.s.find("]", p.i)
            deg = p.s[p.i:j]
            p.i = j + 1
            body = _brace_arg(p)
            return sqrt(body, deg), True
        return sqrt(_brace_arg(p)), True
    if name in ("text", "mathrm", "operatorname"):
        raw = _brace_raw(p)
        if name == "text":
            return run(raw, upright=True), True
        return run(raw, upright=True), True
    if name == "mathit":
        raw = _brace_raw(p)
        return run(raw, upright=False), True
    if name in ("left", "right"):
        ch = p.take()
        return ("\x00" + ch), False
    if name in ("!",):
        return None, False
    if name in (" ", ",", ";", ":", "quad", "qquad"):
        n = {" ": 1, ",": 1, ";": 2, ":": 1, "quad": 3, "qquad": 6}[name]
        return run(" " * n), False
    if name in GREEK:
        return run(GREEK[name]), True
    if name in OPS:
        return run(OPS[name]), True
    if name in FUNCS:
        return run(name, upright=True), True
    if name in ("dot", "hat", "bar", "tilde", "widetilde", "widehat"):
        body = _brace_arg(p)
        acc = {"dot": "\u0307", "hat": "\u0302", "bar": "\u0304",
               "tilde": "\u0303", "widetilde": "\u0303", "widehat": "\u0302"}[name]
        return _accent(body, acc), True
    return run("\\" + name), True


def _accent(body, acc):
    m = re.match(r'<m:r><m:t xml:space="preserve">(.)</m:t></m:r>(.*)', body, re.S)
    if m:
        return ('<m:acc><m:accPr><m:chr m:val="%s"/></m:accPr><m:e>%s</m:e></m:acc>'
                % (acc, body))
    return body


def parse(s):
    p = _P(s)
    xml = parse_group(p)
    return merge_runs(xml)


_MERGE = re.compile(
    r'(<m:r><m:t xml:space="preserve">)([^<]*)(</m:t></m:r>)(<m:r><m:t xml:space="preserve">)([^<]*)(</m:t></m:r>)'
)
_MERGE_P = re.compile(
    r'(<m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t xml:space="preserve">)([^<]*)'
    r'(</m:t></m:r>)(<m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t xml:space="preserve">)([^<]*)'
    r'(</m:t></m:r>)'
)


def merge_runs(xml):
    prev = None
    while prev != xml:
        prev = xml
        xml = _MERGE.sub(lambda m: m.group(1) + m.group(2) + m.group(5) + m.group(3), xml)
        xml = _MERGE_P.sub(lambda m: m.group(1) + m.group(2) + m.group(5) + m.group(3), xml)
    return xml


def set_size(xml, half_points):
    """Force an explicit font size on every math run (half points)."""
    wpr = ('<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/>'
           '<w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr>' % (half_points, half_points))
    xml = re.sub(r"(<m:r><m:rPr>.*?</m:rPr>)", lambda m: m.group(1) + wpr, xml, flags=re.S)
    xml = re.sub(r"(<m:r>)(<m:t)", lambda m: m.group(1) + wpr + m.group(2), xml)
    return xml


def omath(latex, display=False, size=None):
    body = parse(latex)
    if size:
        body = set_size(body, size)
    tag = "oMathPara" if display else "oMath"
    if display:
        return ('<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
                '<m:oMath>%s</m:oMath></m:oMathPara>' % body)
    return OMML_OPEN + body + OMML_CLOSE


def norm_fractions(xml):
    return xml
