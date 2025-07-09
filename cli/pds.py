from pathlib import Path
import typer
from rich import print

from core.pds import Pds

app = typer.Typer(
    help="AutomaBASE – operações para a entidade PDS",
    add_completion=False,
)

# Caminho fixo para o schema YAML
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "pds.yaml"


def _load_schema() -> None:
    """Carrega e armazena o schema em cache dentro de Pds."""
    Pds.load_schema(SCHEMA_PATH)


# --------------------------------------------------------------------------- #
# COMANDO: validate                                                           #
# --------------------------------------------------------------------------- #
@app.command("validate")
def cli_validate(
    file: Path = typer.Argument(
        ..., exists=True, readable=True, help="Arquivo .dat a validar"
    )
) -> None:
    """
    Valida um arquivo **pds.dat** contra o schema YAML.

    Exemplo:

        poetry run autobase validate examples/pds.dat
    """
    _load_schema()
    text = file.read_text(encoding="utf-8")
    p = Pds.from_dat(text)

    errors = p.validate()
    if errors:
        print(f"[red]Erro(s) encontrado(s) ({len(errors)}):[/]")
        for err in errors:
            print(f"  • {err}")
        raise typer.Exit(code=1)

    print("[green]✔ Arquivo válido")


# --------------------------------------------------------------------------- #
# COMANDO: new                                                                #
# --------------------------------------------------------------------------- #
@app.command("new")             #  ← decorador que faltava
def cli_new(
    id:  str = typer.Option(..., "--id", "-i", help="ID do ponto"),
    tac: str = typer.Option(..., "--tac", "-t", help="TAC destino"),
    tipo: str = typer.Option("OUTROS", "--tipo", "-y"),
) -> None:
    """
    Gera um arquivo **pds.dat** (nome fixo) contendo todos os defaults.
    """
    _load_schema()

    # ---------- aplica defaults ----------
    attrs = {"ID": id, "TAC": tac, "TIPO": tipo}
    for key, rule in Pds._schema.items():
        if key not in attrs and "default" in rule:
            attrs[key] = str(rule["default"])

    p = Pds(attrs)

    # ---------- valida antes de gravar ----------
    errs = p.validate()
    if errs:
        print("[red]Não foi possível gerar pds.dat:")
        for e in errs:
            print(" •", e)
        raise typer.Exit(1)

    Path("pds.dat").write_text(p.to_dat(), encoding="utf-8")
    print("[green]Arquivo pds.dat criado/atualizado!")
