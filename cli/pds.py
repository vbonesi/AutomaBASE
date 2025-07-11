import re                # ← nova linha
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
_EXTRA_KV = re.compile(r"^([A-Z0-9_]+)=(.+)$")

@app.command("new")
def cli_new(
    id:      str = typer.Option(..., "--id"),
    tac:     str = typer.Option(..., "--tac"),
    tpeqp:   str = typer.Option(..., "--tpeqp"),
    nome:    str = typer.Option(..., "--nome"),
    ocr:     str = typer.Option(..., "--ocr"),
    tipo:    str = typer.Option("OUTROS", "--tipo"),
    extra:   list[str] = typer.Option(None, "--extra", "-e",
                help="Pares ATRIBUTO=VALOR adicionais, pode repetir"),
) -> None:
    _load_schema()

    # -------- obrigatórios absolutos ------------
    attrs = {
        "ID": id, "TAC": tac, "TPEQP": tpeqp,
        "OCR": ocr, "NOME": nome,
        "TIPO": tipo,
    }

    # -------- campos estrela (defaults) ---------
    for key in _STAR_FIELDS:
        attrs[key] = str(Pds._schema[key].get("default", ""))

    # -------- aplica extras do usuário ----------
    if extra:
        for kv in extra:
            m = _EXTRA_KV.match(kv)
            if not m:
                print(f"[red]Formato inválido para --extra: {kv}")
                raise typer.Exit(1)
            k, v = m.group(1).upper(), m.group(2)
            attrs[k] = v

    # -------- valida e grava --------------------
    p = Pds(attrs)
    errs = p.validate()
    if errs:
        print("[red]Não foi possível gerar pds.dat:")
        for e in errs:
            print(f" • {e}")
        raise typer.Exit(1)

    Path("pds.dat").write_text(p.to_dat(), encoding="utf-8")
    print("[green]Arquivo pds.dat criado/atualizado!")