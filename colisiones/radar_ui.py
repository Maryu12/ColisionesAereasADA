# colisiones/ui_radar.py

import tkinter as tk
from tkinter import ttk
import math
from typing import List, Optional, Tuple
from .generador import generar_puntos
from .algoritmos import pares_en_riesgo
from .modelos import Avion, ResultadoColision

BG_COLOR = "#060714"      # Fondo general
CANVAS_BG = "#02030A"     # Fondo del radar
PRIMARY_COLOR = "#f1acff" 
ACCENT_COLOR = "#bf05e5"  
TEXT_COLOR = "#E5E5E5"   
GRID_COLOR = "#1F2933"   
RADAR_RING = "#ffb2e1"    # Anillos del radar
RADAR_SWEEP = "#ff009b"   # Línea del radar
POINT_COLOR = "#a0fff6"   # Aviones
HIGHLIGHT_COLOR = "#FFEA00"  # Aviones en posible colisión

PLANE_MAX_X = 1000
PLANE_MAX_Y = 1000


class InterfazColisiones:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Radar de Colisiones Aéreas - ADA I 2025")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("1000x720")

        # Estado del radar
        self.radar_angle: float = 0
        self.radar_line: Optional[int] = None


        self.aviones: List[Avion] = []
        self.ultimo_resultado: Optional[ResultadoColision] = None

        self._configurar_estilos()
        self._crear_layout()
        self._dibujar_radar_base()
        self._animar_radar()

    
    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Dark.TFrame", background=BG_COLOR)
        style.configure(
            "Dark.TLabel",
            background=BG_COLOR,
            foreground=TEXT_COLOR,
            font=("Segoe UI", 11),
        )
        style.configure(
            "DarkTitle.TLabel",
            background=BG_COLOR,
            foreground=PRIMARY_COLOR,
            font=("Segoe UI Semibold", 16),
        )
        style.configure(
            "Dark.TButton",
            background=PRIMARY_COLOR,
            foreground="#000000",
            font=("Segoe UI Semibold", 10),
            padding=6,
        )
        style.map("Dark.TButton", background=[("active", "#3CFCE0")])
        style.configure(
            "Dark.TEntry",
            fieldbackground="#111827",
            foreground=TEXT_COLOR,
            insertcolor=TEXT_COLOR,
        )

   
    def _crear_layout(self):
       
        top_frame = ttk.Frame(self.root, style="Dark.TFrame", padding=(20, 15))
        top_frame.pack(side=tk.TOP, fill=tk.X)

        header_frame = ttk.Frame(top_frame, style="Dark.TFrame")
        header_frame.pack(side=tk.TOP, fill=tk.X)

        # Logo 
        logo_canvas = tk.Canvas(
            header_frame,
            width=60,
            height=60,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        logo_canvas.pack(side=tk.LEFT, padx=(0, 10))
        logo_canvas.create_oval(8, 8, 52, 52, outline=PRIMARY_COLOR, width=2)
        logo_canvas.create_polygon(
            30, 12, 25, 28, 30, 48, 35, 28,
            fill=PRIMARY_COLOR,
            outline=PRIMARY_COLOR,
        )
        
        logo_canvas.create_polygon(
            18, 26, 30, 22, 42, 26, 30, 30,
            fill=BG_COLOR,
            outline=PRIMARY_COLOR,
            width=1,
        )

        logo_canvas.create_polygon(
            24, 42, 30, 40, 36, 42, 30, 45,
            fill=BG_COLOR,
            outline=PRIMARY_COLOR,
            width=1,
        )

        title_frame = ttk.Frame(header_frame, style="Dark.TFrame")
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        title_label = ttk.Label(
            title_frame,
            text="Radar de Detección de Posibles Colisiones Aéreas",
            style="DarkTitle.TLabel",
        )
        title_label.pack(side=tk.TOP, anchor="w")

        subtitle_label = ttk.Label(
            title_frame,
            text="Visualización de aeronaves en un plano 1000 x 1000",
            style="Dark.TLabel",
        )
        subtitle_label.pack(side=tk.TOP, anchor="w", pady=(2, 10))

        controls_frame = ttk.Frame(top_frame, style="Dark.TFrame")
        controls_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        ttk.Label(
            controls_frame, text="Número de aeronaves:", style="Dark.TLabel"
        ).pack(side=tk.LEFT)

        self.entry_n = ttk.Entry(controls_frame, width=8, style="Dark.TEntry")
        self.entry_n.pack(side=tk.LEFT, padx=6)

        ttk.Label(
            controls_frame, text="Umbral de colisión:", style="Dark.TLabel"
        ).pack(side=tk.LEFT, padx=(10, 0))

        self.entry_umbral = ttk.Entry(controls_frame, width=8, style="Dark.TEntry")
        self.entry_umbral.pack(side=tk.LEFT, padx=6)

        btn_generar = ttk.Button(
            controls_frame,
            text="Generar puntos",
            style="Dark.TButton",
            command=self.on_generar_puntos,
        )
        btn_generar.pack(side=tk.LEFT, padx=8)

        btn_detectar = ttk.Button(
            controls_frame,
            text="Detectar colisiones",
            style="Dark.TButton",
            command=self.on_detectar_colisiones,
        )
        btn_detectar.pack(side=tk.LEFT, padx=8)

        self.status_label = ttk.Label(
            controls_frame,
            text="Estado: esperando puntos...",
            style="Dark.TLabel",
        )
        self.status_label.pack(side=tk.RIGHT)

        center_frame = ttk.Frame(self.root, style="Dark.TFrame", padding=(10, 10))
        center_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            center_frame,
            width=700,
            height=600,
            bg=CANVAS_BG,
            highlightthickness=0,
        )
        self.canvas.pack(
            side=tk.LEFT, padx=(0, 10), pady=5, fill=tk.BOTH, expand=True
        )

        side_panel = ttk.Frame(center_frame, style="Dark.TFrame")
        side_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 5))

        ttk.Label(
            side_panel, text="Panel de información", style="DarkTitle.TLabel"
        ).pack(anchor="w", pady=(0, 10))

        info_text = (
            "• Ingresa N aeronaves y pulsa 'Generar puntos'.\n"
            "  Se usan coordenadas aleatorias en el plano 1000x1000.\n"
            "• El radar muestra la posición de cada avión.\n"
            "• 'Detectar colisiones' usa una búsqueda sobre todos los pares\n"
            "  (pares_en_riesgo) para encontrar TODAS las parejas cuya\n"
            "  distancia sea menor o igual al umbral.\n\n"
            "📏 Umbral de colisión:\n"
            "Distancia mínima (en unidades del plano 1000x1000) para\n"
            "considerar que dos aeronaves están en posible colisión.\n"
            "Si la distancia entre ellas ≤ umbral, se resaltan en el radar.\n"
        )

        self.info_label = tk.Text(
            side_panel,
            width=35,
            height=25,
            bg="#020617",
            fg=TEXT_COLOR,
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        self.info_label.insert(tk.END, info_text)
        self.info_label.configure(state="disabled")
        self.info_label.pack(fill=tk.BOTH, expand=True)

        autores_label = ttk.Label(
            side_panel,
            text="Responsables del proyecto: Maryury Villa y Karen Duque",
            font=("Segoe UI Semibold", 12),
            background=BG_COLOR,
            foreground=PRIMARY_COLOR,
        )
        autores_label.pack(side=tk.RIGHT)

 
    # radar
    def _dibujar_radar_base(self):
        self.canvas.delete("all")

        w = int(self.canvas["width"])
        h = int(self.canvas["height"])
        self.cx = w // 2
        self.cy = h // 2
        self.r = min(w, h) // 2 - 40

        self.canvas.create_text(
            self.cx,
            20,
            text="Plano cartesiano simulado 1000 x 1000",
            fill=PRIMARY_COLOR,
            font=("Segoe UI Semibold", 11),
        )

        self.canvas.create_rectangle(0, 0, w, h, fill=CANVAS_BG, outline="")
        step = 40
        for x in range(0, w, step):
            self.canvas.create_line(x, 0, x, h, fill=GRID_COLOR)
        for y in range(0, h, step):
            self.canvas.create_line(0, y, w, y, fill=GRID_COLOR)

        for factor in [0.3, 0.5, 0.7, 1.0]:
            r = self.r * factor
            self.canvas.create_oval(
                self.cx - r,
                self.cy - r,
                self.cx + r,
                self.cy + r,
                outline=RADAR_RING,
            )

        self.canvas.create_line(
            self.cx - self.r - 10,
            self.cy,
            self.cx + self.r + 10,
            self.cy,
            fill=RADAR_RING,
        )
        self.canvas.create_line(
            self.cx,
            self.cy - self.r - 10,
            self.cx,
            self.cy + self.r + 10,
            fill=RADAR_RING,
        )

        self.canvas.create_oval(
            self.cx - 5,
            self.cy - 5,
            self.cx + 5,
            self.cy + 5,
            fill=ACCENT_COLOR,
            outline="",
        )

        self.canvas.create_text(
            self.cx,
            self.cy + self.r + 25,
            text="Estación de control - Radar plano 1000 x 1000 (unidades simuladas)",
            fill=PRIMARY_COLOR,
            font=("Segoe UI", 11),
        )


    #  Animación del radar|
    def _animar_radar(self):
        if self.radar_line is not None:
            self.canvas.delete(self.radar_line)

        self.radar_angle = (self.radar_angle + 2) % 360
        angle_rad = math.radians(self.radar_angle)
        x_end = self.cx + self.r * math.cos(angle_rad)
        y_end = self.cy - self.r * math.sin(angle_rad)

        self.radar_line = self.canvas.create_line(
            self.cx,
            self.cy,
            x_end,
            y_end,
            fill=RADAR_SWEEP,
            width=2,
        )

        self.root.after(30, self._animar_radar)

   
    def _mapear_a_canvas(self, x: float, y: float) -> Tuple[float, float]:
        """
        Mapea coordenadas del plano [0,1000]x[0,1000] a la zona circular del radar.
        """
        nx = x / PLANE_MAX_X
        ny = y / PLANE_MAX_Y

        left = self.cx - self.r
        top = self.cy - self.r
        size = 2 * self.r

        cx = left + nx * size
        cy = top + (1 - ny) * size  # invertir eje y
        return cx, cy

    def _dibujar_avion(self, avion: Avion, color: str = POINT_COLOR, radio: int = 5):
        x, y = self._mapear_a_canvas(avion.x, avion.y)
        self.canvas.create_oval(
            x - radio,
            y - radio,
            x + radio,
            y + radio,
            fill=color,
            outline="",
        )


    def on_generar_puntos(self):
        self._dibujar_radar_base()
        self.aviones.clear()
        self.ultimo_resultado = None

        # Leer n
        try:
            n = int(self.entry_n.get())
        except ValueError:
            self.status_label.config(text="Estado: N inválido 👀")
            return

        if n <= 1:
            self.status_label.config(
                text="Estado: deben haber al menos 2 aeronaves."
            )
            return

    
        self.aviones = generar_puntos(
            n=n,
            max_x=PLANE_MAX_X,
            max_y=PLANE_MAX_Y,
            seed=42,
        )

        for avion in self.aviones:
            self._dibujar_avion(avion)

        self.status_label.config(
            text=f"Estado: {n} aeronaves generadas en el plano 1000x1000 ✈️"
        )

    def on_detectar_colisiones(self):
        if not self.aviones:
            self.status_label.config(
                text="Estado: genera primero las aeronaves."
            )
            return

        # Lee el umbral
        umbral_txt = self.entry_umbral.get().strip()
        try:
            umbral = float(umbral_txt)
        except ValueError:
            self.status_label.config(text="Estado: umbral inválido.")
            return

        if umbral <= 0:
            self.status_label.config(
                text="Estado: el umbral debe ser > 0 para detectar colisiones."
            )
            return

        # parejas en riesgo
        distancia_min, pares_riesgo = pares_en_riesgo(self.aviones, umbral)

        self._dibujar_radar_base()
        for avion in self.aviones:
            self._dibujar_avion(avion)

        if not pares_riesgo:
            msg = (
                f"Distancia mínima global: {distancia_min:.2f}. "
                f"No hay pares con distancia ≤ {umbral:.2f}."
            )
            self.status_label.config(text=f"Estado: {msg}")
            self.canvas.create_text(
                self.cx,
                self.cy - self.r - 25,
                text=msg,
                fill=ACCENT_COLOR,
                font=("Segoe UI Semibold", 11),
            )
            return

    
        for a, b in pares_riesgo:
            x1, y1 = self._mapear_a_canvas(a.x, a.y)
            x2, y2 = self._mapear_a_canvas(b.x, b.y)

            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=HIGHLIGHT_COLOR,
                width=2,
            )
            self._dibujar_avion(a, color=HIGHLIGHT_COLOR, radio=6)
            self._dibujar_avion(b, color=HIGHLIGHT_COLOR, radio=6)

        msg = (
            f"{len(pares_riesgo)} posibles colisiones "
            f"(distancia ≤ {umbral:.2f}). "
            f"Distancia mínima global: {distancia_min:.2f}"
        )
        self.status_label.config(text=f"Estado: {msg}")
        self.canvas.create_text(
            self.cx,
            self.cy - self.r - 25,
            text=msg,
            fill=ACCENT_COLOR,
            font=("Segoe UI Semibold", 11),
        )


def run():
    root = tk.Tk()
    app = InterfazColisiones(root)
    root.mainloop()


if __name__ == "__main__":
    run()
