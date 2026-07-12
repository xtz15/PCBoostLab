import ast
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.cleaning.executor import execute_cleaning_candidates
from app.cleaning.simulation import (
    iter_cleaning_candidates,
    simulate_cleaning_candidates,
    visible_report_details,
)


def make_category(name, root, status="Disponível", pattern="*"):
    return {
        "nome": name,
        "caminho": str(root),
        "status": status,
        "padrao": pattern,
    }


class CleaningSimulationTests(unittest.TestCase):
    def test_empty_selection_returns_empty_report(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            (root / "file.tmp").write_text("x", encoding="utf-8")

            report = simulate_cleaning_candidates([make_category("A", root)], set())

            self.assertTrue(report["modo_simulacao"])
            self.assertEqual(report["solicitados"], 0)

    def test_selected_available_category_generates_explicit_candidate(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            file_path = root / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            candidates = list(iter_cleaning_candidates([make_category("A", root)], {"A"}))

            self.assertEqual(
                candidates,
                [{"categoria": "A", "caminho": str(file_path), "raiz": str(root)}],
            )

    def test_non_selected_category_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            (root / "file.tmp").write_text("x", encoding="utf-8")

            candidates = list(iter_cleaning_candidates([make_category("A", root)], {"B"}))

            self.assertEqual(candidates, [])

    def test_unavailable_category_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            (root / "file.tmp").write_text("x", encoding="utf-8")

            candidates = list(iter_cleaning_candidates([make_category("A", root, status="Sem acesso")], {"A"}))

            self.assertEqual(candidates, [])

    def test_specific_pattern_is_respected(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            pf_file = root / "layout.pf"
            pf_file.write_text("x", encoding="utf-8")
            (root / "other.txt").write_text("x", encoding="utf-8")

            candidates = list(iter_cleaning_candidates([make_category("Prefetch", root, pattern="*.pf")], {"Prefetch"}))

            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0]["caminho"], str(pf_file))

    def test_other_extension_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            (root / "other.txt").write_text("x", encoding="utf-8")

            candidates = list(iter_cleaning_candidates([make_category("Prefetch", root, pattern="*.pf")], {"Prefetch"}))

            self.assertEqual(candidates, [])

    def test_file_in_subfolder_is_included(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            subfolder = root / "sub"
            subfolder.mkdir()
            file_path = subfolder / "file.tmp"
            file_path.write_text("x", encoding="utf-8")

            candidates = list(iter_cleaning_candidates([make_category("A", root)], {"A"}))

            self.assertEqual(candidates[0]["caminho"], str(file_path))

    def test_directory_is_not_included(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            (root / "sub").mkdir()

            candidates = list(iter_cleaning_candidates([make_category("A", root)], {"A"}))

            self.assertEqual(candidates, [])

    def test_two_categories_generate_candidates(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            base = Path(temp_dir_name)
            root_a = base / "a"
            root_b = base / "b"
            root_a.mkdir()
            root_b.mkdir()
            (root_a / "a.tmp").write_text("a", encoding="utf-8")
            (root_b / "b.tmp").write_text("b", encoding="utf-8")

            candidates = list(
                iter_cleaning_candidates(
                    [make_category("A", root_a), make_category("B", root_b)],
                    {"A", "B"},
                )
            )

            self.assertEqual(len(candidates), 2)

    def test_invalid_root_is_ignored(self):
        category = {"nome": "A", "caminho": "relative", "status": "Disponível", "padrao": "*"}

        candidates = list(iter_cleaning_candidates([category], {"A"}))

        self.assertEqual(candidates, [])

    def test_item_oserror_does_not_stop_next_item(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            first = root / "a.tmp"
            second = root / "b.tmp"
            first.write_text("a", encoding="utf-8")
            second.write_text("b", encoding="utf-8")

            original_is_file = Path.is_file

            def flaky_is_file(path):
                if path == first:
                    raise OSError("falha simulada")
                return original_is_file(path)

            with patch("pathlib.Path.is_file", flaky_is_file):
                candidates = list(iter_cleaning_candidates([make_category("A", root)], {"A"}))

            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0]["caminho"], str(second))

    def test_public_simulation_does_not_accept_dry_run(self):
        with self.assertRaises(TypeError):
            simulate_cleaning_candidates([], set(), dry_run=False)

    def test_public_simulation_does_not_accept_confirmation_token(self):
        with self.assertRaises(TypeError):
            simulate_cleaning_candidates([], set(), confirmation_token="token")

    def test_simulation_never_deletes_file(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            file_path = root / "file.tmp"
            file_path.write_text("abc", encoding="utf-8")

            report = simulate_cleaning_candidates([make_category("A", root)], {"A"})

            self.assertTrue(file_path.exists())
            self.assertTrue(report["modo_simulacao"])
            self.assertEqual(report["excluidos"], 0)
            self.assertEqual(report["bytes_excluidos"], 0)
            self.assertEqual(report["bytes_simulados"], 3)

    def test_executor_accepts_generator_and_counts_requested(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            root = Path(temp_dir_name)
            first = root / "a.tmp"
            second = root / "b.tmp"
            first.write_text("a", encoding="utf-8")
            second.write_text("bb", encoding="utf-8")

            def candidates():
                yield {"categoria": "A", "caminho": str(first), "raiz": str(root)}
                yield {"categoria": "A", "caminho": str(second), "raiz": str(root)}

            report = execute_cleaning_candidates(candidates(), dry_run=True)

            self.assertEqual(report["solicitados"], 2)
            self.assertEqual(report["simulados"], 2)
            self.assertEqual(report["bytes_simulados"], 3)

    def test_visible_detail_limit_does_not_change_totals(self):
        report = {
            "solicitados": 105,
            "simulados": 105,
            "bytes_simulados": 105,
            "detalhes": [{"resultado": "simulado", "motivo": "modo_simulacao"} for _ in range(105)],
        }

        visible = visible_report_details(report, limit=100)

        self.assertEqual(len(visible["detalhes_visiveis"]), 100)
        self.assertEqual(visible["detalhes_omitidos"], 5)
        self.assertEqual(report["solicitados"], 105)
        self.assertEqual(report["bytes_simulados"], 105)


class CleaningSimulationArchitectureTests(unittest.TestCase):
    def test_main_uses_only_safe_simulation_backend(self):
        main_path = Path("app/main.py")
        tree = ast.parse(main_path.read_text(encoding="utf-8"))

        imported_names = set()
        forbidden_direct_calls = []
        dry_run_false_calls = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "execute_cleaning_candidates":
                    forbidden_direct_calls.append(node)

                for keyword in node.keywords:
                    if (
                        keyword.arg == "dry_run"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is False
                    ):
                        dry_run_false_calls.append(node)

        self.assertNotIn("CONFIRMATION_TOKEN", imported_names)
        self.assertIn("simulate_cleaning_candidates", imported_names)
        self.assertEqual(forbidden_direct_calls, [])
        self.assertEqual(dry_run_false_calls, [])


if __name__ == "__main__":
    unittest.main()
