# -*- coding: utf-8 -*-
"""
Genera las librerías propias del proyecto (footprints y símbolos que no
existen tal cual en las librerías estándar de KiCad 8) y las tablas
fp-lib-table / sym-lib-table del proyecto.

Uso:  python generar_librerias.py
"""
import os
import uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.normpath(os.path.join(AQUI, "..", "KiCad_IngenieriaInversaLampara"))
PRETTY = os.path.join(PROY, "Lampara.pretty")


def u():
    return str(uuid.uuid4())


def font(size=1.0, th=0.15):
    return f'(effects (font (size {size} {size}) (thickness {th})))'


def rect(x1, y1, x2, y2, layer, w):
    return (f'\t(fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid)) '
            f'(fill none) (layer "{layer}") (uuid "{u()}"))\n')


def pad(num, x, y, size, drill, first=False):
    shape = "rect" if first else "circle"
    return (f'\t(pad "{num}" thru_hole {shape} (at {x} {y}) (size {size} {size}) (drill {drill}) '
            f'(layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{u()}"))\n')


def npth(x, y, d):
    return (f'\t(pad "" np_thru_hole circle (at {x} {y}) (size {d} {d}) (drill {d}) '
            f'(layers "*.Cu" "*.Mask") (uuid "{u()}"))\n')


def text(t, x, y, layer, size=1.0):
    return (f'\t(fp_text user "{t}" (at {x} {y} 0) (layer "{layer}") (uuid "{u()}") {font(size)})\n')


def footprint(name, descr, ref_xy, val_xy, body):
    return (f'(footprint "{name}" (version 20240108) (generator "pcbnew") (generator_version "8.0")\n'
            f'\t(layer "F.Cu")\n'
            f'\t(descr "{descr}")\n'
            f'\t(property "Reference" "REF**" (at {ref_xy[0]} {ref_xy[1]} 0) (layer "F.SilkS") (uuid "{u()}") {font()})\n'
            f'\t(property "Value" "{name}" (at {val_xy[0]} {val_xy[1]} 0) (layer "F.Fab") (uuid "{u()}") {font()})\n'
            f'\t(attr through_hole)\n'
            f'{body})\n')


def fp_p1():
    # Origen = centro del borde superior de la placa (se coloca en X=0, Y=0)
    b = ""
    b += pad("1", 4.8, 6.9, 2.6, 1.2, first=True)   # L (cable)
    b += pad("1", 4.6, 4.2, 2.2, 1.0)               # L (pad alterno)
    b += pad("2", -3.6, 7.0, 2.6, 1.2)              # N (cable)
    b += pad("2", -2.4, 4.2, 2.2, 1.0)              # N (pad alterno)
    b += npth(-3.0, 1.8, 1.6)                       # alivio de tensión del cable
    b += npth(4.4, 1.8, 1.6)
    b += text("L", 7.4, 6.9, "F.SilkS")
    b += text("N", -6.2, 7.0, "F.SilkS")
    b += rect(-5.2, 0.6, 6.6, 9.0, "F.Fab", 0.1)
    b += rect(-5.4, 0.4, 8.4, 8.4, "F.CrtYd", 0.05)
    return footprint("P1_Entrada_AC_Cables",
                     "Entrada AC por cables soldados (L y N) con agujeros de alivio; medido de la PCB JT047-V1",
                     (-7.5, 3.5), (1.0, 10.5), b)


def fp_lf1():
    b = ""
    b += pad("1", -3.75, -2.25, 2.0, 1.0, first=True)
    b += pad("2", -3.75, 2.25, 2.0, 1.0)
    b += pad("3", 3.75, -2.25, 2.0, 1.0)
    b += pad("4", 3.75, 2.25, 2.0, 1.0)
    b += rect(-6.75, -4.0, 6.75, 4.0, "F.SilkS", 0.12)
    b += rect(-6.75, -4.0, 6.75, 4.0, "F.Fab", 0.1)
    b += rect(-7.0, -3.4, 7.0, 4.25, "F.CrtYd", 0.05)
    return footprint("LF1_CMC_4pin_7.5x4.5mm",
                     "Choque de modo comun 4 pines, paso 7.5 x 4.5 mm; medido de la PCB JT047-V1",
                     (-8.5, 0), (0, 5.2), b)


