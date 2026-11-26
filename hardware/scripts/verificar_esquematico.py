# -*- coding: utf-8 -*-
"""
Compara el netlist del esquemático (netlist.net, exportado con
'kicad-cli sch export netlist') con las redes de la PCB (redes_pcb.json).

Para cada red de la PCB con 2 o más pines verifica que esos pines formen
exactamente una red en el esquemático, sin pines de más ni de menos.

  python verificar_esquematico.py
"""
import json
import os
import re
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(os.path.join(AQUI, "redes_pcb.json"), encoding="utf-8") as f:
        pcb = json.load(f)
    with open(os.path.join(AQUI, "netlist.net"), encoding="utf-8") as f:
        txt = f.read()
    sch = {}
    for bloque in re.split(r"\(net \(code", txt)[1:]:
        m = re.search(r'\(name "((?:[^"\\]|\\.)*)"\)', bloque)
        for ref, pin in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', bloque):
            sch[f"{ref}.{pin}"] = m.group(1)

    grupos_pcb = defaultdict(set)
    for p, n in pcb.items():
        grupos_pcb[n].add(p)
    grupos_sch = defaultdict(set)
    for p, n in sch.items():
        grupos_sch[n].add(p)

    errores = 0
    for n, pines in sorted(grupos_pcb.items()):
        if len(pines) < 2:
            continue
        redes = {sch.get(p) for p in pines}
        if len(redes) != 1 or None in redes:
            print(f"PARTIDA  {n}: " + ", ".join(f"{p}->{sch.get(p)}" for p in sorted(pines)))
            errores += 1
            continue
        extra = grupos_sch[redes.pop()] - pines
        if extra:
            print(f"DE MAS   {n}: pines extra {sorted(extra)}")
            errores += 1
    print("OK: el esquemático coincide con las redes de la PCB" if not errores else f"{errores} diferencias")


if __name__ == "__main__":
    main()
