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

    # ---------- validação simples ----------
    def validate(self) -> list[str]:
        errors: list[str] = []
        for key, rule in self._schema.items():
            req = rule.get("required")
            if req == "always" and key not in self.attrs:
                errors.append(f"{key} obrigatório não informado")
            if key in self.attrs and "enum" in rule:
                allowed = [v.strip() for v in rule["enum"]]
                if self.attrs[key] not in allowed:
                    errors.append(f"{key}='{self.attrs[key]}' fora de domínio {allowed}")
        return errors

    # ---------- impressor ----------
    def to_dat(self) -> str:
        lines = ["PDS"]
        for k, v in self.attrs.items():
            lines.append(f"   {k:<8}= {v}")
        lines.append(";")
        return "\n".join(lines)
