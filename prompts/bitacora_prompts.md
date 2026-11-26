# Bitácora de prompts

- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Herramienta:** Claude Code (app de escritorio de Claude, pestaña Code)
- **Proyecto:** Ingeniería inversa de la PCB del bombillo LED Tecnolite 50LHBLEDT65MV200

Los prompts aparecen exactamente como los escribí, con sus errores de tipeo. Después de
cada uno resumo lo que hizo la IA.

---

## Prompt 1 — Licencia del hardware

**Fecha:** 2026-11-25

> Hola Claude. Será que podrías generar un arcivo LICENSE en la carpeta Hardware con la siguiente licencia

Junto con el prompt pegué el texto completo de la licencia *Creative Commons
Attribution-ShareAlike 4.0 International*. No lo repito aquí porque es el mismo que
quedó en [`hardware/LICENSE`](../hardware/LICENSE).

**Resultado:** La IA creó `hardware/LICENSE` con el texto pegado, sin cambios. El
`LICENSE` de la raíz del repositorio no se tocó.

---

## Prompt 2 — Esquemático, footprints y layout en KiCad

**Fecha:** 2026-11-25

> Hola Claude. Tengo una tarea importante para ti. Estoy haciendo un mini-proyecto de vacaciones. Para este proyecto saqué la PCB de una lampara LED del modelo Tecnolite 50LHBledt65mv200 y le haré ingeniería inversa: reconstruir la Layout de la PCB y el esquemático del circuito. Para ello estaré utilizando el software KiCad. Dado que considero que la parte iterativa de seleccionar footprints es tediosa y repetitiva, me gustaría que pruebes tomar control de mi computadora y me ayudes colocando componentes en el esquemático, escoger las footprints que correspondan y elaborar la Layout de la PCB en los archivos del proyecto de KiCad. Quiero que tomes de referencia las imagenes adjuntas en la carpeta donde se muestran las dimensiones de largo y ancho de la PCB.
>
> Por favor en la carpeta prompts quiero que hagas un README y una bitácora de los prompts de IA que utilicé para elaborar este proyecto, incluyendo el nombre del modelo (en este caso Opus 5.5) y la herramientas que usé (Claude Code). Quiero que en esta bitácora se incluyan los prompts que utilicé escritos tal y como los puse. Esto ayudará a ser más transparentes sobre cómo me ayudaste a hacer este proyecto.

**Resultado:**

1. **Análisis de las fotos** (`images/`): la IA amplió las fotos de ambas caras para
   leer las etiquetas de serigrafía. Calculó la escala con las reglas, superpuso una
   cuadrícula en mm y reflejó la foto de la cara inferior para que coincidiera con la
   vista superior. Así estimó:
   - Placa: 42.5 mm de ancho, 111.2 mm de largo total (98 mm de cuerpo + pestañas de
     13.2 mm), cuello de 18.4 mm.
   - 50 posiciones de componentes, entre montados y no montados (DNP).
2. **Esquemático:** colocó los 50 símbolos en 4 bloques (entrada AC/EMI, rectificador,
   potencia/salida y control), cada uno con su footprint. Marcó los no montados como DNP
   y los valores ilegibles con `?`. No dibujó conexiones porque requieren trazar las
   pistas.
3. **Footprints:** usó las librerías estándar de KiCad donde había equivalente (SMA,
   SOD-123, SOT-23-6, 1206/0805, TO-220, CP_Radial D13, C_Rect P15, RV_Disc,
   JST XH, etc.). Creó tres footprints propios con las posiciones medidas: entrada AC
   por cables, choque de modo común y transformador de 4 pines.
4. **PCB:** dibujó el contorno en Edge.Cuts con cotas y colocó los footprints (THT
   arriba, SMD abajo), enlazados a los símbolos del esquemático.
