# Pendientes

> **Qué es.** La lista de todo lo que está abierto en el espacio de trabajo, en un solo sitio,
> con dónde vive cada cosa. No es un registro: cada fila apunta a la entrada que **sí** es el
> registro (un `HALLAZGOS`, una ficha, una brecha de `AGENTIC.md`), y lo que dice esa entrada
> manda sobre lo que diga esta fila.
>
> **No guarda historia.** Cuando algo se cierra, se hacen dos cosas en el mismo commit:
> 1. se cambia el **origen** (su línea de estado y su fila de resumen), diciendo cómo se cerró
>    y con qué se verificó;
> 2. se **borra** su fila de aquí.
>
> Nada se tacha ni se marca como cerrado en este documento. Si se cierra solo en parte, el origen
> dice qué queda, y la fila de aquí se reescribe para nombrar únicamente ese resto.
>
> **Para añadir algo** hay que registrarlo antes en su origen. Una fila sin origen no es un
> pendiente, es una nota.
>
> **Comprobado el 2026-10-21.** Cada fila se volvió a ejecutar ese día con el binario de release
> de `interpreter` en `c3468c1` (rama `v0.0.11`), salvo donde la columna dice otra cosa. El
> mismo día se cerraron en su origen once entradas que seguían diciendo «abierta» y no lo
> estaban: DM-28, DM-29, ZethyCLI G1–G3, GO IDEA-001, Zofía GAP-Z005 e IDEA-Z002, BUG-BEN-001,
> IDEA-BEN-002 e IDEA-GOL-007; y a GAP-GOL-009 se le anotó el resto que dejó (DIS-ZYE-005).
>
> **Qué no está aquí.** El plan de la v0.0.11 (`interpreter/ROADMAP_V0011_ES.md`: la 3.3
> aplazada, la etapa 4 en pausa), que son trabajos y no hallazgos. Tampoco las exclusiones de
> entorno de `zyquality/corpus.toml`, que son decisiones tomadas con su razón.
>
> **Rutas.** Relativas a la raíz del espacio de trabajo (`zymbol-lang/`), porque los orígenes
> están en repositorios distintos.

---

## 1. Del lenguaje: decidido, sin corregir

| ID | Qué | Motores | Origen | Comprobado |
|---|---|---|---|---|
| GLB-139 | `s[i]` y un corte buscan su posición recorriendo el texto: cuadrático en un bucle | `zytw`, `zyjs` (la VM, corregida) | `ZyDDT/HALLAZGOS/GLOBAL.md` § GLB-139 | 2026-10-20: `cost` `growth/index-a-text` en KNOWN. Deuda declarada de la v0.0.11 por decisión del autor |
| ZYTW-016 | El tree-walker copia un texto cada vez que lo lee | `zytw` | `ZyDDT/HALLAZGOS/zytw.md` § ZYTW-016 | 2026-10-20: `cost` `growth/read-a-text` y `growth/slice-a-text` en KNOWN. Deuda declarada de la v0.0.11 |

## 2. Decisiones de diseño sin tomar

Son del autor: implementar, aplazar con una razón, o rechazar con una razón.

