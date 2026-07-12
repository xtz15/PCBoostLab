import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.cleaning import scan as cleaning_scan
from app.main import PCBoostLabApp


class CleaningScanTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
