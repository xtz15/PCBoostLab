import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.core.logger import get_logger


logger = get_logger(__name__)
CONFIRMATION_TOKEN = "confirmar-exclusao-segura"


def _is_valid_path_value(value: Any) -> bool:
    return isinstance(value, (str, os.PathLike)) and str(value).strip() != ""


def _absolute_path(value: Any) -> Path | None:
    if not _is_valid_path_value(value):
        return None

    try:
        path = Path(value)
    except (TypeError, OSError, RuntimeError):
        return None

    if not path.is_absolute():
        return None

    return path


def _resolve_absolute_path(path: Path) -> Path | None:
    try:
        return path.resolve(strict=False)
    except (TypeError, OSError, RuntimeError):
        return None


def _normalize_candidate_path(value: Any) -> Path | None:
    path = _absolute_path(value)
    return _resolve_absolute_path(path) if path is not None else None


def _normalize_candidate_root(value: Any) -> Path | None:
    root = _absolute_path(value)
    if root is None:
        return None

    if _has_link_or_junction_from_anchor(root):
        return None

    resolved_root = _resolve_absolute_path(root)
    if resolved_root is None:
        return None

    if not resolved_root.exists() or not resolved_root.is_dir():
        return None

    return resolved_root


def _is_symlink(path: Path) -> bool:
    try:
        return path.is_symlink()
    except (OSError, RuntimeError):
        return False


def _is_junction(path: Path) -> bool:
    if os.name != "nt" or not hasattr(os.path, "isjunction"):
        return False

    try:
        return os.path.isjunction(str(path))
    except (OSError, RuntimeError):
        return False


def _is_link_or_junction(path: Path) -> bool:
    return _is_symlink(path) or _is_junction(path)


def _path_exists_or_is_link(path: Path) -> bool:
    try:
        return path.exists() or _is_link_or_junction(path)
    except (OSError, RuntimeError):
        return _is_link_or_junction(path)


def _existing_components_from_anchor(path: Path) -> list[Path]:
    components = []
    current = Path(path.anchor)

    for part in path.parts[1:]:
        current = current / part
        if _path_exists_or_is_link(current):
            components.append(current)
        else:
            break

    return components


def _existing_components_between(root: Path, path: Path) -> list[Path]:
    try:
        relative_path = path.relative_to(root)
    except ValueError:
        return [path] if _path_exists_or_is_link(path) else []

    components = []
    current = root

    for part in relative_path.parts:
        current = current / part
        if _path_exists_or_is_link(current):
            components.append(current)
        else:
            break

    return components


def _has_link_or_junction_from_anchor(path: Path) -> bool:
    for component in _existing_components_from_anchor(path):
        if _is_link_or_junction(component):
            return True

    return False


def _has_link_or_junction_in_original_path(original_path: Path, original_root: Path) -> bool:
    for component in _existing_components_between(original_root, original_path):
        if _is_link_or_junction(component):
            return True

    return False


def _canonical_duplicate_key(path: Path) -> str:
    return os.path.normcase(os.path.normpath(str(path)))


def _safe_file_size(path: Path) -> int | None:
    try:
        return path.stat().st_size
    except (FileNotFoundError, PermissionError, OSError, RuntimeError) as exc:
        logger.info("Falha ao ler tamanho do arquivo: %s (%s)", path, exc)
        return None


def _build_empty_report(dry_run: bool = True) -> dict:
    return {
        "modo_simulacao": bool(dry_run),
        "solicitados": 0,
        "validos": 0,
        "excluidos": 0,
        "bytes_excluidos": 0,
        "bytes_simulados": 0,
        "simulados": 0,
        "ausentes": 0,
        "ignorados_fora_da_raiz": 0,
        "ignorados_caminho_relativo": 0,
        "ignorados_nao_arquivo": 0,
        "ignorados_link": 0,
        "falhas": 0,
        "recusado_por_confirmacao": 0,
        "duplicados": 0,
        "detalhes": [],
    }


def _detail(category: str, path: Any, result: str, reason: str, **extra) -> dict:
    detail = {
        "categoria": category,
        "caminho": str(path or ""),
        "resultado": result,
        "motivo": reason,
    }
    detail.update(extra)
    return detail


