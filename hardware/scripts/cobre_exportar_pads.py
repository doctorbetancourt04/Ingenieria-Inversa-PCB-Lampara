# -*- coding: utf-8 -*-
"""
Paso 1 de la reconstrucción del cobre: exporta los pads de la PCB a JSON
(posición absoluta en mm, tamaño, forma, capa) para que cobre_segmentar.py
pueda alinear la foto con ellos.

  "C:\\Program Files\\KiCad\\8.0\\bin\\python.exe" cobre_exportar_pads.py
"""
import json
import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar_esquematico import NOMBRE, PROY  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    board = pcbnew.LoadBoard(os.path.join(PROY, NOMBRE + ".kicad_pcb"))
    datos = []
    for fp in list(board.GetFootprints()):
        pads = []
        for p in fp.Pads():
            if not p.GetNumber():
                continue
            pos = p.GetPosition()
            bb = p.GetBoundingBox()
            pads.append(dict(
                num=p.GetNumber(),
                x=pcbnew.ToMM(pos.x), y=pcbnew.ToMM(pos.y),
                w=pcbnew.ToMM(bb.GetWidth()), h=pcbnew.ToMM(bb.GetHeight()),
                tht=p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH,
                redonda=p.GetShape() in (pcbnew.PAD_SHAPE_CIRCLE, pcbnew.PAD_SHAPE_OVAL),
            ))
        datos.append(dict(ref=fp.GetReference(), lado="B" if fp.IsFlipped() else "F",
                          fp=str(fp.GetFPID().GetLibItemName()), pads=pads))
    ruta = os.path.join(AQUI, "cobre_pads.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=1)
    print("escrito:", ruta, len(datos), "footprints")


if __name__ == "__main__":
    main()
