# -*- coding: utf-8 -*-
"""
Actualiza la PCB existente SIN regenerarla: conserva las redes asignadas
desde KiCad (Actualizar placa desde esquema), las pistas y todo lo demás.

  - Redibuja el contorno (Edge.Cuts) con CONTORNO de componentes.py.
  - Reemplaza los footprints indicados por los definidos en componentes.py,
    copiando la red de cada pad (por número de pad).

Cerrar el editor de placas de KiCad antes de ejecutarlo. Uso:
  "C:\\Program Files\\KiCad\\8.0\\bin\\python.exe" actualizar_pcb.py [--contorno] REF [REF ...]
"""
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from componentes import COMPONENTES, CONTORNO  # noqa: E402
from generar_esquematico import uid_simbolo, NOMBRE, PROY  # noqa: E402
from generar_pcb import ruta_lib, colocar, linea, cotas  # noqa: E402


def redibujar_contorno(board, dibujos):
    for d in dibujos:
        if d.GetLayer() == pcbnew.Edge_Cuts or isinstance(d, pcbnew.PCB_DIM_ALIGNED):
            board.Remove(d)
    cotas(board)
    n = len(CONTORNO)
    for i in range(n):
        x1, y1 = CONTORNO[i]
        x2, y2 = CONTORNO[(i + 1) % n]
        linea(board, x1, y1, x2, y2, pcbnew.Edge_Cuts)


def reemplazar(board, c, footprints):
    viejo = next((f for f in footprints if f.GetReference() == c["ref"]), None)
    redes = {}
    if viejo:
        for p in viejo.Pads():
            redes.setdefault(p.GetNumber(), p.GetNet())
        board.Remove(viejo)
    lib, nombre = c["fp"].split(":")
    fp = pcbnew.FootprintLoad(ruta_lib(lib), nombre)
    fp.SetFPID(pcbnew.LIB_ID(lib, nombre))
    fp.SetReference(c["ref"])
    fp.SetValue(c["value"])
    fp.SetPath(pcbnew.KIID_PATH("/" + uid_simbolo(c["ref"])))
    fp.SetSheetname("Root")
    fp.SetSheetfile(NOMBRE + ".kicad_sch")
    if c["dnp"] and hasattr(pcbnew, "FP_DNP"):
        fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_DNP)
    board.Add(fp)
    if c["side"] == "B":
        fp.Flip(fp.GetPosition(), True)
    colocar(fp, c["place"])
    for p in fp.Pads():
        if p.GetNumber() in redes:
            p.SetNet(redes[p.GetNumber()])
    print("reemplazado:", c["ref"], "->", c["fp"])


def main(args):
    ruta = os.path.join(PROY, NOMBRE + ".kicad_pcb")
    board = pcbnew.LoadBoard(ruta)
    refs = [a for a in args if not a.startswith("--")]
    por_ref = {c["ref"]: c for c in COMPONENTES}
    # En KiCad 8, después de board.Remove() los envoltorios SWIG ya no pueden
    # iterar Footprints()/Drawings(), así que se leen ambas listas al inicio.
    footprints = list(board.GetFootprints())
    dibujos = list(board.GetDrawings())
    for r in refs:
        reemplazar(board, por_ref[r], footprints)
    if "--contorno" in args:
        redibujar_contorno(board, dibujos)
        print("contorno redibujado")
    pcbnew.SaveBoard(ruta, board)
    print("guardado:", ruta)


if __name__ == "__main__":
    main(sys.argv[1:])
