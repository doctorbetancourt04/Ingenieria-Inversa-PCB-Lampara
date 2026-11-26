# -*- coding: utf-8 -*-
"""
Genera KiCad_IngenieriaInversaLampara.kicad_sch con todos los componentes de
componentes.py, ordenados por bloques funcionales y con su footprint asignado.

Si existe redes_pcb.json (creado con 'redes_pcb.py exportar' a partir del cobre
reconstruido), cada pin recibe un tramo corto de cable y una etiqueta con el
nombre de su red, de modo que el esquemático queda conectado igual que la PCB.

Uso:  python generar_esquematico.py
"""
import json
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

# Bloques del esquemático: (título, x, y, columnas, referencias en orden)
BLOQUES = [
    ("Entrada AC y filtro EMI", 45.72, 63.5, 4,
     ["P1", "F1", "R1", "VR1", "VR2", "LF1", "L1", "CX1", "RL1"]),
    ("Puente rectificador y bus DC", 304.8, 63.5, 4,
     ["D1", "D2", "D3", "D4", "C6", "VR3", "CE1"]),
    ("Etapa de potencia: T1, Q1, sensado y devanado auxiliar", 45.72, 165.1, 4,
     ["T1", "Q1", "RS1", "RS2", "RS3", "RS4", "D7", "R6", "C3", "D5", "R2", "R3"]),
    ("Salida a los LEDs", 304.8, 165.1, 4,
     ["D8", "CE3", "CE4", "J1", "R14", "R15", "C5", "R13"]),
    ("Controlador U1 y arranque", 45.72, 292.1, 6,
     ["U1", "CE2", "C2", "C1", "R4", "R5", "R7", "R8", "D6", "R9", "R10", "R11", "R12", "C4"]),
]
DX, DY = 50.8, 25.4
STUB = 2.54


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


def fuente(oculto=False, just=None, tam=1.27):
    j = f" (justify {just})" if just else ""
    h = " (hide yes)" if oculto else ""
    return f"(effects (font (size {tam} {tam})){j}{h})"


def prop(nombre, valor, x, y, oculto=False, just=None, ang=0):
    valor = valor.replace('"', '\\"')
    return f'\t\t(property "{nombre}" "{valor}" (at {x:.2f} {y:.2f} {ang}) {fuente(oculto, just)})\n'


def instancia(c, x, y, ang, pines):
    ref = c["ref"]
    ys = [-(rot(px, py, ang)[1]) for px, py, _ in pines.values()]
    arriba, abajo = min(ys + [0]) - 3.81, max(ys + [0]) + 3.81
    if c["sym"] == "Device:Q_NMOS_GDS":
        campos = (prop("Reference", ref, x + 5.08, y - 1.27, just="left"),
                  prop("Value", c["value"], x + 5.08, y + 1.27, just="left"))
    elif ang:
        # símbolo girado: el ángulo del campo se guarda igual al del símbolo
        # para que el texto se vea horizontal
        campos = (prop("Reference", ref, x, y - 2.54, ang=ang), prop("Value", c["value"], x, y + 2.54, ang=ang))
    else:
        campos = (prop("Reference", ref, x, y + arriba), prop("Value", c["value"], x, y + abajo))
    s = (f'\t(symbol (lib_id "{c["sym"]}") (at {x:.2f} {y:.2f} {ang}) (unit 1)\n'
         f'\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp {"yes" if c["dnp"] else "no"})\n'
         f'\t\t(uuid "{uid_simbolo(ref)}")\n')
    s += campos[0] + campos[1]
    s += prop("Footprint", c["fp"], x, y, oculto=True)
    s += prop("Datasheet", "~", x, y, oculto=True)
    s += prop("Description", c.get("desc", ""), x, y, oculto=True)
    s += prop("Lado", "Superior (THT)" if c["side"] == "F" else "Inferior (SMD)", x, y, oculto=True)
    for p in pines:
        s += f'\t\t(pin "{p}" (uuid "{u("pin-" + ref + "-" + p)}"))\n'
    s += (f'\t\t(instances (project "{NOMBRE}" (path "/{RAIZ}" (reference "{ref}") (unit 1))))\n'
          f'\t)\n')
    return s


