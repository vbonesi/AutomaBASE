# tests/test_pdf.py

from pathlib import Path
import pytest

# CORREÇÃO AQUI: Importamos diretamente dos pacotes 'core'
from core import pds, pdf

# O resto do arquivo permanece o mesmo
EXAMPLES_PATH = Path("exemplos")
PDS_FILE = EXAMPLES_PATH / "pds.dat"
PDF_FILE = EXAMPLES_PATH / "pdf.dat"


def test_validacao_cruzada_pdf_pds_com_sucesso():
    """
    Testa se um arquivo pdf.dat válido é aprovado na validação
    cruzada contra um arquivo pds.dat.
    """
    # ETAPA 1: Preparação (Arrange)
    pds_content = PDS_FILE.read_text(encoding="latin-1")
    pdf_content = PDF_FILE.read_text(encoding="latin-1")

    assert pds_content, "Arquivo pds.dat de exemplo não encontrado ou vazio."
    assert pdf_content, "Arquivo pdf.dat de exemplo não encontrado ou vazio."

    pds_records = pds.from_dat(pds_content)
    pdf_records = pdf.from_dat(pdf_content)
    
    pds_collection = pdf.PdsCollection(pds_records)

    # ETAPA 2: Ação (Act)
    validation_errors = pdf.validate(pdf_records, pds_collection)

    # ETAPA 3: Verificação (Assert)
    assert not validation_errors, (
        f"Validação falhou inesperadamente. Erros encontrados: {validation_errors}"
    )