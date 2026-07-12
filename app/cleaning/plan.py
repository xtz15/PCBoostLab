import os
from pathlib import Path

from app.core.logger import get_logger


logger = get_logger(__name__)
MAX_VISIBLE_FILES = 100


def _normalize_path(path: str | os.PathLike[str]) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def _is_within_root(root_path: Path, candidate_path: Path) -> bool:
    try:
        candidate_path.relative_to(root_path)
        return True
    except ValueError:
        return False


def _is_valid_root(path: str | os.PathLike[str]) -> bool:
    if path is None:
        return False

    if isinstance(path, str) and not path.strip():
        return False

    try:
        original_path = Path(path)
    except (TypeError, OSError, RuntimeError):
        return False

    if not original_path.is_absolute():
        return False

    try:
        resolved_path = original_path.expanduser().resolve(strict=False)
    except (TypeError, OSError, RuntimeError):
        return False

    return resolved_path.exists() and resolved_path.is_dir()


def build_cleaning_plan(categories, selected_names):
    selected_categories = [
        category
        for category in categories
        if category.get("nome") in selected_names and category.get("status") == "Disponível"
    ]

    plan = {
        "categorias": [],
        "quantidade_arquivos": 0,
        "tamanho_total_bytes": 0,
        "tamanho_total_mb": 0.0,
        "arquivos_omitidos": 0,
        "modo_simulacao": True,
        "mensagem": "Modo simulação: nenhum arquivo foi excluído.",
    }

    remaining_slots = MAX_VISIBLE_FILES

    for category in selected_categories:
        if not _is_valid_root(category.get("caminho", "")):
            continue

        root_path = _normalize_path(category.get("caminho", ""))
        visible_files = []
        total_bytes = 0
        pattern = category.get("padrao") or "*"
        file_count = 0

        try:
            for item in root_path.rglob(pattern):
                try:
                    item_path = _normalize_path(item)
                except OSError as exc:
                    logger.info("Caminho ignorado na revisão de plano: %s (%s)", item, exc)
                    continue

                if not item_path.is_file():
                    continue

                if not _is_within_root(root_path, item_path):
                    continue

                try:
                    size_bytes = item_path.stat().st_size
                except PermissionError as exc:
                    logger.info("Arquivo ignorado por permissao no plano: %s (%s)", item_path, exc)
                    continue
                except OSError as exc:
                    logger.info("Arquivo ignorado por erro de acesso no plano: %s (%s)", item_path, exc)
                    continue

                file_count += 1
                total_bytes += size_bytes

                if remaining_slots > 0:
                    visible_files.append(
                        {
                            "caminho": str(item_path),
                            "tamanho_bytes": size_bytes,
                            "tamanho_mb": round(size_bytes / (1024 ** 2), 1),
                        }
                    )
                    remaining_slots -= 1
                else:
                    plan["arquivos_omitidos"] += 1
        except PermissionError as exc:
            logger.info("Categoria ignorada por permissao no plano: %s (%s)", root_path, exc)
        except OSError as exc:
            logger.info("Categoria ignorada por erro de acesso no plano: %s (%s)", root_path, exc)

        plan["quantidade_arquivos"] += file_count
        plan["tamanho_total_bytes"] += total_bytes
        plan["tamanho_total_mb"] = round(plan["tamanho_total_bytes"] / (1024 ** 2), 1)

        plan["categorias"].append(
            {
                "nome": category.get("nome"),
                "caminho": str(root_path),
                "arquivos": visible_files,
            }
        )

    return plan
