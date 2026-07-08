from dataclasses import dataclass


@dataclass(frozen=True)
class OptimizationAction:
    id: str
    nome: str
    categoria: str
    descricao: str
    beneficio: str
    risco: str
    requer_admin: bool
    requer_confirmacao: bool
    reversivel: bool