5. **Control de la computadora:** la IA pidió acceso a KiCad para revisar el resultado
   en pantalla y lo denegué. La revisión se hizo exportando el esquemático y la PCB a
   imágenes con `kicad-cli`, y los archivos se generaron con los scripts de
   `hardware/scripts/`.
6. **Verificación:** se corrieron ERC y DRC con `kicad-cli`. Las advertencias que quedan
   son pines sin conectar (normal, aún no hay cables), solapes de courtyard en la zona
   de entrada y entre huellas no montadas, y detalles de serigrafía.
7. Creó este README y esta bitácora.

---

## Prompt 3 — Fotos adicionales

**Fecha:** 2026-11-25

> Dime si necesitas más fotos de la PCB

**Resultado:** La IA respondió que con las fotos actuales podía avanzar y que, para
afinar después, servirían:

- Una foto perpendicular de la cara inferior con regla.
- Acercamientos de las marcas de los SMD.
- Medidas con vernier (ancho, largo, cuello, pestañas y diámetro de CE3/CE4).
- El texto impreso en Q1, CE3/CE4, el capacitor CBB, D8 y los discos azules.

---

## Prompt 4 — Fotos nuevas y segundo intento de control de KiCad

**Fecha:** 2026-11-25

> Agregué más fotografías. Perdona. No quise negarte el acceso a KiCad. Podrías volver a intentar?

**Resultado:**

- La IA revisó las 17 fotos nuevas (acercamientos del CI, del MOSFET y de los diodos,
  cara inferior con regla, vistas 3D y mediciones con vernier) y actualizó
  `hardware/scripts/componentes.py`:
  - Q1 = **FIR12N65F** (MOSFET N, 12 A / 650 V), footprint cambiado a TO-220F.
  - CE2 = 10 µF / 50 V.
  - RS1, RS2, RS3 = 1.2 Ω (1R20); RS4 = 1.3 Ω (1R30).
  - R4, R5 = 330 kΩ (334); R6, R7 = 22 Ω (220); R8, R14 = 75 kΩ (753); R9 = 12 kΩ (123);
    R10 = 560 Ω (561); R11 = 68 kΩ (683); R12 = 0 Ω.
  - D6 = 1N4148W probable (marca T4).
  - C2 y C4 sí están montados (MLCC sin marca). La etiqueta que antes se leyó como
    "RT" es "RL", así que el componente pasó a llamarse RL1 (no montado).
  - El ancho de la placa medido en las fotos con regla es ~43.6 mm, por lo que todas
    las posiciones de la PCB se reescalaron por 43.6/42.5.
- Esta vez acepté el acceso a KiCad. La IA abrió el proyecto, el editor de esquemas
  y, con F8, *Actualizar placa desde esquema* para sincronizar las redes con la PCB.
  KiCad tardó unos segundos en responder mientras cargaba las librerías de footprints.

### Mensajes durante la sesión

> Ohh rayos la pantalla no responde

> Ya respondió, hay una pantalla de actualizar placa desde esquema

**Resultado:** La IA dejó de mandar clics, comprobó que KiCad seguía procesando (no
estaba colgado) y siguió cuando volvió a responder.

---

## Prompt 5 — Serigrafía de VR2

**Fecha:** 2026-11-25

> Podrías hacer la silkscreen de VR2.

**Resultado:**

- La IA midió la serigrafía original de VR2 en `Top Layer.jpeg`: un óvalo vertical de
  ~4.25 × 11 mm, una marca "|" en el centro, la etiqueta "VR2" a la derecha y los dos
  agujeros en diagonal dentro del óvalo (paso ~7.5 mm). Con eso creó el footprint
  `Lampara:VR2_Ovalo_P7.5mm` y lo asignó a VR2 en el esquemático y en la PCB.
- Al medir notó que el hombro del contorno no era una diagonal continua: tiene un
  escalón horizontal corto a Y≈15 mm y luego una diagonal de pendiente ~0.69. Corrigió
  el contorno, lo que también eliminó el choque de VR2 con el borde.
