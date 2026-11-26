# -*- coding: utf-8 -*-
"""
Genera KiCad_IngenieriaInversaLampara.kicad_sch: esquemático CABLEADO en dos etapas
(flujo de izquierda a derecha):

  A. Entrada AC, fusibles, varistores y puente rectificador
  B. Convertidor DC-DC (Q1, T1, controlador U1) y salida a los LEDs

Las posiciones, rotaciones y cables están definidos a mano en esquematico_layout.py.
Las únicas etiquetas son DC+ y DC-, en la frontera entre el rectificador y el
convertidor; todo lo demás va con cables.

Símbolos de varias unidades (T1): en LAYOUT, una referencia puede tener una lista
de colocaciones (x, y, ángulo, unidad); los pines de cada unidad están en PINES_UNIDAD.

Verificación: 'python verificar_esquematico.py' compara el netlist exportado con
redes_pcb.json (las redes de la PCB).

Uso:  python generar_esquematico.py
"""
import math
import os
import re
import uuid

from componentes import COMPONENTES

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.normpath(os.path.join(AQUI, "..", "KiCad_IngenieriaInversaLampara"))
NOMBRE = "KiCad_IngenieriaInversaLampara"
KICAD_SYM = r"C:\Program Files\KiCad\8.0\share\kicad\symbols"

NS = uuid.UUID("6f1c2d1e-5b7a-4c1e-9a43-0c4a1a5e7b10")
RAIZ = str(uuid.uuid5(NS, "hoja-raiz"))

# Disposición (posiciones, cables, etiquetas y textos) en esquematico_layout.py
from esquematico_layout import (LAYOUT, CABLES, ETIQUETAS, TEXTOS, CAMPOS,  # noqa: E402
                                ESPEJO, POTENCIA, PAPEL)


def uid_simbolo(ref):
    """UUID determinista del símbolo; la PCB usa el mismo para enlazar footprints."""
    return str(uuid.uuid5(NS, "sym-" + ref))


def u(sem):
    return str(uuid.uuid5(NS, sem))


def extraer_simbolo(texto, nombre):
    m = re.search(r'\n\t\(symbol "' + re.escape(nombre) + r'"', texto)
    if not m:
        raise KeyError(nombre)
    i = m.start() + 2
    prof, j, en_str = 0, i, False
    while True:
        c = texto[j]
        if en_str:
            if c == "\\":
                j += 1
            elif c == '"':
                en_str = False
        elif c == '"':
            en_str = True
        elif c == "(":
            prof += 1
        elif c == ")":
            prof -= 1
            if prof == 0:
                return texto[i:j + 1]
        j += 1


_cache = {}


def simbolo_lib(lib_id):
    """Devuelve (texto del símbolo para lib_symbols, {pin: (x, y, ángulo)})."""
    lib, nombre = lib_id.split(":")
    if lib not in _cache:
        ruta = (os.path.join(PROY, "Lampara.kicad_sym") if lib == "Lampara"
                else os.path.join(KICAD_SYM, lib + ".kicad_sym"))
        with open(ruta, encoding="utf-8") as f:
            _cache[lib] = "\n" + f.read()
    s = extraer_simbolo(_cache[lib], nombre)
    if "(extends" in s:
        raise ValueError(f"{lib_id} es un símbolo derivado; usar otro")
    s = s.replace(f'(symbol "{nombre}"', f'(symbol "{lib_id}"', 1)
    pines = {}
    for m in re.finditer(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)(?:(?!\(pin ).)*?\(number "([^"]*)"',
                         s, re.S):
        pines.setdefault(m.group(4), (float(m.group(1)), float(m.group(2)), float(m.group(3))))
    return s, pines


def rot(x, y, ang):
    a = math.radians(ang)
    return (round(x * math.cos(a) - y * math.sin(a), 4), round(x * math.sin(a) + y * math.cos(a), 4))


def pos_pin(x, y, ang, pin, espejo=None):
    """Posición del pin en la hoja. espejo: None, "x" (voltea arriba-abajo) o "y" (izquierda-derecha)."""
    dx, dy = rot(pin[0], pin[1], ang)
    if espejo == "y":
        dx = -dx
    elif espejo == "x":
        dy = -dy
    return round(x + dx, 2), round(y - dy, 2)


def fuente(oculto=False, just=None, tam=1.27):
    j = f" (justify {just})" if just else ""
    h = " (hide yes)" if oculto else ""
    return f"(effects (font (size {tam} {tam})){j}{h})"


def prop(nombre, valor, x, y, oculto=False, just=None, ang=0):
    valor = valor.replace('"', '\\"')
    return f'\t\t(property "{nombre}" "{valor}" (at {x:.2f} {y:.2f} {ang}) {fuente(oculto, just)})\n'


