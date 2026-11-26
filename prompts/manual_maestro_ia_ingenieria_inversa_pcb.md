# Manual maestro para IAs: ingeniería inversa de PCBs de una o dos capas

Instrucciones para una IA (con acceso a archivos, terminal y KiCad) que ayuda a una
persona a reconstruir el esquemático y la PCB de una placa de una o dos capas a partir
de fotos y mediciones. Sale de lo aprendido en este proyecto (driver de bombillo LED
Tecnolite, PCB JT047-V1): ver `bitacora_prompts.md` para el historial completo.

La idea central: **la persona tiene la placa y el multímetro; la IA tiene tiempo para
procesar imágenes, generar archivos y razonar sobre el circuito.** El proceso es más
rápido cuando cada uno hace lo que le toca y la IA pide datos concretos en lugar de
adivinar.

---

## 0. Reglas de oro

1. **No adivines conexiones: pide una medición.** Una conexión dudosa cuesta 10
   segundos de multímetro y, si se adivina mal, horas de rehacer. Agrupa las dudas en
   rondas de medición con puntos etiquetados sobre una foto.
2. **El trazado a mano de la persona vale más que la segmentación automática.** La
   segmentación de cobre por color (umbral, Otsu, watershed) ayuda a ubicar islas, pero
   falla con sombras, serigrafía, soldadura y pistas bajo componentes. En este proyecto
   un trazado con colores en Inkscape resolvió en minutos lo que la segmentación no
   resolvió en horas.
3. **No fuerces una topología.** Si la persona dice "conéctalo como un flyback", verifica
   con las conexiones si de verdad lo es (ver la sección 5). Aquí resultó ser un reductor
   no aislado con MOSFET de lado alto: decirlo con argumentos fue más útil que complacer.
4. **Verifica cada esquemático con el netlist** (`kicad-cli sch export netlist`) contra
   la lista de redes esperada, y corre el ERC. No entregues sin esa comprobación.
5. **Seguridad:** las fuentes conectadas a la red son peligrosas. Antes de medir, la
   placa va desconectada y los capacitores de alto voltaje descargados (resistencia de
   ~1 kΩ). Si el convertidor no está aislado, todo el circuito (incluidos los LEDs)
   está al potencial de la red: para medir encendido hace falta un transformador de
   aislamiento o una punta diferencial.