- Para no perder las redes que KiCad asignó con *Actualizar placa desde esquema*, creó
  `hardware/scripts/actualizar_pcb.py`. Este script cambia footprints y contorno sobre
  la placa existente en lugar de regenerarla. Antes cerró la ventana de KiCad que había
  abierto, que no tenía cambios sin guardar.
- DRC después del cambio: 0 problemas de paridad con el esquemático y sin solapes de
  courtyard. Quedan las 2 conexiones de los pads dobles de P1, que se resuelven al
  rutear, y detalles de serigrafía.

---

## Prompt 6 — Pistas de la cara inferior a partir de las fotos

**Fecha:** 2026-11-25

> ¿Podrías intentar hacer las traces en la bottom layer con las imágenes que te pasé?

### Mensajes durante el proceso

> Para fines científicos, podrías colocar todas las imágenes segmentadas y procesadas que generaste para elaborar las traces en una nueva carpeta processed_images. Por favor pon nombres de archivo explicativos y crea un md que explique qué significa cada imagen

> Estoy grabando el proceso, dime cuando ocurra algo interesante xd

> Dime si necesitas que te ayude con alguna conexión

> Creo que el circuito donde tienes problemas es un puente rectificador

> Dame una lista de clarificaciones que necesites que haga para acelerar el proceso de elaborar las traces

> Necesitas que mida continuidad?

> Revisión 1 - Franjas de diodos
> D1 - Cuello
> D2 - Pestañas
> D3 - Pestañas
> D4 - Cuello
>
> Revisión 2
> Defino arriba como la dirección del cuello hacia las pestañas (Donde las etiquetas de la silkscreen salen en orientación correcta). Empiezo con los pines de arriba
>
> * D1 y D4 están conectados
> * D2 y D3 están conectados
>
>
> Y ahora voy con los pines de abajo
>
> * D1 y D2 están conectados
> * D3 y D4 están conectados
>
>
> Revisión 3
>
> * Los diodos D1 y D2 están conectados a F1
>
> Después de una revisión bastante exhaustiva de la placa encontré que R1 no aparece en la bottom layer y en la top layer no hay resistores THT. Los diodos D2 y D3 tienen continuidad con R4 y C1.
>
> Si te ayuda también hice mediciones de continuidad alrededor de U1. Vamos a numerar sus pines desde 1 empezando por la esquina superior derecha, viendo la placa con el cuello abajo y las patas arriba. El número incrementa primero de derecha a izquierda y en la segunda fila de pines de abajo hacia arriba. Piensa que recorremos el integrado en sentido antihorario
>
> 1. se conecta a R9, R1
> 2. Se conecta a R10
> 3. Se conecta a R12. También tiene una track que va por debajo de U1 hacia el nodo que conecta R9 y C4 y el cátodo del diodo de potencia D6.
> 4. Se conecta a C2 y a R6 Y la pata positiva del capacitor THT CE2
> 5. Se conecta a la pata negativa del capacitor THT CE2 y al resistor R8
> 6. Se conecta al resistor R7
>
>
> También pude ver que los resistores RS1-RS4 están conectados en paralelo.
>
> Yo pienso que esta PCB es una fuente de poder AC-DC. En la entrada del cuello podemos ver un filtro de entrada LC. LF1 es un espacio destinado posiblemente a un filtro choke. Por debajo del cuello está el puente rectificador cuya salida se conecta a un varistor (para proteger de picos de voltaje) y un capacitor de filtrado (de ahi su gran tamaño). Lo que sigue después parece ser un convertidor DC-DC aislado magnéticamente. Yo pienso que eso explica el uso del MOSFET, el diodo gigantesco y el transformador de alta frecuencia. Dado que el voltaje de entrada es un voltaje DC de 168 V DC sin carga, y la salida puede ser mayor o menor (dependiendo del número de LEDs), yo sugiero que ese es un convertidor Flyback. El transformador sugiere que este es un convertidor reductor y la salida es un voltaje mucho menor a una corriente alta.
>
> Lo interesante es que parece que ambos el controlador del convertidor y el driver del MOSFET se encuentran en la bottom layer. Muy posiblemente ambos bloques funcionales están implementados a través de U1, y todos los elementos pasivos a su alrededor sirven para compensar el sistema (o son los requeridos por el integrado). Investiga si hay una hoja de datos del dispositivo, o encuentra un dispositivo similar y revisa la layout recomendada.
>
> Los capacitores CE3 y CE4 parecen estar conectados en paralelo. Ambos son capacitores de 270 uF a 100V.

