from dataclasses import dataclass, field
from pathlib import Path
import re, yaml

@dataclass
class Pds:
    """Modelo de um PDS: atributos livres + validação contra schema YAML."""
    attrs: dict[str, str] = field(default_factory=dict)
    _schema: dict[str, dict] = field(default_factory=dict, repr=False)

    # ---------- carregamento do schema ----------
    @classmethod
    def load_schema(cls, schema_path: Path):
        data = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        cls._schema = {k.upper(): v for k, v in data["attributes"].items()}

    # ---------- parser do arquivo .dat ----------
    @classmethod
    def from_dat(cls, text: str) -> "Pds":
        attrs: dict[str, str] = {}
        for line in text.splitlines():
            m = re.match(r"^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$", line)
            if m:
                attrs[m.group(1).upper()] = m.group(2)
        return cls(attrs)

    OCR_RE = re.compile(r"^[A-Z0-9]{1,23}01$")   # 2 dígitos finais “01”, total ≤ 25

    def validate(self) -> list[str]:
        errors = []
        schema = self._schema

        # obrigatórios absolutos + programa
        for key in ("ID", "TAC", "TPEQP", "NOME", "OCR"):
            if key not in self.attrs or not self.attrs[key]:
                errors.append(f"{key} obrigatório não informado")

        # valida OCR formato
        if "OCR" in self.attrs and not self.OCR_RE.fullmatch(self.attrs["OCR"]):
            errors.append("OCR deve ter 5 caracteres alfanuméricos + '01' (ex.: ABCDE01)")

        # regras do YAML (required, enum…)
        for key, rule in schema.items():
            if rule.get("required") == "always" and key not in self.attrs:
                errors.append(f"{key} obrigatório ausente")
            if key in self.attrs and "enum" in rule:
                allowed = rule["enum"]
                if self.attrs[key] not in allowed:
                    errors.append(f"{key}='{self.attrs[key]}' fora de domínio {allowed}")

        return errors

    ORDER_ABS   = ["ID", "TAC", "TPEQP", "OCR", "NOME"]
    ORDER_STAR  = ["CDINIC", "STINI", "STNOR",
                "ALINT", "ALRIN", "ALRP", "INVRT", "SOEIN",
                "TCL", "TPFIL"]

    def to_dat(self) -> str:
        def line(k): return f"   {k:<8}= {self.attrs[k]}"
        lines = ["PDS"]
        # 1) obrigatórios absolutos
        lines += [line(k) for k in ORDER_ABS if k in self.attrs]
        # 2) estrela
        lines += [line(k) for k in ORDER_STAR if k in self.attrs]
        # 3) quaisquer outros que o usuário tenha fornecido
        remaining = sorted(k for k in self.attrs if k not in ORDER_ABS+ORDER_STAR)
        lines += [line(k) for k in remaining]
        return "\n".join(lines) + "\n"
