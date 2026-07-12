import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.core.logger import get_logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
logger = get_logger(__name__)

REPORT_TITLE = "PCBoostLab — Relatório de Simulação de Limpeza Segura"
SIMULATION_NOTICE = "Este relatório é apenas uma simulação. Nenhum arquivo foi excluído."

SUMMARY_FIELDS = [
    ("modo_simulacao", "Modo de simulação"),
    ("solicitados", "Arquivos solicitados"),
    ("validos", "Candidatos válidos"),
    ("simulados", "Arquivos simulados"),
    ("bytes_simulados", "Bytes simulados"),
    ("ausentes", "Arquivos ausentes"),
    ("ignorados_fora_da_raiz", "Arquivos fora da raiz"),
    ("ignorados_caminho_relativo", "Caminhos relativos ignorados"),
    ("ignorados_nao_arquivo", "Itens que não são arquivos"),
    ("ignorados_link", "Links ou junctions ignorados"),
    ("duplicados", "Duplicados"),
    ("falhas", "Falhas"),
    ("excluidos", "Excluídos"),
    ("bytes_excluidos", "Bytes excluídos"),
]


def _format_bytes(size_bytes) -> str:
    try:
        value = int(size_bytes or 0)
    except (TypeError, ValueError):
        value = 0

    if value >= 1024 ** 3:
        return f"{value / (1024 ** 3):.2f} GB"
    if value >= 1024 ** 2:
        return f"{value / (1024 ** 2):.2f} MB"
    if value >= 1024:
        return f"{value / 1024:.2f} KB"
    return f"{value} bytes"


def _validate_simulation_report(report: dict) -> None:
    if not isinstance(report, dict):
        raise ValueError("Relatório de simulação inválido.")

    if report.get("modo_simulacao") is not True:
        raise ValueError("Relatório recusado: modo_simulacao deve ser True.")

    if int(report.get("excluidos", 0) or 0) != 0:
        raise ValueError("Relatório recusado: excluidos deve permanecer zero.")

    if int(report.get("bytes_excluidos", 0) or 0) != 0:
        raise ValueError("Relatório recusado: bytes_excluidos deve permanecer zero.")


def _safe_report_name(now: datetime, suffix: int = 0) -> str:
    base = f"limpeza_simulacao_{now:%Y%m%d_%H%M%S}"
    if suffix:
        base = f"{base}_{suffix:02d}"
    return f"{base}.txt"


def _unique_report_path(destination_dir: Path, now: datetime) -> Path:
    suffix = 0
    while True:
        candidate = destination_dir / _safe_report_name(now, suffix)
        if not candidate.exists():
            return candidate
        suffix += 1


def _build_report_content(report: dict, selected_names, generated_at: datetime) -> str:
    selected = sorted(str(name) for name in (selected_names or []))
    lines = [
        REPORT_TITLE,
        "",
        f"Data/hora da geração: {generated_at:%d/%m/%Y %H:%M:%S}",
        "",
        "AVISO:",
        SIMULATION_NOTICE,
        "",
        "Categorias selecionadas:",
    ]

    if selected:
        lines.extend(f"- {name}" for name in selected)
    else:
        lines.append("- Nenhuma categoria selecionada.")

    lines.extend(["", "Resumo:"])
    for key, label in SUMMARY_FIELDS:
        lines.append(f"- {label}: {report.get(key, 0)}")

    lines.append(f"- Tamanho simulado formatado: {_format_bytes(report.get('bytes_simulados', 0))}")

    lines.extend(["", "Detalhes dos resultados:"])
    details = list(report.get("detalhes", []) or [])
    if not details:
        lines.append("- Nenhum detalhe registrado.")
    else:
        for index, detail in enumerate(details, start=1):
            lines.extend(
                [
                    f"{index}. Resultado: {detail.get('resultado', '')}",
                    f"   Motivo: {detail.get('motivo', '')}",
                    f"   Categoria: {detail.get('categoria', '')}",
                    f"   Caminho: {detail.get('caminho', '')}",
                ]
            )
            if "tamanho_bytes" in detail:
                lines.append(f"   Tamanho em bytes: {detail.get('tamanho_bytes')}")

    lines.append("")
    return "\n".join(lines)


def _write_without_overwriting(final_path: Path, content: str) -> Path:
    temp_path = final_path.with_name(f".{final_path.stem}.{uuid4().hex}.tmp")

    try:
        temp_path.write_text(content, encoding="utf-8-sig")
        os.link(temp_path, final_path)
        return final_path
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError as exc:
            logger.info("Falha ao remover arquivo temporario de relatorio: %s (%s)", temp_path, exc)


def write_cleaning_simulation_report(report, selected_names, destination_dir=None) -> Path:
    _validate_simulation_report(report)

    destination = Path(destination_dir) if destination_dir is not None else REPORTS_DIR
    destination.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now()
    content = _build_report_content(report, selected_names, generated_at)

    while True:
        report_path = _unique_report_path(destination, generated_at)
        try:
            saved_path = _write_without_overwriting(report_path, content)
            logger.info("Relatorio de simulacao de limpeza gerado em: %s", saved_path)
            return saved_path
        except FileExistsError:
            continue
