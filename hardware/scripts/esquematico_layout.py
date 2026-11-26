# -*- coding: utf-8 -*-
"""
Disposición del esquemático cableado, rev 0.6 (lo usa generar_esquematico.py).
Hoja A3. Coordenadas en mm, múltiplos de 1.27. Rotación en grados (antihorario).

Criterios de dibujo:
  - Un solo circuito: el riel DC+ sale del puente y llega con un cable continuo al
    drenaje de Q1 (como en los esquemáticos de fuentes de referencia).
  - Flujo de izquierda a derecha y de mayor a menor tensión: entrada AC -> puente
    -> bus DC -> Q1 -> RS1-RS4 -> T1A -> LEDs. El control (U1) va debajo.
  - Tierras con la convención estándar: GND (= DC- = LED-) con el símbolo de tierra
    de KiCad; la tierra flotante del controlador (fuente de Q1) usa el mismo
    símbolo con otro nombre, GND_U1, como se hace con PGND / SGND.
  - Sin cruces de cables. Bloques punteados por etapa. Valores estándar (DNP para
    no montados). El circuito se centra automáticamente en la hoja.

T1 tiene dos unidades: T1A (devanado principal TC-TD) y T1B (devanado auxiliar TA-TB).
"""

PAPEL = "A3"

YR = 50.80                      # riel DC+ y bus del nodo de conmutación
YL, YN = 58.42, 96.52           # línea L y línea N
BX = 113.03                     # bus izquierdo del puente (GND)
NODO = BX + 15.24
BD = BX + 30.48                 # bus derecho del puente (DC+)
YLED = 66.04                    # riel LED+
DY = 10.16                      # desplazamiento vertical del bloque de control


def c(x, y):
    """Coordenada del bloque de control (desplazado DY hacia abajo)."""
    return (x, round(y + DY, 2))


LAYOUT = {
    # ---- Entrada AC y rectificador ----
    "P1": (20.32, 76.20, 0),
    "F1": (40.64, YL, 90), "R1": (40.64, YN, 90),
    "VR1": (52.07, 77.47, 180), "LF1": (68.58, 77.47, 180),
    "VR2": (82.55, 77.47, 0), "CX1": (93.98, 77.47, 180),
    "L1": (101.60, 102.87, 90), "RL1": (101.60, 110.49, 90),
    "D1": (BX + 7.62, 67.31, 180), "D2": (BX + 22.86, 67.31, 180),
    "D4": (BX + 7.62, 87.63, 180), "D3": (BX + 22.86, 87.63, 180),
    "C6": (151.13, 57.15, 0), "VR3": (166.37, 57.15, 180),
    # ---- Opción no montada (C3.1 medido en DC+) y C1 sin conexión conocida ----
    "C3": (181.61, 57.15, 0), "D5": (181.61, 68.58, 270),
    "R3": (181.61, 80.01, 0), "R2": (181.61, 91.44, 0), "CE1": (191.77, 80.01, 0),
    "C1": (191.77, 101.60, 0),
    # ---- Etapa de potencia ----
    "R4": (203.20, 57.15, 180), "R5": (203.20, 68.58, 0),
    "Q1": (226.06, 53.34, 90),
    "R7": (226.06, 63.50, 180), "D6": (218.44, 63.50, 90), "R8": (231.14, 80.01, 180),
    "D8": (241.30, 57.15, 270),
    "R13": (261.62, 57.15, 180), "C5": (261.62, 68.58, 180),
    "RS1": (274.32, 57.15, 180), "RS2": (284.48, 57.15, 180),
    "RS3": (294.64, 57.15, 180), "RS4": (304.80, 57.15, 180),
    "T1": [(322.58, YLED, 0, 1), c(186.69, 151.13) + (0, 2)],
    "CE3": (337.82, 73.66, 0), "CE4": (353.06, 73.66, 0),
    "R14": (368.30, 73.66, 0), "R15": (378.46, 73.66, 0),
    "J1": (398.78, 68.58, 0),
    # ---- Control ----
    "U1": c(226.06, 120.65) + (0,),
    "R12": c(245.11, 120.65) + (270,),
    "D7": c(194.31, 118.11) + (180,), "R6": c(205.74, 118.11) + (90,),
    "R11": c(195.58, 130.81) + (90,), "R9": c(205.74, 138.43) + (0,),
    "R10": c(231.14, 138.43) + (0,), "C4": c(231.14, 149.86) + (0,),
    "CE2": c(254.00, 140.97) + (0,), "C2": c(269.24, 140.97) + (0,),
}

