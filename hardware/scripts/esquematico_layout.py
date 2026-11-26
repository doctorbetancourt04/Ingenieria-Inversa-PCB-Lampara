# -*- coding: utf-8 -*-
"""
Disposición del esquemático cableado, rev 0.5 (lo usa generar_esquematico.py).
Hoja A3. Coordenadas en mm, múltiplos de 1.27. Rotación en grados (antihorario).

Criterios de dibujo:
  - Flujo de izquierda a derecha y de mayor a menor tensión: entrada AC -> puente
    -> bus DC -> interruptor -> inductor -> LEDs.
  - Etapas agrupadas: A (entrada y rectificador) arriba a la izquierda; B (potencia)
    arriba a la derecha y su control (U1) debajo.
  - Rieles con símbolos de alimentación en lugar de cables largos:
      DC+     riel positivo del bus DC
      DC-     riel negativo del bus DC = LED- (tierra de la placa)
      GND_SW  tierra flotante del controlador = fuente de Q1 (nodo de conmutación).
              Es una tierra distinta de DC-: por eso tiene otro símbolo.
      VDD     alimentación de U1
  - Sin cruces de cables. Los conectores de entrada (P1) y salida (J1) están
    espejados para que sus pines queden en el mismo orden que las líneas.

T1 tiene dos unidades: T1A (devanado principal TC-TD, en serie con la carga) y
T1B (devanado auxiliar TA-TB, junto al controlador).
"""

PAPEL = "A3"

# ---------------------------------------------------------------------------
# A. Entrada AC, fusibles, varistores y puente rectificador
# ---------------------------------------------------------------------------
YL, YN = 63.50, 101.60          # línea L (arriba) y línea N (abajo)
BX = 123.19                     # bus izquierdo del puente (DC-)
NODO = BX + 15.24               # nodo AC de cada rama del puente
BD = BX + 30.48                 # bus derecho del puente (DC+)
YP, YM = 66.04, 82.55           # riel DC+ y pin de los símbolos DC- de la etapa A

LAYOUT_A = {
    "P1": (20.32, 81.28, 0),
    "F1": (40.64, YL, 90), "R1": (40.64, YN, 90),
    "VR1": (54.61, 82.55, 180),
    "LF1": (72.39, 82.55, 180),
    "VR2": (88.90, 82.55, 0), "CX1": (106.68, 82.55, 180),
    "L1": (114.30, 107.95, 90), "RL1": (114.30, 118.11, 90),
    "D1": (BX + 7.62, 72.39, 180), "D2": (BX + 22.86, 72.39, 180),
    "D4": (BX + 7.62, 92.71, 180), "D3": (BX + 22.86, 92.71, 180),
    "C6": (166.37, 76.20, 0), "VR3": (181.61, 76.20, 180),
}

CABLES_A = [
    # P1 (espejado): pin 1 = L arriba, pin 2 = N abajo
    [(25.40, 81.28), (30.48, 81.28), (30.48, YL), (36.83, YL)],
    [(25.40, 83.82), (27.94, 83.82), (27.94, YN), (36.83, YN)],
    # Líneas L y N hasta el puente
    [(44.45, YL), (NODO, YL), (NODO, 72.39)],
    [(44.45, YN), (NODO, YN), (NODO, 92.71)],
    [(54.61, 78.74), (54.61, YL)], [(54.61, 86.36), (54.61, YN)],                  # VR1
    [(67.31, 80.01), (67.31, YL)], [(77.47, 80.01), (77.47, YL)],                  # LF1 (puenteado)
    [(67.31, 85.09), (67.31, YN)], [(77.47, 85.09), (77.47, YN)],
    [(88.90, 78.74), (88.90, YL)], [(88.90, 86.36), (88.90, YN)],                  # VR2
    [(106.68, 78.74), (106.68, YL)], [(106.68, 86.36), (106.68, YN)],              # CX1
    [(110.49, 107.95), (110.49, YN)], [(118.11, 107.95), (118.11, YN)],            # L1 (puenteado)
    [(110.49, 118.11), (110.49, 107.95)], [(118.11, 118.11), (118.11, 107.95)],    # RL1 // L1
    # Puente
    [(BX + 11.43, 72.39), (BX + 19.05, 72.39)], [(BX + 11.43, 92.71), (BX + 19.05, 92.71)],
    [(BX + 3.81, 72.39), (BX, 72.39), (BX, 95.25)], [(BX + 3.81, 92.71), (BX, 92.71)],
    [(BX + 26.67, 72.39), (BD, 72.39), (BD, 92.71), (BX + 26.67, 92.71)],
    [(BD, 72.39), (BD, YP), (187.96, YP)],                                         # riel DC+
    [(166.37, 72.39), (166.37, YP)], [(166.37, 80.01), (166.37, YM)],              # C6
    [(181.61, 72.39), (181.61, YP)], [(181.61, 80.01), (181.61, YM)],              # VR3
]