def etiqueta_en_pin(ref, num, red, x, y, ang, pin):
    """Cable corto hacia afuera del pin y etiqueta local con el nombre de la red."""
    px, py, pa = pin
    dx, dy = rot(px, py, ang)
    x1, y1 = x + dx, y - dy                     # punto de conexión (y de pantalla hacia abajo)
    ox, oy = rot(math.cos(math.radians(pa + 180)), math.sin(math.radians(pa + 180)), ang)
    x2, y2 = x1 + ox * STUB, y1 - oy * STUB
    if abs(ox) > abs(oy):
        a_lbl, just = (0, "left") if ox > 0 else (180, "right")
    else:
        a_lbl, just = (90, "left") if oy > 0 else (270, "right")
    sem = f"{ref}-{num}"
    red_txt = red.replace('"', '\\"')
    return (f'\t(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) '
            f'(stroke (width 0) (type default)) (uuid "{u("w-" + sem)}"))\n'
            f'\t(label "{red_txt}" (at {x2:.2f} {y2:.2f} {a_lbl}) (fields_autoplaced yes) '
            f'(effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid "{u("l-" + sem)}"))\n')


def texto(t, x, y, tam=1.27, negrita=False, sem=None):
    b = " (bold yes)" if negrita else ""
    t = t.replace('"', '\\"')
    return (f'\t(text "{t}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) '
            f'(effects (font (size {tam} {tam}){b}) (justify left bottom)) (uuid "{u(sem or t)}"))\n')


def main():
    ruta_redes = os.path.join(AQUI, "redes_pcb.json")
    redes = {}
    if os.path.exists(ruta_redes):
        with open(ruta_redes, encoding="utf-8") as f:
            redes = json.load(f)
        # Redes de un solo pin = conexión no determinada: el pin queda libre
        # (el ERC lo marca como pendiente) en vez de llevar una etiqueta suelta.
        cuenta = {}
        for n in redes.values():
            cuenta[n] = cuenta.get(n, 0) + 1
        redes = {k: n for k, n in redes.items() if cuenta[n] > 1}

    por_ref = {c["ref"]: c for c in COMPONENTES}
    en_bloques = [r for _, _, _, _, refs in BLOQUES for r in refs]
    faltan = set(por_ref) - set(en_bloques)
    if faltan:
        raise ValueError(f"componentes sin bloque: {sorted(faltan)}")

    libs, cuerpo, n_etiquetas = {}, "", 0
    for titulo, x0, y0, cols, refs in BLOQUES:
        cuerpo += texto(titulo, x0 - 10.16, y0 - 20.32, tam=2.0, negrita=True)
        for k, ref in enumerate(refs):
            c = por_ref[ref]
            if c["sym"] not in libs:
                libs[c["sym"]] = simbolo_lib(c["sym"])
            _, pines = libs[c["sym"]]
            # pasivos de 2 pines con pines verticales -> se giran a horizontal
            ang = 90 if len(pines) == 2 and all(a in (90.0, 270.0) for _, _, a in pines.values()) else 0
            x = x0 + (k % cols) * DX
            y = y0 + (k // cols) * DY
            cuerpo += instancia(c, x, y, ang, pines)
            for num, pin in pines.items():
                red = redes.get(f"{ref}.{num}")
                if red:
                    cuerpo += etiqueta_en_pin(ref, num, red, x, y, ang, pin)
                    n_etiquetas += 1

    nota = ("ESQUEMATICO RECONSTRUIDO por ingenieria inversa de la PCB JT047-V1 (2018-3-19).\\n"
            "Conexiones: cobre de la cara inferior segmentado a partir de fotos + mediciones de continuidad "
            "(ver prompts/ y processed_images/). Cada etiqueta de red = una red de la PCB.\\n"
            "Valores con '?' no legibles. DNP = pads presentes sin componente. Pines sin etiqueta: conexion no determinada.")
    cuerpo += texto(nota, 25.4, 25.4, tam=1.5, sem="nota")

    sch = (f'(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")\n'
           f'\t(uuid "{RAIZ}")\n'
           f'\t(paper "A2")\n'
           f'\t(title_block\n'
           f'\t\t(title "Ingenieria inversa - Driver LED Tecnolite 50LHBLEDT65MV200")\n'
           f'\t\t(date "2026-11-25")\n'
           f'\t\t(rev "0.2")\n'
           f'\t\t(comment 1 "PCB original: JT047-V1 (2018-3-19)")\n'
           f'\t\t(comment 2 "Conexiones reconstruidas del cobre (fotos) y mediciones de continuidad")\n'
           f'\t)\n'
           f'\t(lib_symbols\n')
    for s, _ in libs.values():
        sch += "\t" + s.replace("\n", "\n\t") + "\n"
    sch += "\t)\n" + cuerpo
    sch += '\t(sheet_instances (path "/" (page "1")))\n)\n'

    ruta = os.path.join(PROY, NOMBRE + ".kicad_sch")
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(sch)
    print("escrito:", ruta, "-", len(COMPONENTES), "simbolos,", n_etiquetas, "etiquetas de red")


if __name__ == "__main__":
    main()
