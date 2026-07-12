import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.cleaning import scan as cleaning_scan
from app.cleaning.plan import build_cleaning_plan
from app.main import PCBoostLabApp


class CleaningScanTests(unittest.TestCase):
    def test_build_category_includes_pattern_used_for_analysis(self):
        with TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "sample"
            target_dir.mkdir()
            (target_dir / "file.txt").write_text("conteudo", encoding="utf-8")

            category = cleaning_scan._build_category("Categoria teste", target_dir, pattern="*.pf")

            self.assertEqual(category["padrao"], "*.pf")

    def test_bytes_to_mb_converts_bytes_to_megabytes(self):
        self.assertEqual(cleaning_scan.bytes_to_mb(2_097_152), 2.0)

    def test_build_category_returns_basic_fields(self):
        with TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "sample"
            target_dir.mkdir()
            (target_dir / "file.txt").write_text("conteudo", encoding="utf-8")

            category = cleaning_scan._build_category("Categoria teste", target_dir)

            self.assertEqual(category["nome"], "Categoria teste")
            self.assertEqual(Path(category["caminho"]), target_dir)
            self.assertEqual(category["status"], "Disponível")
            self.assertIn("tamanho_mb", category)

    def test_build_category_includes_details_when_provided(self):
        with TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "sample"
            target_dir.mkdir()
            (target_dir / "file.txt").write_text("conteudo", encoding="utf-8")

            category = cleaning_scan._build_category(
                "Categoria teste",
                target_dir,
                detalhes={"oque_e": "Detalhes da categoria"},
            )

            self.assertEqual(category["oque_e"], "Detalhes da categoria")

    def test_build_category_counts_files_in_subfolders(self):
        with TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "sample"
            subfolder = target_dir / "sub"
            subfolder.mkdir(parents=True)
            (target_dir / "file1.txt").write_text("conteudo", encoding="utf-8")
            (subfolder / "file2.txt").write_text("mais conteudo", encoding="utf-8")

            category = cleaning_scan._build_category("Categoria teste", target_dir)

            self.assertEqual(category["quantidade_arquivos"], 2)

    def test_build_category_includes_file_count_key(self):
        with TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "sample"
            target_dir.mkdir()
            (target_dir / "file.txt").write_text("conteudo", encoding="utf-8")

            category = cleaning_scan._build_category("Categoria teste", target_dir)

            self.assertIn("quantidade_arquivos", category)


class CleaningSummaryTests(unittest.TestCase):
    def setUp(self):
        self.app = PCBoostLabApp.__new__(PCBoostLabApp)

    def test_should_show_file_count_only_for_available_categories(self):
        self.assertTrue(self.app.should_show_file_count({"status": "Disponível", "quantidade_arquivos": 3}))
        self.assertFalse(self.app.should_show_file_count({"status": "Sem acesso", "quantidade_arquivos": 0}))
        self.assertFalse(self.app.should_show_file_count({"status": "Não encontrado", "quantidade_arquivos": 0}))
        self.assertFalse(self.app.should_show_file_count({"status": "Aguardando análise", "quantidade_arquivos": 0}))

    def test_empty_list_returns_none(self):
        self.assertIsNone(self.app.summarize_cleaning_categories([]))

    def test_all_pending_categories_return_none(self):
        categories = [
            {"status": "Aguardando análise", "tamanho_mb": 0},
            {"status": "Aguardando análise", "tamanho_mb": 0},
        ]

        self.assertIsNone(self.app.summarize_cleaning_categories(categories))

    def test_available_categories_are_summed(self):
        categories = [
            {"status": "Disponível", "tamanho_mb": 2.2},
            {"status": "Disponível", "tamanho_mb": 1.1},
        ]

        summary = self.app.summarize_cleaning_categories(categories)

        self.assertEqual(summary["total_estimado_mb"], 3.3)
        self.assertEqual(summary["categorias_disponiveis"], 2)
        self.assertEqual(summary["categorias_indisponiveis"], 0)

    def test_unavailable_categories_are_counted(self):
        categories = [
            {"status": "Disponível", "tamanho_mb": 1.0},
            {"status": "Sem acesso", "tamanho_mb": 2.0},
            {"status": "Não encontrado", "tamanho_mb": 0.5},
        ]

        summary = self.app.summarize_cleaning_categories(categories)

        self.assertEqual(summary["categorias_disponiveis"], 1)
        self.assertEqual(summary["categorias_indisponiveis"], 2)

    def test_pending_category_is_not_counted_as_unavailable(self):
        categories = [
            {"status": "Aguardando análise", "tamanho_mb": 0},
            {"status": "Disponível", "tamanho_mb": 2.5},
            {"status": "Sem acesso", "tamanho_mb": 1.5},
        ]

        summary = self.app.summarize_cleaning_categories(categories)

        self.assertEqual(summary["categorias_disponiveis"], 1)
        self.assertEqual(summary["categorias_indisponiveis"], 1)
        self.assertEqual(summary["total_estimado_mb"], 2.5)