POT_A = [
    ("Lampara:DC-", BX, 95.25),
    ("Lampara:DC-", 166.37, YM), ("Lampara:DC-", 181.61, YM),
    ("Lampara:DC+", 187.96, YP),
    ("power:PWR_FLAG", BD, YP), ("power:PWR_FLAG", BX, 72.39),
]

# ---------------------------------------------------------------------------
# B. Convertidor DC-DC (coordenadas base, luego se desplazan OX)
# ---------------------------------------------------------------------------
OX = -15.24
YSW = 76.20      # bus del nodo de conmutación (fuente de Q1)
YL2 = 91.44      # riel LED+ (después de RS y T1A)
GX = 214.63      # bajada de la señal GATE de U1

LAYOUT_B = {
    # Interruptor y red de compuerta
    "Q1": (231.14, 66.04, 0),
    "R7": (218.44, 66.04, 90), "D6": (218.44, 73.66, 0), "R8": (222.25, 111.76, 180),
    # Rueda libre y sensado
    "D8": (233.68, 83.82, 270),
    "R13": (251.46, 82.55, 180), "C5": (251.46, 93.98, 180),
    "RS1": (269.24, 83.82, 180), "RS2": (279.40, 83.82, 180),
    "RS3": (289.56, 83.82, 180), "RS4": (299.72, 83.82, 180),
    # Inductor acoplado: unidad 1 = devanado principal, unidad 2 = auxiliar
    "T1": [(330.20, YL2, 0, 1), (203.20, 180.34, 0, 2)],
    # Salida
    "CE3": (345.44, 101.60, 0), "CE4": (361.95, 101.60, 0),
    "R14": (378.46, 101.60, 0), "R15": (391.16, 101.60, 0),
    "J1": (416.56, 93.98, 0),
    # Controlador
    "U1": (243.84, 149.86, 0),
    "R4": (193.04, 128.27, 180), "R5": (193.04, 138.43, 0),
    "D7": (210.82, 147.32, 180), "R6": (222.25, 147.32, 90),
    "R11": (213.36, 160.02, 90), "R9": (220.98, 167.64, 0),
    "R10": (248.92, 167.64, 0), "C4": (248.92, 179.07, 0),
    "R12": (262.89, 149.86, 270),
    "CE2": (271.78, 172.72, 0), "C2": (287.02, 172.72, 0),
    # Opción no montada (C3.1 medido en DC+) y C1 sin conexión conocida
    "C3": (330.20, 132.08, 0), "D5": (330.20, 143.51, 270),
    "R3": (330.20, 154.94, 0), "R2": (330.20, 166.37, 0), "CE1": (347.98, 154.94, 0),
    "C1": (365.76, 160.02, 0),
}