def campos(c, x, y, ang, pines):
    """Posición de Reference/Value según el tipo de símbolo y su rotación."""
    ref, val = c["ref"], c["value"]
    a_txt = 90 if ang in (90, 270) else 0       # así el texto se ve horizontal
    n = len(pines)
    vertical = n == 2 and all(abs(pos_pin(0, 0, ang, p)[0]) < 0.01 for p in pines.values())
    if c["sym"] == "Device:Q_NMOS_GDS":
        return (prop("Reference", ref, x + 5.08, y - 1.27, just="left"),
                prop("Value", val, x + 5.08, y + 1.27, just="left"))
    if vertical:
        j = "right" if ang == 180 else "left"  # en 180° KiCad invierte la justificación
        return (prop("Reference", ref, x + 2.54, y - 1.27, just=j, ang=a_txt),
                prop("Value", val, x + 2.54, y + 1.27, just=j, ang=a_txt))
    ys = [pos_pin(0, 0, ang, p)[1] for p in pines.values()]
    arriba = min(ys + [0]) - (2.54 if n == 2 else 3.81)
    abajo = max(ys + [0]) + (2.54 if n == 2 else 3.81)
    return (prop("Reference", ref, x, y + arriba, ang=a_txt), prop("Value", val, x, y + abajo, ang=a_txt))


# Pines de cada unidad en los símbolos de varias unidades
PINES_UNIDAD = {"Lampara:T1_EE_2dev": {1: ["3", "4"], 2: ["1", "2"]}}


def instancia(c, x, y, ang, pines, unidad=1):
    ref = c["ref"]
    f1, f2 = campos(c, x, y, ang, pines)
    clave = ref if unidad == 1 else f"{ref}#{unidad}"
    if clave in CAMPOS:   # posición fija de Reference / Value
        (rx, ry), (vx, vy) = CAMPOS[clave]
        a_txt = 90 if ang in (90, 270) else 0   # el ángulo del campo es relativo al símbolo
        f1, f2 = prop("Reference", ref, rx, ry, ang=a_txt), prop("Value", c["value"], vx, vy, ang=a_txt)
    uid = uid_simbolo(ref) if unidad == 1 else u(f"sym-{ref}-u{unidad}")
    esp = f" (mirror {ESPEJO[ref]})" if ref in ESPEJO else ""
    s = (f'\t(symbol (lib_id "{c["sym"]}") (at {x:.2f} {y:.2f} {ang}){esp} (unit {unidad})\n'
         f'\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp {"yes" if c["dnp"] else "no"})\n'
         f'\t\t(uuid "{uid}")\n')
    s += f1 + f2
    s += prop("Footprint", c["fp"], x, y, oculto=True)
    s += prop("Datasheet", "~", x, y, oculto=True)
    s += prop("Description", c.get("desc", ""), x, y, oculto=True)
    s += prop("Lado", "Superior (THT)" if c["side"] == "F" else "Inferior (SMD)", x, y, oculto=True)
    for p in pines:
        s += f'\t\t(pin "{p}" (uuid "{u("pin-" + ref + "-" + p)}"))\n'
    s += (f'\t\t(instances (project "{NOMBRE}" (path "/{RAIZ}" (reference "{ref}") (unit {unidad}))))\n'
          f'\t)\n')
    return s


def texto(t, x, y, tam=1.27, negrita=False, sem=None):
    b = " (bold yes)" if negrita else ""
    t = t.replace('"', '\\"')
    return (f'\t(text "{t}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) '
            f'(effects (font (size {tam} {tam}){b}) (justify left bottom)) (uuid "{u(sem or t)}"))\n')


def segmentos():
    for k, poli in enumerate(CABLES):
        for i in range(len(poli) - 1):
            yield k, i, poli[i], poli[i + 1]


