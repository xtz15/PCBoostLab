from pathlib import Path

from app.core.logger import get_logger
from app.diagnostics.system_info import collect_system_info


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
logger = get_logger(__name__)


def generate_diagnostic_report() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    info = collect_system_info()

    safe_timestamp = info["data_hora"].replace("/", "-").replace(":", "-").replace(" ", "_")
    report_path = REPORTS_DIR / f"diagnostico_{safe_timestamp}.txt"

    content = (
        "Relatorio de diagnostico - PCBoostLab\n"
        f"Data/hora: {info['data_hora']}\n\n"
        f"CPU: {info['cpu']['nome']}\n"
        f"Uso atual de CPU: {info['cpu']['uso_percentual']}%\n\n"
        f"RAM total: {info['ram']['total_gb']} GB\n"
        f"RAM disponivel: {info['ram']['disponivel_gb']} GB\n"
        f"Uso atual de RAM: {info['ram']['uso_percentual']}%\n\n"
        f"Sistema: {info['sistema']['descricao']}\n"
        f"Versao do sistema: {info['sistema']['versao']}\n"
    )

    report_path.write_text(content, encoding="utf-8")
    logger.info("Relatorio de diagnostico gerado em: %s", report_path)
    return report_path
