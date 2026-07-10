import os
import tempfile
from pathlib import Path

from app.core.logger import get_logger


logger = get_logger(__name__)


def bytes_to_mb(value: int) -> float:
    return round(value / (1024 ** 2), 1)


def _path_status(path: Path) -> str:
    if not path.exists():
        return "Não encontrado"

    try:
        next(iter(path.iterdir()), None)
        return "Disponível"
    except PermissionError:
        return "Sem acesso"
    except OSError as exc:
        logger.info("Caminho indisponivel para analise: %s (%s)", path, exc)
        return "Sem acesso"


def _safe_file_size(path: Path) -> int:
    try:
        if path.is_file():
            return path.stat().st_size
    except PermissionError:
        logger.info("Arquivo ignorado por permissao: %s", path)
    except OSError as exc:
        logger.info("Arquivo ignorado por erro de acesso: %s (%s)", path, exc)

    return 0


def _safe_directory_size(path: Path, pattern: str = "*") -> int:
    if _path_status(path) != "Disponível":
        return 0

    total = 0

    try:
        iterator = path.rglob(pattern)
        for item in iterator:
            total += _safe_file_size(item)
    except PermissionError:
        logger.info("Pasta ignorada por permissao: %s", path)
    except OSError as exc:
        logger.info("Pasta ignorada por erro de acesso: %s (%s)", path, exc)
    except Exception as exc:
        logger.exception("Falha inesperada ao analisar pasta %s: %s", path, exc)

    return total


def _build_category(nome: str, path: Path, pattern: str = "*") -> dict:
    status = _path_status(path)
    size_bytes = _safe_directory_size(path, pattern) if status == "Disponível" else 0

    return {
        "nome": nome,
        "caminho": str(path),
        "status": status,
        "tamanho_mb": bytes_to_mb(size_bytes),
    }


def scan_cleaning_preview() -> list[dict]:
    logger.info("Analisando previa de limpeza segura.")

    user_temp = Path(tempfile.gettempdir())
    windows_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    local_app_data_value = os.environ.get("LOCALAPPDATA")
    local_app_data = Path(local_app_data_value) if local_app_data_value else Path("__localappdata_nao_encontrado__")

    categories = [
        _build_category("TEMP do usuário", user_temp),
        _build_category("TEMP do Windows", windows_root / "Temp"),
        _build_category(
            "Cache de miniaturas",
            local_app_data / "Microsoft" / "Windows" / "Explorer",
            "thumbcache*.db",
        ),
        _build_category("Prefetch", windows_root / "Prefetch"),
    ]

    return categories