**Resultado:**

1. **Segmentación del cobre** (`hardware/scripts/cobre_segmentar.py`; todas las
   imágenes intermedias están en `processed_images/`, con su README):
   - Alineación foto–PCB con 43 puntos de control y una thin-plate spline (error de
     0.09 mm promedio).
   - Primer intento con la foto "volteada", descartado por la iluminación desigual.
     Luego un índice de verdor (G−R)/G con umbral de Otsu sobre `Bottom Layer.jpeg`.
   - Separación de puentes falsos con erosión + watershed.
   - Regla física: un componente montado no puede tener dos pines en la misma isla;
     donde pasaba, la isla se erosionó más hasta separarlos.
   - Error encontrado y corregido: pintar los pads como cobre unía redes (J1 quedó
     sobre la separación entre dos pistas). Ahora cada pad se asigna a la isla con más
     cobre bajo su área.
2. **Mediciones del usuario incorporadas**:
   - D1 y D4 se giraron (franja hacia el cuello).
   - La polaridad de CE2 se corrigió (+ = VCC del CI).
   - CE3 y CE4 = 270 µF / 100 V.
   - Los pines de U1 medidos coinciden 1:1 con la numeración de KiCad, porque la foto
     "volteada" es la vista inferior girada 180°.
3. **Redes y zonas** (`cobre_crear_zonas.py`): 33 redes (AC_L, AC_N, DC+, DC−, VCC,
   GND_CI, COMPUERTA_CI, COMPUERTA_Q1, RS_A/RS_B, LED+, LED−, AUX_T1, …) y 48 zonas
   de cobre en B.Cu, rellenas. DRC: sin cortos ni violaciones de separación. Quedan 15
   conexiones medidas que la foto no muestra como cobre continuo (aparecen como
   ratsnest en KiCad).
4. **Puntos pendientes de la IA:**
   - "R1" en el pin 1 de U1 se interpretó como R11, porque R9 y R11 comparten isla.
   - "C1" con D2/D3 se interpretó como el capacitor rojo (C6 en el esquemático),
     porque la isla de cobre une C6 con D2 y R4.
   - Según las islas, el cátodo de D6 está en la salida de compuerta de U1 (pin 6),
     no en el nodo R9/C4. Falta confirmarlo.
   - T1 queda con los pines 2 y 4 en LED+. Podría ser real (devanados con un nodo
     común) o un error de numeración de T1.
5. **Búsqueda de la hoja de datos de U1:** no se pudo identificar, porque la marca no
   se lee. Con las conexiones medidas los pines serían: 1 = realimentación (divisor
   R11/R9 desde el devanado auxiliar), 2 = sensado de corriente (R10 hacia RS1–RS4),
   3 = compensación/otra función (R12, R9, C4), 4 = VCC, 5 = GND, 6 = GATE. Se
   revisaron controladores PSR en SOT-23-6 (TI TPS92315, Dialog iW3626/iW3627,
   Holtek HT7L5600, onsemi NCL30100/FL7760, Feeling FP7172) y ninguno coincide al 100%.

---

## Prompt 7 — Esquemático conectado

**Fecha:** 2026-11-25

> Genial. Ahora podrías hacer el esquemático.

**Resultado:**

