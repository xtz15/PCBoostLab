# -*- coding: utf-8 -*-
import sys
import threading
from pathlib import Path

import customtkinter as ctk

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.logger import get_logger
from app.diagnostics.processes import collect_top_processes
from app.diagnostics.system_info import collect_system_info, format_diagnostic_text
from app.reports.report_builder import generate_diagnostic_report


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

logger = get_logger(__name__)


class PCBoostLabApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PCBoostLab")
        self.geometry("1100x700")
        self.minsize(1000, 620)

        self.diagnostic_refresh_button = None
        self.diagnostic_load_id = 0
        self.dashboard_load_id = 0
        self.latest_system_info = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content = ctk.CTkFrame(self, corner_radius=12)
        self.content.grid(row=0, column=1, sticky="nsew", padx=14, pady=14)

        self.build_sidebar()
        self.show_dashboard()

    def build_sidebar(self):
        title = ctk.CTkLabel(
            self.sidebar,
            text="PCBoostLab",
            font=ctk.CTkFont(size=25, weight="bold"),
        )
        title.pack(pady=(30, 24), padx=20)

        buttons = [
            ("Painel", self.show_dashboard),
            ("Diagnóstico", self.show_diagnostics),
            ("Otimizações seguras", self.show_safe_optimizations),
            ("Otimizações avançadas", self.show_advanced_optimizations),
            ("Limpeza", self.show_cleaning),
            ("Restauração", self.show_restore),
            ("Relatórios", self.show_reports),
        ]

        for text, command in buttons:
            button = ctk.CTkButton(
                self.sidebar,
                text=text,
                height=42,
                anchor="w",
                command=command,
            )
            button.pack(fill="x", padx=16, pady=6)

    def clear_content(self):
        self.diagnostic_load_id += 1
        self.dashboard_load_id += 1
        self.diagnostic_refresh_button = None

        for widget in self.content.winfo_children():
            widget.destroy()

    def page_header(self, title, subtitle):
        ctk.CTkLabel(
            self.content,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(anchor="w", padx=28, pady=(26, 4))

        ctk.CTkLabel(
            self.content,
            text=subtitle,
            text_color="#9ca3af",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=28, pady=(0, 18))

    def create_card(self, parent, title, value, column):
        parent.grid_columnconfigure(column, weight=1)

        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=column, sticky="ew", padx=8, pady=8)

        ctk.CTkLabel(
            card,
            text=title,
            text_color="#9ca3af",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=18, pady=(18, 6))

        ctk.CTkLabel(
            card,
            text=value,
            wraplength=220,
            justify="left",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(0, 18))

    def add_readonly_box(self, parent, text, height=160):
        box = ctk.CTkTextbox(parent, height=height, font=ctk.CTkFont(size=14))
        box.pack(fill="x", padx=28, pady=(0, 14))
        box.insert("1.0", text)
        box.configure(state="disabled")
        return box

    def section_title(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", padx=28, pady=(4, 8))

    def show_loading_message(self, parent, title, subtitle):
        for widget in parent.winfo_children():
            widget.destroy()

        loading_frame = ctk.CTkFrame(parent, fg_color="transparent")
        loading_frame.pack(fill="x", padx=28, pady=(8, 14))

        ctk.CTkLabel(
            loading_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            loading_frame,
            text=subtitle,
            text_color="#9ca3af",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w")

    def show_error_message(self, parent, message):
        for widget in parent.winfo_children():
            widget.destroy()

        error = ctk.CTkFrame(parent, fg_color="#7f1d1d", corner_radius=8)
        error.pack(fill="x", padx=28, pady=(8, 14))

        ctk.CTkLabel(
            error,
            text=message,
            text_color="#fee2e2",
            justify="left",
            wraplength=760,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=16, pady=12)

    def add_diagnostic_alerts(self, parent, info):
        cpu_usage = info["cpu"]["uso_percentual"]
        ram_usage = info["ram"]["uso_percentual"]
        alerts = []

        if ram_usage > 80:
            alerts.append(f"RAM em uso acima de 80%: {ram_usage}%.")

        if cpu_usage > 80:
            alerts.append(f"CPU em uso acima de 80%: {cpu_usage}%.")

        if not alerts:
            alerts.append("CPU e RAM estão abaixo do limite de alerta de 80%.")
            color = "#14532d"
            text_color = "#dcfce7"
        else:
            color = "#7f1d1d"
            text_color = "#fee2e2"

        alert = ctk.CTkFrame(parent, fg_color=color, corner_radius=8)
        alert.pack(fill="x", padx=28, pady=(0, 14))

        ctk.CTkLabel(
            alert,
            text="\n".join(alerts),
            text_color=text_color,
            justify="left",
            wraplength=760,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=16, pady=12)

    def format_process_table(self, processes):
        if not processes:
            return "Nenhum processo encontrado."

        lines = [f"{'PID':>7}  {'RAM MB':>9}  {'CPU %':>7}  Nome"]
        lines.append("-" * 70)

        for process in processes:
            name = process["nome"][:38]
            lines.append(
                f"{process['pid']:>7}  "
                f"{process['ram_mb']:>9.1f}  "
                f"{process['cpu_percent']:>7.1f}  "
                f"{name}"
            )

        return "\n".join(lines)

    def render_dashboard_content(self, parent, info):
        for widget in parent.winfo_children():
            widget.destroy()

        cpu_name = info["cpu"]["nome"]
        ram_total = round(info["ram"]["total_gb"], 1)
        ram_used = info["ram"]["uso_percentual"]
        system_name = info["sistema"]["descricao"]

        cards = ctk.CTkFrame(parent, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=8)

        self.create_card(cards, "CPU", cpu_name, 0)
        self.create_card(cards, "RAM total", f"{ram_total} GB", 1)
        self.create_card(cards, "RAM em uso", f"{ram_used}%", 2)
        self.create_card(cards, "Sistema operacional", system_name, 3)

    def start_dashboard_load(self, parent):
        self.dashboard_load_id += 1
        load_id = self.dashboard_load_id

        self.show_loading_message(
            parent,
            "Carregando painel...",
            "Coletando resumo do computador.",
        )

        if self.latest_system_info:
            self.after(
                50,
                lambda: self.render_cached_dashboard(parent, load_id, self.latest_system_info),
            )

        def worker():
            try:
                info = collect_system_info()
            except Exception as exc:
                logger.exception("Falha ao carregar painel em segundo plano: %s", exc)
                self.after(0, lambda: self.finish_dashboard_load(parent, load_id, error=exc))
                return

            self.after(0, lambda: self.finish_dashboard_load(parent, load_id, info=info))

        threading.Thread(target=worker, daemon=True).start()

    def render_cached_dashboard(self, parent, load_id, info):
        if load_id != self.dashboard_load_id:
            return

        try:
            if not parent.winfo_exists():
                return
        except Exception:
            return

        self.render_dashboard_content(parent, info)

    def finish_dashboard_load(self, parent, load_id, info=None, error=None):
        if load_id != self.dashboard_load_id:
            return

        try:
            if not parent.winfo_exists():
                return
        except Exception:
            return

        if error:
            self.show_error_message(
                parent,
                "Não foi possível carregar o painel agora. Tente abrir o Painel novamente.",
            )
            return

        self.latest_system_info = info
        self.render_dashboard_content(parent, info)

    def show_dashboard(self):
        self.clear_content()
        self.page_header("Painel", "Resumo geral do computador")

        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=0, pady=(0, 16))
        self.start_dashboard_load(body)

    def collect_diagnostic_data(self):
        return {
            "info": collect_system_info(),
            "process_data": collect_top_processes(limit=10),
        }

    def render_diagnostics_content(self, parent, info, process_data):
        for widget in parent.winfo_children():
            widget.destroy()

        self.add_diagnostic_alerts(parent, info)

        self.section_title(parent, "Resumo atual")
        self.add_readonly_box(parent, format_diagnostic_text(info), height=190)

        self.section_title(parent, "10 processos que mais usam RAM")
        self.add_readonly_box(
            parent,
            self.format_process_table(process_data["por_ram"]),
            height=220,
        )

        self.section_title(parent, "10 processos que mais usam CPU")
        self.add_readonly_box(
            parent,
            self.format_process_table(process_data["por_cpu"]),
            height=220,
        )

    def start_diagnostic_load(self, parent):
        self.diagnostic_load_id += 1
        load_id = self.diagnostic_load_id

        if self.diagnostic_refresh_button:
            self.diagnostic_refresh_button.configure(state="disabled")

        self.show_loading_message(
            parent,
            "Carregando diagnóstico...",
            "Isso pode levar alguns segundos.",
        )

        def worker():
            try:
                result = self.collect_diagnostic_data()
            except Exception as exc:
                logger.exception("Falha ao carregar diagnostico em segundo plano: %s", exc)
                self.after(0, lambda: self.finish_diagnostic_load(parent, load_id, error=exc))
                return

            self.after(0, lambda: self.finish_diagnostic_load(parent, load_id, result=result))

        threading.Thread(target=worker, daemon=True).start()

    def finish_diagnostic_load(self, parent, load_id, result=None, error=None):
        if load_id != self.diagnostic_load_id:
            return

        try:
            if not parent.winfo_exists():
                return
        except Exception:
            return

        if error:
            self.show_error_message(
                parent,
                "Não foi possível carregar o diagnóstico agora. Tente atualizar novamente.",
            )
        else:
            self.latest_system_info = result["info"]
            self.render_diagnostics_content(
                parent,
                result["info"],
                result["process_data"],
            )

        if self.diagnostic_refresh_button:
            self.diagnostic_refresh_button.configure(state="normal")

    def show_diagnostics(self):
        self.clear_content()
        self.page_header("Diagnóstico do PC", "Leitura inicial de CPU, RAM, sistema e processos")

        body = ctk.CTkScrollableFrame(self.content, fg_color="transparent")

        self.diagnostic_refresh_button = ctk.CTkButton(
            self.content,
            text="Atualizar diagnóstico",
            width=190,
            command=lambda: self.start_diagnostic_load(body),
        )
        self.diagnostic_refresh_button.pack(anchor="w", padx=28, pady=(0, 12))

        body.pack(fill="both", expand=True, padx=0, pady=(0, 16))
        self.start_diagnostic_load(body)

    def optimization_card(self, title, description, button_text):
        card = ctk.CTkFrame(self.content, corner_radius=12)
        card.pack(fill="x", padx=28, pady=8)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(16, 4))

        ctk.CTkLabel(
            card,
            text=description,
            text_color="#9ca3af",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 12))

        ctk.CTkButton(
            card,
            text=button_text,
            width=130,
        ).pack(anchor="e", padx=18, pady=(0, 16))

    def show_safe_optimizations(self):
        self.clear_content()
        self.page_header("Otimizações seguras", "Ajustes reversíveis e de baixo risco")

        self.optimization_card(
            "Plano de energia de alto desempenho",
            "Mantém o processador mais responsivo. Pode aumentar consumo e temperatura.",
            "Aplicar",
        )

        self.optimization_card(
            "Desativar apps em segundo plano",
            "Reduz processos desnecessários. Pode impedir notificações de alguns aplicativos.",
            "Aplicar",
        )

    def show_advanced_optimizations(self):
        self.clear_content()
        self.page_header("Otimizações avançadas", "Ajustes que exigem ponto de restauração")

        self.optimization_card(
            "Desativar Inicialização Rápida",
            "Pode evitar problemas de driver, dual boot e hardware. O boot pode ficar um pouco mais lento.",
            "Aplicar",
        )

        self.optimization_card(
            "Ajustes de prioridade Win32",
            "Altera prioridade de resposta entre programas e serviços. Deve ser testado caso a caso.",
            "Aplicar",
        )

    def show_cleaning(self):
        self.clear_content()
        self.page_header("Limpeza", "Remoção de arquivos temporários e caches")

        self.optimization_card(
            "Limpar arquivos temporários",
            "Remove arquivos temporários do usuário e do sistema. Seguro na maioria dos casos.",
            "Limpar",
        )

        self.optimization_card(
            "Limpar cache de miniaturas",
            "O Windows recriará as miniaturas depois. Pode causar lentidão temporária ao abrir pastas com imagens.",
            "Limpar",
        )

    def show_restore(self):
        self.clear_content()
        self.page_header("Restauração", "Criação e controle de pontos de restauração")

        self.optimization_card(
            "Criar ponto de restauração",
            "Permite voltar configurações do sistema caso algum ajuste cause instabilidade.",
            "Criar",
        )

    def show_reports(self):
        self.clear_content()
        self.page_header("Relatórios", "Geração de relatório simples de diagnóstico")

        ctk.CTkLabel(
            self.content,
            text=(
                "Gera um arquivo .txt com CPU, RAM, sistema, data/hora "
                "e uso atual de CPU/RAM. Esta função apenas lê informações "
                "do computador e não altera configurações do Windows."
            ),
            text_color="#9ca3af",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", padx=28, pady=(0, 16))

        result_label = ctk.CTkLabel(
            self.content,
            text="Nenhum relatório gerado nesta sessão.",
            text_color="#9ca3af",
            wraplength=760,
            justify="left",
        )
        result_label.pack(anchor="w", padx=28, pady=(0, 16))

        def on_generate_report():
            try:
                report_path = generate_diagnostic_report()
                result_label.configure(
                    text=f"Relatório gerado com sucesso:\n{report_path}"
                )
            except Exception as exc:
                logger.exception("Falha ao gerar relatorio de diagnostico: %s", exc)
                result_label.configure(
                    text="Não foi possível gerar o relatório. Consulte o log em data/logs/pcboostlab.log."
                )

        ctk.CTkButton(
            self.content,
            text="Gerar relatório",
            width=170,
            command=on_generate_report,
        ).pack(anchor="w", padx=28, pady=(0, 16))


if __name__ == "__main__":
    app = PCBoostLabApp()
    app.mainloop()
