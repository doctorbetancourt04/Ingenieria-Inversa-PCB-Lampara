# -*- coding: utf-8 -*-
"""
Sincroniza los nombres de red entre la PCB y el esquemático (Python de KiCad 8).

  exportar  : escribe redes_pcb.json {"REF.PAD": "nombre"} con las redes reales
              de la PCB (se omiten las "unconnected-..."). generar_esquematico.py
              lo usa para poner las etiquetas de red en cada pin.
  igualar   : lee el netlist del esquemático (netlist.net, exportado con
              kicad-cli) y renombra cada red de la PCB con el nombre que le da
              el esquemático (p. ej. "DC+" -> "/DC+"), usando los pads como llave.

  "C:\\Program Files\\KiCad\\8.0\\bin\\python.exe" redes_pcb.py exportar|igualar
"""
import json
import os
import re
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar_esquematico import NOMBRE, PROY  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RUTA_PCB = os.path.join(PROY, NOMBRE + ".kicad_pcb")


def exportar():
    board = pcbnew.LoadBoard(RUTA_PCB)
    redes = {}
    for fp in list(board.GetFootprints()):
        for p in fp.Pads():
            n = p.GetNetname()
            if p.GetNumber() and n and not n.startswith("unconnected-"):
                redes[f"{fp.GetReference()}.{p.GetNumber()}"] = n.lstrip("/")
    with open(os.path.join(AQUI, "redes_pcb.json"), "w", encoding="utf-8") as f:
        json.dump(redes, f, indent=1, sort_keys=True)
    print(len(redes), "pads con red,", len(set(redes.values())), "redes")


def igualar():
    with open(os.path.join(AQUI, "netlist.net"), encoding="utf-8") as f:
        txt = f.read()
    # (net (code "1") (name "/DC+") ... (node (ref "D2") (pin "1") ...) ...)
    nombre_sch = {}
    for bloque in re.split(r"\(net \(code", txt)[1:]:
        m = re.search(r'\(name "((?:[^"\\]|\\.)*)"\)', bloque)
        if not m:
            continue
        for ref, pin in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', bloque):
            nombre_sch[f"{ref}.{pin}"] = m.group(1)

    board = pcbnew.LoadBoard(RUTA_PCB)
    renombres = {}
    for fp in list(board.GetFootprints()):
        for p in fp.Pads():
            k = f"{fp.GetReference()}.{p.GetNumber()}"
            ni = p.GetNet()
            if k in nombre_sch and ni and ni.GetNetCode() > 0 and ni.GetNetname() != nombre_sch[k]:
                renombres.setdefault(ni.GetNetname(), (ni, nombre_sch[k]))
    for viejo, (ni, nuevo) in renombres.items():
        ni.SetNetname(nuevo)
        print(f"  {viejo} -> {nuevo}")
    board.BuildConnectivity()
    pcbnew.SaveBoard(RUTA_PCB, board)
    print(len(renombres), "redes renombradas")


if __name__ == "__main__":
    {"exportar": exportar, "igualar": igualar}[sys.argv[1]]()