- La IA cerró el editor de esquemas de KiCad que estaba abierto (sin cambios
  pendientes), para que no sobrescribiera el archivo nuevo.
- `redes_pcb.py exportar` leyó la red de cada pad de la PCB. Después
  `generar_esquematico.py` regeneró el esquemático (hoja A2) en 5 bloques: entrada
  AC/EMI, puente rectificador y bus DC, etapa de potencia (T1, Q1, sensado, devanado
  auxiliar), salida a los LEDs, y controlador U1 con su arranque. Cada pin lleva un
  tramo corto de cable con una etiqueta local de su red (101 etiquetas). Los pasivos
  se dibujaron horizontales.
- Las redes de un solo pin (conexión no determinada: drenaje de Q1, R11.1, C2.2,
  C3.1, R2.2, CE1.2) se dejaron sin etiqueta, para que el ERC las marque como
  pendientes en lugar de esconderlas.
- `redes_pcb.py igualar` renombró las redes de la PCB con los nombres que genera el
  esquemático (p. ej. `DC+` → `/DC+`). Así *Actualizar placa desde esquema* (F8)
  ya se puede usar sin perder las zonas de cobre.
- Verificación con `kicad-cli`:
  - ERC: 8 avisos, todos de pines sin conectar: las 6 redes de un pin y C1 (no montado).
  - DRC: 0 problemas de paridad esquemático–PCB y 15 conexiones por rutear con pistas.

---

## Prompt 8 — Identificación de U1 y pin 1

**Fecha:** 2026-11-25

> @"C:\Users\mario\Downloads\WhatsApp Video 2026-11-25 at 5.34.28 PM.mp4"
> Al revisar el integrado encontré que es un H0TN SL87 (o 9L99) flyback converter. No encontré algun fabricante que lo produzca. La inscripción se ve muy borrosa y me cuesta verla con la lupa. Lo que si logré ver es que desde el cuello hacia las pestañas hay un punto en la esquina inferior izquierda del integrado. Grabé este video

### Mensaje durante el proceso

> Y lo que vi es que dos de tres patas no tienen continuidad con el transformer excepto la que está más próxima a las pestañas

**Resultado:**

- La IA extrajo con OpenCV los cuadros más nítidos del video (645 cuadros, 474×850)
  y amplió U1 ×6. Se lee "H0?N" / "•9L9?", con el punto de pin 1 abajo a la
  izquierda (`processed_images/12_*.png` y `13_*.png`). Las búsquedas web con
  H0TN, 9L99 y SL87 no encontraron fabricante; probablemente es un controlador
  genérico que solo trae código de lote.
- **Corrección de numeración:** la medición del prompt 6 numeró desde la esquina
  opuesta al punto, así que pin real = pin medido + 3. Pinout corregido: 1 = VCC,
  2 = GND, 3 = GATE (R7 → Q1), 4 = FB (R9/R11), 5 = CS (R10 → RS1–RS4),
  6 = función desconocida (R12, nodo R9/C4 y fuente de Q1). El footprint de U1 se
  giró 180° y el símbolo `Lampara:IC_SOT-23-6` ahora tiene esos nombres de pin.
- **Q1:** que la pata hacia las pestañas tenga continuidad con T1 coincide con lo
  reconstruido (fuente de Q1 → R12, 0 Ω → T1 pin 3). La pata central (drenaje) no
  conecta con T1 y quedó como conexión por determinar.
- Se volvió a correr toda la cadena (segmentación → zonas → esquemático → nombres de
  red). Resultado: 0 problemas de paridad. El ERC deja solo los 8 pines sin conectar
  conocidos (las redes de un pin y C1, no montado).

---

## Prompt 9 — Segunda ronda de mediciones

**Fecha:** 2026-11-25

> Va mira, hagamos una ronda más exhaustiva de mediciones de continuidad. Dime qué debo medir

