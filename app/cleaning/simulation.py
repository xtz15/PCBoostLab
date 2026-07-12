from pathlib import Path

from app.cleaning.executor import execute_cleaning_candidates
from app.core.logger import get_logger


logger = get_logger(__name__)
MAX_VISIBLE_DETAILS = 100


def _is_available_selected_category(category: dict, selected_names: set[str]) -> bool:
    return (
        category.get("nome") in selected_names
        and category.get("status") == "Disponível"
        and bool(category.get("caminho"))
    )


def iter_cleaning_candidates(categories, selected_names):
    selected_names = set(selected_names or set())

    for category in categories or []:
        if not _is_available_selected_category(category, selected_names):
            continue

        name = category.get("nome") or "Sem categoria"
        pattern = category.get("padrao") or "*"

        try:
            root = Path(category.get("caminho"))
        except (TypeError, OSError, RuntimeError) as exc:
            logger.info("Categoria ignorada por caminho invalido: %s (%s)", name, exc)
            continue

        if not root.is_absolute() or not root.exists() or not root.is_dir():
            logger.info("Categoria ignorada por raiz indisponivel: %s", name)
            continue

        try:
            iterator = root.rglob(pattern)
            for item in iterator:
                try:
                    if not item.is_file():
                        continue
                except (PermissionError, OSError, RuntimeError) as exc:
                    logger.info("Item ignorado na simulacao: %s (%s)", item, exc)
                    continue

                yield {
                    "categoria": name,
                    "caminho": str(item),
                    "raiz": str(root),
                }
        except (PermissionError, OSError, RuntimeError) as exc:
            logger.info("Categoria ignorada por erro de acesso na simulacao: %s (%s)", name, exc)


def simulate_cleaning_candidates(categories, selected_names):
    candidates = iter_cleaning_candidates(categories, selected_names)
    return execute_cleaning_candidates(candidates, dry_run=True)


def visible_report_details(report: dict, limit: int = MAX_VISIBLE_DETAILS) -> dict:
    details = list(report.get("detalhes", []))
    visible = details[:limit]

    return {
        "detalhes_visiveis": visible,
        "detalhes_omitidos": max(len(details) - len(visible), 0),
    }
