from pathlib import Path
import typer, rich
from core.pds import Pds

app = typer.Typer()

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "pds.yaml"

def _load():
    Pds.load_schema(SCHEMA_PATH)

@app.command()
def validate(file: Path):
    """Valida um arquivo pds.dat"""
    _load()
    text = file.read_text(encoding="utf-8")
    p = Pds.from_dat(text)
    errs = p.validate()
    if errs:
        rich.print(f"[red]Erros:[/]\n - " + "\n - ".join(errs))
        raise typer.Exit(code=1)
    rich.print("[green]✔ Arquivo válido")

@app.command()
def new(id: str, tac: str, tipo: str = "OUTROS", out: Path = Path("pds.dat")):
    """Gera um pds.dat mínimo"""
    _load()
    p = Pds({"ID": id, "TAC": tac, "TIPO": tipo})
    out.write_text(p.to_dat(), encoding="utf-8")
    rich.print(f"[green]Arquivo criado em {out}")