**Resultado:** La IA proyectó las posiciones de los pads de la PCB sobre la foto
"volteada" (ajuste afín) y marcó 28 puntos de medición con etiquetas
(`processed_images/14_puntos_de_medicion_ronda2.png` y `14b_..._zona_central.png`).
Además creó la plantilla `hardware/mediciones_continuidad.md`, que documenta la
ronda 1 e incluye tablas para la ronda 2: devanados de T1 en Ω, drenaje de Q1,
aislamiento entrada–salida, tierra del CI y sensado, D8/D7, pads sueltos e
identificación visual.

---

## Prompt 10 — Pad del drenaje despegado y C3

**Fecha:** 2026-11-25

> Espera creo que ya vi cual es el problema. Creo que el pad de la terminal central del transistor (Drain) está suelto. Por eso no medía continuidad. Sin embargo medi en uno de los pines de C3 y sí encontré continuidad con el pin conectado a D3 y D2

**Resultado:**

- El pin de C3 que estaba suelto (C3.1) se agregó a la red DC+ y se regeneraron las
  zonas, el esquemático y los nombres de red. Paridad: 0 problemas. ERC: 7 pines
  pendientes, uno menos que antes.
- La IA señaló que un pad de drenaje despegado o una soldadura fisurada en el MOSFET
  es una falla típica de los bombillos LED por ciclos térmicos, y que podría explicar
  por qué la lámpara dejó de funcionar.
- El drenaje de Q1 queda por confirmar. Si resulta conectado a DC+, encaja con un
  convertidor no aislado con el MOSFET del lado alto (la fuente va a T1 a través de
  R12).

---

## Prompt 11 — Esquemático con cables por etapas

**Fecha:** 2026-11-25

> Va mira antes de hacer eso. Quisiera que refinés el esquemático. Siento que no se entiende nada si conectas todo por etiquetas. Necesito que conectes los componentes con cables en el esquemático. Separa por etapas si quieres (filtro LC de entrada y rectificador, convertidor DC-DC)

Junto con el prompt adjunté dos imágenes de referencia: un diagrama de bloques de una
fuente flyback para LEDs y un esquemático simple de un puente rectificador con filtro.

**Resultado:**

- Corrección encontrada en el proceso: en la PCB estaban invertidas las redes de los
  pines de CE2 (el pad "+" del footprint quedaba en GND). Se corrigió.
- El esquemático se redibujó con cables reales, en tres etapas que fluyen de izquierda
  a derecha:
  - **A.** Entrada AC → R1/F1 → VR1, VR2, CX1, LF1 → puente D1–D4 dibujado en
    escalera → rieles DC+/DC− con C6 y VR3.
  - **B.** Arranque R4–R5, amortiguador (no montado), red de compuerta R7/D6/R8, Q1,
    R12, T1, devanado auxiliar D7/R6, RS1–RS4 y controlador U1 con su desacople, FB y
    filtro de CS.
  - **C.** CE3, CE4, R14, R15, D8 con su RC, y J1.
- Solo se usan etiquetas para unir etapas (DC±, LED±) y para las señales de U1.
- Las posiciones y cables están en `hardware/scripts/esquematico_layout.py`. El
  generador parte los cables en cada derivación en T (KiCad solo conecta por
  extremos) y agrega los puntos de unión.
- `verificar_esquematico.py` compara el netlist del esquemático con las redes de la
  PCB pin por pin: coinciden al 100%. Paridad esquemático–PCB: 0 problemas. ERC:
  solo los 7 pines sin conexión conocida.

---

## Prompt 12 — Esquemático preliminar del convertidor DC-DC

**Fecha:** 2026-11-25

> Claude ayudame a hacer un esquemático preliminar de la etapa del convertidor DC-DC

**Resultado:** La IA preguntó cómo tratar las conexiones aún no medidas (drenaje de Q1,
RS1–RS4, ánodo de D8, R11, C2). En lugar de responder, se pidió el mapa de colores
(prompt 13).

---