CABLES_B = [
    # Q1 y red de compuerta: R7 // D6 (cátodo hacia U1); R8 de la salida GATE a GND_SW
    [(233.68, 60.96), (233.68, 58.42)],
    [(222.25, 66.04), (226.06, 66.04)],
    [(GX, 66.04), (GX, 73.66)], [(222.25, 66.04), (222.25, 73.66)],
    [(GX, 73.66), (GX, 134.62), (243.84, 134.62), (243.84, 139.70)],
    [(GX, 106.68), (222.25, 106.68), (222.25, 107.95)], [(222.25, 115.57), (222.25, 118.11)],
    # Nodo de conmutación: fuente de Q1, D8, GND_SW, RC no montado y RS1-RS4
    [(233.68, 71.12), (233.68, 80.01)], [(233.68, 87.63), (233.68, 90.17)],
    [(233.68, YSW), (299.72, YSW)],
    [(241.30, YSW), (241.30, 80.01)],
    [(251.46, YSW), (251.46, 78.74)], [(251.46, 86.36), (251.46, 90.17)], [(251.46, 97.79), (251.46, 100.33)],
    [(269.24, YSW), (269.24, 80.01)], [(279.40, YSW), (279.40, 80.01)],
    [(289.56, YSW), (289.56, 80.01)], [(299.72, YSW), (299.72, 80.01)],
    [(269.24, 87.63), (269.24, YL2)], [(279.40, 87.63), (279.40, YL2)],
    [(289.56, 87.63), (289.56, YL2)], [(299.72, 87.63), (299.72, YL2)],
    [(269.24, YL2), (322.58, YL2)],                                               # RS -> T1A (TC)
    # Salida: TD -> LED+ -> J1; condensadores y R14/R15 a DC-
    [(337.82, YL2), (411.48, YL2)],
    [(345.44, 97.79), (345.44, YL2)], [(345.44, 105.41), (345.44, 107.95)],
    [(361.95, 97.79), (361.95, YL2)], [(361.95, 105.41), (361.95, 107.95)],
    [(378.46, 97.79), (378.46, YL2)], [(378.46, 105.41), (378.46, 107.95)],
    [(391.16, 97.79), (391.16, YL2)], [(391.16, 105.41), (391.16, 107.95)],
    [(411.48, 93.98), (408.94, 93.98), (408.94, 97.79)],
    # Arranque: DC+ -> R4 -> R5 -> VDD
    [(193.04, 121.92), (193.04, 124.46)], [(193.04, 132.08), (193.04, 134.62)],
    [(193.04, 142.24), (193.04, 144.78), (199.39, 144.78)],
    # Devanado auxiliar: TA -> D7 -> R6 -> VDD de U1 y TA -> R11 -> FB; TB a DC-
    [(203.20, 172.72), (203.20, 147.32), (207.01, 147.32)],
    [(214.63, 147.32), (218.44, 147.32)], [(226.06, 147.32), (231.14, 147.32)], [(228.60, 147.32), (228.60, 144.78)],
    [(203.20, 160.02), (209.55, 160.02)],
    [(217.17, 160.02), (227.33, 160.02), (227.33, 152.40), (231.14, 152.40)],
    [(220.98, 160.02), (220.98, 163.83)], [(220.98, 171.45), (220.98, 173.99)],
    [(203.20, 187.96), (203.20, 190.50)],
    # GND y COMP de U1
    [(238.76, 160.02), (238.76, 163.83)],
    [(248.92, 160.02), (248.92, 163.83)], [(248.92, 171.45), (248.92, 175.26)],
    [(248.92, 182.88), (248.92, 185.42)],
    # CS: U1 -> R12 -> lado inductor de RS1-RS4
    [(256.54, 149.86), (259.08, 149.86)],
    [(266.70, 149.86), (309.88, 149.86), (309.88, YL2)],
    # Desacople de VDD junto al CI
    [(271.78, 168.91), (271.78, 166.37)], [(271.78, 176.53), (271.78, 179.07)],
    [(287.02, 168.91), (287.02, 163.83)], [(287.02, 166.37), (292.10, 166.37)], [(287.02, 176.53), (287.02, 179.07)],
    # Opción no montada
    [(330.20, 125.73), (330.20, 128.27)], [(330.20, 135.89), (330.20, 139.70)],
    [(330.20, 147.32), (330.20, 151.13)], [(330.20, 148.59), (347.98, 148.59), (347.98, 151.13)],
    [(330.20, 158.75), (330.20, 162.56)],
]

POT_B = [
    ("Lampara:DC+", 233.68, 58.42),
    ("Lampara:GND_SW", 222.25, 118.11),
    ("Lampara:DC-", 233.68, 90.17),
    ("Lampara:GND_SW", 241.30, 80.01),
    ("Lampara:DC-", 251.46, 100.33),
    ("Lampara:DC-", 345.44, 107.95), ("Lampara:DC-", 361.95, 107.95),
    ("Lampara:DC-", 378.46, 107.95), ("Lampara:DC-", 391.16, 107.95),
    ("Lampara:DC-", 408.94, 97.79),
    ("Lampara:DC+", 193.04, 121.92), ("power:VDD", 199.39, 144.78), ("power:VDD", 228.60, 144.78),
    ("power:PWR_FLAG", 245.11, YSW), ("power:PWR_FLAG", 292.10, 166.37),
    ("Lampara:GND_SW", 220.98, 173.99), ("Lampara:DC-", 203.20, 190.50),
    ("Lampara:GND_SW", 238.76, 163.83), ("Lampara:GND_SW", 248.92, 185.42),
    ("power:VDD", 271.78, 166.37), ("Lampara:GND_SW", 271.78, 179.07),
    ("power:VDD", 287.02, 163.83), ("Lampara:GND_SW", 287.02, 179.07),
    ("Lampara:DC+", 330.20, 125.73),
]

