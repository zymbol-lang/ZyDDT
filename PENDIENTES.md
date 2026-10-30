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
> **Comprobado el 2026-10-30.** Cada fila se volvió a ejecutar ese día con el binario de release
> de `interpreter` en `5a95444` (rama `v0.0.11`, `--features db`) y, para el navegador, con
> `web` en `22997b7`: **zyjs** es `zymbol.js`, el tree-walker del playground, y **zymbol_vm.js**
> su VM, el motor por defecto desde la v0.0.11. Los de ZyEdit, con sus propios
> `hypotheses/*/check.*`. Se barrieron los registros de todas las aplicaciones, los de ZyDDT
> (`zyddt findings`: ninguna ficha abierta), `AGENTIC.md` (ninguna brecha abierta),
> `zyquality/bench/` y las deudas `open_finding` de la puerta (ninguna).
>
> El mismo día se cerraron en su origen: BUG-VMJS-002, -003, -004, -005 y -006
> (`web/zymbol_vm/HALLAZGOS.md`), BUG-ZYE-013 (su propia prueba en ZyEdit pedía cerrarlo) y
> klingon HLZ-001, rechazado por la premisa MEM-2. Entraron las fichas abiertas de ZyTetris
> (2026-10-27/28), las de ZyEdit posteriores al 2026-10-21 y las dos de zymbol_vm.js que quedan.
>
> **Qué no está aquí.** El plan de la v0.0.11 (`interpreter/ROADMAP_V0011_ES.md`: la 3.3
> aplazada, la etapa 4 en pausa), que son trabajos y no hallazgos. Tampoco las exclusiones de
> entorno de `zyquality/corpus.toml`, que son decisiones tomadas con su razón.
>
> **Rutas.** Relativas a la raíz del espacio de trabajo (`zymbol-lang/`), porque los orígenes
> están en repositorios distintos.

---

## 1. Del lenguaje: decidido, sin corregir

Actualizado el 2026-10-30. Lo que el lenguaje ya dice y algún motor todavía no hace, o una
decisión del autor que espera su implementación.

| ID | Qué | Origen | Comprobado |
|---|---|---|---|
| BUG-TET-009 | `#\|texto\|` con un entero fuera de ±(2^53−1): zyjs da un Int, y lo redondea sin avisar; el resto devuelve el texto intacto. El otro camino de zyjs para lo mismo (`<< #\|v\|`) ya comprueba el rango | `ZyTetris/HALLAZGOS.md` § BUG-TET-009 | `#\|"9007199254740993"\|`: zyjs `9007199254740992 ###`; zytw, zyvm y zymbol_vm.js `9007199254740993 ##"` |
| BUG-VMJS-001 | `#^.N` en zyjs redondea los empates hacia arriba y escribe un `.0` que los motores Rust no escriben | `web/zymbol_vm/HALLAZGOS.md` § BUG-VMJS-001 | zyjs `1.3e0 3.0e0 1.13e0 5.0e-1`; zytw, zyvm y zymbol_vm.js `1.2e0 2e0 1.12e0 5e-1` |
| BUG-ZYE-011 | Tras `(a, k) = v[1]` y `v[1]$~ otra`, la VM copia entero el array `a` en la primera edición; el tree-walker no copia nada. Coste, no salida: la puerta no lo ve | `ZyEdit/HALLAZGOS.md` § BUG-ZYE-011 | `ZyEdit/hypotheses/replaced_tuple/` — HOLDS |
| BUG-ZYE-014 | Insertar en una posición (`a$+[i] v`) y quitar un rango (`a$-[i..j]`) cuestan el array entero en los dos motores de Rust, aunque tenga un solo dueño | `ZyEdit/HALLAZGOS.md` § BUG-ZYE-014 | `ZyEdit/hypotheses/mid_array/` — HOLDS; `ZyEdit/tests/run.sh` lo da como KNOWN en los dos motores |
| GAP-ZYE-015 | No hay **fotograma**: ningún programa puede enseñar una pantalla entera de una vez. Decisión del autor (2026-10-27): la opción 1 en la v0.0.11 (hecha: una escritura por `>>~`), la 2 en la v0.0.12 | `ZyEdit/HALLAZGOS.md` § GAP-ZYE-015 | `ZyEdit/hypotheses/frame/` — HOLDS |

