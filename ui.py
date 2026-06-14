import queue
import threading
import json
import logging

import customtkinter as ctk
from datetime import datetime

from paths import CONFIG_PATH
from database import criar_banco
from logger_setup import configurar_logs
from monitor import monitorar, parar


# ── Tema ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

COR_BG        = "#1C1C1E"
COR_CARD      = "#2C2C2E"
COR_BORDA     = "#3A3A3C"
COR_LARANJA   = "#E07A3A"
COR_ONLINE    = "#32D74B"
COR_OFFLINE   = "#FF453A"
COR_AGUARD    = "#888888"
COR_ENVIADA   = "#4CA3FF"
COR_TEXTO     = "#FFFFFF"
COR_MUTED     = "#888888"

FONTE_NOME    = ("Segoe UI", 13, "bold")
FONTE_IP      = ("Consolas", 11)
FONTE_STATUS  = ("Segoe UI", 11, "bold")
FONTE_BADGE   = ("Segoe UI", 10)
FONTE_META    = ("Segoe UI", 11)
FONTE_LOGO    = ("Segoe UI", 18, "bold")


def carregar_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


# ── Card de dispositivo ──────────────────────────────────────────────────────
class CardDispositivo(ctk.CTkFrame):

    def __init__(self, master, nome, ip, tipo, **kwargs):
        super().__init__(
            master,
            fg_color=COR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COR_BORDA,
            **kwargs
        )

        self.nome  = nome
        self.ip    = ip
        self._status_atual = None

        self.grid_columnconfigure(0, weight=1)

        # Linha principal
        linha = ctk.CTkFrame(self, fg_color="transparent")
        linha.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        linha.grid_columnconfigure(1, weight=1)

        self.dot = ctk.CTkLabel(linha, text="●", font=("Segoe UI", 16), text_color=COR_AGUARD)
        self.dot.grid(row=0, column=0, padx=(0, 10))

        info = ctk.CTkFrame(linha, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(info, text=nome, font=FONTE_NOME, text_color=COR_TEXTO).pack(anchor="w")
        ctk.CTkLabel(info, text=ip,   font=FONTE_IP,   text_color=COR_MUTED).pack(anchor="w")

        self.lbl_status = ctk.CTkLabel(
            linha, text="Aguardando", font=FONTE_STATUS,
            text_color=COR_AGUARD, width=90, anchor="e"
        )
        self.lbl_status.grid(row=0, column=2, padx=(8, 0))

        # Linha de badges
        self.frame_badges = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_badges.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))

        tipo_txt = tipo.upper() if tipo else "DISPOSITIVO"
        ctk.CTkLabel(
            self.frame_badges,
            text=tipo_txt,
            font=FONTE_BADGE,
            text_color=COR_MUTED
        ).pack(side="left")

        self.lbl_enviada = ctk.CTkLabel(
            self.frame_badges,
            text="",
            font=FONTE_BADGE,
            text_color=COR_ENVIADA
        )
        self.lbl_enviada.pack(side="right")

    def atualizar(self, status, telegram_ok):
        if status == "ONLINE":
            cor_dot    = COR_ONLINE
            cor_status = COR_ONLINE
            txt_status = "Online"
            cor_borda  = COR_BORDA

            if self._status_atual == "OFFLINE" and telegram_ok:
                self.lbl_enviada.configure(text="✓ Mensagem enviada!")
            else:
                self.lbl_enviada.configure(text="")

        elif status == "OFFLINE":
            cor_dot    = COR_OFFLINE
            cor_status = COR_OFFLINE
            txt_status = "Offline"
            cor_borda  = "#5A2020"

            if self._status_atual != "OFFLINE" and telegram_ok:
                self.lbl_enviada.configure(text="✓ Mensagem enviada!")
            elif self._status_atual != "OFFLINE":
                self.lbl_enviada.configure(text="")

        else:
            cor_dot    = COR_AGUARD
            cor_status = COR_AGUARD
            txt_status = "Aguardando"
            cor_borda  = COR_BORDA
            self.lbl_enviada.configure(text="")

        self.dot.configure(text_color=cor_dot)
        self.lbl_status.configure(text=txt_status, text_color=cor_status)
        self.configure(border_color=cor_borda)

        self._status_atual = status


