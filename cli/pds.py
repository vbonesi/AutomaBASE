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


_STAR_FIELDS = [
    "CDINIC", "STINI", "STNOR",
    "ALINT", "ALRIN", "ALRP", "INVRT", "SOEIN",
    "TCL", "TPFIL",
]

# --------------------------------------------------------------------------- #
# COMANDO: new                                                                #
# --------------------------------------------------------------------------- #
@app.command("new")
def cli_new(
    id:      str = typer.Option(..., "--id", help="ID do ponto"),
    tac:     str = typer.Option(..., "--tac", help="TAC destino"),
    tpeqp:   str = typer.Option(..., "--tpeqp", help="Tipo de equipamento"),
    nome:    str = typer.Option(..., "--nome", help="Descrição do ponto"),
    ocr:     str = typer.Option(..., "--ocr",  help="Identificador OCR (formato XXXXX01)"),
    tipo:    str = typer.Option("OUTROS", "--tipo"),
) -> None:
    # obrigatórios absolutos vêm do usuário
    attrs = {
        "ID": id,
        "TAC": tac,
        "TPEQP": tpeqp,
        "OCR": ocr,
        "NOME": nome,
    }

    # aplica defaults SOMENTE aos campos estrela
    for key in _STAR_FIELDS:
        rule = Pds._schema[key]
        attrs[key] = str(rule.get("default", ""))

    # o usuário ainda pode sobrescrever qualquer campo via --extra KEY=VAL (futuro)

    p = Pds(attrs)