## 2. Decisiones de diseño sin tomar

Son del autor: implementar, aplazar con una razón, o rechazar con una razón.

**Aplazado a v0.0.12** por el autor el 2026-10-24: todo lo de esta sección, y cualquier hallazgo
nuevo de diseño, a menos que bloquee la salida de la v0.0.11. La razón es el calendario: la
v0.0.11 sale el 2026-11-01 y es una release de optimización. Ninguna de las filas de abajo la
bloquea.

### Entrada y terminal

| ID | Qué | Origen | Comprobado |
|---|---|---|---|
| DIS-ZYE-001 | Inicio, Fin, RePág, AvPág, Supr, F1–F12 y Shift+Tab llegan todas como `0d0`, que es el «no hay tecla» de `<<\|?`. `--keys` tampoco las nombra | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-001 | `ZyEdit/hypotheses/keys/` — HOLDS |
| DIS-ZYE-002 | Shift y Ctrl sobre una flecha se pierden: Shift+→ llega como → | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-002 | `ZyEdit/hypotheses/keys/` — HOLDS |
| DIS-ZYE-003 | Ctrl+/, Ctrl+Espacio y Alt+letra llegan como un carácter imprimible (`7`, espacio, la letra) | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-003 | `ZyEdit/hypotheses/keys/` — HOLDS |
| DIS-ZYE-004 | Dentro de `>>\|` el cursor del terminal está oculto y nada lo muestra ni lo coloca | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-004 | `ZyEdit/hypotheses/cursor/` — HOLDS |
| DIS-ZYE-005 | Ningún programa Zymbol puede arrancar otro en un terminal, escribirle y leer lo que dibuja. Es el resto de GAP-GOL-009, y bloquea las etapas 4 y 5 de ZyEdit | `ZyEdit/HALLAZGOS.md` § DIS-ZYE-005 | las comprobaciones de `ZyEdit/hypotheses/` siguen escritas en Python |
| GAP-ZYE-012 | Un programa bloqueado en `<<\|` no se entera de que la ventana cambió de tamaño hasta la tecla siguiente; ZyEdit sondea con `<<\|?` cada 40 ms | `ZyEdit/HALLAZGOS.md` § GAP-ZYE-012 | `ZyEdit/hypotheses/resize/` — HOLDS |
| Serpiente IDEA-001 | Un módulo `std/ansi` con nombres para los colores de `>>~`, en vez de números sueltos | `serpiente/HALLAZGOS_ES.md` § IDEA-001 | «propuesto», sin decisión |
| Zofía IDEA-Z004 | Lectura con tipo y longitud en el propio operador: `<< :###2 "…"` | `Zofia/HALLAZGOS.md` § IDEA-Z004 | «propuesto», sin decisión |
| GAP-VMJS-001 | En el navegador, un `<<` (o un `@~`) dentro del comparador de `$^` no puede esperar: el comparador corre en una llamada anidada. Lo cerraría ordenar con la máquina en marcha, que la VM de Rust descartó para sí por coste (`SortNext`) | `web/zymbol_vm/HALLAZGOS.md` § GAP-VMJS-001 | por lectura del código: zymbol_vm.js responde *«not yet: a `<<` that has to wait, inside a sort comparator»* |

### Texto