## Prompt 13 — Mapa de conexiones por color

**Fecha:** 2026-11-25

> Dame una imagen mostrando las conexiones con colores distintos.

**Resultado:** `hardware/scripts/colorear_redes.py` genera
`processed_images/15_mapa_de_redes_por_color.png`:

- La cara inferior se ve con el cuello abajo y cada isla de cobre va pintada con el
  color de su red (27 redes de 2 o más pads).
- Los pads de conexión desconocida aparecen en gris.
- Las líneas punteadas marcan las conexiones medidas que en la foto no se ven como
  cobre continuo.
- Una leyenda lista los pads de cada red.

---

## Prompt 14 — Esquemático del rectificador y del convertidor DC-DC (rev 0.4)

**Fecha:** 2026-11-25

> Revisa la carpeta pcb_tracing. Aquí puse las conexiones que encontré en la etapa del rectificador y una imagen donde coloreé una imagen de la bottom layer de la PCB en la parte del convertidor DC-DC. Intenta elaborar el esquemático de KiCad de ambos, tomando la imagen del rectificador que tomé como base. Quiero que utilices etiquetas únicamente cuando termine la etapa rectificadora y empiece la etapa del convertidor DC-DC
>
> Dado que no sabemos nada sobre el integrado debajo del MOSFET, intenta conectar los elementos del circuito como en un convertidor flyback (por el número de MOSFETs y devanados de transformador). Verifica que sea posible lograr un esquemático como los mostrados arriba. [...]

Durante el prompt se agregaron: la red de compuerta (R7 en paralelo con D6 para apagar
rápido), fotos de los componentes THT (`images/`), el trazado con símbolos de
componentes (`pcb_tracing/pcb_tracing_con_componentes.pdf/.svg`) y el dato de que T1
tiene un devanado entre el trazo blanco (LED+) y el amarillo claro (lado de RS1–RS4).

**Resultado:**

- Las coordenadas de cada trazo se leyeron directamente del SVG de Inkscape y se
  ubicaron sobre la foto con los puntos TA–TD, QS/QD/QG, etc.
- **Conclusión sobre la topología:** con las conexiones trazadas el circuito **no puede
  ser un flyback**: el drenaje de Q1 va directo a DC+, LED− está unido a DC−
  (no hay aislamiento) y T1 tiene un solo devanado de potencia (TC–TD, en serie con la
  carga) más uno auxiliar (TA–TB). Las conexiones corresponden a un **reductor (buck)
  no aislado con el MOSFET del lado alto y el controlador flotante**: la tierra de U1 es
  la fuente de Q1, RS1–RS4 (0.31 Ω) sensan la corriente del inductor, D8 es el diodo de
  rueda libre (ánodo en DC−) y el devanado auxiliar alimenta VDD (D7, R6) y da la
  realimentación FB (divisor R11 / R9). El CI sigue siendo compatible con un
  controlador PWM tipo flyback/PSR.
- Pinout de U1 por función: 1 VDD, 2 GND, 3 GATE, 4 FB, 5 COMP (R10 + C4 a GND),
  6 CS (por R12 = 0 Ω). No se encontró un modelo comercial confirmado con la marca
  H0TN: el símbolo `Lampara:IC_SOT-23-6` usa nombres de pin por función.
- Nuevo símbolo `Lampara:T1_EE_2dev` de dos unidades: T1A (devanado principal) y T1B
  (devanado auxiliar), para dibujar el auxiliar junto al controlador.
- Valores tomados de las fotos: Q1 FIR12N65F, C6 CBB 630 V 334J (330 nF), VR1 y VR3
  10D561K, CE2 10 µF 50 V, CE3/CE4 270 µF 100 V, D1–D4 S2M. Se quitaron todos los "?".
- Esquemático rev 0.4 (`esquematico_layout.py`): todo cableado; las únicas etiquetas
  son DC+ y DC− entre el rectificador y el convertidor. Quedan tres cruces de cables
  sin conexión, inevitables sin etiquetas (la rev 0.5 los elimina, ver prompt 15).
