# Imágenes procesadas

Imágenes intermedias que se generaron (con ayuda de IA, ver `prompts/`) para
reconstruir en KiCad la PCB JT047-V1 del bombillo Tecnolite 50LHBLEDT65MV200.
Todas salen de las fotos originales de `images/`. Las del cobre las genera
`hardware/scripts/cobre_segmentar.py`, así que se pueden reproducir.

Convenciones:
- "Vista superior" = vista desde el lado de los componentes THT, como en KiCad.
  Para que la cara inferior quede en esa orientación se espeja la foto (vista "de rayos X").
- Las coordenadas en mm son las de `hardware/scripts/componentes.py`: X = 0 en el
  eje central, Y = 0 en el borde superior del cuello.

## 1. Colocación de componentes (`colocacion_componentes/`)

| Archivo | Qué muestra |
|---|---|
| `cuadricula_mm_cara_superior_*.png` | Foto `Top Layer.jpeg` con cuadrícula en mm (rojo = X, azul = Y), por secciones. Sirvió para medir la posición de los componentes THT y el contorno. |
| `cuadricula_mm_cara_inferior_espejada_*.png` | Foto `Bottom Layer.jpeg` espejada para que coincida con la vista superior, con la misma cuadrícula. Sirvió para ubicar los pads y los SMD. |
| `acercamiento_x4_etiquetas_*.png` | Recortes ampliados ×4 de la cara inferior para leer las etiquetas de serigrafía (R2, R3, D5, D6, U1, RS1–RS4, etc.). |
| `acercamiento_serigrafia_VR2.png` | Ampliación del óvalo de VR2, usado para dibujar su serigrafía. |
| `primera_version_pcb_superior_e_inferior.png` | Primera versión de la PCB generada (capas superior e inferior) para compararla con las fotos. |

## 2. Reconstrucción del cobre: intento 1 (descartado)

Se usó `Bottom Layer (Volteada verticalmente).jpeg`. Se descartó porque la
iluminación no es uniforme: el cobre en sombra y el laminado verde tienen
colores parecidos y todo terminaba en una sola isla.

| Archivo | Qué muestra |
|---|---|
| `intento1_01_foto_inferior_puntos_de_control.png` | Puntos de control (círculos rojos) marcados sobre la foto: centros de SMD y pads cuya posición en la PCB se conoce. |
| `intento1_02_foto_inferior_alineada_vista_superior.png` | Foto deformada con thin-plate spline para que coincida con las coordenadas de la PCB (20 px/mm). |
| `intento1_03_clasificacion_por_color.png` | Clasificación HSV: naranja = cobre, verde = sin cobre, morado = muy oscuro, gris = pads/serigrafía. La zona de los diodos se clasifica mal. |
| `intento1_04_mascara_cobre_cruda.png` | Máscara binaria de cobre (blanco) obtenida de la clasificación HSV. |
| `intento1_05_mascara_cobre_limpia_con_pads.png` | Máscara después de apertura y cierre morfológicos y de pintar los pads. |
| `intento1_06_islas_de_cobre_numeradas.png` | Componentes conexos: casi todo quedó en una sola isla (azul), señal de que la segmentación falló. |
| `intento1_07_islas_superpuestas_a_la_foto.png` | Islas superpuestas a la foto alineada. |
| `intento1_08_indice_verdor.png` | Primer cálculo del índice de verdor (G−R)/G: claro = laminado sin cobre, oscuro = cobre. |
| `intento1_09_umbral_otsu_133.png`, `intento1_10_umbral_fijo_110.png` | Umbrales del índice. Ninguno separa bien por el gradiente de iluminación. |
| `intento1_11..13_cuadricula_pixeles_*.png` | Cuadrícula en pixeles sobre la foto, usada para leer las coordenadas de los puntos de control. |

## 3. Reconstrucción del cobre: intento 2 (vigente)

Se usó `Bottom Layer.jpeg`, que tiene una iluminación más pareja.

