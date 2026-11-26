# -*- coding: utf-8 -*-
"""
Paso 3 de la reconstrucción del cobre (Python de KiCad 8).

1. Construye las redes uniendo:
   - los pads que comparten una isla de cobre (cobre_islas.json), y
   - las conexiones medidas con multímetro (CONEXIONES_MEDIDAS).
   Las islas marcadas como poco confiables no unen sus pads automáticamente.
2. Asigna esas redes a los pads de la PCB.
3. Crea una zona de cobre en B.Cu por cada isla, con la red de la mayoría de
   sus pads, y rellena las zonas.
4. Escribe cobre_reporte.txt con las redes y las contradicciones encontradas.

  "C:\\Program Files\\KiCad\\8.0\\bin\\python.exe" cobre_crear_zonas.py
"""
import json
import os
import sys
from collections import Counter, defaultdict

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from componentes import COMPONENTES  # noqa: E402
from generar_esquematico import NOMBRE, PROY  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))

# Mediciones de continuidad hechas en la placa real (ver prompts/bitacora_prompts.md).
# Numeración de pads de KiCad. Diodos: pad 1 = cátodo (franja).
CONEXIONES_MEDIDAS = [
    # Puente rectificador: D1 y D4 con la franja hacia el cuello, D2 y D3 hacia las pestañas
    ["D1.2", "D4.2"],                 # ánodos D1+D4 (lado pestañas) -> DC-
    ["D2.1", "D3.1"],                 # cátodos D2+D3 (lado pestañas) -> DC+
    ["D1.1", "D2.2", "F1.2"],         # lado cuello D1+D2, conectado a F1 -> AC (fase)
    ["D3.2", "D4.1"],                 # lado cuello D3+D4 -> AC (neutro)
    ["D2.1", "R4.2", "C6.1"],         # DC+ con R4 y el capacitor rojo
    ["VR3.2", "D2.1"],                # varistor a la salida del puente (deducido)
    ["VR2.2", "D4.1"],                # varistor de entrada entre fase y neutro (deducido)
    # RS1-RS4 en paralelo; CE3 y CE4 en paralelo
    ["RS1.1", "RS2.1", "RS3.1", "RS4.1"], ["RS1.2", "RS2.2", "RS3.2", "RS4.2"],
    ["CE3.1", "CE4.1"], ["CE3.2", "CE4.2"],
    # U1: pin 1 real = punto (esquina inferior izquierda con el cuello abajo).
    # La primera medición numeró desde la esquina opuesta: pin real = medido + 3.
    ["U1.4", "R9.1", "R11.2"],        # pin 4 (medido 1): R9 y R11        -> FB
    ["U1.5", "R10.1"],                # pin 5 (medido 2): R10             -> CS
    ["U1.6", "R12.2", "R9.2", "C4.2"],  # pin 6 (medido 3): R12, nodo R9/C4
    ["U1.1", "C2.1", "R6.2", "CE2.2"],  # pin 1 (medido 4): C2, R6, CE2 (+) -> VCC
    ["U1.2", "CE2.1", "R8.1"],        # pin 2 (medido 5): CE2 (-), R8      -> GND del CI
    ["U1.3", "R7.1"],                 # pin 3 (medido 6): R7               -> GATE
    # Q1: la pata hacia las pestañas tiene continuidad con T1 (a través de R12, 0 ohm)
    ["Q1.3", "R12.2"],
    # Ronda 2: un pin de C3 (pad suelto en la foto) tiene continuidad con DC+.
    # El pad del drenaje de Q1 está despegado: su conexión queda por confirmar.
    ["C3.1", "D2.1"],
]

# Islas cuyos pads NO se unen automáticamente (la foto mezcla redes): las que
# contienen pines de U1 o de CE2.
NO_CONFIABLES = {"U1", "CE2"}

# Nombres para las redes identificadas (cualquier pad de la red sirve de llave)
NOMBRES = {
    "P1.1": "AC_L_ENTRADA", "P1.2": "AC_N_ENTRADA",
    "F1.2": "AC_L", "D4.1": "AC_N",
    "D2.1": "DC+", "D1.2": "DC-",
    "U1.1": "VCC", "U1.2": "GND_CI", "U1.3": "COMPUERTA_CI", "Q1.1": "COMPUERTA_Q1",
    "U1.4": "FB", "U1.5": "CS", "U1.6": "U1_PIN6",
    "RS1.1": "RS_A", "RS1.2": "RS_B",
    "CE4.1": "LED+", "CE4.2": "LED-", "T1.1": "AUX_T1",
}


class UF:
    def __init__(self):
        self.p = {}

    def f(self, a):
        self.p.setdefault(a, a)
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def u(self, a, b):
        self.p[self.f(a)] = self.f(b)


