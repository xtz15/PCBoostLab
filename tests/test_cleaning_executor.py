import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.cleaning.executor import execute_cleaning_candidates


CONFIRMATION_TOKEN = "confirmar-exclusao-segura"


class CleaningExecutorTests(unittest.TestCase):
    def _assert_root_is_temporary(self, root: Path, temp_dir: Path) -> None:
        self.assertTrue(root.exists())
        self.assertTrue(root.is_dir())
        self.assertTrue(root.resolve().is_relative_to(temp_dir.resolve()))

    def _execute_real_delete(self, temp_dir: Path, root: Path, candidates):
        self._assert_root_is_temporary(root, temp_dir)
        return execute_cleaning_candidates(
            candidates,
            dry_run=False,
            confirmation_token=CONFIRMATION_TOKEN,
        )

    def _make_junction(self, junction_path: Path, target: Path) -> None:
        try:
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(junction_path), str(target)],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            self.skipTest("Junction creation not supported in this environment")

        if not hasattr(os.path, "isjunction") or not os.path.isjunction(str(junction_path)):
            self.skipTest("Junction detection not supported in this environment")

    def test_dry_run_is_default(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}]
            )

            self.assertTrue(report["modo_simulacao"])
            self.assertEqual(report["simulados"], 1)
            self.assertTrue(file_path.exists())

    def test_dry_run_does_not_delete_file(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertTrue(file_path.exists())
            self.assertEqual(report["excluidos"], 0)
            self.assertEqual(report["simulados"], 1)

    def test_dry_run_returns_valid_file_as_simulated(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("abc", encoding="utf-8")

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["validos"], 1)
            self.assertEqual(report["simulados"], 1)
            self.assertEqual(report["detalhes"][0]["resultado"], "simulado")

    def test_real_delete_without_token_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            self._assert_root_is_temporary(root, temp_dir)
            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
                dry_run=False,
            )

            self.assertTrue(file_path.exists())
            self.assertEqual(report["recusado_por_confirmacao"], 1)
            self.assertEqual(report["excluidos"], 0)
            self.assertFalse(report["modo_simulacao"])

    def test_real_delete_with_wrong_token_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            self._assert_root_is_temporary(root, temp_dir)
            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
                dry_run=False,
                confirmation_token="token-errado",
            )

            self.assertTrue(file_path.exists())
            self.assertEqual(report["recusado_por_confirmacao"], 1)

    def test_valid_file_is_deleted_with_correct_token(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("abc", encoding="utf-8")

            report = self._execute_real_delete(
                temp_dir,
                root,
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
            )

            self.assertFalse(file_path.exists())
            self.assertEqual(report["excluidos"], 1)
            self.assertEqual(report["bytes_excluidos"], 3)

    def test_other_files_remain_intact(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            kept_path = root / "keep.txt"
            file_path.write_text("abc", encoding="utf-8")
            kept_path.write_text("keep", encoding="utf-8")

            self._execute_real_delete(
                temp_dir,
                root,
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
            )

            self.assertFalse(file_path.exists())
            self.assertTrue(kept_path.exists())
            self.assertEqual(kept_path.read_text(encoding="utf-8"), "keep")

    def test_valid_file_in_subfolder_can_be_deleted(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            subfolder = root / "sub"
            subfolder.mkdir(parents=True)
            file_path = subfolder / "nested.tmp"
            file_path.write_text("ok", encoding="utf-8")

            report = self._execute_real_delete(
                temp_dir,
                root,
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
            )

            self.assertFalse(file_path.exists())
            self.assertEqual(report["excluidos"], 1)

    def test_file_outside_root_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            outside = temp_dir / "outside"
            outside.mkdir()
            file_path = outside / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["ignorados_fora_da_raiz"], 1)
            self.assertTrue(file_path.exists())

    def test_relative_path_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": "file.tmp", "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["ignorados_caminho_relativo"], 1)

    def test_tilde_path_is_rejected_as_non_absolute(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": "~/arquivo.tmp", "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["ignorados_caminho_relativo"], 1)

    def test_relative_root_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": "root"}],
                dry_run=True,
            )

            self.assertEqual(report["ignorados_caminho_relativo"], 0)
            self.assertEqual(report["ignorados_fora_da_raiz"], 0)
            self.assertEqual(report["falhas"], 1)

    def test_tilde_root_is_rejected_as_non_absolute(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": "~"}],
                dry_run=True,
            )

            self.assertEqual(report["falhas"], 1)
            self.assertEqual(report["detalhes"][0]["motivo"], "raiz_invalida")

    def test_empty_path_is_ignored(self):
        report = execute_cleaning_candidates([{"categoria": "TEMP", "caminho": "", "raiz": "/tmp"}], dry_run=True)
        self.assertEqual(report["falhas"], 1)

    def test_empty_root_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": ""}],
                dry_run=True,
            )

            self.assertEqual(report["falhas"], 1)

    def test_malformed_candidate_does_not_stop_batch(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            report = execute_cleaning_candidates(
                [
                    None,
                    "invalido",
                    ["lista"],
                    {"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)},
                ],
                dry_run=True,
            )

            self.assertEqual(report["falhas"], 3)
            self.assertEqual(report["simulados"], 1)

    def test_directory_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(root), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["ignorados_nao_arquivo"], 1)

    def test_missing_file_is_reported_as_absent(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            missing = root / "missing.tmp"

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(missing), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["ausentes"], 1)

    def test_duplicate_candidates_only_delete_once(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            report = self._execute_real_delete(
                temp_dir,
                root,
                [
                    {"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)},
                    {"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)},
                ],
            )

            self.assertEqual(report["duplicados"], 1)
            self.assertEqual(report["excluidos"], 1)

    def test_duplicate_candidates_with_case_difference_are_detected_on_windows(self):
        if os.name != "nt":
            self.skipTest("Case-insensitive duplicate test is Windows-specific")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "CaseFile.tmp"
            file_path.write_text("x", encoding="utf-8")

            report = self._execute_real_delete(
                temp_dir,
                root,
                [
                    {"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)},
                    {"categoria": "TEMP", "caminho": str(file_path).upper(), "raiz": str(root)},
                ],
            )

            self.assertEqual(report["duplicados"], 1)
            self.assertEqual(report["excluidos"], 1)

    def test_bytes_excluded_are_calculated_correctly(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("abc", encoding="utf-8")

            report = self._execute_real_delete(
                temp_dir,
                root,
                [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
            )

            self.assertEqual(report["bytes_excluidos"], 3)

    def test_two_valid_files_are_deleted(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            first = root / "a.tmp"
            second = root / "b.tmp"
            first.write_text("1", encoding="utf-8")
            second.write_text("22", encoding="utf-8")

            report = self._execute_real_delete(
                temp_dir,
                root,
                [
                    {"categoria": "TEMP", "caminho": str(first), "raiz": str(root)},
                    {"categoria": "TEMP", "caminho": str(second), "raiz": str(root)},
                ],
            )

            self.assertEqual(report["excluidos"], 2)
            self.assertFalse(first.exists())
            self.assertFalse(second.exists())

    def test_failure_in_one_candidate_does_not_stop_others(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            valid = root / "valid.tmp"
            valid.write_text("x", encoding="utf-8")
            outside = temp_dir / "outside"
            outside.mkdir()
            invalid = outside / "invalid.tmp"
            invalid.write_text("x", encoding="utf-8")

            report = self._execute_real_delete(
                temp_dir,
                root,
                [
                    {"categoria": "TEMP", "caminho": str(valid), "raiz": str(root)},
                    {"categoria": "TEMP", "caminho": str(invalid), "raiz": str(root)},
                ],
            )

            self.assertEqual(report["excluidos"], 1)
            self.assertEqual(report["ignorados_fora_da_raiz"], 1)
            self.assertFalse(valid.exists())
            self.assertTrue(invalid.exists())

    def test_dry_run_stat_failure_does_not_stop_next_candidate(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            first = root / "a.tmp"
            second = root / "b.tmp"
            first.write_text("1", encoding="utf-8")
            second.write_text("2", encoding="utf-8")

            with patch("app.cleaning.executor._safe_file_size", side_effect=[None, 1]):
                report = execute_cleaning_candidates(
                    [
                        {"categoria": "TEMP", "caminho": str(first), "raiz": str(root)},
                        {"categoria": "TEMP", "caminho": str(second), "raiz": str(root)},
                    ],
                    dry_run=True,
                )

            self.assertEqual(report["falhas"], 1)
            self.assertEqual(report["simulados"], 1)
            self.assertTrue(first.exists())
            self.assertTrue(second.exists())

    def test_final_revalidation_refuses_candidate_changed_before_unlink(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            self._assert_root_is_temporary(root, temp_dir)
            with patch(
                "app.cleaning.executor._validate_final_unlink",
                return_value=(False, "caminho_alterado", file_path),
            ):
                report = execute_cleaning_candidates(
                    [{"categoria": "TEMP", "caminho": str(file_path), "raiz": str(root)}],
                    dry_run=False,
                    confirmation_token=CONFIRMATION_TOKEN,
                )

            self.assertTrue(file_path.exists())
            self.assertEqual(report["falhas"], 1)
            self.assertEqual(report["excluidos"], 0)
            self.assertEqual(report["detalhes"][0]["motivo"], "revalidacao_caminho_alterado")

    def test_empty_list_returns_empty_report(self):
        report = execute_cleaning_candidates([], dry_run=True)
        self.assertEqual(report["solicitados"], 0)
        self.assertEqual(report["validos"], 0)
        self.assertEqual(report["detalhes"], [])

    def test_no_directories_are_removed(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            child_dir = root / "child"
            child_dir.mkdir()

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(child_dir), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertTrue(child_dir.exists())
            self.assertEqual(report["ignorados_nao_arquivo"], 1)

    def test_unselected_files_remain_intact(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            kept = root / "keep.tmp"
            kept.write_text("x", encoding="utf-8")

            report = execute_cleaning_candidates([], dry_run=True)

            self.assertTrue(kept.exists())
            self.assertEqual(report["solicitados"], 0)

    def test_symlink_is_ignored_when_supported(self):
        if os.name != "nt":
            self.skipTest("Symlink test is Windows-specific")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            target = root / "target.txt"
            target.write_text("x", encoding="utf-8")
            link_path = root / "link.txt"
            try:
                os.symlink(target, link_path)
            except (OSError, NotImplementedError, AttributeError):
                self.skipTest("Symlink creation not supported in this environment")

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(link_path), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["ignorados_link"], 1)
            self.assertTrue(link_path.exists())

    def test_junction_is_ignored_when_supported(self):
        if os.name != "nt":
            self.skipTest("Junction test is Windows-specific")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            target = root / "target"
            target.mkdir()
            junction_path = root / "junction"
            self._make_junction(junction_path, target)

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(junction_path), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["ignorados_link"], 1)
            self.assertTrue(junction_path.exists())

    def test_file_accessed_through_junction_is_ignored_when_supported(self):
        if os.name != "nt":
            self.skipTest("Junction test is Windows-specific")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            root = temp_dir / "root"
            root.mkdir()
            target = root / "target"
            target.mkdir()
            target_file = target / "file.tmp"
            target_file.write_text("x", encoding="utf-8")
            junction_path = root / "junction"
            self._make_junction(junction_path, target)

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(junction_path / "file.tmp"), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["ignorados_link"], 1)
            self.assertTrue(target_file.exists())

    def test_root_junction_is_ignored_when_supported(self):
        if os.name != "nt":
            self.skipTest("Junction test is Windows-specific")

        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            target = temp_dir / "target"
            target.mkdir()
            file_path = target / "file.tmp"
            file_path.write_text("x", encoding="utf-8")
            root = temp_dir / "root_junction"
            self._make_junction(root, target)

            report = execute_cleaning_candidates(
                [{"categoria": "TEMP", "caminho": str(root / "file.tmp"), "raiz": str(root)}],
                dry_run=True,
            )

            self.assertEqual(report["ignorados_link"], 1)
            self.assertTrue(file_path.exists())


if __name__ == "__main__":
    unittest.main()
