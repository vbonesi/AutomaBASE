# autobase/core/pdf.py

from pydantic import BaseModel, Field, validator
from typing import List

# Representa uma única linha (registro) no arquivo pdf.dat
# Os nomes dos campos devem corresponder ao seu schema YAML para facilitar.
class PdfRecord(BaseModel):
    pds_name: str = Field(alias="NOME_PDS")
    attribute_2: str # Adicione os outros atributos do PDF aqui
    # ...

    class Config:
        allow_population_by_field_name = True # Permite usar 'NOME_PDS' para popular 'pds_name'

# Representa a coleção de todos os PDSs, para validação.
# Usaremos apenas os nomes para a verificação de existência.
class PdsCollection:
    def __init__(self, records: List[BaseModel]): # Usamos BaseModel para ser genérico
        # Criamos um set para busca rápida (muito mais eficiente que percorrer uma lista)
        self.pds_names = {record.pds_name for record in records}

    def name_exists(self, pds_name: str) -> bool:
        return pds_name in self.pds_names

# --- FUNÇÕES PRINCIPAIS ---

def from_dat(file_content: str) -> List[PdfRecord]:
    """
    Converte o conteúdo de um arquivo pdf.dat (string) para uma lista de PdfRecord.
    A lógica de parsing do formato de colunas fixas entrará aqui.
    """
    # Lógica de parsing (a ser implementada)
    # Por enquanto, retornamos uma lista vazia para a estrutura existir.
    print("LOG: Parsing pdf.dat...")
    records = []
    # Exemplo de como seria:
    # for line in file_content.splitlines():
    #     if not line.strip(): continue
    #     pds_name = line[0:32].strip() # Exemplo de posições
    #     records.append(PdfRecord(NOME_PDS=pds_name, ...))
    return records


def to_dat(records: List[PdfRecord]) -> str:
    """
    Converte uma lista de PdfRecord de volta para o formato string de um pdf.dat.
    """
    # Lógica de formatação (a ser implementada)
    print("LOG: Gerando conteúdo para pdf.dat...")
    return ""


def validate(records: List[PdfRecord], pds_collection: PdsCollection) -> List[str]:
    """
    Valida uma lista de registros de PDF contra a coleção de PDS.
    Retorna uma lista de erros. Se a lista estiver vazia, a validação passou.
    """
    errors = []
    for i, record in enumerate(records, start=1):
        # **AQUI ACONTECE A VALIDAÇÃO CRUZADA!**
        if not pds_collection.name_exists(record.pds_name):
            error_msg = (
                f"Erro de integridade na linha {i} do PDF: "
                f"O PDS '{record.pds_name}' não existe na base de dados PDS."
            )
            errors.append(error_msg)

        # Outras validações específicas do PDF podem vir aqui...
        # ex: if not is_valid_format(record.some_field): ...

    return errors