6. **Valores sin "?"**: usa "DNP" para no montados y descripciones neutras ("Diodo
   rápido", "MLCC") cuando no se puede leer el valor.

---

## 1. Lo que hay que pedirle a la persona desde el inicio

Pídelo todo en el primer mensaje; ahorra muchas idas y vueltas.

| Qué | Para qué | Cómo |
|---|---|---|
| Foto de cada cara, **perpendicular, con luz difusa y una regla** | Escala y alineación | Sin flash directo; la placa llenando el cuadro; regla en el mismo plano |
| Foto de la cara inferior **a contraluz** (linterna detrás) | En placas de una capa las pistas se ven solas | Linterna o pantalla blanca detrás |
| Acercamientos de cada CI, transistor, diodo y capacitor grande | Marcas y valores | Varias fotos con distinto ángulo de luz; un video corto sirve para CIs pequeños |
| Medidas con vernier de los encapsulados SMD | Elegir footprints | 1206 / 0805 / SOD-123 / SMA / SOT-23-6 |
| **Trazado de pistas a mano** sobre la foto (Inkscape, un color por red) | Conexiones | Guardar como SVG: la IA lee las coordenadas exactas de cada trazo |
| Mismo trazado **con los símbolos de los componentes dibujados encima** | Saber qué pad es de qué pieza | Capa aparte en Inkscape |
| Dibujo a mano de las etapas que ya entiende | Base del esquemático | Foto del cuaderno |
| Esquemáticos de referencia del tipo de circuito | Estilo y topología | Imágenes de internet |
| Modelo del aparato y datos de la etiqueta (V, W, Hz) | Valores esperados | Foto de la carcasa |

---

## 2. Flujo de trabajo recomendado (de más rápido a más lento)

### Fase A. Inventario (30 min)
1. Lista de componentes con referencia de serigrafía, lado (THT/SMD), valor leído y
   encapsulado → un solo archivo de datos (aquí `hardware/scripts/componentes.py`).
2. Identifica las etapas: entrada AC/fusibles/varistores → filtro EMI → puente →
   bus DC → conversión → salida. Marca los componentes no montados (pads vacíos).

### Fase B. Conexiones (lo más importante)
1. **Primero el trazado a mano de la persona.** Del SVG de Inkscape extrae la imagen
   embebida (`<image>` en base64) y los `<path>` con su color de trazo; convierte las
   coordenadas del SVG a pixeles con `x`, `y`, `width`, `height` de la imagen. Dibuja los
   trazos sobre la foto y haz acercamientos para ver a qué pad llega cada uno.
2. Ubica los pads con etiquetas (TA, TB, QD, QS...) sobre la foto para referirte a ellos
   sin ambigüedad.
3. Traduce cada trazo a "red = lista de pads". Usa la **regla física**: un componente
   montado no puede tener dos pines en la misma red (salvo puentes de 0 Ω).
4. Arma una **ronda de medición** con lo que falte: tabla de "entre A y B, ¿sí o no?" y
   una imagen con los puntos marcados. En modo continuidad, una resistencia de menos de
   ~0.5 Ω (resistores de sensado, puentes) también pita: interpreta con cuidado.
5. Solo si no hay trazado manual: segmentación automática (ver la sección 7).

### Fase C. Topología (razonar antes de dibujar)
Responde con las conexiones, no con la suposición inicial:
- ¿Hay aislamiento? Mide L− (salida) contra DC− (bus). Si hay continuidad, **no es
  aislado** (no es un flyback "de libro").
- ¿A dónde va el drenaje del MOSFET? A DC+ → interruptor del lado alto (buck o
  buck-boost flotante). Al transformador → flyback o boost con interruptor del lado bajo.
- ¿Cuántos devanados de potencia tiene el transformador? Uno en serie con la carga + uno
  pequeño que alimenta el CI → inductor con devanado auxiliar (no es transformador de
  flyback).
- ¿Dónde está la tierra del CI? Si es la fuente del MOSFET, el controlador **flota** con
  el nodo de conmutación.
- Resistores de < 1 Ω en paralelo en el camino de la corriente → sensado de corriente.
- Diodo en paralelo con la resistencia de compuerta (cátodo hacia el CI) → apagado rápido.
- Divisor desde el devanado auxiliar hacia un pin del CI → realimentación (FB) / detección
  de desmagnetización.

### Fase D. Esquemático en KiCad
Genera el archivo `.kicad_sch` con un script (sección 6) y verifica con `kicad-cli`.

### Fase E. PCB
Coloca footprints con las coordenadas medidas en las fotos, crea zonas de cobre desde las
islas o traza pistas, actualiza la PCB desde el esquemático y corre el DRC.

---

## 3. Errores que costaron tiempo en este proyecto (evítalos)

| Error | Consecuencia | Cómo evitarlo |
|---|---|---|
| Numerar los pines del CI desde la esquina equivocada | Pinout desplazado 3 pines | Confirmar el punto del pin 1 con una foto inclinada **y** con la cara que se está viendo (en la cara inferior la placa se ve espejada) |
| Pad del MOSFET con soldadura fisurada | "No hay continuidad" donde sí hay pista | Si una medición contradice la foto, revisar la soldadura (falla típica de bombillos LED) |
| Segmentar el cobre con una foto con sombras | Todo quedó en una sola isla | Usar la foto con luz más pareja; índice de verdor (G−R)/G; o pedir el trazado a mano |
| Pintar los pads como cobre en la máscara | Un pad mal alineado unió dos redes | No pintar pads; asignar cada pad a la isla más cercana |
| Suponer la polaridad de diodos por el footprint | D7 y D8 quedaron al revés de lo funcional | Pedir que digan de qué lado está la franja |
| Aceptar "es un flyback" sin verificar | Esquemático imposible | Sección 2, fase C |
| KiCad abierto mientras se regenera el archivo | La persona veía la versión vieja | Avisar que cierre el esquemático sin guardar y lo reabra |
| Valores con códigos de marca y "No montado" | Textos largos que se enciman | Valores cortos estándar (330k, DNP); el código de marca va en la descripción |

---

## 4. Estética del esquemático (lo que pidió la persona y funcionó)

- Flujo de izquierda a derecha y de mayor a menor tensión; la potencia arriba y el
  control abajo.
- Un solo circuito en la hoja: el riel DC+ es un cable continuo del puente al
  interruptor. Etiquetas solo para **nombrar** redes clave (DC+, LED+), no para conectar
  partes lejanas.
- Tierras estándar: `power:GND` para la tierra principal; las tierras distintas usan el
  mismo símbolo con otro nombre (aquí `GND_U1`, la tierra flotante del controlador).
  `PWR_FLAG` en cada red de alimentación para que el ERC no marque errores.
- Cero cruces de cables. Si un cruce parece inevitable, revisa la orientación de los
  símbolos, espeja conectores (`mirror`) o divide un transformador en unidades
  (devanado principal y auxiliar).
- Conectores de entrada y salida espejados para que sus pines queden en el orden de las
  líneas (sin vueltas).
- Bloques punteados por etapa con título; título grande arriba a la izquierda; notas
  numeradas abajo a la izquierda; cajetín completo (título, fecha, revisión, autor,
  descripción).
- Hoja del tamaño justo (A3 para ~50 componentes) y circuito centrado.
- Revisa el dibujo renderizado (sección 6) y corrige cada texto encimado antes de
  entregar.

---

## 5. Pistas rápidas por tipo de circuito (fuentes conectadas a la red)

| Si ves... | Probablemente es... |
|---|---|
| Puente + capacitor de película pequeño (CBB 0.33 µF) en lugar de un electrolítico grande | Driver LED sin almacenamiento en el bus (alto factor de potencia) |
| MOSFET con el drenaje a DC+ y el CI referido a la fuente | Buck de lado alto con controlador flotante |
| Diodo rápido entre la salida negativa y la fuente del MOSFET | Diodo de rueda libre del buck |
| Transformador con 4 pines, uno de ellos a un diodo SMD pequeño y a un resistor de 10–47 Ω hacia el VDD del CI | Devanado auxiliar de alimentación |
| Dos resistores de 100–470 kΩ en serie desde DC+ al VDD del CI | Arranque |
| Optoacoplador + TL431 | Flyback aislado con realimentación del secundario |
| Sin optoacoplador, divisor desde el auxiliar al FB | Regulación del lado primario (PSR) |

Controladores PWM en SOT-23-6 con marcas cortas (como H0TN) casi nunca aparecen en
internet: nombra los pines por función (VDD, GND, GATE, FB, COMP, CS) según sus
conexiones y dilo en la descripción del símbolo.

---

## 6. Recetas técnicas (KiCad 8 por línea de comandos)

- **No hace falta la GUI.** Genera el `.kicad_sch` como texto (expresiones S) desde un
  script con: lista de componentes, posiciones, cables, símbolos de alimentación y
  textos. Toma los símbolos de las librerías de KiCad e incrústalos en `lib_symbols`.
- Coordenadas en múltiplos de **1.27 mm**. Los cables solo se conectan por sus
  extremos: parte cada tramo donde llegue otro cable o un pin (derivación en T) y pon
  un `junction` donde se toquen 3 o más extremos.
- Posición de un pin en la hoja: rota (x, y) del símbolo según el ángulo, invierte la Y
  (la hoja crece hacia abajo) y aplica el espejado (`mirror x` voltea arriba-abajo,
  `mirror y` izquierda-derecha).
- Los campos (`Reference`, `Value`) de un símbolo rotado 90/270 necesitan ángulo 90
  para verse horizontales.
- Símbolos de varias unidades (transformador con dos devanados): una instancia por
  unidad con `(unit n)`, cada una solo con sus pines.
- Comandos útiles:
  - `kicad-cli sch export netlist -o netlist.net archivo.kicad_sch`
  - `kicad-cli sch erc -o erc.rpt archivo.kicad_sch`
  - `kicad-cli sch export pdf|svg ...` y luego Inkscape para PNG:
    `inkscape archivo.svg --export-type=png --export-dpi=200 --export-background=white`
  - `kicad-cli sym export svg` para revisar símbolos propios.
- Compara el netlist con la lista de redes esperada **pin por pin**
  (`hardware/scripts/verificar_esquematico.py`). Si solo cambias la estética, las redes
  deben quedar idénticas.
- Para leer SVG de Inkscape: imagen en `<image xlink:href="data:image/jpeg;base64,...">`
  con atributos `x y width height`; trazos en `<path d="m ... l ... h ... v ...">`
  (comandos relativos en minúscula) con `stroke:#rrggbb` en `style`.

---

## 7. Segmentación automática del cobre (solo si no hay trazado manual)

1. 20–40 puntos de control (centros de SMD y pads THT con posición conocida) → ajuste
   afín o thin-plate spline a coordenadas de la PCB (20 px/mm).
2. Índice de verdor (G−R)/G → umbral de Otsu → apertura/cierre de 0.25 mm.
3. Borra los cuerpos de los SMD (entre sus pads) para no unir redes.
4. Erosión + watershed para separar islas unidas por puentes finos; regla física de
   "dos pines de un componente montado no pueden estar en la misma isla".
5. Revisa siempre superponiendo las islas a la foto, y confirma las zonas dudosas
   midiendo.

---

## 8. Plantillas de mensajes para la persona

- **Ronda de medición:** "Con la placa desconectada y los capacitores descargados, mide
  continuidad entre estos pares (puntos marcados en la imagen X). Anota sí/no, o los Ω
  si pita dudoso: ..."
- **Polaridad:** "¿De qué lado está la franja de D7: hacia 7a (pestañas) o hacia 7b
  (cuello)?"
- **Antes de abrir KiCad:** "Cierra el esquemático sin guardar y vuelve a abrirlo; el
  archivo en disco ya está actualizado."

---

## 9. Qué puede hacer la persona más rápido que la IA (repártanse el trabajo)

| Tarea | Quién | Por qué |
|---|---|---|
| Trazar pistas sobre la foto | Persona | Ve la placa real, gira la luz y la lupa; la IA solo tiene pixeles |
| Medir continuidad y polaridad | Persona | 10 s por medición contra horas de inferencia |
| Leer marcas pequeñas de CIs y diodos | Persona (con lupa) | Las fotos suelen salir borrosas |
| Mover un par de textos o un símbolo en el esquemático | Persona en KiCad | Un arrastre contra una vuelta de generar y renderizar |
| Decidir el estilo del dibujo | Persona, desde el inicio | Evita rehacer la estética varias veces |
| Ordenar datos, generar archivos completos, verificar netlists, razonar la topología, documentar | IA | Es repetitivo y sistemático |