# Posición fija de (Reference, Value); clave "REF" o "REF#unidad"
CAMPOS_B = {
    "U1": ((253.99, 140.97), (269.24, 144.78)),
    "D8": ((226.06, 81.28), (224.79, 85.09)),
    "J1": ((416.56, 85.09), (416.56, 87.63)),
    "T1#2": ((193.04, 179.07), (190.50, 181.61)),
    "R4": ((186.69, 127.00), (185.42, 129.54)),
    "R5": ((186.69, 137.16), (185.42, 139.70)),
}
CAMPOS_A = {"P1": ((20.32, 76.20), (22.86, 90.17))}

# Espejado: P1 y J1 con los pines en el mismo orden que las líneas
ESPEJO = {"P1": "y", "J1": "x"}

# ---------------------------------------------------------------------------
# Textos: (texto, x, y, tamaño, negrita). Las coordenadas de B ya van desplazadas.
# ---------------------------------------------------------------------------
TEXTOS = [
    ("ESQUEMATICO RECONSTRUIDO por ingenieria inversa de la PCB JT047-V1 (2018-3-19), rev 0.5. "
     "Conexiones: trazado manual del cobre (pcb_tracing/) + mediciones de continuidad.\\n"
     "Componentes tachados = no montados (DNP). DC- (triangulo lleno) y GND_SW (triangulo hueco) "
     "son tierras distintas.", 20.32, 25.40, 1.5, False),
    ("A. ENTRADA AC Y PUENTE RECTIFICADOR", 20.32, 43.18, 2.0, True),
    ("Fusibles", 35.56, 55.88, 1.27, False),
    ("Puente D1-D4 (S2M)", 126.73, 58.42, 1.27, False),
    ("Bus DC", 163.83, 58.42, 1.27, False),
    ("LF1, L1, RL1, VR2 y CX1 no estan montados;\\nel cobre de la PCB puentea LF1, L1 y RL1.",
     20.32, 127.00, 1.27, False),
    ("B. CONVERTIDOR DC-DC: REDUCTOR (BUCK) NO AISLADO CON MOSFET DE LADO ALTO", 182.88, 43.18, 2.0, True),
    ("R7 // D6: D6 descarga la compuerta al apagar", 191.77, 53.34, 1.27, False),
    ("Q1: pad del drenaje despegado; resoldar", 226.06, 60.96, 1.27, False),
    ("Rueda libre", 208.28, 97.79, 1.27, False),
    ("Sensado de corriente: RS1-RS4 en paralelo = 0.31 ohm", 251.46, 71.12, 1.27, False),
    ("T1A: devanado principal", 299.72, 100.33, 1.27, False),
    ("Salida a los LEDs", 335.28, 85.09, 1.5, True),
    ("CONTROL (U1 flota sobre GND_SW = fuente de Q1)", 172.72, 116.84, 1.5, True),
    ("T1B: devanado auxiliar (TA-TB),\\nmismo nucleo que T1A", 160.02, 203.20, 1.27, False),
    ("Desacople de VDD", 254.00, 189.23, 1.27, False),
    ("Opcion no montada (C3.1 medido en DC+)\\ny C1, de conexion no determinada", 307.34, 119.38, 1.27, False),
]


# ---------------------------------------------------------------------------
# Ensamblado (desplaza la etapa B)
# ---------------------------------------------------------------------------
def _dx(p):
    return (round(p[0] + OX, 2), p[1])


def _coloc(c):
    if isinstance(c, list):
        return [(round(x + OX, 2), y, a, u) for x, y, a, u in c]
    x, y, a = c
    return (round(x + OX, 2), y, a)


LAYOUT = dict(LAYOUT_A)
LAYOUT.update({k: _coloc(v) for k, v in LAYOUT_B.items()})
CABLES = CABLES_A + [[_dx(p) for p in poli] for poli in CABLES_B]
POTENCIA = POT_A + [(lib, round(x + OX, 2), y) for lib, x, y in POT_B]
CAMPOS = dict(CAMPOS_A)
CAMPOS.update({k: (_dx(r), _dx(v)) for k, (r, v) in CAMPOS_B.items()})
ETIQUETAS = []
