"""Post-process docx: add continuous line numbering (journal requirement)."""
import sys
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

path = sys.argv[1]
doc = Document(path)
for section in doc.sections:
    sectPr = section._sectPr
    ln = sectPr.find(qn('w:lnNumType'))
    if ln is None:
        ln = OxmlElement('w:lnNumType')
        sectPr.append(ln)
    ln.set(qn('w:countBy'), '1')
    ln.set(qn('w:restart'), 'continuous')
doc.save(path)
print("line numbering added:", path)
