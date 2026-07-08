import psutil

from app.core.logger import get_logger


logger = get_logger(__name__)


def bytes_to_gb(value: int) -> float:
    return round(value / (1024 ** 3), 1)


def collect_disks_info() -> list[dict]:
    logger.info("Coletando informacoes de discos e particoes.")

    disks = []

    try:
        partitions = psutil.disk_partitions(all=False)
    except Exception as exc:
        logger.exception("Falha ao listar particoes de disco: %s", exc)
        return disks

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except (PermissionError, OSError) as exc:
            logger.info(
                "Particao ignorada por acesso indisponivel: %s (%s)",
                partition.device,
                exc,
            )
            continue
        except Exception as exc:
            logger.exception("Falha ao ler uso da particao %s: %s", partition.device, exc)
            continue

        disks.append(
            {
                "unidade": partition.device or partition.mountpoint,
                "ponto_montagem": partition.mountpoint,
                "sistema_arquivos": partition.fstype or "Desconhecido",
                "total_gb": bytes_to_gb(usage.total),
                "usado_gb": bytes_to_gb(usage.used),
                "livre_gb": bytes_to_gb(usage.free),
                "percentual_usado": round(usage.percent, 1),
            }
        )

    return disks