class CleaningSelectionSummaryTests(unittest.TestCase):
    def setUp(self):
        self.app = PCBoostLabApp.__new__(PCBoostLabApp)

    def test_empty_selection_returns_zeroed_summary(self):
        categories = [
            {"nome": "A", "status": "Disponível", "tamanho_mb": 1.5, "quantidade_arquivos": 3},
        ]

        summary = self.app.summarize_selected_categories(categories, set())

        self.assertEqual(summary["quantidade_categorias"], 0)
        self.assertEqual(summary["quantidade_arquivos"], 0)
        self.assertEqual(summary["tamanho_estimado_mb"], 0.0)

    def test_single_selected_category_is_summed(self):
        categories = [
            {"nome": "A", "status": "Disponível", "tamanho_mb": 2.2, "quantidade_arquivos": 4},
        ]

        summary = self.app.summarize_selected_categories(categories, {"A"})

        self.assertEqual(summary["quantidade_categorias"], 1)
        self.assertEqual(summary["quantidade_arquivos"], 4)
        self.assertEqual(summary["tamanho_estimado_mb"], 2.2)

    def test_two_selected_categories_are_summed(self):
        categories = [
            {"nome": "A", "status": "Disponível", "tamanho_mb": 1.5, "quantidade_arquivos": 2},
            {"nome": "B", "status": "Disponível", "tamanho_mb": 2.5, "quantidade_arquivos": 3},
        ]

        summary = self.app.summarize_selected_categories(categories, {"A", "B"})

        self.assertEqual(summary["quantidade_categorias"], 2)
        self.assertEqual(summary["quantidade_arquivos"], 5)
        self.assertEqual(summary["tamanho_estimado_mb"], 4.0)

    def test_non_selected_categories_are_ignored(self):
        categories = [
            {"nome": "A", "status": "Disponível", "tamanho_mb": 1.0, "quantidade_arquivos": 1},
            {"nome": "B", "status": "Disponível", "tamanho_mb": 2.0, "quantidade_arquivos": 2},
        ]

        summary = self.app.summarize_selected_categories(categories, {"B"})

        self.assertEqual(summary["quantidade_categorias"], 1)
        self.assertEqual(summary["quantidade_arquivos"], 2)
        self.assertEqual(summary["tamanho_estimado_mb"], 2.0)

    def test_unavailable_categories_are_ignored_even_if_selected_in_test_data(self):
        categories = [
            {"nome": "A", "status": "Sem acesso", "tamanho_mb": 10.0, "quantidade_arquivos": 99},
            {"nome": "B", "status": "Disponível", "tamanho_mb": 3.0, "quantidade_arquivos": 4},
        ]

        summary = self.app.summarize_selected_categories(categories, {"A", "B"})

        self.assertEqual(summary["quantidade_categorias"], 1)
        self.assertEqual(summary["quantidade_arquivos"], 4)
        self.assertEqual(summary["tamanho_estimado_mb"], 3.0)


