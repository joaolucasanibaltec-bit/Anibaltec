import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
from pathlib import Path
import threading
import logging

def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

base_path = get_base_path()
sys.path.insert(0, str(base_path / 'src'))

from reader import SGAReader
from converter import Converter
from xlsx_writer import XLSXWriter
from ibge_lookup import IBGELookup

theme_path = str(base_path / "config" / "anibaltec_theme.json")
ctk.set_appearance_mode("dark")
if os.path.exists(theme_path):
    ctk.set_default_color_theme(theme_path)
else:
    ctk.set_default_color_theme("blue")

COLORS = {
    "amber": "#d4942b",
    "amber_hover": "#b87a1f",
    "green": "#2ecc71",
    "green_hover": "#27ae60",
    "red": "#e74c3c",
    "surface": "#1a2d4a",
    "border": "#2a3f5f",
    "muted": "#6b7f9f",
    "step_active": "#d4942b",
    "step_inactive": "#2a3f5f",
    "step_done": "#2ecc71",
}


class SGAConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SGA → SGAcloud Converter")
        self.root.geometry("860x680")
        self.root.minsize(720, 580)

        self.current_step = 0
        self.total_steps = 4

        self.product_sga_path = ctk.StringVar()
        self.product_template_path = ctk.StringVar()
        self.client_sga_path = ctk.StringVar()
        self.supplier_sga_path = ctk.StringVar()
        self.client_template_path = ctk.StringVar()
        self.default_cep = ctk.StringVar()
        self.handle_missing = ctk.StringVar(value='keep')
        self.fill_city = ctk.StringVar()
        self.fill_uf = ctk.StringVar()

        self.client_output_path = ctk.StringVar()

        self.convert_products_var = ctk.BooleanVar(value=True)
        self.convert_clients_var = ctk.BooleanVar(value=True)

        self.product_template_path.set(str(base_path / "SgaCloud" / "TEMPLATE MERCADORIAS.xlsx"))
        self.client_template_path.set(str(base_path / "SgaCloud" / "TEMPLATE CLIENTES.xlsx"))
        self.product_output_path.set(str(Path.home() / "Downloads" / "MERCADORIAS_SGACLOUD.xlsx"))
        self.client_output_path.set(str(Path.home() / "Downloads" / "CLIENTES_SGACLOUD.xlsx"))

        self.is_converting = False
        self.step_frames = []
        self.step_indicators = []
        self.step_connectors = []

        self.create_widgets()
        self.show_step(0)

    def create_widgets(self):
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=16, pady=16)

        self.create_step_indicator(main_container)

        self.content_container = ctk.CTkFrame(main_container, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, pady=(12, 12))

        self.create_step0_config()
        self.create_step1_products()
        self.create_step2_clients()
        self.create_step3_generate()

        self.create_navigation(main_container)

        self.progress_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(0, 4))

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8)
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self.progress_frame, text="Pronto para converter",
            anchor="w", font=ctk.CTkFont(size=12), text_color=COLORS["muted"]
        )
        self.status_label.pack(fill="x", pady=(4, 0))

        self.log_text = ctk.CTkTextbox(main_container, height=120, font=ctk.CTkFont(size=11))
        self.log_text.pack(fill="x")
        self.log_text.configure(state="disabled")

    def create_step_indicator(self, parent):
        step_container = ctk.CTkFrame(parent, fg_color="transparent", height=50)
        step_container.pack(fill="x")
        step_container.grid_columnconfigure(tuple(range(7)), weight=1)

        labels = ["Config", "Mercadorias", "Clientes", "Gerar"]
        icons = ["\u2699", "\U0001f4e6", "\U0001f465", "\u25b6"]

        for i in range(4):
            col = i * 2
            frame = ctk.CTkFrame(step_container, fg_color="transparent")
            frame.grid(row=0, column=col, padx=2)

            circle = ctk.CTkLabel(
                frame, text=icons[i], font=ctk.CTkFont(size=16),
                width=36, height=36, corner_radius=18
            )
            circle.pack()

            label_w = ctk.CTkLabel(
                frame, text=labels[i], font=ctk.CTkFont(size=11),
                text_color=COLORS["muted"]
            )
            label_w.pack(pady=(2, 0))

            self.step_indicators.append((circle, label_w))

            if i < 3:
                connector = ctk.CTkFrame(
                    step_container, fg_color=COLORS["step_inactive"], height=2, width=60
                )
                connector.grid(row=0, column=col + 1, padx=4, pady=(0, 20))
                self.step_connectors.append(connector)

    def update_step_indicator(self):
        for i, (circle, label_w) in enumerate(self.step_indicators):
            if i < self.current_step:
                circle.configure(
                    fg_color=COLORS["step_done"], text_color="#ffffff", text="\u2713"
                )
                label_w.configure(text_color=COLORS["step_done"])
            elif i == self.current_step:
                circle.configure(
                    fg_color=COLORS["step_active"], text_color="#0f1a2e"
                )
                label_w.configure(text_color="#ffffff")
            else:
                circle.configure(
                    fg_color=COLORS["step_inactive"], text_color=COLORS["muted"]
                )
                label_w.configure(text_color=COLORS["muted"])

        for i, conn in enumerate(self.step_connectors):
            if i < self.current_step:
                conn.configure(fg_color=COLORS["step_done"])
            else:
                conn.configure(fg_color=COLORS["step_inactive"])

    def create_step0_config(self):
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.step_frames.append(frame)

        title = ctk.CTkLabel(
            frame, text="Configura\u00e7\u00f5es",
            font=ctk.CTkFont(size=18, weight="bold"), anchor="w"
        )
        title.pack(anchor="w", pady=(0, 8))

        subtitle = ctk.CTkLabel(
            frame, text="Defina as configura\u00e7\u00f5es gerais da convers\u00e3o.",
            font=ctk.CTkFont(size=12), text_color=COLORS["muted"], anchor="w"
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        card = ctk.CTkFrame(frame, fg_color=COLORS["surface"], corner_radius=8)
        card.pack(fill="x", ipadx=12, ipady=12)

        ctk.CTkLabel(
            card, text="CEP Padr\u00e3o (quando vazio):",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=12, pady=(8, 4))

        entry = ctk.CTkEntry(
            card, textvariable=self.default_cep,
            placeholder_text="Ex: 59500000", height=36
        )
        entry.pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkLabel(
            card,
            text="Ser\u00e1 usado quando o cliente/fornecedor n\u00e3o tiver CEP preenchido.\nDatas padr\u00e3o: 01/01/1900 (usado quando cadastro/anivers\u00e1rio estiverem vazios).",
            font=ctk.CTkFont(size=11), text_color=COLORS["muted"], justify="left",
            wraplength=700
        ).pack(anchor="w", padx=12, pady=(0, 8))

        # Records without IBGE handling
        card2 = ctk.CTkFrame(frame, fg_color=COLORS["surface"], corner_radius=8)
        card2.pack(fill="x", ipadx=12, ipady=12, pady=(12, 0))

        ctk.CTkLabel(
            card2, text="Registros sem endere\u00e7o (cidade/UF n\u00e3o preenchidos):",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=12, pady=(8, 4))

        rb_frame = ctk.CTkFrame(card2, fg_color="transparent")
        rb_frame.pack(fill="x", padx=12, pady=(0, 4))

        rb_keep = ctk.CTkRadioButton(
            rb_frame, text="Manter registros (IBGE ficar\u00e1 em branco)",
            variable=self.handle_missing, value="keep",
            font=ctk.CTkFont(size=12)
        )
        rb_keep.pack(anchor="w", pady=2)

        rb_fill = ctk.CTkRadioButton(
            rb_frame, text="Preencher com dados padr\u00e3o:",
            variable=self.handle_missing, value="fill",
            font=ctk.CTkFont(size=12)
        )
        rb_fill.pack(anchor="w", pady=2)

        fill_row = ctk.CTkFrame(rb_frame, fg_color="transparent")
        fill_row.pack(fill="x", padx=(24, 0), pady=(2, 4))

        ctk.CTkLabel(fill_row, text="Cidade:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 4))
        ctk.CTkEntry(fill_row, textvariable=self.fill_city, placeholder_text="Ex: Mossor\u00f3", width=200, height=30).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(fill_row, text="UF:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 4))
        ctk.CTkEntry(fill_row, textvariable=self.fill_uf, placeholder_text="Ex: RN", width=60, height=30).pack(side="left")

        rb_remove = ctk.CTkRadioButton(
            rb_frame, text="Excluir registros sem endere\u00e7o",
            variable=self.handle_missing, value="remove",
            font=ctk.CTkFont(size=12)
        )
        rb_remove.pack(anchor="w", pady=2)

        ctk.CTkLabel(
            card2,
            text="Registros sem cidade e UF n\u00e3o podem ter c\u00f3digo IBGE. Escolha como tratar esses registros.",
            font=ctk.CTkFont(size=11), text_color=COLORS["muted"], justify="left",
            wraplength=700
        ).pack(anchor="w", padx=12, pady=(0, 8))

    def create_step1_products(self):
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.step_frames.append(frame)

        title = ctk.CTkLabel(
            frame, text="Mercadorias",
            font=ctk.CTkFont(size=18, weight="bold"), anchor="w"
        )
        title.pack(anchor="w", pady=(0, 8))

        subtitle = ctk.CTkLabel(
            frame, text="Selecione os arquivos para convers\u00e3o de produtos/mercadorias.",
            font=ctk.CTkFont(size=12), text_color=COLORS["muted"], anchor="w"
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        self._create_file_row(frame, 0, "Planilha SGA (Produtos):", self.product_sga_path,
                              self.select_product_sga, "CSV")
        self._create_file_row(frame, 1, "Template SGAcloud:", self.product_template_path,
                              self.select_product_template, "XLSX")
        self._create_file_row(frame, 2, "Arquivo de Sa\u00edda:", self.product_output_path,
                              self.select_product_output, "XLSX")

        info = ctk.CTkLabel(
            frame,
            text="O arquivo SGA deve ser a planilha de produtos exportada do sistema SGA.\nO template SGAcloud deve ser o arquivo TEMPLATE MERCADORIAS.xlsx.",
            justify="left", text_color=COLORS["muted"], font=ctk.CTkFont(size=11),
            wraplength=700
        )
        info.pack(anchor="w", padx=4, pady=(12, 4))

    def create_step2_clients(self):
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.step_frames.append(frame)

        title = ctk.CTkLabel(
            frame, text="Clientes / Fornecedores",
            font=ctk.CTkFont(size=18, weight="bold"), anchor="w"
        )
        title.pack(anchor="w", pady=(0, 8))

        subtitle = ctk.CTkLabel(
            frame, text="Selecione os arquivos para convers\u00e3o de clientes e fornecedores.",
            font=ctk.CTkFont(size=12), text_color=COLORS["muted"], anchor="w"
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        self._create_file_row(frame, 0, "Planilha SGA (Clientes):", self.client_sga_path,
                              self.select_client_sga, "CSV")
        self._create_file_row(frame, 1, "Planilha SGA (Fornecedores):", self.supplier_sga_path,
                              self.select_supplier_sga, "CSV")
        self._create_file_row(frame, 2, "Template SGAcloud:", self.client_template_path,
                              self.select_client_template, "XLSX")
        self._create_file_row(frame, 3, "Arquivo de Sa\u00edda:", self.client_output_path,
                              self.select_client_output, "XLSX")

        info = ctk.CTkLabel(
            frame,
            text="Os arquivos SGA devem ser as planilhas de clientes e fornecedores exportadas do sistema SGA.\nO template SGAcloud deve ser o arquivo TEMPLATE CLIENTES.xlsx.",
            justify="left", text_color=COLORS["muted"], font=ctk.CTkFont(size=11),
            wraplength=700
        )
        info.pack(anchor="w", padx=4, pady=(12, 4))

    def _create_file_row(self, parent, row, label_text, variable, command, file_type):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=8)
        card.pack(fill="x", pady=(0, 8), ipady=2)

        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(
            card, text=label_text, font=ctk.CTkFont(size=12), anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=(12, 8), pady=8)

        entry = ctk.CTkEntry(
            card, textvariable=variable, height=34,
            font=ctk.CTkFont(size=12)
        )
        entry.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=8)

        type_label = ctk.CTkLabel(
            card, text=f".{file_type.lower()}", text_color=COLORS["amber"],
            font=ctk.CTkFont(size=11, weight="bold"), width=36
        )
        type_label.grid(row=0, column=2, padx=(0, 4), pady=8)

        btn = ctk.CTkButton(
            card, text="Selecionar", command=command,
            width=90, height=32, font=ctk.CTkFont(size=12)
        )
        btn.grid(row=0, column=3, padx=(0, 12), pady=8)

    def create_step3_generate(self):
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.step_frames.append(frame)

        title = ctk.CTkLabel(
            frame, text="Gerar Arquivos",
            font=ctk.CTkFont(size=18, weight="bold"), anchor="w"
        )
        title.pack(anchor="w", pady=(0, 8))

        subtitle = ctk.CTkLabel(
            frame, text="Revise as configura\u00e7\u00f5es e inicie a convers\u00e3o.",
            font=ctk.CTkFont(size=12), text_color=COLORS["muted"], anchor="w"
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        self.summary_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.summary_frame.pack(fill="x")

        self.products_check_frame = ctk.CTkFrame(self.summary_frame, fg_color=COLORS["surface"], corner_radius=8)
        self.products_check_frame.pack(fill="x", pady=(0, 8))
        self.products_check_frame.grid_columnconfigure(1, weight=1)

        self.chk_products = ctk.CTkCheckBox(
            self.products_check_frame, text="Converter Mercadorias",
            variable=self.convert_products_var, font=ctk.CTkFont(size=13, weight="bold"),
            checkbox_width=22, checkbox_height=22, corner_radius=4,
            border_width=2, hover_color=COLORS["border"],
            fg_color=COLORS["amber"], border_color=COLORS["border"]
        )
        self.chk_products.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))

        self.products_summary = ctk.CTkLabel(
            self.products_check_frame, text="", font=ctk.CTkFont(size=11),
            text_color=COLORS["muted"], anchor="w", justify="left"
        )
        self.products_summary.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(2, 8))

        self.clients_check_frame = ctk.CTkFrame(self.summary_frame, fg_color=COLORS["surface"], corner_radius=8)
        self.clients_check_frame.pack(fill="x", pady=(0, 8))
        self.clients_check_frame.grid_columnconfigure(1, weight=1)

        self.chk_clients = ctk.CTkCheckBox(
            self.clients_check_frame, text="Converter Clientes/Fornecedores",
            variable=self.convert_clients_var, font=ctk.CTkFont(size=13, weight="bold"),
            checkbox_width=22, checkbox_height=22, corner_radius=4,
            border_width=2, hover_color=COLORS["border"],
            fg_color=COLORS["amber"], border_color=COLORS["border"]
        )
        self.chk_clients.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))

        self.clients_summary = ctk.CTkLabel(
            self.clients_check_frame, text="", font=ctk.CTkFont(size=11),
            text_color=COLORS["muted"], anchor="w", justify="left"
        )
        self.clients_summary.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(2, 8))

        self.btn_generate = ctk.CTkButton(
            frame,
            text="GERAR ARQUIVOS",
            command=self.start_conversion,
            fg_color=COLORS["green"],
            hover_color=COLORS["green_hover"],
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=8
        )
        self.btn_generate.pack(fill="x", pady=(8, 0))

    def create_navigation(self, parent):
        nav_frame = ctk.CTkFrame(parent, fg_color="transparent", height=44)
        nav_frame.pack(fill="x", pady=(8, 8))

        self.btn_back = ctk.CTkButton(
            nav_frame, text="\u2190 Voltar",
            command=self.go_back,
            fg_color="transparent",
            text_color=COLORS["amber"],
            hover_color=COLORS["border"],
            width=100, height=36,
            font=ctk.CTkFont(size=13),
            border_width=1,
            border_color=COLORS["amber"]
        )
        self.btn_back.pack(side="left")

        self.btn_next = ctk.CTkButton(
            nav_frame, text="Avan\u00e7ar \u2192",
            command=self.go_next,
            width=120, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=6
        )
        self.btn_next.pack(side="right")

    def show_step(self, index):
        for i, frame in enumerate(self.step_frames):
            frame.pack_forget() if i != index else frame.pack(fill="both", expand=True)

        self.current_step = index
        self.update_step_indicator()

        self.btn_back.configure(state="normal")
        if index == 0:
            self.btn_back.configure(state="disabled")

        if index == self.total_steps - 1:
            self.btn_next.pack_forget()
            self.update_summary()
        else:
            self.btn_next.pack(side="right")

    def update_summary(self):
        has_products = bool(self.product_sga_path.get())
        has_clients = bool(self.client_sga_path.get()) and bool(self.supplier_sga_path.get())

        if has_products:
            self.products_check_frame.pack(fill="x", pady=(0, 8))
            self.products_summary.configure(
                text=f"SGA: {os.path.basename(self.product_sga_path.get())}\n"
                     f"Sa\u00edda: {self.product_output_path.get()}"
            )
        else:
            self.products_check_frame.pack_forget()
            self.convert_products_var.set(False)

        if has_clients:
            self.clients_check_frame.pack(fill="x", pady=(0, 8))
            self.clients_summary.configure(
                text=f"Clientes: {os.path.basename(self.client_sga_path.get())}\n"
                     f"Fornecedores: {os.path.basename(self.supplier_sga_path.get())}\n"
                     f"Sa\u00edda: {self.client_output_path.get()}"
            )
        else:
            self.clients_check_frame.pack_forget()
            self.convert_clients_var.set(False)

        if has_products and has_clients:
            self.convert_products_var.set(True)
            self.convert_clients_var.set(True)

        if not has_products and not has_clients:
            self.btn_generate.configure(state="disabled", text="NENHUM ARQUIVO SELECIONADO")
        else:
            self.btn_generate.configure(state="normal", text="GERAR ARQUIVOS")

    def go_next(self):
        if self.current_step < self.total_steps - 1:
            self.show_step(self.current_step + 1)

    def go_back(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def select_product_sga(self):
        filename = filedialog.askopenfilename(
            title="Selecione a planilha de produtos SGA",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.product_sga_path.set(filename)

    def select_product_template(self):
        filename = filedialog.askopenfilename(
            title="Selecione o template SGAcloud (Mercadorias)",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.product_template_path.set(filename)

    def select_product_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar arquivo de sa\u00edda",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="MERCADORIAS_SGACLOUD.xlsx"
        )
        if filename:
            self.product_output_path.set(filename)

    def select_client_sga(self):
        filename = filedialog.askopenfilename(
            title="Selecione a planilha de clientes SGA",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.client_sga_path.set(filename)

    def select_supplier_sga(self):
        filename = filedialog.askopenfilename(
            title="Selecione a planilha de fornecedores SGA",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.supplier_sga_path.set(filename)

    def select_client_template(self):
        filename = filedialog.askopenfilename(
            title="Selecione o template SGAcloud (Clientes)",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.client_template_path.set(filename)

    def select_client_output(self):
        filename = filedialog.asksaveasfilename(
            title="Salvar arquivo de sa\u00edda",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="CLIENTES_SGACLOUD.xlsx"
        )
        if filename:
            self.client_output_path.set(filename)

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.root.update_idletasks()

    def update_progress(self, value, status):
        self.progress_bar.set(value)
        self.status_label.configure(text=status)
        self.root.update_idletasks()

    def start_conversion(self):
        if self.is_converting:
            return

        run_products = self.convert_products_var.get()
        run_clients = self.convert_clients_var.get()

        if not run_products and not run_clients:
            messagebox.showwarning("Aten\u00e7\u00e3o", "Selecione ao menos uma convers\u00e3o!")
            return

        self.is_converting = True
        self.btn_generate.configure(state="disabled", text="CONVERTENDO...")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

        thread = threading.Thread(target=self.run_conversion, args=(run_products, run_clients))
        thread.daemon = True
        thread.start()

    def run_conversion(self, run_products, run_clients):
        try:
            reader = SGAReader()
            converter = Converter()
            writer = XLSXWriter()
            ibge_lookup = IBGELookup()

            success_count = 0

            if run_products:
                self.log("Iniciando convers\u00e3o de Mercadorias...")
                self.update_progress(0.05, "Lendo planilha de produtos...")

                df_products = reader.read(self.product_sga_path.get())
                self.log(f"Lidos {len(df_products)} registros de produtos")
                self.update_progress(0.2, "Convertendo produtos...")

                df_converted = converter.convert_products(df_products)
                self.log(f"Convertidos {len(df_converted)} registros")
                self.update_progress(0.35, "Gerando arquivo...")

                Path(self.product_output_path.get()).parent.mkdir(parents=True, exist_ok=True)
                writer.write_products(
                    df_converted,
                    self.product_template_path.get(),
                    self.product_output_path.get()
                )
                self.log(f"\u2705 Mercadorias salvas em: {self.product_output_path.get()}")
                success_count += 1

            if run_clients:
                progress_start = 0.5 if run_products else 0.05
                self.update_progress(progress_start, "Lendo clientes e fornecedores...")

                df_clients = reader.read(self.client_sga_path.get())
                df_suppliers = reader.read(self.supplier_sga_path.get())
                self.log(f"Lidos {len(df_clients)} clientes e {len(df_suppliers)} fornecedores")
                self.update_progress(progress_start + 0.15, "Convertendo...")

                df_converted = converter.convert_clients_suppliers_no_ibge(
                    df_clients,
                    df_suppliers,
                    ibge_lookup,
                    default_cep=self.default_cep.get(),
                    handle_missing=self.handle_missing.get(),
                    fill_city=self.fill_city.get(),
                    fill_uf=self.fill_uf.get()
                )
                self.log(f"Convertidos {len(df_converted)} registros")
                self.update_progress(progress_start + 0.3, "Gerando arquivo...")

                Path(self.client_output_path.get()).parent.mkdir(parents=True, exist_ok=True)
                writer.write_clients(
                    df_converted,
                    self.client_template_path.get(),
                    self.client_output_path.get()
                )
                self.log(f"\u2705 Clientes/Fornecedores salvos em: {self.client_output_path.get()}")
                success_count += 1

            self.update_progress(1.0, "Conclu\u00eddo!")
            self.log(f"\n\u2705 Convers\u00e3o realizada com sucesso! ({success_count}/{2 if run_products and run_clients else 1})")

            parts = []
            if run_products:
                parts.append(f"Mercadorias: {self.product_output_path.get()}")
            if run_clients:
                parts.append(f"Clientes: {self.client_output_path.get()}")

            messagebox.showinfo(
                "Sucesso",
                f"Arquivos gerados com sucesso!\n\n" + "\n".join(parts)
            )

        except Exception as e:
            self.log(f"Erro: {str(e)}")
            self.update_progress(0, "Erro na convers\u00e3o")
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}")

        finally:
            self.is_converting = False
            self.btn_generate.configure(state="normal", text="GERAR ARQUIVOS")


if __name__ == "__main__":
    root = ctk.CTk()
    app = SGAConverterApp(root)
    root.mainloop()
