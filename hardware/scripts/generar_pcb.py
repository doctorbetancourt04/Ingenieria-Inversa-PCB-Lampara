# -*- coding: utf-8 -*-
"""
Genera KiCad_IngenieriaInversaLampara.kicad_pcb: contorno de la placa,
footprints colocados según las fotos (THT arriba, SMD abajo) y enlazados a
los símbolos del esquemático (mismo UUID).

Debe ejecutarse con el Python que trae KiCad 8:
  "C:\\Program Files\\KiCad\\8.0\\bin\\python.exe" generar_pcb.py
"""
import math
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from componentes import COMPONENTES, CONTORNO, ORIGEN_X, ORIGEN_Y, ESCALA  # noqa: E402
from generar_esquematico import uid_simbolo, NOMBRE, PROY  # noqa: E402

KICAD_FP = r"C:\Program Files\KiCad\8.0\share\kicad\footprints"
MM = pcbnew.FromMM


def abs_xy(x, y):
    return pcbnew.VECTOR2I(MM(ORIGEN_X + ESCALA * x), MM(ORIGEN_Y + ESCALA * y))


def ruta_lib(lib):
    if lib == "Lampara":
        return os.path.join(PROY, "Lampara.pretty")
    return os.path.join(KICAD_FP, lib + ".pretty")


def pads_por_nombre(fp, nombre):
    return [p for p in fp.Pads() if p.GetNumber() == nombre]


def centro_pads(fp):
    xs = [p.GetPosition().x for p in fp.Pads() if p.GetNumber()]
    ys = [p.GetPosition().y for p in fp.Pads() if p.GetNumber()]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def mover(fp, dx, dy):
    fp.Move(pcbnew.VECTOR2I(int(round(dx)), int(round(dy))))


def colocar(fp, place):
    tipo = place[0]
    if tipo == "o":
        _, x, y, rot = place
        fp.SetOrientationDegrees(rot)
        p = abs_xy(x, y)
        mover(fp, p.x - fp.GetPosition().x, p.y - fp.GetPosition().y)
    elif tipo == "c":
        _, x, y, rot = place
        fp.SetOrientationDegrees(rot)
        cx, cy = centro_pads(fp)
        p = abs_xy(x, y)
        mover(fp, p.x - cx, p.y - cy)
    elif tipo == "2p":
        _, na, (xa, ya), nb, (xb, yb) = place
        a, b = abs_xy(xa, ya), abs_xy(xb, yb)
        deseado = math.degrees(math.atan2(b.y - a.y, b.x - a.x))
        for _ in range(3):  # gira hasta que el vector padA->padB coincida
            pa = pads_por_nombre(fp, na)[0].GetPosition()
            pb = pads_por_nombre(fp, nb)[0].GetPosition()
            actual = math.degrees(math.atan2(pb.y - pa.y, pb.x - pa.x))
            delta = (deseado - actual + 180) % 360 - 180
            if abs(delta) < 0.05:
                break
            # en pantalla (Y hacia abajo) un ángulo positivo de KiCad es antihorario
            fp.Rotate(fp.GetPosition(), pcbnew.EDA_ANGLE(-delta, pcbnew.DEGREES_T))
        pa = pads_por_nombre(fp, na)[0].GetPosition()
        pb = pads_por_nombre(fp, nb)[0].GetPosition()
        mover(fp, (a.x + b.x) / 2 - (pa.x + pb.x) / 2, (a.y + b.y) / 2 - (pa.y + pb.y) / 2)
    # redondear orientación a 1 grado para que quede limpia
    o = round(fp.GetOrientationDegrees())
    fp.SetOrientationDegrees(o)


def linea(board, x1, y1, x2, y2, capa, ancho=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(abs_xy(x1, y1))
    s.SetEnd(abs_xy(x2, y2))
    s.SetLayer(capa)
    s.SetWidth(MM(ancho))
    board.Add(s)


def cota(board, x1, y1, x2, y2, altura):
    d = pcbnew.PCB_DIM_ALIGNED(board)
    d.SetLayer(pcbnew.Cmts_User)
    d.SetStart(abs_xy(x1, y1))
    d.SetEnd(abs_xy(x2, y2))
    d.SetHeight(MM(altura))
    d.SetUnitsMode(pcbnew.DIM_UNITS_MODE_MILLIMETRES)
    d.SetPrecision(pcbnew.DIM_PRECISION_X_X)
    board.Add(d)


def cotas(board):
    """Cotas generales: ancho, largo total y cuello."""
    cota(board, -21.25, 98.0, 21.25, 98.0, 18.0)
    cota(board, -21.25, 0.0, -21.25, 111.2, 8.0)
    cota(board, -9.0, 0.0, 9.0, 0.0, -5.0)


def texto(board, t, x, y, capa, tam=1.5):
    tx = pcbnew.PCB_TEXT(board)
    tx.SetText(t)
    tx.SetPosition(abs_xy(x, y))
    tx.SetLayer(capa)
    tx.SetTextSize(pcbnew.VECTOR2I(MM(tam), MM(tam)))
    tx.SetTextThickness(MM(tam * 0.15))
    if capa == pcbnew.B_SilkS:
        tx.SetMirrored(True)
    board.Add(tx)


def main():
    ruta = os.path.join(PROY, NOMBRE + ".kicad_pcb")
    board = pcbnew.NewBoard(ruta)
    board.SetCopperLayerCount(2)

    # Contorno
    n = len(CONTORNO)
    for i in range(n):
        x1, y1 = CONTORNO[i]
        x2, y2 = CONTORNO[(i + 1) % n]
        linea(board, x1, y1, x2, y2, pcbnew.Edge_Cuts)

    cotas(board)
    texto(board, "JT047-V1  2018-3-19", -2.0, 70.0, pcbnew.F_SilkS, 1.2)
    texto(board, "Reconstruccion KiCad - dimensiones aprox. (+/-1 mm)", 0.0, 120.0, pcbnew.Cmts_User, 1.2)

    sin_dnp = not hasattr(pcbnew, "FP_DNP")
    for c in COMPONENTES:
        lib, nombre = c["fp"].split(":")
        fp = pcbnew.FootprintLoad(ruta_lib(lib), nombre)
        if fp is None:
            raise RuntimeError("No se encontró el footprint " + c["fp"])
        fp.SetFPID(pcbnew.LIB_ID(lib, nombre))
        fp.SetReference(c["ref"])
        fp.SetValue(c["value"])
        fp.SetPath(pcbnew.KIID_PATH("/" + uid_simbolo(c["ref"])))
        fp.SetSheetname("Root")
        fp.SetSheetfile(NOMBRE + ".kicad_sch")
        if c["dnp"] and not sin_dnp:
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_DNP)
        board.Add(fp)
        if c["side"] == "B":
            fp.Flip(fp.GetPosition(), True)
        colocar(fp, c["place"])

    pcbnew.SaveBoard(ruta, board)
    print("escrito:", ruta, "-", len(COMPONENTES), "footprints",
          "(sin atributo DNP en esta versión)" if sin_dnp else "")


if __name__ == "__main__":
    main()
