import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import json
from database import (
    init_db, sincronizar_bases_json, validar_bi_angolano, 
    validar_telefone_angolano, obter_saudacao_fuso, DB_NAME, 
    OPCOES_CARGOS, OPCOES_SANGUE
)

class AdminSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🏛️ Painel Administrativo de Gestão Agrícola")
        self.geometry("1180x750")
        self.configure(bg="#1E1E2E")
        
        init_db()
        self.setup_styles()

        header = tk.Frame(self, bg="#2D2D3F", height=60)
        header.pack(fill="x", side="top")
        lbl_titulo = tk.Label(header, text="PAINEL DE CONTROLO DE RECURSOS HUMANOS E ACESSOS", 
                              font=("Helvetica", 14, "bold"), fg="#00FFC6", bg="#2D2D3F")
        lbl_titulo.pack(pady=15)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tab_registro_rh = ttk.Frame(self.notebook, style="TFrame")
        self.tab_lista_funcionarios = ttk.Frame(self.notebook, style="TFrame")
        self.tab_analise_subscricoes = ttk.Frame(self.notebook, style="TFrame")
        self.tab_gestao_acessos = ttk.Frame(self.notebook, style="TFrame")
        self.tab_previsoes = ttk.Frame(self.notebook, style="TFrame")

        self.notebook.add(self.tab_registro_rh, text=" 📝 Registrar Funcionário ")
        self.notebook.add(self.tab_lista_funcionarios, text=" 👥 Quadro de Funcionários ")
        self.notebook.add(self.tab_analise_subscricoes, text=" 📩 Análise de Subscrições ")
        self.notebook.add(self.tab_gestao_acessos, text=" 🔑 Acessos Aprovados ")
        self.notebook.add(self.tab_previsoes, text=" 🌦️ Histórico de Previsões ")

        self.setup_rh_form()
        self.setup_lista_funcionarios()
        self.setup_analise_subscricoes()
        self.setup_gestao_acessos()
        self.setup_aba_previsoes()

        self.iniciar_atualizacao_tempo_real()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(".", background="#1E1E2E", foreground="#FFFFFF", font=("Segoe UI", 10))
        style.configure("TFrame", background="#1E1E2E")
        style.configure("TNotebook", background="#1E1E2E", borderwidth=0)
        style.configure("TNotebook.Tab", background="#2D2D3F", foreground="#A6ADC8", padding=[12, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#00ADB5")], foreground=[("selected", "#FFFFFF")])

        style.configure("TLabelFrame", background="#252538", foreground="#00FFC6", borderwidth=1, relief="solid")
        style.configure("TLabelFrame.Label", background="#252538", foreground="#00FFC6", font=("Segoe UI", 11, "bold"))
        
        style.configure("TEntry", fieldbackground="#FFFFFF", foreground="#000000", insertcolor="#000000")
        style.map("TEntry", fieldbackground=[("active", "#FFFFFF"), ("focus", "#FFFFFF")], foreground=[("active", "#000000"), ("focus", "#000000")])
        
        style.configure("TCombobox", fieldbackground="#FFFFFF", foreground="#000000", selectbackground="#00ADB5", selectforeground="#FFFFFF")
        style.map("TCombobox", 
                  fieldbackground=[("readonly", "#FFFFFF"), ("active", "#FFFFFF")], 
                  foreground=[("readonly", "#000000"), ("active", "#000000")])

        style.configure("Treeview", background="#252538", foreground="#FFFFFF", fieldbackground="#252538", rowheight=28)
        style.configure("Treeview.Heading", background="#00ADB5", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#393E46")])

    def setup_rh_form(self):
        frame = ttk.LabelFrame(self.tab_registro_rh, text=" Ficha de Cadastro do Funcionário ")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        fields_c1 = [
            ("Número do BI (14 Caracteres):", "bi"),
            ("Nome Completo:", "nome"),
            ("Data de Nascimento:", "nascimento"),
            ("Número de Telefone:", "telefone"),
            ("Género:", "genero"),
            ("Função / Cargo:", "cargo"),
        ]

        fields_c2 = [
            ("Tipo Sanguíneo:", "sangue"),
            ("Província:", "provincia"),
            ("Município:", "municipio"),
            ("Bairro:", "bairro"),
            ("Rua:", "rua"),
        ]

        self.inputs = {}

        for i, (label_text, key) in enumerate(fields_c1):
            lbl = ttk.Label(frame, text=label_text)
            lbl.grid(row=i, column=0, sticky="w", padx=15, pady=8)

            if key == "genero":
                cb = ttk.Combobox(frame, values=["Masculino", "Feminino"], state="readonly", width=35)
                cb.grid(row=i, column=1, sticky="w", padx=10, pady=8)
                self.inputs[key] = cb
            elif key == "cargo":
                cb = ttk.Combobox(frame, values=OPCOES_CARGOS, state="readonly", width=35)
                cb.grid(row=i, column=1, sticky="w", padx=10, pady=8)
                self.inputs[key] = cb
            elif key == "nascimento":
                ent = DateEntry(frame, width=33, background="#00ADB5", foreground="white", headersbackground="#00ADB5", normalforeground="black", date_pattern="yyyy-mm-dd")
                ent.grid(row=i, column=1, sticky="w", padx=10, pady=8)
                self.inputs[key] = ent
            else:
                ent = ttk.Entry(frame, width=38)
                ent.grid(row=i, column=1, sticky="w", padx=10, pady=8)
                self.inputs[key] = ent

        for i, (label_text, key) in enumerate(fields_c2):
            lbl = ttk.Label(frame, text=label_text)
            lbl.grid(row=i, column=2, sticky="w", padx=15, pady=8)

            if key == "sangue":
                cb = ttk.Combobox(frame, values=OPCOES_SANGUE, state="readonly", width=35)
                cb.grid(row=i, column=3, sticky="w", padx=10, pady=8)
                self.inputs[key] = cb
            else:
                ent = ttk.Entry(frame, width=38)
                ent.grid(row=i, column=3, sticky="w", padx=10, pady=8)
                self.inputs[key] = ent

        lbl_casa = ttk.Label(frame, text="Número da Casa:")
        lbl_casa.grid(row=len(fields_c2), column=2, sticky="w", padx=15, pady=8)
        
        frame_casa = ttk.Frame(frame)
        frame_casa.grid(row=len(fields_c2), column=3, sticky="w", padx=10, pady=8)
        
        self.ent_numero_casa = ttk.Entry(frame_casa, width=15)
        self.ent_numero_casa.pack(side="left", padx=(0, 10))
        
        self.var_sem_numero = tk.BooleanVar()
        chk_sem_numero = ttk.Checkbutton(
            frame_casa, 
            text="Sem número", 
            variable=self.var_sem_numero,
            command=self.toggle_casa_num
        )
        chk_sem_numero.pack(side="left")

        btn_salvar = tk.Button(
            frame, text="💾 CADASTRAR FUNCIONÁRIO", bg="#00E676", fg="#000000",
            font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=8,
            cursor="hand2", command=self.salvar_funcionario
        )
        btn_salvar.grid(row=7, column=0, columnspan=4, pady=25)

    def toggle_casa_num(self):
        if self.var_sem_numero.get():
            self.ent_numero_casa.delete(0, tk.END)
            self.ent_numero_casa.config(state="disabled")
        else:
            self.ent_numero_casa.config(state="normal")

    def salvar_funcionario(self):
        bi = self.inputs["bi"].get().strip()
        tel = self.inputs["telefone"].get().strip()

        if not validar_bi_angolano(bi):
            messagebox.showerror("Erro de Validação", "Número do BI angolano inválido! Deve conter 14 caracteres.")
            return

        if not validar_telefone_angolano(tel):
            messagebox.showerror("Erro de Validação", "Telefone inválido! Deve conter 9 dígitos (ex.: 974453534).")
            return

        if not self.inputs["cargo"].get():
            messagebox.showerror("Erro", "Por favor selecione a Função/Cargo na lista.")
            return

        if not self.inputs["sangue"].get():
            messagebox.showerror("Erro", "Por favor selecione o Tipo Sanguíneo.")
            return

        num_casa = "Sem número" if self.var_sem_numero.get() else self.ent_numero_casa.get().strip()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO funcionarios (bi, nome_completo, data_nascimento, telefone, genero, cargo, tipo_sanguineo, provincia, municipio, bairro, rua, numero_casa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bi,
                self.inputs["nome"].get().strip(),
                self.inputs["nascimento"].get(),
                tel,
                self.inputs["genero"].get(),
                self.inputs["cargo"].get(),
                self.inputs["sangue"].get(),
                self.inputs["provincia"].get().strip(),
                self.inputs["municipio"].get().strip(),
                self.inputs["bairro"].get().strip(),
                self.inputs["rua"].get().strip(),
                num_casa
            ))
            conn.commit()
            sincronizar_bases_json()
            messagebox.showinfo("Sucesso", "Funcionário registrado e sincronizado no ficheiro JSON com sucesso!")
            self.atualizar_quadro_funcionarios()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um funcionário cadastrado com este BI.")
        finally:
            conn.close()

    def setup_lista_funcionarios(self):
        columns = ("id", "bi", "nome", "telefone", "cargo", "sangue", "provincia")
        self.tree_rh = ttk.Treeview(self.tab_lista_funcionarios, columns=columns, show="headings")
        
        for col in columns:
            self.tree_rh.heading(col, text=col.upper())
            self.tree_rh.column(col, width=140, anchor="center")
            
        self.tree_rh.pack(fill="both", expand=True, padx=10, pady=10)
        self.atualizar_quadro_funcionarios()

    def atualizar_quadro_funcionarios(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, bi, nome_completo, telefone, cargo, tipo_sanguineo, provincia FROM funcionarios ORDER BY nome_completo ASC")
        rows = cursor.fetchall()
        conn.close()

        current_items = [self.tree_rh.item(child)["values"] for child in self.tree_rh.get_children()]
        new_items = [list(r) for r in rows]
        
        if current_items != new_items:
            for item in self.tree_rh.get_children():
                self.tree_rh.delete(item)
            for row in rows:
                self.tree_rh.insert("", tk.END, values=row)

    def setup_analise_subscricoes(self):
        columns = ("id", "bi", "nome", "cargo", "telefone", "status")
        self.tree_sub = ttk.Treeview(self.tab_analise_subscricoes, columns=columns, show="headings")
        for col in columns:
            self.tree_sub.heading(col, text=col.upper())
            self.tree_sub.column(col, width=150, anchor="center")
            
        self.tree_sub.pack(fill="both", expand=True, padx=10, pady=10)
        
        frame_actions = ttk.Frame(self.tab_analise_subscricoes)
        frame_actions.pack(pady=10)
        
        btn_aprovar = tk.Button(frame_actions, text="✅ APROVAR SUBSCRIÇÃO", bg="#00E676", fg="black", font=("Segoe UI", 10, "bold"), padx=15, command=self.aprovar_subscricao)
        btn_aprovar.pack(side="left", padx=10)
        
        btn_recusar = tk.Button(frame_actions, text="❌ RECUSAR SUBSCRIÇÃO", bg="#FF5252", fg="white", font=("Segoe UI", 10, "bold"), padx=15, command=self.recusar_subscricao)
        btn_recusar.pack(side="left", padx=10)
        
        self.carregar_subscricoes()

    def carregar_subscricoes(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, bi, nome_usuario, cargo, telefone, status FROM usuarios_sistema WHERE status = 'EM_ANALISE'")
        rows = cursor.fetchall()
        conn.close()

        current_ids = set(self.tree_sub.get_children())
        new_ids_map = {str(r[0]): r for r in rows}

        if set(new_ids_map.keys()) != set([self.tree_sub.item(c)["values"][0] for c in current_ids if self.tree_sub.item(c)["values"]]):
            for item in self.tree_sub.get_children():
                self.tree_sub.delete(item)
            for row in rows:
                self.tree_sub.insert("", tk.END, values=row)

    def aprovar_subscricao(self):
        selected = self.tree_sub.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pedido para aprovar.")
            return
            
        item_vals = self.tree_sub.item(selected[0], "values")
        user_id, bi, nome, cargo, telefone, _ = item_vals
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios_sistema SET status = 'APROVADO' WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

        sincronizar_bases_json()
        messagebox.showinfo("Sucesso", f"Subscrição aprovada para {nome}. Base JSON atualizada!")
        self.carregar_subscricoes()
        self.carregar_acessos_aprovados()

    def recusar_subscricao(self):
        selected = self.tree_sub.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pedido para recusar.")
            return
            
        item_vals = self.tree_sub.item(selected[0], "values")
        user_id = item_vals[0]
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios_sistema SET status = 'RECUSADO' WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

        sincronizar_bases_json()
        messagebox.showinfo("Sucesso", "Subscrição recusada.")
        self.carregar_subscricoes()

    def setup_gestao_acessos(self):
        columns = ("id", "bi", "nome", "cargo", "telefone")
        self.tree_aprovados = ttk.Treeview(self.tab_gestao_acessos, columns=columns, show="headings")
        for col in columns:
            self.tree_aprovados.heading(col, text=col.upper())
            self.tree_aprovados.column(col, width=180, anchor="center")
            
        self.tree_aprovados.pack(fill="both", expand=True, padx=10, pady=10)
        self.carregar_acessos_aprovados()

    def carregar_acessos_aprovados(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, bi, nome_usuario, cargo, telefone FROM usuarios_sistema WHERE status = 'APROVADO'")
        rows = cursor.fetchall()
        conn.close()

        current_items = [self.tree_aprovados.item(child)["values"] for child in self.tree_aprovados.get_children()]
        new_items = [list(r) for r in rows]

        if current_items != new_items:
            for item in self.tree_aprovados.get_children():
                self.tree_aprovados.delete(item)
            for row in rows:
                self.tree_aprovados.insert("", tk.END, values=row)

    def setup_aba_previsoes(self):
        columns = ("id", "data_previsao", "precipitacao", "temp_solo", "humidade", "criado_em")
        self.tree_prev = ttk.Treeview(self.tab_previsoes, columns=columns, show="headings")
        for col in columns:
            self.tree_prev.heading(col, text=col.upper())
            self.tree_prev.column(col, width=150, anchor="center")
        self.tree_prev.pack(fill="both", expand=True, padx=10, pady=10)

        btn_atualizar = tk.Button(self.tab_previsoes, text="🔄 Atualizar Lista de Previsões", bg="#00ADB5", fg="white", font=("Segoe UI", 10, "bold"), command=self.carregar_previsoes)
        btn_atualizar.pack(pady=10)
        self.carregar_previsoes()

    def carregar_previsoes(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, data_previsao, precipitacao, temp_solo, humidade, criado_em FROM previsoes_historico ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        current_items = [self.tree_prev.item(child)["values"] for child in self.tree_prev.get_children()]
        new_items = [list(r) for r in rows]

        if current_items != new_items:
            for item in self.tree_prev.get_children():
                self.tree_prev.delete(item)
            for row in rows:
                self.tree_prev.insert("", tk.END, values=row)

    def iniciar_atualizacao_tempo_real(self):
        try:
            sincronizar_bases_json()
            self.carregar_subscricoes()
            self.carregar_acessos_aprovados()
            self.carregar_quadro_funcionarios_silencioso()
            self.carregar_previsoes_silencioso()
        except Exception as e:
            print(f"Erro na sincronização em tempo real: {e}")
        finally:
            self.after(5000, self.iniciar_atualizacao_tempo_real)

    def carregar_quadro_funcionarios_silencioso(self):
        self.atualizar_quadro_funcionarios()

    def carregar_previsoes_silencioso(self):
        self.carregar_previsoes()

if __name__ == "__main__":
    app = AdminSystem()
    app.mainloop()