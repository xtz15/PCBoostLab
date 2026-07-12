import ast
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.reports.cleaning_report import write_cleaning_simulation_report


def make_report(**overrides):
    report = {
        "modo_simulacao": True,
        "solicitados": 2,
        "validos": 1,
        "simulados": 1,
        "bytes_simulados": 1536,
        "ausentes": 1,
        "ignorados_fora_da_raiz": 2,
        "ignorados_caminho_relativo": 3,
        "ignorados_nao_arquivo": 4,
        "ignorados_link": 5,
        "duplicados": 6,
        "falhas": 7,
        "excluidos": 0,
        "bytes_excluidos": 0,
        "detalhes": [
            {
                "resultado": "simulado",
                "motivo": "modo_simulacao",
                "categoria": "TEMP do usuário",
                "caminho": r"C:\Temp\arquivo-á.txt",
                "tamanho_bytes": 1536,
            },
            {
                "resultado": "ausente",
                "motivo": "arquivo_nao_encontrado",
                "categoria": "Cache de miniaturas",
                "caminho": r"C:\Temp\ausente.tmp",
            },
        ],
    }
    report.update(overrides)
    return report


class CleaningSimulationReportTests(unittest.TestCase):
    def read_report(self, path: Path) -> str:
        return path.read_text(encoding="utf-8-sig")

    def test_report_is_created_in_destination_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            destination = Path(temp_dir_name)

            report_path = write_cleaning_simulation_report(
                make_report(),
                {"TEMP do usuário"},
                destination_dir=destination,
            )

            self.assertTrue(report_path.exists())
            self.assertEqual(report_path.parent, destination)

    def test_filename_is_safe_for_windows(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            report_path = write_cleaning_simulation_report(make_report(), set(), destination_dir=temp_dir_name)

            self.assertRegex(
                report_path.name,
                r"^limpeza_simulacao_\d{8}_\d{6}(?:_\d{2})?\.txt$",
            )
            self.assertIsNone(re.search(r'[<>:"/\\|?*]', report_path.name))

    def test_notice_says_no_file_was_deleted(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            report_path = write_cleaning_simulation_report(make_report(), set(), destination_dir=temp_dir_name)

            content = self.read_report(report_path)

            self.assertIn("Este relatório é apenas uma simulação. Nenhum arquivo foi excluído.", content)

    def test_selected_categories_are_written(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            report_path = write_cleaning_simulation_report(
                make_report(),
                {"TEMP do usuário", "Prefetch"},
                destination_dir=temp_dir_name,
            )

            content = self.read_report(report_path)

            self.assertIn("- TEMP do usuário", content)
            self.assertIn("- Prefetch", content)

    def test_all_summary_totals_are_written(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            report_path = write_cleaning_simulation_report(make_report(), set(), destination_dir=temp_dir_name)

            content = self.read_report(report_path)

            expected_lines = [
                "Modo de simulação: True",
                "Arquivos solicitados: 2",
                "Candidatos válidos: 1",
                "Arquivos simulados: 1",
                "Bytes simulados: 1536",
                "Arquivos ausentes: 1",
                "Arquivos fora da raiz: 2",
                "Caminhos relativos ignorados: 3",
                "Itens que não são arquivos: 4",
                "Links ou junctions ignorados: 5",
                "Duplicados: 6",
                "Falhas: 7",
                "Excluídos: 0",
                "Bytes excluídos: 0",
            ]
            for line in expected_lines:
                self.assertIn(line, content)

    def test_formatted_simulated_size_is_written(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            report_path = write_cleaning_simulation_report(make_report(), set(), destination_dir=temp_dir_name)

            self.assertIn("Tamanho simulado formatado: 1.50 KB", self.read_report(report_path))

    def test_details_are_written(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            report_path = write_cleaning_simulation_report(make_report(), set(), destination_dir=temp_dir_name)

            content = self.read_report(report_path)

            self.assertIn("Resultado: simulado", content)
            self.assertIn("Motivo: modo_simulacao", content)
            self.assertIn("Categoria: TEMP do usuário", content)
            self.assertIn(r"C:\Temp\arquivo-á.txt", content)
            self.assertIn("Tamanho em bytes: 1536", content)

    def test_accents_are_written_readably(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            report_path = write_cleaning_simulation_report(
                make_report(),
                {"Área temporária"},
                destination_dir=temp_dir_name,
            )

            content = self.read_report(report_path)

            self.assertIn("Relatório de Simulação", content)
            self.assertIn("Área temporária", content)
            self.assertIn("arquivo-á.txt", content)

    def test_existing_file_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            destination = Path(temp_dir_name)
            first = write_cleaning_simulation_report(make_report(), set(), destination_dir=destination)
            first.write_text("conteudo original", encoding="utf-8-sig")

            second = write_cleaning_simulation_report(make_report(), set(), destination_dir=destination)

            self.assertNotEqual(first, second)
            self.assertEqual(first.read_text(encoding="utf-8-sig"), "conteudo original")

    def test_destination_dir_is_created(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            destination = Path(temp_dir_name) / "relatorios" / "limpeza"

            report_path = write_cleaning_simulation_report(make_report(), set(), destination_dir=destination)

            self.assertTrue(destination.exists())
            self.assertTrue(report_path.exists())

    def test_write_failure_does_not_create_final_report(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            destination = Path(temp_dir_name)

            with patch("pathlib.Path.write_text", side_effect=OSError("falha simulada")):
                with self.assertRaises(OSError):
                    write_cleaning_simulation_report(make_report(), set(), destination_dir=destination)

            self.assertEqual(list(destination.glob("*.txt")), [])

    def test_mode_false_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            with self.assertRaises(ValueError):
                write_cleaning_simulation_report(
                    make_report(modo_simulacao=False),
                    set(),
                    destination_dir=temp_dir_name,
                )

    def test_excluded_count_greater_than_zero_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            with self.assertRaises(ValueError):
                write_cleaning_simulation_report(
                    make_report(excluidos=1),
                    set(),
                    destination_dir=temp_dir_name,
                )

    def test_excluded_bytes_greater_than_zero_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            with self.assertRaises(ValueError):
                write_cleaning_simulation_report(
                    make_report(bytes_excluidos=1),
                    set(),
                    destination_dir=temp_dir_name,
                )

    def test_function_does_not_accept_dry_run(self):
        with self.assertRaises(TypeError):
            write_cleaning_simulation_report(make_report(), set(), dry_run=False)

    def test_function_does_not_accept_confirmation_token(self):
        with self.assertRaises(TypeError):
            write_cleaning_simulation_report(make_report(), set(), confirmation_token="token")

    def test_candidate_file_is_not_modified_or_deleted(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            candidate = temp_dir / "arquivo.txt"
            candidate.write_text("conteúdo original", encoding="utf-8")
            report = make_report(
                detalhes=[
                    {
                        "resultado": "simulado",
                        "motivo": "modo_simulacao",
                        "categoria": "TEMP",
                        "caminho": str(candidate),
                        "tamanho_bytes": candidate.stat().st_size,
                    }
                ]
            )

            write_cleaning_simulation_report(report, {"TEMP"}, destination_dir=temp_dir / "reports")

            self.assertTrue(candidate.exists())
            self.assertEqual(candidate.read_text(encoding="utf-8"), "conteúdo original")


class CleaningReportArchitectureTests(unittest.TestCase):
    def test_main_does_not_import_confirmation_token(self):
        tree = ast.parse(Path("app/main.py").read_text(encoding="utf-8"))
        imported_names = {
            alias.asname or alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }

        self.assertNotIn("CONFIRMATION_TOKEN", imported_names)

    def test_main_does_not_call_executor_directly(self):
        tree = ast.parse(Path("app/main.py").read_text(encoding="utf-8"))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "execute_cleaning_candidates"
        ]

        self.assertEqual(calls, [])

    def test_main_does_not_use_dry_run_false(self):
        tree = ast.parse(Path("app/main.py").read_text(encoding="utf-8"))
        dry_run_false_calls = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            for keyword in node.keywords:
                if (
                    keyword.arg == "dry_run"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is False
                ):
                    dry_run_false_calls.append(node)

        self.assertEqual(dry_run_false_calls, [])

    def test_report_module_does_not_import_cleaning_executor(self):
        tree = ast.parse(Path("app/reports/cleaning_report.py").read_text(encoding="utf-8"))
        imported_modules = [
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ]

        self.assertNotIn("app.cleaning.executor", imported_modules)


if __name__ == "__main__":
    unittest.main()
