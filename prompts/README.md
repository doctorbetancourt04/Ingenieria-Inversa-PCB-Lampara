# Uso de IA en este proyecto

En esta carpeta registro cómo usé inteligencia artificial durante la ingeniería
inversa de la PCB del bombillo LED Tecnolite 50LHBLEDT65MV200 (placa JT047-V1).
La idea es ser transparente: qué le pedí a la IA, con qué herramienta y qué
produjo, para separar claramente mi trabajo del trabajo asistido.

## Herramientas

| Elemento | Detalle |
|---|---|
| Modelo de IA | Claude Opus 5.5 (`claude-opus-5-5`), de Anthropic |
| Herramienta | Claude Code (pestaña Code de la app de escritorio de Claude, Windows) |
| Software EDA | KiCad 8.0.5 |

## Contenido

- [`bitacora_prompts.md`](bitacora_prompts.md): bitácora cronológica con los prompts
  tal como los escribí y un resumen de lo que hizo la IA en cada uno.

## Qué se hizo con IA y qué falta revisar a mano

La IA generó:

- El archivo `hardware/LICENSE` (CC BY-SA 4.0, texto proporcionado por mí).
- El esquemático `KiCad_IngenieriaInversaLampara.kicad_sch`: los 50 componentes
  identificados en las fotos, agrupados por bloque funcional, con su footprint y con
  etiquetas de red en cada pin. Las conexiones salen del cobre segmentado de las fotos
  (`processed_images/`) y de mis mediciones de continuidad.
- La capa B.Cu de la PCB como zonas de cobre con sus redes, sincronizada con el
  esquemático.
- La PCB `KiCad_IngenieriaInversaLampara.kicad_pcb`: contorno con las medidas tomadas
  de las fotos con regla (43.6 × 114.1 mm aprox.) y los footprints colocados en su
  posición aproximada (THT en la cara superior, SMD en la inferior). Las redes se
  sincronizaron con el esquemático desde KiCad (*Actualizar placa desde esquema*).
- Footprints propios en `Lampara.pretty` (entrada AC, choque de modo común,
  transformador de 4 pines y VR2 con su serigrafía ovalada original) y el símbolo
  genérico del CI en `Lampara.kicad_sym`.
- Los scripts en `hardware/scripts/` que generan todo lo anterior, para poder
  reproducirlo o ajustarlo (editando `componentes.py`).

Pendiente de verificación manual:

- Las posiciones salen de fotografías, así que tienen un error de ±1 mm aprox.
  Conviene confirmar las medidas con vernier.
- Los valores marcados con `?` no se leyeron en las fotos.
- La polaridad de diodos y electrolíticos y el pinout de T1 y U1 son supuestos.
- Las conexiones del esquemático y el ruteo de pistas se hacen a mano.