CABLES = [
    # ---- Entrada AC (P1 espejado: pin 1 = L arriba, pin 2 = N abajo) ----
    [(25.40, 76.20), (30.48, 76.20), (30.48, YL), (36.83, YL)],
    [(25.40, 78.74), (27.94, 78.74), (27.94, YN), (36.83, YN)],
    [(44.45, YL), (NODO, YL), (NODO, 67.31)],
    [(44.45, YN), (NODO, YN), (NODO, 87.63)],
    [(52.07, 73.66), (52.07, YL)], [(52.07, 81.28), (52.07, YN)],                  # VR1
    [(63.50, 74.93), (63.50, YL)], [(73.66, 74.93), (73.66, YL)],                  # LF1 (puenteado)
    [(63.50, 80.01), (63.50, YN)], [(73.66, 80.01), (73.66, YN)],
    [(82.55, 73.66), (82.55, YL)], [(82.55, 81.28), (82.55, YN)],                  # VR2
    [(93.98, 73.66), (93.98, YL)], [(93.98, 81.28), (93.98, YN)],                  # CX1
    [(97.79, 102.87), (97.79, YN)], [(105.41, 102.87), (105.41, YN)],              # L1 (puenteado)
    [(97.79, 110.49), (97.79, 102.87)], [(105.41, 110.49), (105.41, 102.87)],      # RL1 // L1
    # ---- Puente ----
    [(BX + 11.43, 67.31), (BX + 19.05, 67.31)], [(BX + 11.43, 87.63), (BX + 19.05, 87.63)],
    [(BX + 3.81, 67.31), (BX, 67.31), (BX, 90.17)], [(BX + 3.81, 87.63), (BX, 87.63)],
    [(BX + 26.67, 67.31), (BD, 67.31), (BD, 87.63), (BX + 26.67, 87.63)],
    # ---- Riel DC+: puente -> C6, VR3, opción DNP, arranque -> drenaje de Q1 ----
    [(BD, 67.31), (BD, YR), (220.98, YR)],
    [(151.13, 53.34), (151.13, YR)], [(151.13, 60.96), (151.13, 63.50)],          # C6
    [(166.37, 53.34), (166.37, YR)], [(166.37, 60.96), (166.37, 63.50)],          # VR3
    [(181.61, 53.34), (181.61, YR)], [(181.61, 60.96), (181.61, 64.77)],          # C3 - D5
    [(181.61, 72.39), (181.61, 76.20)], [(181.61, 74.93), (191.77, 74.93), (191.77, 76.20)],
    [(181.61, 83.82), (181.61, 87.63)],                                           # R3 - R2
    [(203.20, 53.34), (203.20, YR)], [(203.20, 60.96), (203.20, 64.77)],          # R4 - R5
    [(203.20, 72.39), (203.20, 78.74), (208.28, 78.74)],                          # R5 -> VDD
    # ---- Red de compuerta (debajo de Q1): R7 // D6, cátodo de D6 hacia U1 ----
    [(218.44, 59.69), (218.44, 58.42), (226.06, 58.42), (226.06, 59.69)],
    [(218.44, 67.31), (218.44, 69.85), (226.06, 69.85)],
    [(226.06, 67.31), c(226.06, 110.49)],                                         # GATE de U1
    [(226.06, 74.93), (231.14, 74.93), (231.14, 76.20)], [(231.14, 83.82), (231.14, 86.36)],  # R8
    # ---- Nodo de conmutación: fuente de Q1 -> D8, RC (DNP), RS1-RS4 ----
    [(231.14, YR), (304.80, YR)],
    [(233.68, YR), (233.68, 53.34)],                                              # GND_U1
    [(241.30, YR), (241.30, 53.34)], [(241.30, 60.96), (241.30, 63.50)],          # D8
    [(261.62, YR), (261.62, 53.34)], [(261.62, 60.96), (261.62, 64.77)], [(261.62, 72.39), (261.62, 74.93)],
    [(274.32, YR), (274.32, 53.34)], [(284.48, YR), (284.48, 53.34)],
    [(294.64, YR), (294.64, 53.34)], [(304.80, YR), (304.80, 53.34)],
    [(274.32, 60.96), (274.32, YLED)], [(284.48, 60.96), (284.48, YLED)],
    [(294.64, 60.96), (294.64, YLED)], [(304.80, 60.96), (304.80, YLED)],
    [(274.32, YLED), (314.96, YLED)],                                             # RS -> T1A (TC)
    # ---- Salida: TD -> LED+ -> J1 ----
    [(330.20, YLED), (393.70, YLED)],
    [(337.82, 69.85), (337.82, YLED)], [(337.82, 77.47), (337.82, 80.01)],
    [(353.06, 69.85), (353.06, YLED)], [(353.06, 77.47), (353.06, 80.01)],
    [(368.30, 69.85), (368.30, YLED)], [(368.30, 77.47), (368.30, 80.01)],
    [(378.46, 69.85), (378.46, YLED)], [(378.46, 77.47), (378.46, 80.01)],
    [(393.70, 68.58), (391.16, 68.58), (391.16, 73.66)],
    # ---- Control: CS hacia el lado inductor de RS1-RS4 ----
    [c(238.76, 120.65), c(241.30, 120.65)],
    [c(248.92, 120.65), c(309.88, 120.65), (309.88, YLED)],
    # ---- VDD: D7 -> R6 -> VDD de U1 ----
    [c(190.50, 118.11), c(186.69, 118.11)],
    [c(198.12, 118.11), c(201.93, 118.11)], [c(209.55, 118.11), c(213.36, 118.11)],
    [c(210.82, 118.11), c(210.82, 115.57)],
    # ---- FB: T1B (TA) -> R11 -> FB; R9 a GND_U1 ----
    [c(213.36, 123.19), c(209.55, 123.19), c(209.55, 130.81), c(199.39, 130.81)],
    [c(191.77, 130.81), c(186.69, 130.81)],
    [c(205.74, 130.81), c(205.74, 134.62)], [c(205.74, 142.24), c(205.74, 144.78)],
    [c(186.69, 143.51), c(186.69, 118.11)],                                       # TA
    [c(186.69, 158.75), c(186.69, 161.29)],                                       # TB -> GND
    # ---- GND y COMP de U1 ----
    [c(220.98, 130.81), c(220.98, 137.16)],
    [c(231.14, 130.81), c(231.14, 134.62)], [c(231.14, 142.24), c(231.14, 146.05)],
    [c(231.14, 153.67), c(231.14, 156.21)],
    # ---- Desacople de VDD ----
    [c(254.00, 137.16), c(254.00, 134.62)], [c(254.00, 144.78), c(254.00, 149.86)], [c(254.00, 147.32), c(259.08, 147.32)],
    [c(269.24, 137.16), c(269.24, 132.08)], [c(269.24, 134.62), c(274.32, 134.62)],
    [c(269.24, 144.78), c(269.24, 147.32)],
]