class CleaningPlanTests(unittest.TestCase):
    def test_plan_respects_specific_pattern_and_ignores_other_extensions(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            (root / "file.pf").write_text("x", encoding="utf-8")
            (root / "file.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível", "padrao": "*.pf"}],
                {"Categoria"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 1)
            self.assertEqual(plan["categorias"][0]["arquivos"][0]["caminho"], str(root / "file.pf"))

    def test_relative_existing_path_is_rejected(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            (root / "file.txt").write_text("x", encoding="utf-8")

            original_cwd = Path.cwd()
            try:
                os.chdir(temp_dir)
                plan = build_cleaning_plan(
                    [{"nome": "Categoria", "caminho": "root", "status": "Disponível"}],
                    {"Categoria"},
                )
            finally:
                os.chdir(original_cwd)

            self.assertEqual(plan["quantidade_arquivos"], 0)
            self.assertEqual(plan["categorias"], [])

    def test_absolute_path_is_accepted(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            file_path = root / "file.txt"
            file_path.write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                {"Categoria"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 1)
            self.assertEqual(plan["categorias"][0]["arquivos"][0]["caminho"], str(file_path))

    def test_empty_selection_returns_empty_plan(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            (root / "file.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                set(),
            )

            self.assertEqual(plan["quantidade_arquivos"], 0)
            self.assertEqual(plan["categorias"], [])
            self.assertEqual(plan["arquivos_omitidos"], 0)

    def test_single_file_inside_category_is_included(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            file_path = root / "file.txt"
            file_path.write_text("conteudo", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                {"Categoria"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 1)
            self.assertEqual(plan["categorias"][0]["nome"], "Categoria")
            self.assertEqual(plan["categorias"][0]["arquivos"][0]["caminho"], str(file_path))

    def test_file_inside_subfolder_is_included(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            subfolder = root / "sub"
            subfolder.mkdir(parents=True)
            file_path = subfolder / "nested.txt"
            file_path.write_text("conteudo", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                {"Categoria"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 1)
            self.assertEqual(plan["categorias"][0]["arquivos"][0]["caminho"], str(file_path))

    def test_two_selected_categories_are_added(self):
        with TemporaryDirectory() as temp_dir:
            root_a = Path(temp_dir) / "a"
            root_b = Path(temp_dir) / "b"
            root_a.mkdir()
            root_b.mkdir()
            (root_a / "one.txt").write_text("1", encoding="utf-8")
            (root_b / "two.txt").write_text("22", encoding="utf-8")

            plan = build_cleaning_plan(
                [
                    {"nome": "A", "caminho": str(root_a), "status": "Disponível"},
                    {"nome": "B", "caminho": str(root_b), "status": "Disponível"},
                ],
                {"A", "B"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 2)
            self.assertEqual(len(plan["categorias"]), 2)

    def test_non_selected_category_is_ignored(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            (root / "file.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                set(),
            )

            self.assertEqual(plan["quantidade_arquivos"], 0)
            self.assertEqual(plan["categorias"], [])

    def test_unavailable_category_is_ignored(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            (root / "file.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Sem acesso"}],
                {"Categoria"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 0)
            self.assertEqual(plan["categorias"], [])

    def test_directories_are_not_counted_as_files(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            subfolder = root / "sub"
            subfolder.mkdir(parents=True)
            (root / "file.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                {"Categoria"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 1)
            self.assertEqual(len(plan["categorias"][0]["arquivos"]), 1)

    def test_total_size_is_calculated(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            file_path = root / "file.txt"
            file_path.write_text("abc", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                {"Categoria"},
            )

            self.assertEqual(plan["tamanho_total_bytes"], 3)
            self.assertEqual(plan["tamanho_total_mb"], 0.0)

    def test_visual_limit_truncates_display_without_changing_total(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            for index in range(105):
                (root / f"file{index}.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                {"Categoria"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 105)
            self.assertEqual(len(plan["categorias"][0]["arquivos"]), 100)
            self.assertEqual(plan["arquivos_omitidos"], 5)

    def test_two_categories_share_global_visual_limit(self):
        with TemporaryDirectory() as temp_dir:
            root_a = Path(temp_dir) / "a"
            root_b = Path(temp_dir) / "b"
            root_a.mkdir()
            root_b.mkdir()
            for index in range(70):
                (root_a / f"a{index}.txt").write_text("x", encoding="utf-8")
            for index in range(70):
                (root_b / f"b{index}.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [
                    {"nome": "A", "caminho": str(root_a), "status": "Disponível"},
                    {"nome": "B", "caminho": str(root_b), "status": "Disponível"},
                ],
                {"A", "B"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 140)
            self.assertEqual(len(plan["categorias"][0]["arquivos"]), 70)
            self.assertEqual(len(plan["categorias"][1]["arquivos"]), 30)
            self.assertEqual(plan["arquivos_omitidos"], 40)

    def test_category_after_global_limit_keeps_total_and_empty_visual_list(self):
        with TemporaryDirectory() as temp_dir:
            root_a = Path(temp_dir) / "a"
            root_b = Path(temp_dir) / "b"
            root_a.mkdir()
            root_b.mkdir()
            for index in range(100):
                (root_a / f"a{index}.txt").write_text("x", encoding="utf-8")
            for index in range(5):
                (root_b / f"b{index}.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [
                    {"nome": "A", "caminho": str(root_a), "status": "Disponível"},
                    {"nome": "B", "caminho": str(root_b), "status": "Disponível"},
                ],
                {"A", "B"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 105)
            self.assertEqual(plan["categorias"][1]["arquivos"], [])
            self.assertEqual(plan["arquivos_omitidos"], 5)

    def test_total_size_includes_omitted_files(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            for index in range(101):
                (root / f"file{index}.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                {"Categoria"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 101)
            self.assertEqual(plan["tamanho_total_bytes"], 101)
            self.assertEqual(plan["arquivos_omitidos"], 1)

    def test_empty_path_is_ignored(self):
        plan = build_cleaning_plan(
            [{"nome": "Categoria", "caminho": "", "status": "Disponível"}],
            {"Categoria"},
        )

        self.assertEqual(plan["quantidade_arquivos"], 0)
        self.assertEqual(plan["categorias"], [])

    def test_relative_path_is_ignored(self):
        plan = build_cleaning_plan(
            [{"nome": "Categoria", "caminho": "./relative", "status": "Disponível"}],
            {"Categoria"},
        )

        self.assertEqual(plan["quantidade_arquivos"], 0)
        self.assertEqual(plan["categorias"], [])

    def test_helper_confirms_path_outside_root_is_not_allowed(self):
        from app.cleaning import plan as cleaning_plan

        self.assertFalse(cleaning_plan._is_within_root(Path("/tmp/root"), Path("/tmp/outside")))

    def test_path_outside_root_is_ignored(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            outside = Path(temp_dir) / "outside"
            outside.mkdir()
            (outside / "file.txt").write_text("x", encoding="utf-8")

            plan = build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                {"Categoria"},
            )

            self.assertEqual(plan["quantidade_arquivos"], 0)

    def test_plan_does_not_delete_or_modify_files(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "root"
            root.mkdir()
            file_path = root / "file.txt"
            file_path.write_text("conteudo", encoding="utf-8")

            build_cleaning_plan(
                [{"nome": "Categoria", "caminho": str(root), "status": "Disponível"}],
                {"Categoria"},
            )

            self.assertTrue(file_path.exists())
            self.assertEqual(file_path.read_text(encoding="utf-8"), "conteudo")


if __name__ == "__main__":
    unittest.main()