def fp_t1():
    b = ""
    b += pad("1", -6.0, -7.5, 2.6, 1.3, first=True)
    b += pad("2", -6.0, 7.5, 2.6, 1.3)
    b += pad("3", 6.0, -2.8, 2.6, 1.3)
    b += pad("4", 6.0, 7.4, 2.6, 1.3)
    b += rect(-9.6, -16.2, 8.7, 12.0, "F.SilkS", 0.12)
    b += rect(-9.6, -16.2, 8.7, 12.0, "F.Fab", 0.1)
    b += rect(-9.85, -16.45, 8.95, 12.25, "F.CrtYd", 0.05)
    b += text("1", -6.0, -9.6, "F.SilkS", 0.8)
    return footprint("T1_EE_4pin",
                     "Transformador EE (nucleo amarillo) de 4 pines, posiciones medidas de la PCB JT047-V1",
                     (0, -18.2), (0, 13.2), b)


def fp_vr2():
    """Óvalo de la serigrafía original de VR2 (medido en 'Top Layer.jpeg').
    Origen = centro del óvalo. Los pads van en diagonal dentro del óvalo,
    igual que en la placa."""
    r, h = 2.125, 3.375          # radio de los extremos y mitad del tramo recto
    w = 0.2                      # grosor de línea de la serigrafía original (~0.25 mm)

    def estadio(capa, ancho):
        s = ""
        for x in (-r, r):
            s += (f'\t(fp_line (start {x} {-h}) (end {x} {h}) (stroke (width {ancho}) (type solid)) '
                  f'(layer "{capa}") (uuid "{u()}"))\n')
        for yc, signo in ((-h, -1), (h, 1)):
            s += (f'\t(fp_arc (start {-r} {yc}) (mid 0 {yc + signo * r}) (end {r} {yc}) '
                  f'(stroke (width {ancho}) (type solid)) (layer "{capa}") (uuid "{u()}"))\n')
        return s

    b = ""
    b += pad("1", 0.62, -3.6, 2.0, 1.0, first=True)
    b += pad("2", -0.75, 3.6, 2.0, 1.0)
    b += estadio("F.SilkS", w)
    b += (f'\t(fp_line (start 0 0.85) (end 0 1.95) (stroke (width {w}) (type solid)) '
          f'(layer "F.SilkS") (uuid "{u()}"))\n')          # marca "|" del centro
    b += estadio("F.Fab", 0.1)
    b += rect(-2.4, -5.75, 2.4, 5.75, "F.CrtYd", 0.05)
    txt = footprint("VR2_Ovalo_P7.5mm",
                    "Varistor en disco, serigrafia ovalada 4.25 x 11 mm con marca central; medido de la PCB JT047-V1",
                    (4.65, 1.5), (0, 6.6), b)
    # La etiqueta original "VR2" está girada 180 grados
    return txt.replace('(property "Reference" "REF**" (at 4.65 1.5 0)',
                       '(property "Reference" "REF**" (at 4.65 1.5 180)')


