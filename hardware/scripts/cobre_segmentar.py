# -*- coding: utf-8 -*-
"""
Paso 2 de la reconstrucción del cobre (Python normal con opencv, numpy, scipy).

Lee la foto 'Bottom Layer (Volteada verticalmente).jpeg', la alinea con los
pads de la PCB (cobre_pads.json) mediante puntos de control y una
transformación thin-plate spline, segmenta el cobre por color y genera:

  - cobre_islas.json : polígonos (mm absolutos de KiCad) de cada isla de
                       cobre y los pads que conecta.
  - processed_images/: imágenes intermedias de cada paso (ver README.md ahí).

  python cobre_segmentar.py
"""
import json
import os
import sys

import cv2
import numpy as np
from scipy.interpolate import RBFInterpolator

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)
from componentes import CONTORNO, ORIGEN_X, ORIGEN_Y, ESCALA  # noqa: E402

# Intento 1 (descartado): "Bottom Layer (Volteada verticalmente).jpeg". Su
# iluminación no es uniforme y el color no separaba bien cobre y laminado.
# Intento 2: la foto original de la cara inferior, con luz más pareja.
FOTO = os.path.join(REPO, "images", "Bottom Layer.jpeg")
SALIDA = os.path.join(REPO, "processed_images")
PPMM = 20  # resolución del raster alineado (pixeles por mm)

# Puntos de control: (referencia, pad o None = centro del footprint, x_foto, y_foto)
# Coordenadas leídas sobre 'Bottom Layer.jpeg' (vista desde abajo, sin espejar).
CONTROL = [
    ("D1", None, 352.5, 687.5), ("D2", None, 422.5, 687.5), ("D3", None, 510, 690), ("D4", None, 580, 690),
    ("R2", None, 250, 665), ("R3", None, 250, 732.5), ("D5", None, 180, 798.5), ("D6", None, 267.5, 836),
    ("R8", None, 325, 837.5), ("R7", None, 265, 862.5), ("R4", None, 442.5, 785), ("R5", None, 442.5, 837.5),
    ("R6", None, 442.5, 882.5), ("D7", None, 507.5, 912.5), ("C2", None, 362.5, 920), ("C3", None, 175, 945),
    ("R9", None, 290, 982.5), ("C4", None, 245, 994), ("U1", None, 337.5, 977.5), ("R12", None, 387.5, 1000),
    ("R10", None, 256, 1031), ("R11", None, 330, 1031), ("R13", None, 242.5, 1092), ("RS2", None, 330, 1079),
    ("RS1", None, 327.5, 1110), ("RS3", None, 327.5, 1139), ("RS4", None, 327.5, 1168.5), ("C5", None, 242.5, 1162),
    ("R14", None, 252.5, 1247.5), ("R15", None, 472.5, 1245), ("RL1", None, 532.5, 557.5),
    # pads THT cuyos footprints coinciden con lo medido
    ("T1", "1", 565, 925), ("T1", "2", 565, 1100), ("T1", "3", 430, 980), ("T1", "4", 427.5, 1097.5),
    ("LF1", "1", 430, 455), ("LF1", "2", 430, 505), ("LF1", "3", 345, 450), ("LF1", "4", 345, 505),
    ("CE3", "1", 512.5, 1277.5), ("CE3", "2", 512.5, 1220), ("CE4", "1", 220, 1270), ("CE4", "2", 222.5, 1210),
]


# Componentes a los que no se aplica la regla "pines distintos = islas distintas":
# U1 puede tener pines unidos a propósito (p. ej. tierra o pines NC).
EXENTOS_REGLA = {"U1"}

# Ajustes manuales de pads donde la foto no alcanza (soldadura entre pines a
# 2.5 mm). Valor = pad cuya isla se copia, o None = dejar el pad sin isla.
AJUSTES_PADS = {
    ("J1", "1"): ("CE4", "2"),   # J1 pin 1 (LED -) con los negativos de CE3/CE4
    ("CE2", "1"): None,          # pines de CE2: la foto no los separa; se asignan
    ("CE2", "2"): None,          # con las mediciones de continuidad (cobre_redes.py)
}


def mm_abs(x, y):
    return ORIGEN_X + ESCALA * x, ORIGEN_Y + ESCALA * y


def guardar(nombre, img):
    os.makedirs(SALIDA, exist_ok=True)
    cv2.imwrite(os.path.join(SALIDA, nombre), img)
    print("imagen:", nombre)