# Símbolos de alimentación y banderas: (lib_id, x, y)
POTENCIA = [
    ("power:GND", BX, 90.17), ("power:PWR_FLAG", BX, 67.31),
    ("power:GND", 151.13, 63.50), ("power:GND", 166.37, 63.50),
    ("power:VDD", 208.28, 78.74),
    ("Lampara:GND_U1", 231.14, 86.36), ("Lampara:GND_U1", 233.68, 53.34),
    ("power:GND", 241.30, 63.50), ("power:GND", 261.62, 74.93),
    ("power:GND", 337.82, 80.01), ("power:GND", 353.06, 80.01),
    ("power:GND", 368.30, 80.01), ("power:GND", 378.46, 80.01),
    ("power:GND", 391.16, 73.66),
    ("power:VDD",) + c(210.82, 115.57),
    ("Lampara:GND_U1",) + c(205.74, 144.78),
    ("power:GND",) + c(186.69, 161.29),
    ("Lampara:GND_U1",) + c(220.98, 137.16),
    ("Lampara:GND_U1",) + c(231.14, 156.21),
    ("power:VDD",) + c(254.00, 134.62), ("Lampara:GND_U1",) + c(254.00, 149.86), ("power:PWR_FLAG",) + c(259.08, 147.32),
    ("power:VDD",) + c(269.24, 132.08), ("power:PWR_FLAG",) + c(274.32, 134.62),
    ("Lampara:GND_U1",) + c(269.24, 147.32),
]

# Etiquetas que solo nombran redes importantes (no conectan nada a distancia)
ETIQUETAS = [
    ("DC+", 146.05, YR, 0),
    ("LED+", 332.74, YLED, 0),
]

# Posición fija de (Reference, Value); clave "REF" o "REF#unidad"
CAMPOS = {
    "P1": ((20.32, 71.12), (20.32, 83.82)),
    "Q1": ((226.06, 44.45), (226.06, 46.99)),
    "D6": ((212.09, 62.23), (211.46, 64.77)),
    "J1": ((398.78, 60.96), (398.78, 63.50)),
    "T1#2": (c(179.07, 149.86), c(175.26, 152.40)),
    "U1": (c(236.22, 111.76), c(250.19, 116.84)),
}

# Espejado: P1 y J1 con los pines en el mismo orden que las líneas
ESPEJO = {"P1": "y", "J1": "x"}

