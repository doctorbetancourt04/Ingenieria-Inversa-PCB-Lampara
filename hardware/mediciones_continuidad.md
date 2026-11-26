# Mediciones de continuidad – PCB JT047-V1

Placa vista desde el lado del cobre, con el **cuello abajo y las pestañas arriba**
(como en `images/Bottom Layer (Volteada verticalmente).jpeg`). Las etiquetas de
los puntos están en `processed_images/14_puntos_de_medicion_ronda2.png` y en
`processed_images/14b_puntos_de_medicion_ronda2_zona_central.png`.

**Antes de medir:** placa desconectada; descargar C6 (puntos DC+ y DC−), CE3/CE4
(L+ y L−) y CE2 (VCC y GND) uniendo sus patas unos segundos con una resistencia de
~1 kΩ.

**Criterio:** en modo continuidad, "sí" = menos de ~0.5 Ω. RS1–RS4 (1.2 Ω), los
diodos y los capacitores al cargarse también pueden pitar; si hay duda, anotar los Ω.

## Ronda 1 (2026-11-25), ya incorporada a la PCB

- Franjas: D1 y D4 hacia el cuello; D2 y D3 hacia las pestañas.
- Lado pestañas: D1–D4 conectados; D2–D3 conectados. Lado cuello: D1–D2 conectados;
  D3–D4 conectados. F1 con D1 y D2. D2/D3 con R4 y el capacitor rojo.
- U1 (pin real = medido + 3; el pin 1 es el del punto): 1 = C2, R6, CE2+;
  2 = CE2−, R8; 3 = R7; 4 = R9, R11; 5 = R10; 6 = R12 y nodo R9/C4.
- RS1–RS4 en paralelo. CE3 ∥ CE4 (270 µF / 100 V).
- Q1: solo la pata hacia las pestañas (QS) tiene continuidad con T1.

## Ronda 2 (en curso)

Resultados ya incorporados:
- **El pad del drenaje de Q1 (QD) está despegado o con la soldadura fisurada.** Por
  eso no daba continuidad. Puede ser la causa de la falla de la lámpara; conviene
  resoldarlo antes de seguir midiendo QD.
- Un pin de C3 (C3x) tiene continuidad con DC+ (nodo de los cátodos de D2/D3).

### A. Devanados de T1 (modo resistencia, anotar Ω)

| # | Entre | Ω |
|---|---|---|
| A1 | TA – TB | |
| A2 | TA – TC | |
| A3 | TA – TD | |
| A4 | TB – TC | |
| A5 | TB – TD | |
| A6 | TC – TD | |

### B. Drenaje de Q1 y aislamiento entrada–salida (continuidad)

| # | Entre | ¿Sí/No? |
|---|---|---|
| B1 | QD – DC+ | |
| B2 | QD – DC− | |
| B3 | QD – L+ | |
| B4 | QD – L− | |
| B5 | QS – TC | |
| B6 | L− – DC− | |
| B7 | L− – DC+ | |
| B8 | L+ – DC+ | |
| B9 | L+ – DC− | |

### C. Tierra del CI y resistores de sensado (continuidad)

| # | Entre | ¿Sí/No? |
|---|---|---|
| C1 | GND – DC− | |
| C2 | GND – L− | |
| C3 | GND – QS | |
| C4 | GND – RA | |
| C5 | GND – RB | |
| C6 | RA – QS | |
| C7 | RB – QS | |
| C8 | RA – DC− | |
| C9 | RB – DC− | |

### D. Diodo de salida D8 y devanado auxiliar

| # | Qué | Resultado |
|---|---|---|
| D1 | Franja de D8: ¿en la pata doblada de arriba o en el cuerpo junto a la placa? ¿8a o 8b corresponde a la pata doblada? | |
| D2 | 8a – L− / 8a – L+ | |
| D3 | 8b con TA, TB, TC, TD, DC+ o QD (¿con cuál?) | |
| D4 | 13b – 8b | |
| D5 | Franja de D7: ¿hacia 7a (pestañas) o hacia 7b (cuello)? | |
| D6 | 7a con TA, TB, TC o TD (¿con cuál?) | |
| D7 | 11x (extremo libre de R11) con TA, TB, TC, TD, 7a, 7b o GND (¿con cuál?) | |

### E. Pads que quedaron sueltos

| # | Entre | Resultado |
|---|---|---|
| E1 | C2x – GND | |
| E2 | 12T – TC | |
| E3 | C3x con GND, VCC, QD, QS o CS (¿con cuál?) | |
| E4 | E1+ – DC+ / E1− – DC− (CE1, no montado) | |
| E5 | 5b – E1+ | |
| E6 | R2x con DC+, DC−, E1+ o 5b (¿con cuál?) | |

### F. Identificación visual

| # | Qué | Resultado |
|---|---|---|
| F1 | Serigrafía (cara superior) del componente negro vertical junto al cable N (el que se llamó R1) | |
| F2 | Texto impreso en los discos azules VR1 (entre L y N) y VR3 (junto al capacitor rojo) | |
