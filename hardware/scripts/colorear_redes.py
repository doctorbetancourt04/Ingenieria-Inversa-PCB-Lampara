# -*- coding: utf-8 -*-
"""
Mapa de redes por color: pinta cada isla de cobre con el color de su red sobre
la foto alineada de la cara inferior y agrega una leyenda con los pads de cada red.

- Orientación: cuello abajo, pestañas arriba (como al medir con la placa volteada).
- Línea punteada = conexión medida con multímetro que no se ve como cobre
  continuo en la foto (pads de la misma red en islas distintas).
- Gris = pads cuya conexión no se ha determinado.

Entradas: cobre_islas.json, cobre_pads.json, redes_pcb.json y
processed_images/02_foto_inferior_alineada_vista_superior.png
Salida:   processed_images/15_mapa_de_redes_por_color.png

  python colorear_redes.py
"""
import colorsys
import json
import os
import sys
from collections import Counter, defaultdict

import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)
from componentes import CONTORNO, ORIGEN_X, ORIGEN_Y, ESCALA  # noqa: E402

PPMM = 20
FIJOS = {  # colores BGR para las redes principales
    "DC+": (40, 40, 230), "DC-": (230, 90, 30), "AC_L": (20, 90, 150), "AC_N": (200, 200, 30),
    "AC_L_ENTRADA": (60, 130, 190), "AC_N_ENTRADA": (230, 230, 120),
    "LED+": (0, 150, 255), "LED-": (200, 60, 160), "VCC": (0, 220, 255), "GND_CI": (90, 90, 90),
    "COMPUERTA_CI": (60, 200, 60), "COMPUERTA_Q1": (130, 255, 130), "FB": (255, 120, 200),
    "CS": (180, 0, 255), "U1_PIN6": (255, 0, 120), "AUX_T1": (0, 120, 60),
    "RS_A": (120, 60, 255), "RS_B": (255, 200, 120),
}


def colores(nombres):
    res, libres = {}, [n for n in nombres if n not in FIJOS]
    for n in nombres:
        if n in FIJOS:
            res[n] = FIJOS[n]
    for i, n in enumerate(libres):
        r, g, b = colorsys.hsv_to_rgb((i * 0.618) % 1.0, 0.75, 0.95 if i % 2 else 0.75)
        res[n] = (int(b * 255), int(g * 255), int(r * 255))
    return res