def main():
    with open(os.path.join(AQUI, "cobre_islas.json"), encoding="utf-8") as f:
        islas = json.load(f)
    uf = UF()
    for isla in islas:
        pads = [f"{r}.{n}" for r, n in isla["pads"]]
        for p in pads:
            uf.f(p)
        if any(p.split(".")[0] in NO_CONFIABLES for p in pads):
            continue
        for p in pads[1:]:
            uf.u(pads[0], p)
    for grupo in CONEXIONES_MEDIDAS:
        for p in grupo[1:]:
            uf.u(grupo[0], p)

    grupos = defaultdict(list)
    for p in list(uf.p):
        grupos[uf.f(p)].append(p)

    nombre_de = {}
    for raiz, pads in grupos.items():
        nombre = next((NOMBRES[p] for p in sorted(pads) if p in NOMBRES), None)
        if nombre is None:
            nombre = "N-" + sorted(pads)[0].replace(".", "-")
        for p in pads:
            nombre_de[p] = nombre

    # ---- PCB ----
    ruta = os.path.join(PROY, NOMBRE + ".kicad_pcb")
    board = pcbnew.LoadBoard(ruta)
    footprints = list(board.GetFootprints())
    zonas_viejas = list(board.Zones())
    for z in zonas_viejas:
        board.Remove(z)

    redes = {}

    def red(nombre):
        if nombre not in redes:
            # si el esquemático ya la nombró con prefijo de hoja ("/VCC"), se reutiliza
            ni = board.FindNet("/" + nombre)
            if ni is None or ni.GetNetCode() <= 0:
                ni = board.FindNet(nombre)
            if ni is None or ni.GetNetCode() <= 0:
                ni = pcbnew.NETINFO_ITEM(board, nombre)
                board.Add(ni)
            redes[nombre] = ni
        return redes[nombre]

    asignados = 0
    for fp in footprints:
        for pad in fp.Pads():
            k = f"{fp.GetReference()}.{pad.GetNumber()}"
            if k in nombre_de:
                pad.SetNet(red(nombre_de[k]))
                asignados += 1

    mm = pcbnew.FromMM
    prioridad = 0
    for isla in islas:
        pads = [f"{r}.{n}" for r, n in isla["pads"]]
        votos = Counter(nombre_de[p] for p in pads if p in nombre_de)
        nombre = votos.most_common(1)[0][0] if votos else None
        for poli in isla["poligonos"]:
            z = pcbnew.ZONE(board)
            z.SetLayer(pcbnew.B_Cu)
            z.SetIsRuleArea(False)
            if nombre:
                z.SetNet(red(nombre))
            z.SetLocalClearance(mm(0.25))
            z.SetMinThickness(mm(0.2))
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
            z.SetAssignedPriority(prioridad)
            z.SetZoneName(f"isla_{isla['id']}")
            prioridad += 1
            o = z.Outline()
            io = o.NewOutline()
            for x, y in poli["exterior"]:
                o.Append(mm(x), mm(y), io)
            for ag in poli["agujeros"]:
                ih = o.NewHole(io)
                for x, y in ag:
                    o.Append(mm(x), mm(y), io, ih)
            # Inflar 0.15 mm: une fragmentos de la misma red separados por las
            # líneas de corte del watershed (1 px = 0.05 mm). Entre redes
            # distintas manda la prioridad: la zona de menor prioridad respeta
            # 0.25 mm de separación con el relleno de la de mayor prioridad.
            o.Inflate(mm(0.15), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, mm(0.01))
            board.Add(z)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(ruta, board)

    # ---- reporte ----
    montados = {c["ref"] for c in COMPONENTES if not c["dnp"]}
    lineas = ["REDES RECONSTRUIDAS (islas de cobre + mediciones)", ""]
    for nombre in sorted(set(nombre_de.values())):
        miembros = sorted(p for p, n in nombre_de.items() if n == nombre)
        lineas.append(f"{nombre:16s} {' '.join(miembros)}")
    lineas += ["", "CONTRADICCIONES (dos pines de un componente montado en la misma red):"]
    por_ref = defaultdict(lambda: defaultdict(list))
    for p, n in nombre_de.items():
        r, num = p.split(".")
        por_ref[r][n].append(num)
    hay = False
    for r in sorted(por_ref):
        for n, nums in por_ref[r].items():
            if r in montados and len(set(nums)) > 1:
                lineas.append(f"  {r}: pines {sorted(set(nums))} en {n}")
                hay = True
    if not hay:
        lineas.append("  ninguna")
    with open(os.path.join(AQUI, "cobre_reporte.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"{asignados} pads con red, {prioridad} zonas, {len(set(nombre_de.values()))} redes")
    print("\n".join(lineas[-6:]))


if __name__ == "__main__":
    main()