# Recuadros punteados por etapa: (x1, y1, x2, y2, título, x del título, y del título)
BLOQUES = [
    (12.70, 39.37, 177.80, 116.84, "ENTRADA AC Y PUENTE RECTIFICADOR", 15.24, 43.18),
    (200.66, 39.37, 405.13, 92.71, "ETAPA DE POTENCIA: REDUCTOR (BUCK) NO AISLADO", 287.02, 43.18),
    (162.56, 120.65, 284.48, 180.34, "CONTROL DE U1", 165.10, 124.46),
]

# Textos dentro del circuito: (texto, x, y, tamaño, negrita)
TEXTOS = [
    ("Opcion no montada", 177.80, 107.95, 1.27, False),
]

# ---------------------------------------------------------------------------
# Textos fijos de la hoja (no se centran) y cajetín
# ---------------------------------------------------------------------------
TITULO_GRANDE = [
    ("DRIVER LED TECNOLITE 50LHBLEDT65MV200", 17.78, 25.40, 5.0, True),
    ("Esquematico reconstruido por ingenieria inversa de la PCB JT047-V1", 17.78, 33.02, 2.5, False),
]

NOTAS_TITULO = "NOTAS"
NOTAS = [
    "1. GND = DC- = LED-. GND_U1 es la tierra flotante del controlador (fuente de Q1, nodo de conmutacion): no es la misma red que GND.",
    "2. DNP = no montado. LF1, L1 y RL1 estan puenteados por el cobre de la PCB.",
    "3. RS1-RS4 en paralelo (0.31 ohm) sensan la corriente del inductor en ambos estados de Q1.",
    "4. D6 en paralelo con R7 descarga la compuerta de Q1 al apagar (transicion ON -> OFF rapida).",
    "5. T1A y T1B son dos devanados del mismo nucleo T1. U1: controlador PWM SOT-23-6 marca H0TN, pines por funcion.",
    "6. Q1 tiene el pad del drenaje despegado. Polaridad de D7 y D8 deducida del funcionamiento (falta medirla).",
]

CAJETIN = {
    "title": "Driver LED Tecnolite 50LHBLEDT65MV200 - Esquematico",
    "date": "2026-11-25",
    "rev": "0.6",
    "company": "Ingenieria inversa de la PCB JT047-V1 (2018-3-19)",
    "comments": [
        "Autor: Mario Betancourt",
        "Rectificador de onda completa + reductor (buck) no aislado con MOSFET de lado alto",
        "Conexiones: trazado manual del cobre (pcb_tracing/) y mediciones de continuidad",
        "Elaborado con asistencia de IA (ver prompts/bitacora_prompts.md)",
    ],
}

# Área donde se centra el circuito (entre el título y las notas)
AREA_CENTRO = (10.0, 40.0, 410.0, 228.0)


# ---------------------------------------------------------------------------
# Centrado: desplaza todo el circuito (no el título, las notas ni el cajetín)
# para que su caja envolvente quede centrada en AREA_CENTRO, en la rejilla de 1.27
# ---------------------------------------------------------------------------
def _centrar():
    global LAYOUT, CABLES, POTENCIA, ETIQUETAS, CAMPOS, BLOQUES, TEXTOS
    xs = [b[0] for b in BLOQUES] + [b[2] for b in BLOQUES]
    ys = [b[1] for b in BLOQUES] + [b[3] for b in BLOQUES]
    ax1, ay1, ax2, ay2 = AREA_CENTRO
    g = 1.27
    dx = round((((ax1 + ax2) - (min(xs) + max(xs))) / 2) / g) * g
    dy = round((((ay1 + ay2) - (min(ys) + max(ys))) / 2) / g) * g

    def p(x, y):
        return (round(x + dx, 2), round(y + dy, 2))

    nuevo = {}
    for k, v in LAYOUT.items():
        if isinstance(v, list):
            nuevo[k] = [p(x, y) + (a, u) for x, y, a, u in v]
        else:
            nuevo[k] = p(v[0], v[1]) + (v[2],)
    LAYOUT = nuevo
    CABLES = [[p(*q) for q in poli] for poli in CABLES]
    POTENCIA = [(lib,) + p(x, y) for lib, x, y in POTENCIA]
    ETIQUETAS = [(t,) + p(x, y) + (a,) for t, x, y, a in ETIQUETAS]
    CAMPOS = {k: (p(*r), p(*v)) for k, (r, v) in CAMPOS.items()}
    BLOQUES = [p(x1, y1) + p(x2, y2) + (t,) + p(tx, ty) for x1, y1, x2, y2, t, tx, ty in BLOQUES]
    TEXTOS = [(t,) + p(x, y) + (tam, neg) for t, x, y, tam, neg in TEXTOS]


_centrar()