| Archivo | Qué muestra |
|---|---|
| `comparacion_foto_bottom_layer_e_indice_verdor.png` | Izquierda: foto alineada. Derecha: índice de verdor. El cobre (negro) y el laminado (blanco) se separan con claridad; por eso se eligió esta foto. |
| `01_foto_inferior_puntos_de_control.png` | 43 puntos de control: centros de 31 SMD y 12 pads THT (T1, LF1, CE3, CE4). Error del ajuste afín: 0.09 mm promedio, 0.38 mm máximo. |
| `02_foto_inferior_alineada_vista_superior.png` | Foto deformada (thin-plate spline) a coordenadas de la PCB, 20 px/mm. |
| `03_indice_verdor_gris.png` | Índice de verdor (G−R)/G en escala de grises. |
| `04_mascara_cobre_cruda_otsu.png` | Cobre (blanco) con umbral automático de Otsu sobre el índice, dentro del contorno de la placa. |
| `05_mascara_cobre_limpia_y_pads.png` | Máscara tras: (a) apertura/cierre de 0.25 mm para quitar serigrafía, y (b) borrar el cuerpo de cada SMD (entre sus pads). Rectángulos rojos = área de cada pad de la PCB. |
| `descartada_05_mascara_con_pads_pintados_unia_redes.png` | Versión descartada: los pads se pintaban como cobre, y con ±0.4 mm de error un pad (J1) cayó sobre la separación entre dos pistas y las unió. |
| `05b_nucleos_erosionados.png` | Máscara erosionada 0.25 mm. Los puentes falsos más finos desaparecen, y cada núcleo se vuelve a expandir con watershed. |
| `05c_islas_tras_regla_de_cortos.png` | Islas (tonos de gris) después de aplicar la regla física: un componente montado no puede tener dos pines en la misma isla. Donde pasaba, esa isla se erosionó más (0.35–1.0 mm) hasta separar los pines. |
| `06_islas_de_cobre_numeradas.png` | Islas finales, cada una con un color y su número (ver la lista de pads en `hardware/scripts/cobre_islas.json`). Puntos negros = pads asignados a una isla; puntos rojos = pads sin isla. |
| `07_islas_superpuestas_a_la_foto.png` | Islas finales superpuestas a la foto alineada, para revisar visualmente. |
| `diagnostico_puente_rectificador_*.png` | Acercamiento con cuadrícula en mm a la zona de D1–D4 (foto e islas). Era la zona más dudosa y se confirmó con mediciones de continuidad. |
| `08_cobre_reconstruido_en_kicad_vs_foto_inferior.png` | Izquierda: foto original de la cara inferior. Derecha: capa B.Cu reconstruida en KiCad (zonas rellenas, vista desde abajo). |
| `09_capa_B_Cu_reconstruida_vista_inferior.png` | Solo la capa B.Cu reconstruida con su serigrafía, vista desde abajo. |
| `10_reporte_redes_reconstruidas.txt` | Lista de redes resultante (islas de cobre + mediciones con multímetro) y contradicciones detectadas. |
| `12_marca_U1_cuadros_video_ampliados.png`, `13_marca_U1_cuadros_video_ampliados_2.png` | Cuadros del video de U1 (ampliados ×6 y con nitidez realzada; los números rojos indican el cuadro del video). Se lee "H0?N / •9L9?" y el punto de pin 1 abajo a la izquierda, con el cuello hacia abajo. |
| `14_puntos_de_medicion_ronda2.png`, `14b_..._zona_central.png` | Foto "volteada" (cuello abajo) con los puntos de la segunda ronda de mediciones marcados con etiquetas (TA–TD, QG/QD/QS, DC±, L±, GND, VCC, RA/RB, etc.). Las posiciones se proyectaron desde la PCB con un ajuste afín. Ver `hardware/mediciones_continuidad.md`. |
| `11_esquematico_reconstruido_con_redes.png` | Esquemático final exportado de KiCad: cada pin lleva una etiqueta con la red de la PCB. Los pines sin etiqueta son conexiones que no se pudieron determinar. |

## 4. Cómo se obtuvieron las redes

1. Cada isla de cobre une los pads que contiene (`cobre_islas.json`).
2. Se agregaron las conexiones medidas con multímetro: puente rectificador, pines de
   U1, RS1–RS4 en paralelo y CE3 ∥ CE4 (ver `prompts/bitacora_prompts.md`).
3. Las islas alrededor de U1 y CE2 no unen sus pads automáticamente, porque la foto
   mezcla ahí varias redes.
4. Cada isla se convirtió en una zona de cobre en B.Cu (`cobre_crear_zonas.py`) con
   la red mayoritaria de sus pads, inflada 0.15 mm y con prioridades distintas para
   respetar 0.25 mm de separación entre redes distintas.

## Limitaciones

- Error de posición de ±0.4 mm por la alineación foto–PCB.
- La foto no distingue el cobre que queda bajo la soldadura ni bajo los cuerpos de los componentes.
- Las conexiones dudosas se confirman midiendo continuidad en la placa real.