# ── Janela principal ─────────────────────────────────────────────────────────
class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("GestãoIP")
        self.geometry("560x640")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)

        self._fila     = queue.Queue()
        self._cards    = {}
        self._config   = None
        self._thread   = None

        self._construir_ui()
        self._iniciar_monitoramento()
        self.after(300, self._processar_fila)
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _construir_ui(self):
        try:
            self._config = carregar_config()
        except Exception as e:
            logging.error("Erro ao carregar config: %s", e)
            self._config = {"cliente": "—", "equipamentos": []}

        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color="#232325", corner_radius=0, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(logo_frame, text="Gestão", font=FONTE_LOGO, text_color=COR_TEXTO).pack(side="left")
        ctk.CTkLabel(logo_frame, text="IP",     font=FONTE_LOGO, text_color=COR_LARANJA).pack(side="left")

        # Métricas
        frame_metricas = ctk.CTkFrame(self, fg_color="transparent")
        frame_metricas.pack(fill="x", padx=20, pady=(20, 0))

        self.lbl_total   = self._metrica(frame_metricas, "Total",   "0")
        self.lbl_online  = self._metrica(frame_metricas, "Online",  "0", COR_ONLINE)
        self.lbl_offline = self._metrica(frame_metricas, "Offline", "0", COR_OFFLINE)

        # Título da lista
        ctk.CTkLabel(
            self,
            text="EQUIPAMENTOS MONITORADOS",
            font=("Segoe UI", 11, "bold"),
            text_color=COR_MUTED
        ).pack(anchor="w", padx=20, pady=(18, 6))

        # Área dos cards
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", scrollbar_button_color=COR_BORDA
        )
        self.scroll.pack(fill="both", expand=True, padx=20)

        equipamentos = self._config.get("equipamentos", [])
        self.lbl_total.configure(text=str(len(equipamentos)))

        for eq in equipamentos:
            card = CardDispositivo(
                self.scroll,
                nome=eq["nome"],
                ip=eq["ip"],
                tipo=eq.get("tipo", ""),
            )
            card.pack(fill="x", pady=5)
            self._cards[eq["ip"]] = card

        # Rodapé
        rodape = ctk.CTkFrame(self, fg_color="#232325", corner_radius=0, height=36)
        rodape.pack(fill="x", side="bottom")
        rodape.pack_propagate(False)

        self.lbl_ultima = ctk.CTkLabel(
            rodape,
            text="Iniciando monitoramento...",
            font=FONTE_META,
            text_color=COR_MUTED
        )
        self.lbl_ultima.place(relx=0.5, rely=0.5, anchor="center")

    def _metrica(self, parent, label, valor, cor=None):
        frame = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=8)
        frame.pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkLabel(frame, text=label, font=FONTE_META, text_color=COR_MUTED).pack(pady=(10, 0))
        lbl = ctk.CTkLabel(frame, text=valor, font=("Segoe UI", 22, "bold"), text_color=cor or COR_TEXTO)
        lbl.pack(pady=(2, 10))
        return lbl

    def _iniciar_monitoramento(self):
        if not self._config:
            return

        criar_banco()

        def callback(nome, ip, status, telegram_ok):
            self._fila.put((ip, status, telegram_ok))

        self._thread = threading.Thread(
            target=monitorar,
            args=(self._config, callback),
            daemon=True
        )
        self._thread.start()

    def _processar_fila(self):
        online  = 0
        offline = 0

        try:
            while True:
                ip, status, telegram_ok = self._fila.get_nowait()
                card = self._cards.get(ip)
                if card:
                    card.atualizar(status, telegram_ok)
        except queue.Empty:
            pass

        for card in self._cards.values():
            s = card._status_atual
            if s == "ONLINE":
                online += 1
            elif s == "OFFLINE":
                offline += 1

        self.lbl_online.configure(text=str(online))
        self.lbl_offline.configure(text=str(offline))
        self.lbl_ultima.configure(
            text=f"Última verificação: {datetime.now().strftime('%H:%M:%S')}"
        )

        self.after(300, self._processar_fila)

    def _ao_fechar(self):
        parar()
        self.destroy()


def iniciar():
    configurar_logs()
    app = App()
    app.mainloop()