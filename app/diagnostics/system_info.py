import platform
from datetime import datetime

import cpuinfo
import psutil

from app.core.logger import get_logger


logger = get_logger(__name__)


def bytes_to_gb(value: int, digits: int = 2) -> float:
    return round(value / (1024 ** 3), digits)


def collect_system_info() -> dict:
    logger.info("Coletando diagnostico basico do sistema.")

    try:
        cpu_name = cpuinfo.get_cpu_info().get("brand_raw", "Processador nao identificado")
    except Exception as exc:
        logger.exception("Falha ao coletar informacoes da CPU: %s", exc)
        cpu_name = "Processador nao identificado"

    try:
        ram = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=1)
    except Exception as exc:
        logger.exception("Falha ao coletar uso de CPU/RAM: %s", exc)
        ram = None
        cpu_usage = 0

    return {
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "cpu": {
            "nome": cpu_name,
            "nucleos_fisicos": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "uso_percentual": cpu_usage,
        },
        "ram": {
            "total_gb": bytes_to_gb(ram.total) if ram else 0,
            "disponivel_gb": bytes_to_gb(ram.available) if ram else 0,
            "uso_percentual": ram.percent if ram else 0,
        },
        "sistema": {
            "nome": platform.system(),
            "release": platform.release(),
            "versao": platform.version(),
            "descricao": f"{platform.system()} {platform.release()}",
        },
    }


def format_diagnostic_text(info: dict) -> str:
    return (
        f"CPU: {info['cpu']['nome']}\n"
        f"Nucleos fisicos: {info['cpu']['nucleos_fisicos']}\n"
        f"Threads: {info['cpu']['threads']}\n"
        f"Uso de CPU atual: {info['cpu']['uso_percentual']}%\n\n"
        f"RAM total: {info['ram']['total_gb']} GB\n"
        f"RAM em uso: {info['ram']['uso_percentual']}%\n"
        f"RAM disponivel: {info['ram']['disponivel_gb']} GB\n\n"
        f"Sistema: {info['sistema']['descricao']}\n"
        f"Versao: {info['sistema']['versao']}"
    )