def en_interior(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if abs(x1 - x2) < 0.01 and abs(x - x1) < 0.01:
        return min(y1, y2) + 0.01 < y < max(y1, y2) - 0.01
    if abs(y1 - y2) < 0.01 and abs(y - y1) < 0.01:
        return min(x1, x2) + 0.01 < x < max(x1, x2) - 0.01
    return False


def uniones(pines_xy):
    """Junction donde se tocan 3 o más extremos de cable/pin, o un extremo cae a mitad de cable."""
    puntos = {}
    for _, _, a, b in segmentos():
        for p in (a, b):
            k = (round(p[0], 2), round(p[1], 2))
            puntos[k] = puntos.get(k, 0) + 1
    res = []
    for p, n in puntos.items():
        n += sum(1 for q in pines_xy if abs(q[0] - p[0]) < 0.01 and abs(q[1] - p[1]) < 0.01)
        n += sum(2 for _, _, a, b in segmentos() if en_interior(p, a, b))
        if n >= 3:
            res.append(p)
    return res


def main():
    por_ref = {c["ref"]: c for c in COMPONENTES}
    faltan = set(por_ref) - set(LAYOUT)
    if faltan:
        raise ValueError(f"componentes sin posición: {sorted(faltan)}")

    libs, cuerpo, pines_xy = {}, "", []
    for ref, coloc in LAYOUT.items():
        c = por_ref[ref]
        if c["sym"] not in libs:
            libs[c["sym"]] = simbolo_lib(c["sym"])
        _, pines = libs[c["sym"]]
        if not isinstance(coloc, list):
            coloc = [tuple(coloc) + (1,)]
        for x, y, ang, unidad in coloc:
            sel = PINES_UNIDAD.get(c["sym"], {}).get(unidad)
            pu = {k: v for k, v in pines.items() if sel is None or k in sel}
            cuerpo += instancia(c, x, y, ang, pu, unidad)
            pines_xy += [pos_pin(x, y, ang, p, ESPEJO.get(ref)) for p in pu.values()]

    # Símbolos de alimentación (DC+, DC-, GND_SW, VDD): no van a la PCB ni a la BOM
    for k, (lib_id, x, y) in enumerate(POTENCIA, start=1):
        if lib_id not in libs:
            libs[lib_id] = simbolo_lib(lib_id)
        texto_lib, pines = libs[lib_id]
        val = lib_id.split(":")[1]
        vy = float(re.search(r'\(property\s+"Value"\s+"[^"]*"\s+\(at\s+[-\d.]+\s+([-\d.]+)', texto_lib).group(1))
        ref = f"#PWR{k:03d}"
        s = (f'\t(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1)\n'
             f'\t\t(exclude_from_sim no) (in_bom no) (on_board no) (dnp no)\n'
             f'\t\t(uuid "{u("pwr-" + str(k))}")\n')
        s += prop("Reference", ref, x, y, oculto=True)
        s += prop("Value", val, x, round(y - vy, 2))
        s += prop("Footprint", "", x, y, oculto=True) + prop("Datasheet", "", x, y, oculto=True)
        s += f'\t\t(pin "1" (uuid "{u("pwr-pin-" + str(k))}"))\n'
        s += (f'\t\t(instances (project "{NOMBRE}" (path "/{RAIZ}" (reference "{ref}") (unit 1))))\n\t)\n')
        cuerpo += s
        pines_xy.append((x, y))

    # KiCad solo conecta cables por sus extremos: cada tramo se parte en los
    # puntos donde llega otro cable o un pin (derivaciones en T).
    extremos = {(round(p[0], 2), round(p[1], 2)) for _, _, a, b in segmentos() for p in (a, b)}
    extremos |= {(round(p[0], 2), round(p[1], 2)) for p in pines_xy}
    for k, i, a, b in segmentos():
        if abs(a[0] - b[0]) > 0.01 and abs(a[1] - b[1]) > 0.01:
            raise ValueError(f"cable no ortogonal: {a} -> {b}")
        cortes = sorted((p for p in extremos if en_interior(p, a, b)),
                        key=lambda p: abs(p[0] - a[0]) + abs(p[1] - a[1]))
        tramo = [a] + cortes + [b]
        for j in range(len(tramo) - 1):
            p, q = tramo[j], tramo[j + 1]
            cuerpo += (f'\t(wire (pts (xy {p[0]:.2f} {p[1]:.2f}) (xy {q[0]:.2f} {q[1]:.2f})) '
                       f'(stroke (width 0) (type default)) (uuid "{u(f"w-{k}-{i}-{j}")}"))\n')
    for x, y in uniones(pines_xy):
        cuerpo += f'\t(junction (at {x:.2f} {y:.2f}) (diameter 0) (color 0 0 0 0) (uuid "{u(f"j-{x}-{y}")}"))\n'
    for n, (t, x, y, a) in enumerate(ETIQUETAS):
        just = "left" if a in (0, 90) else "right"
        cuerpo += (f'\t(label "{t}" (at {x:.2f} {y:.2f} {a}) (fields_autoplaced yes) '
                   f'(effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid "{u(f"l-{n}-{t}")}"))\n')
    for n, (t, x, y, tam, neg) in enumerate(TEXTOS):
        cuerpo += texto(t, x, y, tam, neg, sem=f"t-{n}")

    sch = (f'(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")\n'
           f'\t(uuid "{RAIZ}")\n'
           f'\t(paper "{PAPEL}")\n'
           f'\t(title_block\n'
           f'\t\t(title "Ingenieria inversa - Driver LED Tecnolite 50LHBLEDT65MV200")\n'
           f'\t\t(date "2026-11-25")\n'
           f'\t\t(rev "0.5")\n'
           f'\t\t(comment 1 "PCB original: JT047-V1 (2018-3-19)")\n'
           f'\t\t(comment 2 "Conexiones: trazado manual del cobre (pcb_tracing/) y mediciones de continuidad")\n'
           f'\t)\n'
           f'\t(lib_symbols\n')
    for s, _ in libs.values():
        sch += "\t" + s.replace("\n", "\n\t") + "\n"
    sch += "\t)\n" + cuerpo
    sch += '\t(sheet_instances (path "/" (page "1")))\n)\n'

    ruta = os.path.join(PROY, NOMBRE + ".kicad_sch")
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(sch)
    print("escrito:", ruta, "-", len(LAYOUT), "simbolos,", sum(len(p) - 1 for p in CABLES), "cables,",
          len(ETIQUETAS), "etiquetas")


if __name__ == "__main__":
    main()