- Respaldo de la rev 0.3 en `KiCad_IngenieriaInversaLampara-backups/`.
- Diferencias con las redes de la PCB (`verificar_esquematico.py`): Q1.D en DC+;
  LED− = DC− (incluye T1 pin 2); la tierra del CI incluye la fuente de Q1, un lado de
  RS1–RS4, R9, C2, C4, D8 y R13; el otro lado de RS1–RS4 va a T1 pin 3 y R12; D7 y D8
  quedan con la polaridad funcional (ánodo de D7 en TA, ánodo de D8 en DC−), opuesta a
  la que se supuso en sus footprints. La PCB todavía no se actualizó.

**Pendiente de medir:** continuidad L− – DC− y QD – DC+ (después de resoldar Q1),
polaridad de D7 y D8, y que TB (T1 pin 2) esté en DC−.

---

## Prompt 15 — Estética del esquemático (rev 0.5) y subida a GitHub

**Fecha:** 2026-11-25

> Muy buen trabajo. La verdad tu argumento me parece muy convincente. Gracias por no ser tan complaciente con mi idea original. Por favor coloca estos avances en la bitácora de uso de IA y pushea en Github, indicando los avances.
>
> Lo que sí quisiera es que mejores un poco la estética del esquemático. Siento que tienes muy saturado el esquemático del convertidor buck boost. Por favor toma las siguientes consideraciones estéticas [...] También quisiera que en los pines de entrada y salida de voltaje no des vueltas. Me gustaría que el tamaño de la hoja sea más adecuado a la cantidad de componentes presentes. Quisiera que evites las conexiones cruzadas tanto como sea posible. [...] También quisiera que las etiquetas del integrado U1 no aparezcan tan pegadas entre sí. Haz el bloque más grande.

Junto con el prompt se adjuntaron una guía de buenas prácticas para esquemáticos de
fuentes (flujo izquierda-derecha y de mayor a menor tensión, bloques por etapa, símbolos
de alimentación y de tierra en vez de cables largos, tierras distintas con nombres
distintos, sin cruces) y dos esquemáticos de referencia.

**Resultado (rev 0.5):**

- Hoja A3 en lugar de A2.
- Rieles con símbolos de alimentación propios (`Lampara.kicad_sym`): `DC+`, `DC-`
  (triángulo lleno, = LED−) y `GND_SW` (triángulo hueco): la tierra flotante del
  controlador, que es la fuente de Q1. Además `VDD` (de la librería de KiCad) y
  banderas PWR_FLAG para el ERC. Ya no hacen falta etiquetas.
- **Cero cruces de cables.** La etapa de potencia va arriba
  (Q1 → nodo de conmutación → RS1–RS4 → T1A → LEDs) y el control de U1 abajo.
- P1 y J1 están espejados para que sus pines entren directo a las líneas, sin vueltas.
- U1 más grande (20 × 15 mm) con los pines a 5 mm: VDD y FB a la izquierda, GATE
  arriba (hacia Q1), CS a la derecha (hacia RS) y GND y COMP abajo.
- Textos sin encimarse: valores cortos para RS1–RS4 (1.2 / 1.3) y para C6
  (330nF 630V; la marca CBB 334J queda en la descripción), y posiciones fijas para
  los textos de U1, D8, J1, T1B, R4 y R5.
- Las redes son idénticas a las de la rev 0.4 (comparado con el netlist). ERC: solo
  los 4 pines de R2, CE1 y C1, que no están montados y cuya conexión no se conoce.
- Imagen: `processed_images/16_esquematico_rev0.5.png` / `.pdf`.

---

<!-- Para nuevas entradas copiar el formato:
## Prompt N — Título
**Fecha:** AAAA-MM-DD
> prompt tal cual
**Resultado:** ...
-->
