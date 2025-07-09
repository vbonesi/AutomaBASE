from pathlib import Path
from core.pds import Pds

def test_pds_ok():
    schema = Path(__file__).resolve().parent.parent / "schemas" / "pds.yaml"
    Pds.load_schema(schema)
    sample = Path(__file__).resolve().parent.parent / "examples" / "pds.dat"
    text = sample.read_text(encoding="utf-8")
    p = Pds.from_dat(text)
    assert p.validate() == []