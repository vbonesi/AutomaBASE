from pathlib import Path
import re, typer
from rich import print
from core.pdd import Pdd

app = typer.Typer(add_completion=False)
SCHEMA = Path(__file__).resolve().parent.parent / "schemas" / "pdd.yaml"
_EXTRA  = re.compile(r"^([A-Z0-9_]+)=(.+)$")

def _load(): Pdd.load_schema(SCHEMA)

@app.command("validate")
def validate(file: Path):
    _load(); text=file.read_text()
    p=Pdd.from_dat(text); errs=p.validate()
    if errs: print("[red]Erros:");[print(" •",e) for e in errs]; raise typer.Exit(1)
    print("[green]✔ válido")

@app.command("new")
def new(
    id:  str = typer.Option(..., "--id"),
    pds: str = typer.Option(..., "--pds"),
    tdd: str = typer.Option(..., "--tdd"),
    extra: list[str] = typer.Option(None, "--extra", "-e"),
):
    _load()
    attrs = {"ID": id, "PDS": pds, "TDD": tdd}
    if extra:
        for kv in extra:
            m=_EXTRA.match(kv)
            if not m: print(f"[red]--extra inválido: {kv}"); raise typer.Exit(1)
            attrs[m[1].upper()] = m[2]
    p=Pdd(attrs); errs=p.validate()
    if errs: [print(" •",e) for e in errs]; raise typer.Exit(1)
    Path("pdd.dat").write_text(p.to_dat())
    print("[green]pdd.dat criado")
