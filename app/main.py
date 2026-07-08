import platform
import psutil
import cpuinfo
import customtkinter as ctk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PCBoostLabApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PCBoostLab")
        self.geometry("1100x700")
        self.minsize(1000, 620)

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
            font=ctk.CTkFont(size=25, weight="bold")
        )
        title.pack(pady=(30, 24), padx=20)

        buttons = [
            ("Painel", self.show_dashboard),
            ("Diagnóstico", self.show_diagnostics),
            ("Otimizações seguras", self.show_safe_optimizations),
            ("Otimizações avançadas", self.show_advanced_optimizations),
            ("Limpeza", self.show_cleaning),
            ("Restauração", self.show_restore),
        ]

        for text, command in buttons:
            button = ctk.CTkButton(
                self.sidebar,
                text=text,
                height=42,
                anchor="w",
                command=command
            )
            button.pack(fill="x", padx=16, pady=6)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def page_header(self, title, subtitle):
        ctk.CTkLabel(
            self.content,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(anchor="w", padx=28, pady=(26, 4))

        ctk.CTkLabel(
            self.content,
            text=subtitle,
            text_color="#9ca3af",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=28, pady=(0, 24))

    def create_card(self, parent, title, value, column):
        parent.grid_columnconfigure(column, weight=1)

        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=column, sticky="ew", padx=8, pady=8)

        ctk.CTkLabel(
            card,
            text=title,
            text_color="#9ca3af",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=18, pady=(18, 6))

        ctk.CTkLabel(
            card,
            text=value,
            wraplength=260,
            justify="left",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(anchor="w", padx=18, pady=(0, 18))

    def show_dashboard(self):
        self.clear_content()
        self.page_header("Painel", "Resumo geral do computador")

        cpu_name = cpuinfo.get_cpu_info().get("brand_raw", "Processador não identificado")
        ram_total = round(psutil.virtual_memory().total / (1024 ** 3), 1)
        ram_used = psutil.virtual_memory().percent
        system_name = f"{platform.system()} {platform.release()}"

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=8)

        self.create_card(cards, "Processador", cpu_name, 0)
        self.create_card(cards, "Memória RAM", f"{ram_total} GB\nUso atual: {ram_used}%", 1)
        self.create_card(cards, "Sistema", system_name, 2)

    def show_diagnostics(self):
        self.clear_content()
        self.page_header("Diagnóstico do PC", "Leitura inicial de CPU, RAM e sistema")

        ram = psutil.virtual_memory()

        diagnostic_text = (
            f"CPU: {cpuinfo.get_cpu_info().get('brand_raw', 'Não identificado')}\n"
            f"Núcleos físicos: {psutil.cpu_count(logical=False)}\n"
            f"Threads: {psutil.cpu_count(logical=True)}\n"
            f"Uso de CPU atual: {psutil.cpu_percent(interval=1)}%\n\n"
            f"RAM total: {round(ram.total / (1024 ** 3), 2)} GB\n"
            f"RAM em uso: {ram.percent}%\n"
            f"RAM disponível: {round(ram.available / (1024 ** 3), 2)} GB\n\n"
            f"Sistema: {platform.system()} {platform.release()}\n"
            f"Versão: {platform.version()}"
        )

        box = ctk.CTkTextbox(self.content, height=300, font=ctk.CTkFont(size=15))
        box.pack(fill="x", padx=28, pady=10)
        box.insert("1.0", diagnostic_text)
        box.configure(state="disabled")

    def optimization_card(self, title, description, button_text):
        card = ctk.CTkFrame(self.content, corner_radius=12)
        card.pack(fill="x", padx=28, pady=8)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=18, pady=(16, 4))

        ctk.CTkLabel(
            card,
            text=description,
            text_color="#9ca3af",
            wraplength=760,
            justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 12))

        ctk.CTkButton(
            card,
            text=button_text,
            width=130
        ).pack(anchor="e", padx=18, pady=(0, 16))

    def show_safe_optimizations(self):
        self.clear_content()
        self.page_header("Otimizações seguras", "Ajustes reversíveis e de baixo risco")

        self.optimization_card(
            "Plano de energia de alto desempenho",
            "Mantém o processador mais responsivo. Pode aumentar consumo e temperatura.",
            "Aplicar"
        )

        self.optimization_card(
            "Desativar apps em segundo plano",
            "Reduz processos desnecessários. Pode impedir notificações de alguns aplicativos.",
            "Aplicar"
        )

    def show_advanced_optimizations(self):
        self.clear_content()
        self.page_header("Otimizações avançadas", "Ajustes que exigem ponto de restauração")

        self.optimization_card(
            "Desativar Inicialização Rápida",
            "Pode evitar problemas de driver, dual boot e hardware. O boot pode ficar um pouco mais lento.",
            "Aplicar"
        )

        self.optimization_card(
            "Ajustes de prioridade Win32",
            "Altera prioridade de resposta entre programas e serviços. Deve ser testado caso a caso.",
            "Aplicar"
        )

    def show_cleaning(self):
        self.clear_content()
        self.page_header("Limpeza", "Remoção de arquivos temporários e caches")

        self.optimization_card(
            "Limpar arquivos temporários",
            "Remove arquivos temporários do usuário e do sistema. Seguro na maioria dos casos.",
            "Limpar"
        )

        self.optimization_card(
            "Limpar cache de miniaturas",
            "O Windows recriará as miniaturas depois. Pode causar lentidão temporária ao abrir pastas com imagens.",
            "Limpar"
        )

    def show_restore(self):
        self.clear_content()
        self.page_header("Restauração", "Criação e controle de pontos de restauração")

        self.optimization_card(
            "Criar ponto de restauração",
            "Permite voltar configurações do sistema caso algum ajuste cause instabilidade.",
            "Criar"
        )


if __name__ == "__main__":
    app = PCBoostLabApp()
    app.mainloop()
