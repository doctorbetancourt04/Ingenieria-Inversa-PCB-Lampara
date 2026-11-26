# -*- coding: utf-8 -*-
"""
Lista de componentes de la PCB JT047-V1 (Tecnolite 50LHBLEDT65MV200).

Coordenadas en mm, vista superior (lado de componentes THT):
  X = 0 en el eje central de la placa (positivo hacia la derecha)
  Y = 0 en el borde superior del cuello (positivo hacia abajo)

Las posiciones se estimaron a partir de las fotos de la carpeta images/
(escala tomada del ancho de la placa medido con regla, ~42.5 mm), por lo que
tienen un error aproximado de +/-1 mm. Los valores con "?" no se pudieron
leer en las fotos y deben verificarse en la placa física.

Tipos de colocación:
  ("c",  x, y, rot)              -> centro de los pads en (x, y), rotación en grados
  ("2p", padA, (x, y), padB, (x, y)) -> el pad A y el pad B quedan en esas posiciones
  ("o",  x, y, rot)              -> el origen del footprint queda en (x, y)
"""

# Origen de la placa dentro de la hoja de KiCad (mm)
ORIGEN_X = 121.25   # eje central
ORIGEN_Y = 50.0     # borde superior

# Las coordenadas de abajo se midieron suponiendo un ancho de 42.5 mm. Las fotos
# "Bottom Layer con Regla 1/2" dan un ancho de ~43.6 mm, así que la PCB se
# genera escalando todas las posiciones por este factor (no los footprints).
ESCALA = 43.6 / 42.5

# Contorno de la placa (Edge.Cuts), vista superior
# El hombro tiene un escalón horizontal corto en Y=15 y luego una diagonal
# de pendiente ~0.69 (medido en ambas fotos).
CONTORNO = [
    (-9.0, 0.0), (9.0, 0.0), (9.0, 15.0), (11.6, 15.0), (21.25, 29.0), (21.25, 98.0),
    (15.2, 98.0), (15.2, 111.2), (10.0, 111.2), (10.0, 98.0),
    (-10.0, 98.0), (-10.0, 111.2), (-15.2, 111.2), (-15.2, 98.0),
    (-21.25, 98.0), (-21.25, 29.0), (-11.6, 15.0), (-9.0, 15.0),
]

R1206 = "Resistor_SMD:R_1206_3216Metric"
R0805 = "Resistor_SMD:R_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"

# grupo -> bloque del esquemático
G_ENT = "Entrada AC y filtro EMI"
G_REC = "Rectificador y bus DC"
G_POT = "Etapa de potencia y salida LED"
G_CTL = "Control (CI y red de sensado)"

