import time

import psutil

from app.core.logger import get_logger


logger = get_logger(__name__)
IGNORED_PROCESS_NAMES = {"system idle process", "idle"}


def _is_ignored_process(pid: int, name: str = "") -> bool:
    return pid == 0 or name.strip().lower() in IGNORED_PROCESS_NAMES


def _normalize_cpu_percent(cpu_percent: float) -> float:
    logical_cpus = psutil.cpu_count(logical=True) or 1
    normalized = cpu_percent / logical_cpus
    return round(min(max(normalized, 0.0), 100.0), 1)


def _empty_process_info(process: psutil.Process) -> dict:
    return {
        "pid": process.pid,
        "nome": "Processo sem acesso",
        "ram_mb": 0.0,
        "cpu_percent": 0.0,
    }


def _read_process_info(process: psutil.Process) -> dict | None:
    if process.pid == 0:
        return None

    try:
        with process.oneshot():
            name = process.name() or "Processo sem nome"

            if _is_ignored_process(process.pid, name):
                return None

            memory_info = process.memory_info()
            cpu_percent = _normalize_cpu_percent(process.cpu_percent(interval=None))

        return {
            "pid": process.pid,
            "nome": name,
            "ram_mb": round(memory_info.rss / (1024 ** 2), 1),
            "cpu_percent": cpu_percent,
        }
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess) as exc:
        logger.info(
            "Processo ignorado por acesso indisponivel: PID %s (%s)",
            process.pid,
            exc,
        )
        return _empty_process_info(process)
    except Exception as exc:
        logger.exception("Falha inesperada ao ler processo PID %s: %s", process.pid, exc)
        return _empty_process_info(process)


def collect_top_processes(limit: int = 10, sample_interval: float = 0.5) -> dict:
    logger.info("Coletando processos com maior uso de RAM e CPU.")

    processes = [process for process in psutil.process_iter() if process.pid != 0]

    for process in processes:
        try:
            process.cpu_percent(interval=None)
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except Exception as exc:
            logger.exception("Falha ao preparar leitura de CPU do PID %s: %s", process.pid, exc)

    time.sleep(sample_interval)

    process_info = [_read_process_info(process) for process in processes]
    visible_processes = [
        item
        for item in process_info
        if item and (item["ram_mb"] > 0 or item["cpu_percent"] > 0)
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
