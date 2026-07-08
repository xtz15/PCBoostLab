import time

import psutil

from app.core.logger import get_logger


logger = get_logger(__name__)


def _empty_process_info(process: psutil.Process) -> dict:
    return {
        "pid": process.pid,
        "nome": "Processo sem acesso",
        "ram_mb": 0.0,
        "cpu_percent": 0.0,
    }


def _read_process_info(process: psutil.Process) -> dict:
    try:
        with process.oneshot():
            memory_info = process.memory_info()
            name = process.name() or "Processo sem nome"
            cpu_percent = process.cpu_percent(interval=None)

        return {
            "pid": process.pid,
            "nome": name,
            "ram_mb": round(memory_info.rss / (1024 ** 2), 1),
            "cpu_percent": round(cpu_percent, 1),
        }
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess) as exc:
        logger.info("Processo ignorado por acesso indisponivel: PID %s (%s)", process.pid, exc)
        return _empty_process_info(process)
    except Exception as exc:
        logger.exception("Falha inesperada ao ler processo PID %s: %s", process.pid, exc)
        return _empty_process_info(process)


def collect_top_processes(limit: int = 10) -> dict:
    logger.info("Coletando processos com maior uso de RAM e CPU.")

    processes = list(psutil.process_iter())

    for process in processes:
        try:
            process.cpu_percent(interval=None)
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except Exception as exc:
            logger.exception("Falha ao preparar leitura de CPU do PID %s: %s", process.pid, exc)

    time.sleep(0.2)

    process_info = [_read_process_info(process) for process in processes]
    visible_processes = [
        item for item in process_info if item["ram_mb"] > 0 or item["cpu_percent"] > 0
    ]

    return {
        "por_ram": sorted(
            visible_processes,
            key=lambda item: item["ram_mb"],
            reverse=True,
        )[:limit],
        "por_cpu": sorted(
            visible_processes,
            key=lambda item: item["cpu_percent"],
            reverse=True,
        )[:limit],
    }
