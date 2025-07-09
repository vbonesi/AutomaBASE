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
@app.command("new")
def cli_new(
    id: str = typer.Option(..., "--id", "-i", help="ID do ponto"),
    tac: str = typer.Option(..., "--tac", "-t", help="TAC a que o ponto pertence"),
    tipo: str = typer.Option(
        "OUTROS",
        "--tipo",
        "-y",
        help="TIPO do ponto (enum; padrão = OUTROS)",
        show_default=True,
    ),
    output: Path = typer.Option(
        Path("pds.dat"),
        "--out",
        "-o",
        help="Caminho do arquivo de saída",
        show_default=True,
    ),
) -> None:
    """
    Gera um **pds.dat** mínimo contendo ID, TAC e TIPO.

    Exemplo:

        poetry run autobase new --id TESTE1 --tac TAC_EXEMPLO --tipo FLCN -o out.dat
    """
    _load_schema()

    p = Pds({"ID": id, "TAC": tac, "TIPO": tipo})

    # Valida antes de gravar – avisa mas não aborta caso existam alertas
    warn = p.validate()
    if warn:
        print("[yellow]Aviso: ponto gerado contém inconsistências:")
        for w in warn:
            print(f"  • {w}")

    output.write_text(p.to_dat(), encoding="utf-8")
    print(f"[green]Arquivo gerado em {output.resolve()}")