def main():
    with open(os.path.join(AQUI, "cobre_pads.json"), encoding="utf-8") as f:
        fps = {d["ref"]: d for d in json.load(f)}
    foto = cv2.imread(FOTO)

    # ---------- 1. puntos de control ----------
    tablero, imagen = [], []
    for ref, num, xi, yi in CONTROL:
        pads = fps[ref]["pads"]
        if num is not None:
            pads = [p for p in pads if p["num"] == num]
        tablero.append((np.mean([p["x"] for p in pads]), np.mean([p["y"] for p in pads])))
        imagen.append((xi, yi))
    tablero, imagen = np.array(tablero), np.array(imagen)

    # Ajuste afín (diagnóstico) y residuos
    A = np.c_[tablero, np.ones(len(tablero))]
    coef, *_ = np.linalg.lstsq(A, imagen, rcond=None)
    res = np.linalg.norm(A @ coef - imagen, axis=1)
    escala_px = np.sqrt(abs(np.linalg.det(coef[:2])))
    print(f"ajuste afín: {escala_px:.2f} px/mm, residuo medio {res.mean() / escala_px:.2f} mm, "
          f"máx {res.max() / escala_px:.2f} mm ({CONTROL[int(res.argmax())][0]})")

    vis = foto.copy()
    for (xi, yi), (ref, num, *_ ) in zip(imagen, CONTROL):
        cv2.circle(vis, (int(xi), int(yi)), 6, (0, 0, 255), 2)
        cv2.putText(vis, ref + (f".{num}" if num else ""), (int(xi) + 7, int(yi) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    guardar("01_foto_inferior_puntos_de_control.png", vis)

    # ---------- 2. alineación thin-plate spline (tablero -> foto) ----------
    tps = RBFInterpolator(tablero, imagen, kernel="thin_plate_spline", smoothing=2.0)
    cont = np.array([mm_abs(x, y) for x, y in CONTORNO])
    x0, y0 = cont.min(0) - 1.0
    x1, y1 = cont.max(0) + 1.0
    W, H = int((x1 - x0) * PPMM), int((y1 - y0) * PPMM)
    gx, gy = np.meshgrid(x0 + (np.arange(W) + 0.5) / PPMM, y0 + (np.arange(H) + 0.5) / PPMM)
    mapa = tps(np.c_[gx.ravel(), gy.ravel()]).astype(np.float32)
    mx, my = mapa[:, 0].reshape(H, W), mapa[:, 1].reshape(H, W)
    alineada = cv2.remap(foto, mx, my, cv2.INTER_LINEAR, borderValue=(255, 255, 255))
    guardar("02_foto_inferior_alineada_vista_superior.png", alineada)

    def a_px(x, y):
        return (x - x0) * PPMM, (y - y0) * PPMM

    contorno_px = np.array([a_px(x, y) for x, y in cont], np.int32)
    dentro = np.zeros((H, W), np.uint8)
    cv2.fillPoly(dentro, [contorno_px], 255)
    dentro = cv2.erode(dentro, np.ones((5, 5), np.uint8))

    # ---------- 3. índice de verdor y umbral ----------
    # La máscara verde sobre laminado desnudo refleja mucho más verde que rojo;
    # sobre cobre se ve café/oliva (G ~ R). Índice = (G - R) / G.
    f = alineada.astype(np.float32)
    indice = (f[..., 1] - f[..., 2]) / (f[..., 1] + 1)
    indice_u8 = np.clip((indice + 0.2) / 1.2 * 255, 0, 255).astype(np.uint8)
    guardar("03_indice_verdor_gris.png", indice_u8)
    umbral, _ = cv2.threshold(indice_u8[dentro > 0], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    print(f"umbral Otsu: {umbral:.0f} (índice {umbral / 255 * 1.2 - 0.2:.2f})")
    cobre = ((indice_u8 < umbral) & (dentro > 0)).astype(np.uint8) * 255
    guardar("04_mascara_cobre_cruda_otsu.png", cobre)

    # ---------- 4. limpieza ----------
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cobre = cv2.morphologyEx(cobre, cv2.MORPH_OPEN, k)    # quita trazos finos de serigrafía sobre verde
    cobre = cv2.morphologyEx(cobre, cv2.MORPH_CLOSE, k)   # rellena serigrafía sobre cobre

    # cuerpos de componentes SMD: el espacio entre pads no es cobre
    for d in fps.values():
        if d["lado"] != "B" or len(d["pads"]) < 2:
            continue
        P = d["pads"]
        xs = [p["x"] for p in P]
        ys = [p["y"] for p in P]
        if len(P) == 2:
            a, b = P
            horiz = abs(a["x"] - b["x"]) > abs(a["y"] - b["y"])
            # el cuerpo suele ser más ancho que el pad: se corta 0.5 mm extra a cada lado
            if horiz:
                xa, xb = sorted([a["x"], b["x"]])
                w = min(a["w"], b["w"]) / 2
                r = (xa + w + 0.05, (a["y"] + b["y"]) / 2 - a["h"] / 2 - 0.5,
                     xb - w - 0.05, (a["y"] + b["y"]) / 2 + a["h"] / 2 + 0.5)
            else:
                ya, yb = sorted([a["y"], b["y"]])
                hh = min(a["h"], b["h"]) / 2
                r = ((a["x"] + b["x"]) / 2 - a["w"] / 2 - 0.5, ya + hh + 0.05,
                     (a["x"] + b["x"]) / 2 + a["w"] / 2 + 0.5, yb - hh - 0.05)
        else:  # SOT-23-6: zona entre las dos filas de pines
            ymin = min(p["y"] for p in P)
            ymax = max(p["y"] for p in P)
            r = (min(xs) - 0.3, ymin + 0.5, max(xs) + 0.3, ymax - 0.5)
        p1, p2 = a_px(r[0], r[1]), a_px(r[2], r[3])
        cv2.rectangle(cobre, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), 0, -1)

    # Los pads NO se pintan como cobre: con ±0.4 mm de error de alineación, un
    # pad pintado puede caer sobre la separación de 0.5 mm entre dos pistas y
    # unirlas (le pasó a J1 en una prueba). Cada pad se asigna después a la isla
    # que más cobre tiene bajo su área.
    pads_px = []
    for d in fps.values():
        for p in d["pads"]:
            cx, cy = a_px(p["x"], p["y"])
            pads_px.append((d["ref"], p["num"], int(cx), int(cy),
                            int(p["w"] / 2 * PPMM), int(p["h"] / 2 * PPMM)))
    cobre[dentro == 0] = 0
    vis = cv2.cvtColor(cobre, cv2.COLOR_GRAY2BGR)
    for _, _, cx, cy, rw, rh in pads_px:
        cv2.rectangle(vis, (cx - rw, cy - rh), (cx + rw, cy + rh), (0, 0, 255), 1)
    guardar("05_mascara_cobre_limpia_y_pads.png", vis)

    # ---------- 5. separar puentes finos (erosión + watershed) ----------
    # Las separaciones verdes entre pistas miden ~0.4-0.6 mm; con sombras o con
    # la serigrafía a veces quedan "puentes" de cobre falsos de pocos pixeles.
    # Se erosiona 0.25 mm, se etiquetan los núcleos y cada pixel de cobre se
    # asigna al núcleo más cercano (watershed). Así se cortan los puentes finos
    # sin adelgazar las pistas.
    R_EROSION = int(0.25 * PPMM)
    nucleo = cv2.erode(cobre, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * R_EROSION + 1,) * 2))
    guardar("05b_nucleos_erosionados.png", nucleo)
    n, marcas = cv2.connectedComponents(nucleo, connectivity=4)
    marcas = marcas.astype(np.int32)
    marcas[cobre == 0] = n            # fondo: marca propia
    cv2.watershed(cv2.cvtColor(cobre, cv2.COLOR_GRAY2BGR), marcas)
    etiquetas = np.where((marcas > 0) & (marcas < n) & (cobre > 0), marcas, 0)

    def asignar_pads(etq):
        """isla de cada pad = etiqueta más frecuente bajo el área del pad"""
        res = {}
        for r, num, cx, cy, rw, rh in pads_px:
            sub = etq[max(cy - rh, 0):cy + rh + 1, max(cx - rw, 0):cx + rw + 1].ravel()
            sub = sub[sub > 0]
            if sub.size >= 0.15 * (2 * rw + 1) * (2 * rh + 1):
                res[(r, num)] = int(np.bincount(sub).argmax())
        return res

    # ---------- 5c. regla física: un componente montado no puede quedar en corto ----------
    # Si dos pines distintos de un componente montado caen en la misma isla, esa
    # isla se vuelve a separar con erosiones cada vez mayores (se cortan primero
    # los puentes más angostos) hasta que los pines queden en islas distintas.
    # Los componentes no montados (DNP) quedan exentos: la placa original puentea
    # con cobre algunos de ellos (L1, LF1, RL) para que el circuito funcione sin ellos.
    from componentes import COMPONENTES
    montados = {c["ref"] for c in COMPONENTES if not c["dnp"]} - EXENTOS_REGLA

    def conflictos(asig):
        malos = {}
        for (r, num), isla in asig.items():
            if r in montados:
                malos.setdefault((r, isla), set()).add(num)
        return {k: v for k, v in malos.items() if len(v) > 1}

    siguiente = int(etiquetas.max()) + 1
    for _ in range(40):
        malos = conflictos(asignar_pads(etiquetas))
        if not malos:
            break
        (ref, isla), nums = next(iter(malos.items()))
        mask_isla = (etiquetas == isla).astype(np.uint8) * 255
        resuelto = False
        for r_mm in (0.35, 0.45, 0.55, 0.65, 0.8, 1.0):
            rr = int(r_mm * PPMM)
            nuc = cv2.erode(mask_isla, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * rr + 1,) * 2))
            k2, lab = cv2.connectedComponents(nuc, connectivity=4)
            if k2 <= 2:
                continue
            mk = lab.astype(np.int32)
            mk[mask_isla == 0] = k2
            cv2.watershed(cv2.cvtColor(mask_isla, cv2.COLOR_GRAY2BGR), mk)
            prueba = etiquetas.copy()
            sub = (mask_isla > 0) & (mk > 0) & (mk < k2)
            prueba[mask_isla > 0] = 0
            prueba[sub] = mk[sub] + siguiente
            if not any(k[0] == ref for k in conflictos(asignar_pads(prueba))):
                etiquetas, resuelto = prueba, True
                siguiente += k2
                print(f"  corte: {ref} {sorted(nums)} separados con erosión {r_mm} mm")
                break
        if not resuelto:
            print(f"  AVISO: no se pudo separar {ref} {sorted(nums)} (isla {isla})")
            montados.discard(ref)
    guardar("05c_islas_tras_regla_de_cortos.png",
            (np.where(etiquetas > 0, 60 + (etiquetas * 37) % 190, 255)).astype(np.uint8))

    # ---------- 6. islas de cobre ----------
    isla_de_pad = asignar_pads(etiquetas)
    for (r, num), destino in AJUSTES_PADS.items():
        if destino is None:
            isla_de_pad.pop((r, num), None)
            print(f"  ajuste manual: {r}.{num} sin isla (por verificar)")
        elif destino in isla_de_pad:
            isla_de_pad[(r, num)] = isla_de_pad[destino]
            print(f"  ajuste manual: {r}.{num} -> isla de {destino[0]}.{destino[1]}")
    n = int(etiquetas.max()) + 1

    islas = []
    rng = np.random.default_rng(7)
    colores = np.zeros((H, W, 3), np.uint8) + 255
    for i in range(1, n):
        m = (etiquetas == i)
        area = m.sum() / PPMM ** 2
        if area < 0.5:
            continue
        miembros = sorted(k for k, v in isla_de_pad.items() if v == i)
        if not miembros and area < 3:
            continue  # fragmento pequeño sin pads (ruido)
        mask = m.astype(np.uint8) * 255
        cnts, jer = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        polis = []
        for j, c in enumerate(cnts):
            if jer[0][j][3] != -1:
                continue  # agujero: se agrega con su exterior
            ext = cv2.approxPolyDP(c, 1.5, True).reshape(-1, 2)
            agujeros = []
            hijo = jer[0][j][2]
            while hijo != -1:
                ag = cv2.approxPolyDP(cnts[hijo], 1.5, True).reshape(-1, 2)
                if cv2.contourArea(cnts[hijo]) > (0.8 * PPMM) ** 2 and len(ag) >= 3:
                    agujeros.append([[x0 + (px + 0.5) / PPMM, y0 + (py + 0.5) / PPMM] for px, py in ag])
                hijo = jer[0][hijo][0]
            if len(ext) >= 3:
                polis.append(dict(exterior=[[x0 + (px + 0.5) / PPMM, y0 + (py + 0.5) / PPMM] for px, py in ext],
                                  agujeros=agujeros))
        islas.append(dict(id=len(islas) + 1, area_mm2=round(float(area), 1),
                          pads=[[r, num] for r, num in miembros], poligonos=polis))
        colores[m] = rng.integers(40, 230, 3)

    for r, num, cx, cy, _, _ in pads_px:
        cv2.circle(colores, (cx, cy), 3, (0, 0, 0) if (r, num) in isla_de_pad else (0, 0, 255), -1)
    cv2.polylines(colores, [contorno_px], True, (0, 0, 0), 1)
    for isla in islas:
        p = np.array(isla["poligonos"][0]["exterior"])
        cx, cy = a_px(*p.mean(0))
        cv2.putText(colores, str(isla["id"]), (int(cx), int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    guardar("06_islas_de_cobre_numeradas.png", colores)

    sobre = cv2.addWeighted(alineada, 0.55, colores, 0.45, 0)
    guardar("07_islas_superpuestas_a_la_foto.png", sobre)

    with open(os.path.join(AQUI, "cobre_islas.json"), "w", encoding="utf-8") as f:
        json.dump(islas, f, indent=1)
    print(len(islas), "islas")
    for isla in islas:
        print(f"  isla {isla['id']:2d} ({isla['area_mm2']:6.1f} mm2):",
              " ".join(f"{r}.{n}" for r, n in isla["pads"]))


if __name__ == "__main__":
    main()