| ID | Qué | Origen | Comprobado |
|---|---|---|---|
| G1 | Sin control de capacidades: `std/net`, `std/io`, `std/db` y `<\ \>` no tienen restricción, y `zyp.toml` no declara efectos | `interpreter/AGENTIC.md` § gaps, G1 | 2026-10-21: `zymbol run --help` no tiene ninguna opción de denegar |
| G2 | Inyección en `<\ "{v}" \>`: se interpola sin escapar | `interpreter/AGENTIC.md` § gaps, G2 | 2026-10-21: con `v = "x; echo INYECTADO"` se ejecutan las dos órdenes |
| G3 | Sin límite de terminación en los motores Rust: un bucle infinito o una recursión de cola corren hasta un timeout externo | `interpreter/AGENTIC.md` § gaps, G3 | 2026-10-21: `zymbol run --help` no tiene ninguna opción de límite |
| G4 | Usar una variable destruida (`\ x`) solo se detecta al ejecutar | `interpreter/AGENTIC.md` § gaps, G4 | 2026-10-21: `check` no da ningún error; `run` falla con `use after destruction` |
| G5 | Un `??` que no cubre todos los casos solo se detecta al ejecutar | `interpreter/AGENTIC.md` § gaps, G5 | 2026-10-21: `check` no da ningún error; `run` falla con `no pattern matched` |
| G8 | `std/random` no deja fijar la semilla: no hay ejecución reproducible | `interpreter/AGENTIC.md` § gaps, G8 | 2026-10-21: `std/random` exporta `entero`, `rango` y `peso_f64`, ninguna semilla |
| DIS-ZYE-001 | Inicio, Fin, RePág, AvPág, Supr, F1–F12 y Shift+Tab llegan todas como `0d0`, que es el «no hay tecla» de `<<\|?`. `--keys` tampoco las nombra | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-001 | `ZyEdit/hypotheses/keys/` — HOLDS, 2026-10-20 |
| DIS-ZYE-002 | Shift y Ctrl sobre una flecha se pierden: Shift+→ llega como → | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-002 | `ZyEdit/hypotheses/keys/` — HOLDS, 2026-10-20 |
| DIS-ZYE-003 | Ctrl+/, Ctrl+Espacio y Alt+letra llegan como un carácter imprimible (`7`, espacio, la letra) | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-003 | `ZyEdit/hypotheses/keys/` — HOLDS, 2026-10-20 |
| DIS-ZYE-004 | Dentro de `>>\|` el cursor del terminal está oculto y nada lo muestra ni lo coloca | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-004 | `ZyEdit/hypotheses/cursor/` — HOLDS, 2026-10-20 |
| DIS-ZYE-005 | Ningún programa Zymbol puede arrancar otro en un terminal, escribirle y leer lo que dibuja. Es el resto de GAP-GOL-009, y bloquea las etapas 4 y 5 de ZyEdit | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-005 | las dos comprobaciones de `ZyEdit/hypotheses/` tuvieron que escribirse en Python |
| ZethyCLI G1 (resto) | `std/net` no tiene control de timeout desde Zymbol | `ZethyCLI/GAPS.md` § G1 y su fila | 2026-10-21: `GUIDE.md` § `std/net` solo admite cabeceras opcionales |
| Serpiente IDEA-001 | Un módulo `std/ansi` con nombres para los colores de `>>~`, en vez de números sueltos | `serpiente/HALLAZGOS_ES.md` § IDEA-001 | «propuesto», sin decisión |
| Zofía IDEA-Z004 | Lectura con tipo y longitud en el propio operador: `<< :###2 "…"` | `Zofia/HALLAZGOS.md` § IDEA-Z004 | «propuesto», sin decisión |

## 3. Verificaciones pendientes

Corregidas en su origen, a falta de una medición que la puerta no puede hacer.

| ID | Qué falta | Origen |
|---|---|---|
| PERF-08 / GLB-134 | Repetir la medición del binario estático con musl **en la release**: la puerta no construye el estático | `zyquality/bench/big/HALLAZGOS.md`, tabla «Estado en la rama `v0.0.11`», fila PERF-08 |

## 4. Documentación

| ID | Qué | Origen | Comprobado |
|---|---|---|---|
| ERROR-BEN-004 | `MANUAL.md` sigue diciendo que la VM es «~1.1–1.5× más rápida que Python en la mayoría de las cargas», y no se sostiene fuera de los bucles de enteros. El documento está marcado como instantánea obsoleta de la v0.0.4, pero la frase sigue ahí | `zyquality/bench/python/HALLAZGOS.md` § ERROR-BEN-004 | 2026-10-21: `interpreter/MANUAL.md:121` |

## 5. Restos en las aplicaciones

El lenguaje ya lo permite; la aplicación todavía no se ha migrado.

| ID | Qué | Origen |
|---|---|---|
| ZethyCLI G4 (resto) | `lib/config.zy` sigue leyendo su configuración con `jq` a través de `<\ \>` | `ZethyCLI/GAPS.md` § G4 y su fila |