COMPONENTES = [
    # ---------------- Entrada AC (lado superior, THT) ----------------
    dict(ref="P1", sym="Connector_Generic:Conn_01x02", value="AC 120V (L, N)",
         fp="Lampara:P1_Entrada_AC_Cables", side="F", dnp=False, grp=G_ENT,
         place=("o", 0.0, 0.0, 0), desc="Cables de entrada de línea (pad 1 = L, pad 2 = N)"),
    dict(ref="R1", sym="Device:R", value="R fusible ?",
         fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical", side="F", dnp=False, grp=G_ENT,
         place=("2p", "1", (-4.6, 10.5), "2", (-5.6, 15.0)), desc="Resistor fusible vertical (cuerpo negro)"),
    dict(ref="F1", sym="Device:Fuse", value="Fusible ?",
         fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical", side="F", dnp=False, grp=G_ENT,
         place=("2p", "1", (5.1, 10.5), "2", (6.1, 14.8)), desc="Fusible vertical (cuerpo negro)"),
    dict(ref="VR1", sym="Device:Varistor", value="MOV ?",
         fp="Varistor:RV_Disc_D7mm_W3.4mm_P5mm", side="F", dnp=False, grp=G_ENT,
         place=("2p", "1", (-2.5, 15.0), "2", (3.0, 15.0)), desc="Disco azul entre L y N (sin etiqueta visible)"),
    dict(ref="LF1", sym="Device:L_Ferrite_Coupled", value="CMC (no montado)",
         fp="Lampara:LF1_CMC_4pin_7.5x4.5mm", side="F", dnp=True, grp=G_ENT,
         place=("c", 0.15, 21.75, 0), desc="Choque de modo común, no montado"),
    dict(ref="VR2", sym="Device:Varistor", value="MOV (no montado)",
         fp="Lampara:VR2_Ovalo_P7.5mm", side="F", dnp=True, grp=G_ENT,
         place=("o", 10.35, 21.3, 0), desc="Varistor, no montado (serigrafía ovalada original)"),
    dict(ref="L1", sym="Device:L", value="L (no montado)",
         fp="Inductor_THT:L_Radial_D12.5mm_P7.00mm_Fastron_09HCP", side="F", dnp=True, grp=G_ENT,
         place=("2p", "1", (-16.4, 31.1), "2", (-8.9, 31.1)), desc="Inductor radial, no montado"),
    dict(ref="CX1", sym="Device:C", value="X2 (no montado)",
         fp="Capacitor_THT:C_Rect_L19.0mm_W8.0mm_P15.00mm_MKS4", side="F", dnp=True, grp=G_ENT,
         place=("2p", "1", (-0.3, 31.7), "2", (15.3, 31.3)), desc="Capacitor X2, no montado"),
    dict(ref="RL1", sym="Device:R", value="(no montado)", fp=R1206, side="B", dnp=True, grp=G_ENT,
         place=("c", -12.8, 28.5, 0), desc="Pads con etiqueta 'RL' en la cara inferior, no montado"),

    # ---------------- Rectificador y bus DC ----------------
    dict(ref="D1", sym="Device:D", value="M7 ?", fp="Diode_SMD:D_SMA", side="B", dnp=False, grp=G_REC,
         place=("c", 2.7, 39.7, 270), desc="Puente rectificador (franja/cátodo hacia el cuello, medido)"),
    dict(ref="D2", sym="Device:D", value="M7 ?", fp="Diode_SMD:D_SMA", side="B", dnp=False, grp=G_REC,
         place=("c", -3.4, 39.7, 90), desc="Puente rectificador (franja/cátodo hacia las pestañas, medido)"),
    dict(ref="D3", sym="Device:D", value="M7 ?", fp="Diode_SMD:D_SMA", side="B", dnp=False, grp=G_REC,
         place=("c", -11.2, 39.9, 90), desc="Puente rectificador (franja/cátodo hacia las pestañas, medido)"),
    dict(ref="D4", sym="Device:D", value="M7 ?", fp="Diode_SMD:D_SMA", side="B", dnp=False, grp=G_REC,
         place=("c", -17.3, 39.9, 270), desc="Puente rectificador (franja/cátodo hacia el cuello, medido)"),
    dict(ref="CE1", sym="Device:C_Polarized", value="CE (no montado)",
         fp="Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", side="F", dnp=True, grp=G_REC,
         place=("2p", "1", (15.6, 44.4), "2", (16.6, 40.8)), desc="Electrolítico, no montado"),
    dict(ref="VR3", sym="Device:Varistor", value="MOV ?",
         fp="Varistor:RV_Disc_D12mm_W4.2mm_P7.5mm", side="F", dnp=False, grp=G_REC,
         place=("2p", "1", (7.6, 39.7), "2", (6.1, 47.2)), desc="Disco azul junto a la etiqueta VR3"),
    dict(ref="C6", sym="Device:C", value="CBB ?",
         fp="Capacitor_THT:C_Rect_L19.0mm_W9.0mm_P15.00mm_MKS4", side="F", dnp=False, grp=G_REC,
         place=("2p", "1", (-3.1, 45.3), "2", (-18.4, 45.5)), desc="Capacitor de película rojo (CBB); etiqueta no visible en la foto"),

    # ---------------- Etapa de potencia y salida ----------------
    dict(ref="T1", sym="Device:Transformer_1P_1S", value="Transformador EE ?",
         fp="Lampara:T1_EE_4pin", side="F", dnp=False, grp=G_POT,
         place=("o", -10.8, 67.6, 0), desc="Transformador/inductor EE con núcleo amarillo, 4 pines"),
    dict(ref="Q1", sym="Device:Q_NMOS_GDS", value="FIR12N65F",
         fp="Package_TO_SOT_THT:TO-220F-3_Vertical", side="F", dnp=False, grp=G_POT,
         place=("2p", "1", (11.0, 57.1), "3", (11.0, 62.2)), desc="MOSFET N 12 A / 650 V (FIR12N65F) con disipador"),
    dict(ref="D8", sym="Device:D", value="Diodo rápido ?",
         fp="Diode_THT:D_DO-201AD_P5.08mm_Vertical_KathodeUp", side="F", dnp=False, grp=G_POT,
         place=("2p", "2", (16.4, 71.5), "1", (16.2, 78.3)), desc="Diodo axial montado vertical (verificar polaridad)"),
    dict(ref="D7", sym="Device:D", value="?", fp="Diode_SMD:D_SMA", side="B", dnp=False, grp=G_POT,
         place=("c", -11.5, 59.0, 90), desc="Diodo SMD"),
    dict(ref="CE3", sym="Device:C_Polarized", value="270uF 100V",
         fp="Capacitor_THT:CP_Radial_D13.0mm_P5.00mm", side="F", dnp=False, grp=G_POT,
         place=("2p", "1", (-12.8, 90.4), "2", (-12.6, 85.4)), desc="Electrolítico de salida"),
    dict(ref="CE4", sym="Device:C_Polarized", value="270uF 100V",
         fp="Capacitor_THT:CP_Radial_D13.0mm_P5.00mm", side="F", dnp=False, grp=G_POT,
         place=("2p", "1", (13.0, 89.7), "2", (13.0, 84.6)), desc="Electrolítico de salida"),
    dict(ref="J1", sym="Connector_Generic:Conn_01x02", value="LED (- , +)",
         fp="Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", side="F", dnp=False, grp=G_POT,
         place=("2p", "1", (-1.25, 92.2), "2", (1.25, 92.2)), desc="Conector blanco a la placa de LEDs (1 = -, 2 = +)"),
    dict(ref="R14", sym="Device:R", value="75k (753)", fp=R1206, side="B", dnp=False, grp=G_POT,
         place=("c", 10.2, 87.8, 90), desc=""),
    dict(ref="R15", sym="Device:R", value="(no montado)", fp=R1206, side="B", dnp=True, grp=G_POT,
         place=("c", -9.2, 87.6, 90), desc=""),

    # ---------------- Control ----------------
    dict(ref="U1", sym="Lampara:IC_SOT-23-6", value="H0TN 9L99 ? (flyback)",
         fp="Package_TO_SOT_SMD:SOT-23-6", side="B", dnp=False, grp=G_CTL,
         place=("c", 3.4, 64.6, 270),
         desc="Controlador flyback SOT-23-6, marca 'H0TN / 9L99' (o SL87), fabricante no identificado. "
              "Pin 1 = punto, esquina inferior izquierda viendo la placa con el cuello abajo"),
    dict(ref="CE2", sym="Device:C_Polarized", value="10uF 50V",
         fp="Capacitor_THT:CP_Radial_D5.0mm_P2.50mm", side="F", dnp=False, grp=G_CTL,
         place=("2p", "1", (1.9, 55.8), "2", (1.7, 53.2)), desc="Electrolítico pequeño; polaridad deducida de la continuidad con U1 (+ = VCC)"),
    dict(ref="D5", sym="Device:D", value="(no montado)", fp="Diode_SMD:D_MiniMELF", side="B", dnp=True, grp=G_CTL,
         place=("c", 17.7, 49.2, 90), desc=""),
    dict(ref="D6", sym="Device:D", value="1N4148W ? (T4)", fp="Diode_SMD:D_SOD-123", side="B", dnp=False, grp=G_CTL,
         place=("c", 9.9, 52.4, 0), desc=""),
    dict(ref="R2", sym="Device:R", value="(no montado)", fp=R0805, side="B", dnp=True, grp=G_CTL,
         place=("c", 11.8, 37.7, 90), desc=""),
    dict(ref="R3", sym="Device:R", value="(no montado)", fp=R0805, side="B", dnp=True, grp=G_CTL,
         place=("c", 11.7, 43.5, 90), desc=""),
    dict(ref="R4", sym="Device:R", value="330k (334)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", -5.4, 48.1, 0), desc=""),
    dict(ref="R5", sym="Device:R", value="330k (334)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", -5.6, 52.6, 0), desc=""),
    dict(ref="R6", sym="Device:R", value="22 (220)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", -5.7, 56.4, 0), desc=""),
    dict(ref="R7", sym="Device:R", value="22 (220)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", 10.0, 54.7, 0), desc=""),
    dict(ref="R8", sym="Device:R", value="75k (753)", fp=R0805, side="B", dnp=False, grp=G_CTL,
         place=("c", 4.8, 52.6, 0), desc=""),
    dict(ref="R9", sym="Device:R", value="12k (123)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", 7.6, 65.0, 90), desc=""),
    dict(ref="R10", sym="Device:R", value="560 (561)", fp=R0805, side="B", dnp=False, grp=G_CTL,
         place=("c", 10.4, 69.2, 0), desc=""),
    dict(ref="R11", sym="Device:R", value="68k (683)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", 3.9, 69.2, 0), desc=""),
    dict(ref="R12", sym="Device:R", value="0", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", -1.1, 66.5, 0), desc="Puente de 0 ohm"),
    dict(ref="R13", sym="Device:R", value="(no montado)", fp=R0805, side="B", dnp=True, grp=G_CTL,
         place=("c", 11.5, 74.4, 90), desc=""),
    dict(ref="RS1", sym="Device:R", value="1.2 (1R20)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", 3.9, 76.0, 0), desc="Resistor de sensado de corriente"),
    dict(ref="RS2", sym="Device:R", value="1.2 (1R20)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", 3.8, 73.3, 0), desc="Resistor de sensado de corriente"),
    dict(ref="RS3", sym="Device:R", value="1.2 (1R20)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", 3.9, 78.6, 0), desc="Resistor de sensado de corriente"),
    dict(ref="RS4", sym="Device:R", value="1.3 (1R30)", fp=R1206, side="B", dnp=False, grp=G_CTL,
         place=("c", 3.8, 81.2, 0), desc="Resistor de sensado de corriente"),
    dict(ref="C1", sym="Device:C", value="(no montado)", fp=C0805, side="B", dnp=True, grp=G_CTL,
         place=("c", -0.4, 63.4, 90), desc="Posición aproximada (junto a U1)"),
    dict(ref="C2", sym="Device:C", value="? (MLCC)", fp=C0805, side="B", dnp=False, grp=G_CTL,
         place=("c", 1.3, 59.4, 90), desc=""),
    dict(ref="C3", sym="Device:C", value="(no montado)", fp=C1206, side="B", dnp=True, grp=G_CTL,
         place=("c", 17.8, 61.8, 90), desc=""),
    dict(ref="C4", sym="Device:C", value="? (MLCC)", fp=C0805, side="B", dnp=False, grp=G_CTL,
         place=("c", 11.5, 66.0, 90), desc=""),
    dict(ref="C5", sym="Device:C", value="(no montado)", fp=C1206, side="B", dnp=True, grp=G_CTL,
         place=("c", 11.3, 80.4, 90), desc=""),
]