| ID | Qué | Origen | Comprobado |
|---|---|---|---|
| BUG-TET-001 · GAP-TET-002 | El texto se ordena por **punto de código** en los motores de Rust y en zymbol_vm.js (`Ё` antes de `А`); zyjs ordena `$^+`/`$^-` por la configuración regional del navegador. Falta decidir qué lado tiene razón y la frase que lo documente (`GUIDE.md` dice «lexicográfico») | `ZyTetris/HALLAZGOS.md` § BUG-TET-001 y § GAP-TET-002 | `["b", "A", "a", "B"] $^+`: zyjs `[a, A, b, B]`; zytw, zyvm y zymbol_vm.js `[A, B, a, b]` |
| GAP-ZYE-010 · GAP-TET-005 | No hay conversión de mayúsculas a minúsculas: ZyEdit la hace con una tabla ASCII y ZyTetris pliega A–Z y А–Я por punto de código | `ZyEdit/HALLAZGOS.md` § GAP-ZYE-010; `ZyTetris/HALLAZGOS.md` § GAP-TET-005 | ningún operador ni módulo de `std/` la tiene |
| GAP-ZYE-007 | El lenguaje no segmenta en clústeres de grafemas: un `Char` es un punto de código, y el editor aproxima el clúster con `t::width(c) == 0` | `ZyEdit/HALLAZGOS.md` § GAP-ZYE-007 | `continues` sigue en `ZyEdit/src/buffer.zy` |
| GAP-TET-003 | `й` (U+0439) e `и`+U+0306 son identificadores distintos que se ven igual; `check` avisa de uno como sin uso y del otro como indefinido. El lenguaje no ha dicho si normaliza | `ZyTetris/HALLAZGOS.md` § GAP-TET-003 | `check`: *unused variable 'й'* sobre la grafía compuesta |
| GAP-TET-004 | La `a` latina y la `а` cirílica son variables distintas y nada avisa | `ZyTetris/HALLAZGOS.md` § GAP-TET-004 | `check`: *No errors or warnings* |
| GAP-ZYE-006 | Un fichero que no es UTF-8 válido no se puede abrir: no hay lectura de bytes | `ZyEdit/HALLAZGOS.md` § GAP-ZYE-006 | `io::read` de `a\xffb`: `##IO(stream did not contain valid UTF-8)` |

### Forma y diagnóstico

| ID | Qué | Origen | Comprobado |
|---|---|---|---|
| GAP-ZYE-008 (resto) | `#\|texto\|` lee un texto como número, pero ningún error de `###"42"`, `##."42"` o `"12" + 1` dice que esa es la forma. Dos proyectos llegaron a la conclusión equivocada (GAP-TET-006) | `ZyEdit/HALLAZGOS.md` § GAP-ZYE-008 | los cuatro motores: `### requires a numeric value, got String`, sin línea de ayuda |
| BUG-ZYE-009 | `@ i:r1 + 1..r2 - 1` es un error en los dos motores de Rust (*ranges can only be used in for-each loops*); zyjs y zymbol_vm.js lo ejecutan. Aceptarlo o rechazarlo en los cuatro con un mensaje que pida paréntesis | `ZyEdit/HALLAZGOS.md` § BUG-ZYE-009 | zytw y zyvm: el error; zyjs y zymbol_vm.js: un aviso de dirección del rango, y corren |
| IDEA-TET-007 | Los símbolos de tipo de `#?` (salvo `##_`) no se pueden escribir en una expresión ni en un patrón: `t == ##]` no se parsea | `ZyTetris/HALLAZGOS.md` § IDEA-TET-007 | error de análisis en los cuatro motores |
| IDEA-TET-008 | `zymbol fmt` rompe un arreglo de 8 números con dos o más negativos en un número por línea; el mismo sin negativos queda en una | `ZyTetris/HALLAZGOS.md` § IDEA-TET-008 | `fmt` de las dos líneas de la ficha: 11 líneas |

## 3. Verificaciones pendientes

Corregidas en su origen, a falta de una medición que la puerta no puede hacer.

| ID | Qué falta | Dónde se hace, y lo último medido |
|---|---|---|
| PERF-08 / GLB-134 | Repetir la medición del binario estático con musl **en la release**: la puerta no construye el estático. Es un paso de la fase 5 de `agents/release_installers.md` desde el 2026-10-21 | `ZyDDT/HALLAZGOS/GLOBAL.md` § GLB-134, «Segunda comprobación intermedia»: el `HEAD` del 2026-10-23 (`30195b2`) se sostiene — ×1,050 en los 16 programas, `s = s "x"` ×1,025 —, y los avisos de 5 rondas eran ruido |

## 4. Documentación

Nada, a 2026-10-30. La frase sobre el orden del texto depende de una decisión y está en la § 2
(BUG-TET-001 · GAP-TET-002).

## 5. Restos en las aplicaciones

El lenguaje ya lo permite; la aplicación todavía no se ha migrado.

| Aplicación | Qué | Origen | Comprobado |
|---|---|---|---|
| GoL | `μέτρηση/όλα.zy` conserva `αριθμός`, una lectura de número escrita a mano, cuando `#\|texto\|` ya lo hace (como migró ZyTetris) | `ZyTetris/HALLAZGOS.md` § GAP-TET-006, «Lo que sigue abierto» | `αριθμός(κείμενο)` sigue en la línea 28 |