def _validate_final_unlink(
    original_path: Path,
    original_root: Path,
    expected_path: Path,
    expected_root: Path,
) -> tuple[bool, str, Path | None]:
    """Revalida o candidato imediatamente antes da exclusão real."""

    if not original_path.is_absolute() or not original_root.is_absolute():
        return False, "caminho_relativo", None

    if _has_link_or_junction_from_anchor(original_root):
        return False, "link_ou_junction", None

    if _has_link_or_junction_in_original_path(original_path, original_root):
        return False, "link_ou_junction", None

    current_root = _normalize_candidate_root(original_root)
    current_path = _normalize_candidate_path(original_path)

    if current_root is None or current_path is None:
        return False, "caminho_invalido", None

    if current_root != expected_root or current_path != expected_path:
        return False, "caminho_alterado", None

    try:
        current_path.relative_to(current_root)
    except ValueError:
        return False, "fora_da_raiz", None

    if not current_path.exists():
        return False, "arquivo_nao_encontrado", current_path

    if not current_path.is_file():
        return False, "nao_e_arquivo", current_path

    return True, "ok", current_path


def execute_cleaning_candidates(candidates, dry_run=True, confirmation_token=None):
    """Executa exclusão segura de arquivos individuais, apenas para candidatos explícitos.

    O motor é seguro por padrão e não exclui arquivos em modo simulação. Para exclusão real,
    é necessário passar dry_run=False e um token de confirmação exato.
    """

    report = _build_empty_report(dry_run=dry_run)

    seen_paths = set()
    for candidate in candidates or []:
        report["solicitados"] += 1

        if not isinstance(candidate, Mapping):
            report["falhas"] += 1
            report["detalhes"].append(
                _detail("Sem categoria", candidate, "falha", "candidato_malformado")
            )
            logger.info("Candidato ignorado: formato inválido")
            continue

        category = candidate.get("categoria") or "Sem categoria"
        raw_path = candidate.get("caminho")
        raw_root = candidate.get("raiz")

        if not _is_valid_path_value(raw_path):
            report["falhas"] += 1
            report["detalhes"].append(
                _detail(category, raw_path, "falha", "caminho_vazio")
            )
            logger.info("Candidato ignorado: caminho vazio para categoria %s", category)
            continue

        if not _is_valid_path_value(raw_root):
            report["falhas"] += 1
            report["detalhes"].append(
                _detail(category, raw_path, "falha", "raiz_vazia")
            )
            logger.info("Candidato ignorado: raiz vazia para categoria %s", category)
            continue

        original_path = _absolute_path(raw_path)
        original_root = _absolute_path(raw_root)
        path = _normalize_candidate_path(raw_path)
        root = _normalize_candidate_root(raw_root)

        if original_path is None or path is None:
            report["ignorados_caminho_relativo"] += 1
            report["detalhes"].append(
                _detail(category, raw_path, "ignorado", "caminho_relativo")
            )
            logger.info("Candidato ignorado: caminho relativo ou inválido para categoria %s", category)
            continue

        if original_root is None:
            report["falhas"] += 1
            report["detalhes"].append(
                _detail(category, raw_path, "falha", "raiz_invalida")
            )
            logger.info("Candidato ignorado: raiz inválida para categoria %s", category)
            continue

        if _has_link_or_junction_from_anchor(original_root):
            report["ignorados_link"] += 1
            report["detalhes"].append(
                _detail(category, original_root, "ignorado", "raiz_link_ou_junction")
            )
            logger.info("Candidato ignorado: raiz contém link ou junction para categoria %s", category)
            continue

        if root is None:
            report["falhas"] += 1
            report["detalhes"].append(
                _detail(category, raw_path, "falha", "raiz_invalida")
            )
            logger.info("Candidato ignorado: raiz inválida para categoria %s", category)
            continue

        if _has_link_or_junction_in_original_path(original_path, original_root):
            report["ignorados_link"] += 1
            report["detalhes"].append(
                _detail(category, original_path, "ignorado", "link_ou_junction")
            )
            logger.info("Candidato ignorado: link ou junction para categoria %s", category)
            continue

        try:
            path.relative_to(root)
        except ValueError:
            report["ignorados_fora_da_raiz"] += 1
            report["detalhes"].append(
                _detail(category, path, "ignorado", "fora_da_raiz")
            )
            logger.info("Candidato ignorado: arquivo fora da raiz autorizada para categoria %s", category)
            continue

        duplicate_key = _canonical_duplicate_key(path)
        if duplicate_key in seen_paths:
            report["duplicados"] += 1
            report["detalhes"].append(
                _detail(category, path, "duplicado", "duplicidade")
            )
            logger.info("Candidato duplicado ignorado: %s", path)
            continue
        seen_paths.add(duplicate_key)

        if not path.exists():
            report["ausentes"] += 1
            report["detalhes"].append(
                _detail(category, path, "ausente", "arquivo_nao_encontrado")
            )
            logger.info("Candidato ausente: %s", path)
            continue

        if not path.is_file():
            report["ignorados_nao_arquivo"] += 1
            report["detalhes"].append(
                _detail(category, path, "ignorado", "nao_e_arquivo")
            )
            logger.info("Candidato ignorado: não é um arquivo regular para categoria %s", category)
            continue

        if dry_run:
            size_bytes = _safe_file_size(path)
            if size_bytes is None:
                report["falhas"] += 1
                report["detalhes"].append(
                    _detail(category, path, "falha", "erro_leitura")
                )
                continue

            report["validos"] += 1
            report["simulados"] += 1
            report["bytes_simulados"] += size_bytes
            report["detalhes"].append(
                _detail(
                    category,
                    path,
                    "simulado",
                    "modo_simulacao",
                    tamanho_bytes=size_bytes,
                )
            )
            logger.info("Candidato simulado: %s", path)
            continue

        if confirmation_token != CONFIRMATION_TOKEN:
            report["recusado_por_confirmacao"] += 1
            report["detalhes"].append(
                _detail(category, path, "recusado", "confirmacao_invalida")
            )
            logger.info("Exclusao recusada por confirmacao para categoria %s", category)
            continue

        is_valid, reason, final_path = _validate_final_unlink(
            original_path,
            original_root,
            path,
            root,
        )
        if not is_valid:
            if reason == "link_ou_junction":
                report["ignorados_link"] += 1
                result = "ignorado"
            elif reason == "fora_da_raiz":
                report["ignorados_fora_da_raiz"] += 1
                result = "ignorado"
            elif reason == "arquivo_nao_encontrado":
                report["ausentes"] += 1
                result = "ausente"
            elif reason == "nao_e_arquivo":
                report["ignorados_nao_arquivo"] += 1
                result = "ignorado"
            else:
                report["falhas"] += 1
                result = "falha"

            report["detalhes"].append(
                _detail(category, final_path or path, result, f"revalidacao_{reason}")
            )
            logger.info("Exclusao recusada na revalidacao final: %s (%s)", path, reason)
            continue

        try:
            size_bytes = final_path.stat().st_size
        except (PermissionError, OSError, RuntimeError) as exc:
            report["falhas"] += 1
            report["detalhes"].append(
                _detail(category, final_path, "falha", "erro_leitura")
            )
            logger.info("Falha ao ler arquivo para exclusao: %s (%s)", final_path, exc)
            continue

        try:
            final_path.unlink()
        except FileNotFoundError:
            report["ausentes"] += 1
            report["detalhes"].append(
                _detail(category, final_path, "ausente", "arquivo_ausente_durante_exclusao")
            )
            logger.info("Arquivo desapareceu antes da exclusao: %s", final_path)
            continue
        except PermissionError as exc:
            report["falhas"] += 1
            report["detalhes"].append(
                _detail(category, final_path, "falha", "permissao")
            )
            logger.info("Falha de permissao ao excluir arquivo: %s (%s)", final_path, exc)
            continue
        except OSError as exc:
            report["falhas"] += 1
            report["detalhes"].append(
                _detail(category, final_path, "falha", "erro_exclusao")
            )
            logger.info("Falha inesperada ao excluir arquivo: %s (%s)", final_path, exc)
            continue

        if final_path.exists():
            report["falhas"] += 1
            report["detalhes"].append(
                _detail(category, final_path, "falha", "arquivo_permanente")
            )
            logger.info("Arquivo ainda existe depois da exclusao: %s", final_path)
            continue

        report["validos"] += 1
        report["excluidos"] += 1
        report["bytes_excluidos"] += size_bytes
        report["detalhes"].append(
            _detail(
                category,
                final_path,
                "excluido",
                "excluido",
                tamanho_bytes=size_bytes,
            )
        )
        logger.info("Exclusao concluida: %s", final_path)

    return report
