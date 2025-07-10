from pathlib import Path
from core.pdf import Pdf; from core.pdd import Pdd

def test_pdf_ok():
    Pdf.load_schema(Path("schemas/pdf.yaml"))
    text = Path("examples/pdf.dat").read_text()
    assert Pdf.from_dat(text).validate() == []

def test_pdd_ok():
    Pdd.load_schema(Path("schemas/pdd.yaml"))
    text = Path("examples/pdd.dat").read_text()
    assert Pdd.from_dat(text).validate() == []
