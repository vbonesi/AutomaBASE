from pathlib import Path
import re, typer
from rich import print
from core.pdf import Pdf

app = typer.Typer(add_completion=False)
SCHEMA = Path(__file__).resolve().parent.parent / "schemas" / "pdf.yaml"
_EXTRA = re.compile(r"^([A-Z0-9_]+)=(.+)$")
_STAR  = ["ORDEM", "KCONV"]

def _load(): Pdf.load_schema(SCHEMA)

@app.command("validate")
def validate(file: Path):
    _load()
    text = file.read_text()
    p = Pdf.from_dat(text)
    errs = p.validate()
    if errs:
        print("[red]Erros:"); [print(" •", e) for e in errs]; raise typer.Exit(1)
    print("[green]✔ válido")

@app.command("new")
def new(
    id:   str = typer.Option(..., "--id"),
    nv2:  str = typer.Option(..., "--nv2"),
    extra: list[str] = typer.Option(None, "--extra", "-e"),
):
    _load()
    attrs = {"ID": id, "NV2": nv2}
    for k in _STAR:
        attrs[k] = str(Pdf._schema[k]["default"])
    if extra:
        for kv in extra:
            m = _EXTRA.match(kv)
            if not m: print(f"[red]--extra inválido: {kv}"); raise typer.Exit(1)
            attrs[m[1].upper()] = m[2]
    p = Pdf(attrs); errs = p.validate()
    if errs: [print(" •", e) for e in errs]; raise typer.Exit(1)
    Path("pdf.dat").write_text(p.to_dat())
    print("[green]pdf.dat criado")