def main():
    islas = json.load(open(os.path.join(AQUI, "cobre_islas.json"), encoding="utf-8"))
    pads = {d["ref"]: d for d in json.load(open(os.path.join(AQUI, "cobre_pads.json"), encoding="utf-8"))}
    red_de = json.load(open(os.path.join(AQUI, "redes_pcb.json"), encoding="utf-8"))
    foto = cv2.imread(os.path.join(REPO, "processed_images", "02_foto_inferior_alineada_vista_superior.png"))
    H, W = foto.shape[:2]

    cont = np.array([(ORIGEN_X + ESCALA * x, ORIGEN_Y + ESCALA * y) for x, y in CONTORNO])
    x0, y0 = cont.min(0) - 1.0

    def px(x, y):  # mm absolutos -> pixel, con volteo vertical (cuello abajo)
        return int((x - x0) * PPMM), int(H - 1 - (y - y0) * PPMM)

    cuenta = Counter(red_de.values())
    redes = sorted(n for n, k in cuenta.items() if k >= 2)
    col = colores(redes)

    # posición de cada pad
    pos = {}
    for ref, d in pads.items():
        for p in d["pads"]:
            pos.setdefault(f"{ref}.{p['num']}", (p["x"], p["y"]))

    base = cv2.addWeighted(cv2.flip(foto, 0), 0.55, np.full_like(foto, 255), 0.45, 0)
    capa = base.copy()
    isla_de_pad = {}
    for isla in islas:
        nombres = [red_de.get(f"{r}.{n}") for r, n in isla["pads"]]
        votos = Counter(n for n in nombres if n in col)
        c = col[votos.most_common(1)[0][0]] if votos else (170, 170, 170)
        for r, n in isla["pads"]:
            isla_de_pad[f"{r}.{n}"] = isla["id"]
        for poli in isla["poligonos"]:
            ext = np.array([px(x, y) for x, y in poli["exterior"]], np.int32)
            cv2.fillPoly(capa, [ext], c)
            for ag in poli["agujeros"]:
                cv2.fillPoly(capa, [np.array([px(x, y) for x, y in ag], np.int32)], base[0, 0].tolist())
    img = cv2.addWeighted(capa, 0.7, base, 0.3, 0)
    cv2.polylines(img, [np.array([px(x, y) for x, y in cont], np.int32)], True, (0, 0, 0), 2)

    # conexiones medidas sin cobre visible: unir islas distintas de la misma red
    def punteada(a, b, c):
        a, b = np.array(a, float), np.array(b, float)
        n = max(int(np.linalg.norm(b - a) / 12), 1)
        for i in range(0, n, 2):
            p, q = a + (b - a) * i / n, a + (b - a) * min(i + 1, n) / n
            cv2.line(img, tuple(int(v) for v in p), tuple(int(v) for v in q), c, 4, cv2.LINE_AA)

    for n in redes:
        miembros = [p for p, r in red_de.items() if r == n and p in pos]
        grupos = defaultdict(list)
        for p in miembros:
            grupos[isla_de_pad.get(p, "sola-" + p)].append(p)
        grupos = list(grupos.values())
        conectados = grupos[0]
        for g in grupos[1:]:
            a, b = min(((a, b) for a in conectados for b in g),
                       key=lambda ab: np.hypot(pos[ab[0]][0] - pos[ab[1]][0], pos[ab[0]][1] - pos[ab[1]][1]))
            punteada(px(*pos[a]), px(*pos[b]), (0, 0, 0))
            punteada(px(*pos[a]), px(*pos[b]), col[n])
            conectados += g

    # pads
    for k, (x, y) in pos.items():
        n = red_de.get(k)
        c = col.get(n, (150, 150, 150))
        cv2.circle(img, px(x, y), 7, c, -1, cv2.LINE_AA)
        cv2.circle(img, px(x, y), 7, (0, 0, 0), 1, cv2.LINE_AA)

    # nombre de cada red junto a su isla más grande
    mayor = {}
    for isla in islas:
        nombres = [red_de.get(f"{r}.{n}") for r, n in isla["pads"]]
        votos = Counter(n for n in nombres if n in col)
        if votos:
            n = votos.most_common(1)[0][0]
            if isla["area_mm2"] > mayor.get(n, (0, None))[0]:
                mayor[n] = (isla["area_mm2"], isla)
    for n, (_, isla) in mayor.items():
        p = np.array(isla["poligonos"][0]["exterior"]).mean(0)
        x, y = px(*p)
        for grosor, c in ((5, (255, 255, 255)), (2, (0, 0, 0))):
            cv2.putText(img, n, (x - 6 * len(n), y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, c, grosor, cv2.LINE_AA)

    # leyenda
    leyenda = np.full((H, 760, 3), 255, np.uint8)
    cv2.putText(leyenda, "Redes de la PCB JT047-V1 (cara inferior,", (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(leyenda, "cuello abajo, como al medir)", (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    yy = 115
    for n in redes:
        miembros = sorted(p for p, r in red_de.items() if r == n)
        cv2.rectangle(leyenda, (15, yy - 18), (45, yy + 4), col[n], -1)
        cv2.rectangle(leyenda, (15, yy - 18), (45, yy + 4), (0, 0, 0), 1)
        cv2.putText(leyenda, n, (55, yy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        linea, yy2 = "", yy + 24
        for m in miembros:
            if len(linea) + len(m) > 58:
                cv2.putText(leyenda, linea, (55, yy2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 60, 60), 1)
                linea, yy2 = "", yy2 + 20
            linea += m + "  "
        cv2.putText(leyenda, linea, (55, yy2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 60, 60), 1)
        yy = yy2 + 36
    for t in ("Linea punteada = conexion medida que no se ve",
              "como cobre continuo en la foto (por rutear).",
              "Gris = conexion no determinada."):
        cv2.putText(leyenda, t, (15, yy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        yy += 24

    salida = os.path.join(REPO, "processed_images", "15_mapa_de_redes_por_color.png")
    cv2.imwrite(salida, np.hstack([img, leyenda]))
    print("escrito:", salida, len(redes), "redes")


if __name__ == "__main__":
    main()