SIMBOLOS = '''(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor") (generator_version "8.0")
	(symbol "IC_SOT-23-6" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
		(property "Reference" "U" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
		(property "Value" "Controlador PWM SOT-23-6" (at 0 -13.97 0) (effects (font (size 1.27 1.27))))
		(property "Footprint" "Package_TO_SOT_SMD:SOT-23-6" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Description" "Controlador PWM de convertidor (tipo flyback / PSR) en SOT-23-6, marca H0TN / 9L99, fabricante no identificado. Nombres de pin por funcion, deducidos de las conexiones de la placa: 1 VDD, 2 GND, 3 GATE, 4 FB (divisor del devanado auxiliar), 5 COMP (red RC a GND), 6 CS (sensado de corriente)" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(symbol "IC_SOT-23-6_0_1"
			(rectangle (start -10.16 7.62) (end 10.16 -7.62) (stroke (width 0.254) (type default)) (fill (type background)))
		)
		(symbol "IC_SOT-23-6_1_1"
			(pin passive line (at -12.7 2.54 0) (length 2.54) (name "VDD" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -5.08 -10.16 90) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
			(pin output line (at 0 10.16 270) (length 2.54) (name "GATE" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
			(pin input line (at -12.7 -2.54 0) (length 2.54) (name "FB" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 5.08 -10.16 90) (length 2.54) (name "COMP" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
			(pin input line (at 12.7 0 180) (length 2.54) (name "CS" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
		)
	)
	(symbol "T1_EE_2dev" (pin_names (offset 0.254) hide) (exclude_from_sim no) (in_bom yes) (on_board yes)
		(property "Reference" "T" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
		(property "Value" "T1_EE_2dev" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
		(property "Footprint" "Lampara:T1_EE_4pin" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Description" "Inductor acoplado / transformador EE de 4 pines con dos devanados. Unidad A: devanado principal, pines 3 (TC) y 4 (TD). Unidad B: devanado auxiliar, pines 1 (TA) y 2 (TB)" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(symbol "T1_EE_2dev_1_1"
			(arc (start -5.08 0) (mid -3.81 1.27) (end -2.54 0) (stroke (width 0.254) (type default)) (fill (type none)))
			(arc (start -2.54 0) (mid -1.27 1.27) (end 0.0 0) (stroke (width 0.254) (type default)) (fill (type none)))
			(arc (start 0.0 0) (mid 1.27 1.27) (end 2.54 0) (stroke (width 0.254) (type default)) (fill (type none)))
			(arc (start 2.54 0) (mid 3.81 1.27) (end 5.08 0) (stroke (width 0.254) (type default)) (fill (type none)))
			(polyline (pts (xy -5.08 -1.016) (xy 5.08 -1.016)) (stroke (width 0.254) (type default)) (fill (type none)))
			(polyline (pts (xy -5.08 -1.778) (xy 5.08 -1.778)) (stroke (width 0.254) (type default)) (fill (type none)))
			(pin passive line (at -7.62 0 0) (length 2.54) (name "TC" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 7.62 0 180) (length 2.54) (name "TD" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
		)
		(symbol "T1_EE_2dev_2_1"
			(arc (start 0 5.08) (mid 1.27 3.81) (end 0 2.54) (stroke (width 0.254) (type default)) (fill (type none)))
			(arc (start 0 2.54) (mid 1.27 1.27) (end 0 0.0) (stroke (width 0.254) (type default)) (fill (type none)))
			(arc (start 0 0.0) (mid 1.27 -1.27) (end 0 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))
			(arc (start 0 -2.54) (mid 1.27 -3.81) (end 0 -5.08) (stroke (width 0.254) (type default)) (fill (type none)))
			(polyline (pts (xy -1.016 5.08) (xy -1.016 -5.08)) (stroke (width 0.254) (type default)) (fill (type none)))
			(polyline (pts (xy -1.778 5.08) (xy -1.778 -5.08)) (stroke (width 0.254) (type default)) (fill (type none)))
			(pin passive line (at 0 7.62 270) (length 2.54) (name "TA" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 0 -7.62 90) (length 2.54) (name "TB" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
		)
	)
	(symbol "GND_U1" (power) (pin_numbers hide) (pin_names (offset 0) hide) (exclude_from_sim no) (in_bom yes) (on_board yes)
		(property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Value" "GND_U1" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Description" "Tierra flotante del controlador U1 = fuente de Q1 = nodo de conmutacion. Distinta de GND (DC-)" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "ki_keywords" "global power" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(symbol "GND_U1_0_1"
			(polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none)))
		)
		(symbol "GND_U1_1_1"
			(pin power_in line (at 0 0 270) (length 0) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
		)
	)
)
'''

FP_TABLE = '''(fp_lib_table
  (version 7)
  (lib (name "Lampara")(type "KiCad")(uri "${KIPRJMOD}/Lampara.pretty")(options "")(descr "Footprints medidos de la PCB JT047-V1"))
)
'''

SYM_TABLE = '''(sym_lib_table
  (version 7)
  (lib (name "Lampara")(type "KiCad")(uri "${KIPRJMOD}/Lampara.kicad_sym")(options "")(descr "Simbolos propios del proyecto"))
)
'''


def escribir(ruta, txt):
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    print("escrito:", os.path.relpath(ruta, PROY))


if __name__ == "__main__":
    os.makedirs(PRETTY, exist_ok=True)
    escribir(os.path.join(PRETTY, "P1_Entrada_AC_Cables.kicad_mod"), fp_p1())
    escribir(os.path.join(PRETTY, "LF1_CMC_4pin_7.5x4.5mm.kicad_mod"), fp_lf1())
    escribir(os.path.join(PRETTY, "T1_EE_4pin.kicad_mod"), fp_t1())
    escribir(os.path.join(PRETTY, "VR2_Ovalo_P7.5mm.kicad_mod"), fp_vr2())
    escribir(os.path.join(PROY, "Lampara.kicad_sym"), SIMBOLOS)
    escribir(os.path.join(PROY, "fp-lib-table"), FP_TABLE)
    escribir(os.path.join(PROY, "sym-lib-table"), SYM_TABLE)
