# Hallazgos — sin culpable único

> La regla y el formato están en [`INDICE.md`](INDICE.md). Aquí van tres clases,
> y la primera es la razón de que este fichero exista.

---

## Las tres clases

**1. Los tres coinciden, y los tres están mal.**
Ningún diferencial puede verla: tres motores equivocados coinciden perfectamente.
Sólo la encuentra un **oráculo** —una implementación en otro lenguaje— o un
**`expect`**, la categoría que la forma tiene que alcanzar.

No es una posibilidad remota, es lo esperable: `zytw` y `zyvm` comparten lexer,
parser y analizador semántico, y `zyjs` se portó a mano de ellos. Un error
heredado por los tres es el caso normal, no el raro. `DM-17` ya lo era — *«cada
motor inventa una respuesta distinta, y las tres mal»*.

**2. Los tres difieren entre sí.** No hay un motor que se salga: se salen todos.
En el sondeo: `DM-05`, `DM-09`, `DM-13`, `DM-17`.

**3. El culpable es una pareja.** `DM-23` — los dos motores Rust no ven una
función declarada dentro de un bloque, y el del navegador sí.

---

## Abiertos

| | | |
|---|---|---|
| [`GLB-006`](#glb-006--hay-un-tercer-resaltador-y-nadie-lo-mira) | abierto | el curso lleva su propia copia, 1798 líneas sin marcar |
| [`GLB-007`](#glb-007--un-rechazo-dentro-de-un-bloque-de-una-línea-se-lleva-por-delante-la-llave-que-lo-cierra) | **corregido 2026-09-07** | `skip_statement` produce la cascada que fue escrito para evitar |

## Cerrados

| | | |
|---|---|---|
| [`GLB-001`](#glb-001--el-analizador-no-mira-dentro-del-operando-de-un-operador-) | **corregido 2026-08-30** | los dos motores Rust no comprobaban nada escrito dentro de un operando `$` |
| [`GLB-002`](#glb-002--el-acumulador-yuxtapuesto-sin-declarar-tres-motores-tres-respuestas) | **corregido 2026-08-30** | `s = °s "x"` sin declarar `s`: rechazo, `0xxx` y `0` |
| [`GLB-003`](#glb-003--dos-bucles-que-reutilizan-el-nombre-del-iterador-un-aviso-o-dos) | **corregido 2026-08-30** | un aviso por sitio, no por nombre |
| [`GLB-004`](#glb-004--seis-ficheros-del-corpus-escritos-en-una-forma-que-el-lenguaje-no-tiene) | **corregido 2026-08-30** | reescritos; cuatro módulos vuelven al gate |
| [`GLB-005`](#glb-005--check-rechaza-un-programa-que-los-tres-motores-ejecutan) | **corregido 2026-08-30** | la convención la exigen los cuatro |

| | | |
|---|---|---|
| [`GLOBAL-001`](#global-001--los-tres-motores-redactan-el-mismo-rechazo-de-tres-maneras-28-celdas) | **corregido 2026-08-30** | la comparación imposible se rechazaba con tres redacciones — 28 celdas |

---

## GLOBAL-001 — Los tres motores redactan el mismo rechazo de tres maneras (28 celdas)

**Estado:** **corregido 2026-08-30**
**Veredicto:** la forma es **el tipo solo** — la de la VM.
**Encontrado por:** eje `operator` (`axes/operator.toml`), 28 de 252 celdas
**Clase:** la **2** de las tres de arriba — los tres difieren entre sí, no hay
uno que se salga.

### Qué se observa

`<`, `<=`, `>`, `>=` entre dos especies que no se pueden ordenar. Los tres
motores rechazan —el veredicto es el mismo, `error/runtime`— y los tres escriben
un mensaje distinto:

```zymbol
>> ("ab" < 'c') ¶
```

| motor | mensaje |
|---|---|
| `zytw` | `cannot compare values with operator 'Lt': String("ab") and Char('c')` |
| `zyvm` | `cannot compare values with operator 'Lt': String and Char` |
| `zyjs` | `cannot compare string 'ab' with char c using operator 'Lt'` |

Tres decisiones distintas, y cada una es defendible por separado:

- **el tipo con el valor dentro** (`String("ab")`) — el tree-walker;
- **el tipo solo** (`String`) — la VM, que en ese punto no tiene el valor a mano;
- **el valor en prosa, el tipo en minúsculas** (`string 'ab'`) — el navegador.

Ninguna es un error. Lo que es un error es que sean tres, porque el mensaje es
parte de la respuesta: un programa que se porta igual en los tres motores no se
*explica* igual en los tres, y la documentación sólo puede citar uno.

### Por qué aquí y no en un fichero de motor

Porque no hay un motor que corregir. Elegir a `zytw` como referencia porque es
«el banco de diagnósticos» sería una decisión de diseño disfrazada de arreglo:
la forma de la VM existe porque en ese punto **no tiene el valor**, y unificar
hacia el tree-walker le exige cargarlo hasta el sitio del error. Eso es una
decisión sobre la VM, no sobre un mensaje.

### El reparto de las 28 celdas

Los cuatro operadores de orden contra los siete pares que no se pueden ordenar
(`string-char`, `char-char`, `char-int`, `int-bool`, `bool-bool`, `array-array`,
`array-int`). Las 4 de `tuple-tuple` no están aquí: ahí la VM **no rechaza**, y
eso es [`ZYVM-001`](zyvm.md). Las 4 de `unit-unit` tampoco: ahí los dos motores
Rust coinciden y sólo `zyjs` difiere ([`ZYJS-006`](zyjs.md)).

### Qué se decidió

**El tipo solo**: `cannot compare values with operator 'Lt': String and Char`.

El argumento no es que sea la más bonita, es que es la única que los tres
motores pueden emitir **siempre**. La VM no tiene el valor a mano en ese punto;
unificar hacia el tree-walker la obligaría a arrastrarlo hasta el sitio del
error, y eso es una decisión sobre la VM disfrazada de arreglo de un mensaje.

### Qué se cambió

| motor | cambio |
|---|---|
| `zyvm` | ninguno — ya decía la forma elegida |
| `zytw` | `arithmetic_ops.rs` interpolaba `{:?}` sobre el `Value`, que da `String("ab")`. Pasa a `type_ident()`, un método nuevo junto a `type_word()`, que es el `type_name` de la VM |
| `zyjs` | reescrito a la forma canónica, con `typeIdent()` junto a `typeSymbolBase` |

**Las cuatro parejas cadena↔número se quedan como estaban** —
`cannot compare string 'a' with integer 7 using operator 'Lt'`— y en los tres
motores. Esa comparación **está definida** cuando la cadena es un número en
cualquier escritura, así que el rechazo va de ese texto concreto, no de los
tipos. Los tres ya coincidían en ella.

### La regla se llevó a toda la familia

No sólo a la comparación. El mismo criterio —*un diagnóstico nombra tipos, no
valores*— se aplicó a `arithmetic requires numeric operands`, a
`power operator requires numeric operands`, a
`logical AND/OR requires boolean operands` y a
`negation requires numeric operand`, en los tres motores.

Eso cierra [`ZYJS-006`](zyjs.md) por construcción: si el mensaje no interpola un
valor, ningún `[object Object]` puede aparecer en él. Y el diccionario se llama
`Dict` en los tres, no `Tuple` — que es el vocabulario que el propio código ya
usaba (`RequireDict`, `ModuleConst::Dict`, `GlobalInit::Dict`).

El radio en goldens fue **cero**: `zyquality/messages/baseline.txt` normaliza las
interpolaciones a `§`, así que `String("ab")` y `String` son la misma línea allí.

---

## GLB-001 — El analizador no mira dentro del operando de un operador `$`

**Estado:** **corregido 2026-08-30**
**Clase:** la **3** de las tres de arriba — el culpable es una **pareja**:
`zytw` y `zyvm` comparten el analizador semántico, así que el hueco es el mismo
en los dos y ninguna vista por motor lo enseñaría.
**Encontrado por:** la validación contra las aplicaciones LDV — Chaturanga.
**Archivado primero como `ZYJS-008`**, mal, y eso es parte de la ficha.

### Qué se observa

```zymbol
s = noexiste$#
```

| motor | qué dice |
|---|---|
| `zytw` / `zyvm` | **nada**. `No errors or warnings` |
| `zyjs` | `error: undefined variable 'noexiste'` |

Lo mismo con la aridad de una llamada y con la marca `<~` de un parámetro de
salida. Y la misma línea **un carácter a la izquierda** —`s = noexiste`— se
rechaza desde siempre. No es una comprobación que falte: es una **posición** que
nadie miraba.

### Causa

`crates/zymbol-semantic/src/type_check.rs`, tres brazos de `infer_expr`:

```rust
Expr::CollectionLength(_) => ZymbolType::Int,
Expr::CollectionContains(_) => ZymbolType::Bool,
Expr::CollectionFindAll(_) => ZymbolType::Array(Box::new(ZymbolType::Int)),
```

El `(_)` descarta el operando. Y `infer_expr` **no sólo infiere**: es donde se
emiten las comprobaciones —«¿existe este nombre?», «¿tiene la llamada los
argumentos que toca?», «¿lleva su `<~`?»—. Un brazo que devuelve un tipo sin
descender deja sin mirar todo lo que hay dentro.

Los demás operadores de colección sí infieren sus operandos, porque necesitaban
el tipo para otra cosa. Estos tres no lo necesitaban, y por eso son los tres que
se quedaron ciegos: **el efecto útil viajaba de gorra en el valor de retorno.**

### Arreglo

Descender siempre, aunque el tipo del operando no haga falta:

```rust
Expr::CollectionLength(op) => { self.infer_expr(&op.collection); ZymbolType::Int }
```

y los dos operandos en `$?` y `$??`.

### Cómo se encontró, que es la parte que importa

No lo vio nada de esto: ni las 397 celdas de ZyDDT, ni los 661 ficheros del
corpus, ni los 222 ejemplos, ni los 1026 tests de Rust. Lo vio **Chaturanga**.

Y la prueba de que el hueco era real está en dónde estaban los errores. Al
arreglar el analizador aparecieron **cuatro** llamadas de la suite de Chaturanga
a las que les faltaba la marca `<~`, y las cuatro estaban dentro de un `$#`:

```zymbol
निवेदनम्("black has exactly one move", (नि::वैधचालाः(मातस्थितिः, 2))$#, 1, दोषाः<~)
```

Las líneas vecinas —231 y 233— sí la llevan. El autor escribió la marca en todos
los sitios donde el analizador miraba y se le olvidó exactamente donde no
miraba, que es lo que hace una herramienta cuando calla: no deja un hueco al
azar, deja el hueco con su forma.

### Qué lo sujeta

Tres celdas de `axes/refusal.toml` —`undefined-inside-a-collection-operand`,
`undefined-inside-a-contains-operand`, `arity-inside-a-collection-operand`— más
las cuatro llamadas corregidas en `Chaturanga/परीक्षा/`, que su propio gate
vuelve a ejecutar.

Una de las tres deja una división de redacción anotada en
[`wording.baseline`](../wording.baseline): los dos motores Rust añaden
`= help: expected signature: g(Number, Number)`, con los tipos **inferidos** de
los parámetros, y `zyjs` no tiene inferencia de parámetros con que construirla.
Se anota con su razón en vez de arreglarse a medias.

---

## GLB-002 — El acumulador yuxtapuesto sin declarar: tres motores, tres respuestas

**Estado:** **corregido 2026-08-30**
**Clase:** la **2** — los tres difieren entre sí, no hay uno que se salga.
**Encontrado por:** estrechar [`ZYJS-011`](zyjs.md), no buscarlo.

### Qué se observaba

```zymbol
@ _i:1..3 { s = °s "x" }
>> "[" s "]" ¶
```

| motor | respuesta |
|---|---|
| `zytw` | `Runtime error: 's' is undefined — did you mean 's°' (hot definition)?` |
| `zyvm` | `[0xxx]` |
| `zyjs` | `[0]` |

Con `s = ""` delante los tres contestaban `[xxx]` (una vez corregido
`ZYJS-011`). Sin declarar, cada uno inventaba una cosa.

### Causa — la misma en los tres, por sitios distintos

`GUIDE.md` § *Hot Definition Operator* dice que la variable se inicializa al
**valor neutro**, y el neutro es una propiedad **del operador**: `+` → `0`,
`$+` → `[]`, yuxtaposición → `""`. Los tres motores lo sabían en el camino de
la asignación y ninguno en el de la expresión:

| motor | dónde |
|---|---|
| `zytw` | `expressions.rs`, el bloque de inicialización caliente en RHS sólo miraba `BinaryOp::Add`; con `Concat` el `°s` se evaluaba como una variable inexistente |
| `zyvm` | `compile_expr` emite `HotInit(dst, HotNeutral::Int)` desde la rama genérica de identificador, que **no sabe bajo qué operador está**; `hot_neutral_instr`, en el camino de la asignación, sí lo sabía |
| `zyjs` | `_hotNeutralForExpr` devolvía `mkInt(0)` para un identificador pelado |

### Arreglo

Darle a cada uno el operador donde se decide el neutro: el `Concat` en el
bloque del tree-walker, un pre-paso en `compile_binary` para la VM, y el número
de elementos tras el centinela en `zyjs`. Ninguno es una decisión de diseño —
la respuesta ya estaba escrita en el GUIDE, y las tres implementaciones la
tenían a medias.

### Qué lo sujeta

[`ZYJS-011_acumulador_yuxtapuesto.zy`](../cases/pin/ZYJS-011_acumulador_yuxtapuesto.zy),
que hace las dos formas —declarada y sin declarar— y las tres que ya
funcionaban.

---

## GLB-003 — Dos bucles que reutilizan el nombre del iterador: ¿un aviso o dos?

**Estado:** **corregido 2026-08-30**
**Veredicto:** **dos avisos, uno por sitio.** Cambian los dos motores Rust.
**Clase:** la **3** — el culpable era una pareja.
**Encontrado por:** limpiar la chincheta de [`ZYJS-011`](zyjs.md)

### Qué se observa

```zymbol
@ i:1..3 { s = °s "x" }
@ i:1..3 { t = °t "y" }
>> s t ¶
```

| motor | avisos `unused variable 'i'` |
|---|---|
| `zytw` / `zyvm` | **1** |
| `zyjs` | **2** |

Son dos bucles, dos iteradores y ninguno se usa. Que salgan dos avisos es
defendible; que los motores Rust deduplican por nombre también lo es —el
consejo es el mismo y repetirlo no añade nada—. Lo que no puede quedarse es que
dependa del motor.

### Causa

`variable_analysis.rs` guardaba las declaraciones en un `HashMap` indexado
**por nombre**, así que la segunda `i` desplazaba a la primera. No salía un
aviso más corto: salía un aviso **sobre uno de los dos sitios**, y el otro se
perdía en silencio. Un aviso lleva posición; uno para dos sitios no es un
resumen, es un informe incompleto.

### Arreglo

Un campo `retired`: lo que una declaración desplaza se guarda y se avisa al
final. El uso sigue marcando la declaración **actual**, que es lo correcto —
una lectura tras una redeclaración lee la nueva variable. Los prefijados con
`_` siguen sin avisar, las veces que hagan falta.

Ningún golden del corpus cambió: no había ningún fichero con dos declaraciones
sin usar del mismo nombre, que es exactamente por qué nadie lo había visto.

### Qué lo sujeta

[`GLB-003_aviso_por_sitio.zy`](../cases/pin/GLB-003_aviso_por_sitio.zy), que
afirma las dos mitades: los dos avisos, y que `_k` sigue callando.

---

## GLB-004 — Seis ficheros del corpus escritos en una forma que el lenguaje no tiene

**Estado:** **corregido 2026-08-30**
**Veredicto:** **reescribirlos** a la forma con comillas.
**Clase:** ninguna de las tres. No era que los motores discreparan: es que
**nadie los ejecutaba**, y la exclusión que lo tapaba daba una razón falsa.
**Encontrado por:** revisar las exclusiones de `corpus.toml` que no eran
ambientales.

### Qué se observa

`corpus/i18n/matematicas/{archivos,db,http,sistema}.zy` y sus dos importadores
`i18n/test_archivos.zy`, `i18n/test_database.zy` escriben así:

```zymbol
resultado = <\ find . "-maxdepth" 1 "-name" "*.zy" \>
resultado = <\ sqlite3 {nombre_db} "SELECT 1;" \>
```

Ninguno de los seis parsea en el CLI. Medido:

```text
<\ "echo hola" \>        → hola
<\ echo "hola" \>        → Runtime error: 'echo' is undefined
<\ "find" "." "-maxdepth" "1" \>  → funciona
```

**Cada argumento de `<\ … \>` es una EXPRESIÓN**, no una palabra de shell. Un
`echo` desnudo es la búsqueda de una variable llamada `echo`. `GUIDE.md` § BashExec
documenta la forma con la orden entre comillas —`<\ "date +%Y-%m-%d" \>`, con la
interpolación DENTRO de la cadena— y sólo esa.

### Por qué llevaban ahí

Porque `zyjs` los «acepta»: su shell es un stub que devuelve una marca de tiempo
y **nunca evalúa sus argumentos**, así que el `echo` desnudo no se busca nunca.
Y la exclusión decía *«el parser del CLI rechaza estas formas como tokens
inválidos»*, que suena a defecto del CLI y no lo es.

Una exclusión con una razón falsa es peor que una sin razón: la segunda invita a
mirar y la primera cierra la pregunta.

### Arreglo

**59 líneas reescritas en siete ficheros**, cada `<\ … \>` con la orden en una
sola cadena. El entrecomillado del shell se conserva donde hace falta: un
argumento que ya venía entre comillas y contiene un metacarácter sigue
entrecomillado, así que `-name "*.zy"` es `-name '*.zy'` y **no** un glob que
el shell expande. El primer intento no lo hizo y lo habría cambiado en silencio.

### Y lo que se descubrió al hacerlos correr

Los cuatro `matematicas/*.zy` son **ficheros de módulo**, así que ejecutados
directamente se rechazan como tales — que es lo que `zyjs` decía desde siempre y
lo que hacen sus vecinos del mismo directorio. Los tres motores coinciden ahora,
así que sus **cuatro exclusiones se retiraron**: el corpus pasa de 627 a **631
acuerdos** para el navegador.

Los cuatro `test_*.zy` que los importan son otra historia. Ahora corren de
verdad, y correr es justo lo que los descalifica:

- imprimen **el reloj, la máquina y el directorio** — `date`, `uname`,
  `whoami`, un recuento de ficheros, otro de procesos;
- y **escriben dentro del corpus**: una ejecución dejó `corpus/25`,
  `corpus/test_archivo.txt` y `corpus/test_zymbol.db`.

Un test que muta el árbol desde el que se le juzga no puede estar en un gate.
Se quedan con una exclusión para **todos** los motores y la razón verdadera,
bajo la etiqueta nueva `ENVIRONMENT`. Siguen barridos por `zymbol check`, así
que una regresión de parseo se caza — que es más de lo que hacían antes.

Si algún día se quieren graduar, el mecanismo existe: `corpus.toml` § wildcard
permite `****` en un golden, y la **estructura** de su salida sí es fija. No lo
hice porque grabar el golden en esta máquina mete esta máquina en el corpus.

### Lo que además destapa

`zyjs` acepta `{var}` fuera de una cadena dentro de `<\ … \>` y el CLI lo
rechaza. Ahí el CLI tiene razón —la guía documenta la interpolación **dentro**
de la cadena— así que es sobre-aceptación del navegador, de la familia de
`ZYJS-001`. Sin chincheta todavía: mientras los seis ficheros sigan muertos, la
forma no tiene dónde asentarse.

---

## GLB-005 — `check` rechaza un programa que los tres motores ejecutan

**Estado:** **corregido 2026-08-30**
**Veredicto:** **que los motores la exijan.** Medido antes de decidir: de 84
módulos con forma de punto en todo el repositorio, **uno** incumplía.
**Clase:** ninguna de las tres, y por eso importa: no discrepaban los motores,
discrepaba **una herramienta con los motores**. `zyq consensus` no puede verlo —
compara motores— y `zyq expect` tampoco, porque el programa se ejecuta bien.
**Encontrado por:** el único desacuerdo de `zyq suite --only lsp` que no estaba
en la línea base.

### Qué se observa

Dos ficheros, `sub/m.zy` declarando `# .m`:

| herramienta | respuesta |
|---|---|
| `zymbol run` | `hola` |
| `zymbol run --vm` | `hola` |
| `zyjs` | `hola` |
| **`zymbol check`** | **`error: E001: module '.m' should be named 'sub_m' for its path`** |

`REFERENCE.md` presenta `check` como *«syntax/semantic check only»* del mismo
programa. Aquí rechaza uno que los tres motores corren.

### Y debajo, un defecto que no depende de la decisión

El nombre que E001 exige **depende del directorio desde el que se invoca**:

```text
$ cd corpus        && zymbol check modules_scope/funcion_de_modulo_valor.zy
error: … should be named 'modules_scope_funcion_de_modulo_valor_m'
$ cd corpus/modules_scope && zymbol check funcion_de_modulo_valor.zy
error: … should be named '_funcion_de_modulo_valor_m'
```

`validate_module_name` (`crates/zymbol-semantic/src/modules.rs`) toma
`file_path.parent().file_name()` sobre la ruta **tal como se escribió**, no sobre
la ruta real. El mismo fichero pide dos nombres distintos, y ninguno puede
satisfacer a los dos. Eso está mal se decida lo que se decida sobre lo de arriba.

### Arreglo, en tres piezas

**1. La ruta se canonicaliza** (`modules.rs`). Eso solo elimina el falso
positivo entero: `Chaturanga/परीक्षा/आकृतिः.zy` cumplía la convención y sólo
fallaba al analizarse desde su propio directorio.

**2. Los motores la exigen.** Hecho **una vez en el CLI** y no en cada cargador:
el tree-walker tiene uno, la VM otro y el navegador un tercero, y una regla
escrita tres veces es como pasó `GLOBAL-001`. `run_file_inner` recorre los
imports transitivamente y pregunta **sólo** por el nombre del módulo — no la
comprobación entera, que emitiría los avisos de estilo de un módulo cada vez que
se ejecute un programa que lo importa.

**3. `zyjs` la exige en su fase estática**, no en su cargador. Levantarla al
cargar da `error/runtime` donde los dos motores Rust dan `error/static`, y un
rechazo que cae en otra categoría es una divergencia aunque las palabras
coincidan. Deriva el directorio del **fichero que importa** más la ruta del
import, que es la única forma que ese motor tiene de saber dónde está el fichero
de verdad — usar el nombre que el resolvedor le da es el mismo defecto de la
pieza 1, una capa más arriba.

Y el fichero que incumplía —`corpus/modules_scope/funcion_de_modulo_valor_m.zy`—
pasa a la forma **desnuda**, que es la que usan sus siete vecinos del mismo
directorio.

### El LSP, de paso

Callaba porque informa por documento y el error estaba en el módulo importado.
Con la convención aplicada en los cuatro sitios, `zyq suite --only lsp` va a
**18 desacuerdos, 0 fuera de la línea base**.

### Qué lo sujeta

[`ZYQ-001_convencion_de_nombre.zy`](../cases/pin/ZYQ-001_convencion_de_nombre.zy).

---

## GLB-006 — Hay un tercer resaltador, y nadie lo mira

**Estado:** **abierto** — pendiente de tu veredicto
**Clase:** ninguna de las tres. No discrepan los motores: hay una **superficie
que el CHARTER no declara** y que por tanto ningún gate recorre.
**Encontrado por:** buscar los ficheros de la superficie 4 para construirle una
suite, y encontrar tres en vez de uno.

### Qué se observa

`aprende_zymbol/zymbol-highlight.js`, cuya primera línea dice:

```js
/* Zymbol syntax highlighter — ported directly from web/playground.html */
```

Portado, y desde entonces a la deriva: **223 líneas frente a las 430** del
original. Barrido contra el corpus con el mismo método de CHARTER § 4:

| | `web/src/playground/highlight.js` | `aprende_zymbol/zymbol-highlight.js` |
|---|---:|---:|
| líneas con algo sin marcar | **0** | **1798** |

Lo que deja desnudo son exactamente los defectos que la auditoría del playground
corrigió, más uno propio:

- **773 `#`** — la familia entera del `#`, que es el caso que el CHARTER cita
  como «328 `#` sin marcar en el corpus» para la versión de entonces;
- **653 `.`**;
- y **pares suplentes partidos** (`\ud805`, `\ud835`, …): parte los dígitos
  fuera del BMP por la mitad, así que ninguna de las 31 escrituras astrales que
  el lenguaje soporta se colorea entera.

### Por qué importa más de lo que parece

`aprende_zymbol` es **el curso**: es donde alguien ve Zymbol por primera vez. El
código que peor se colorea de todo el proyecto es el que se enseña primero.

Y el repositorio no tiene gate ninguno, así que esto no se degradó — nunca se
midió.

### Qué habría que decidir

1. **Que el curso cargue el resaltador del playground** en vez de una copia.
   Es un fichero ES-module y el curso usa un script de globales de navegador,
   así que hace falta un envoltorio pequeño; a cambio la copia desaparece y con
   ella la deriva.
2. **Declararlo superficie 6** en `CHARTER.md` § 4 y graduarlo aquí, con su
   propio driver. Sigue habiendo dos implementaciones que mantener, pero al
   menos la divergencia se ve.
3. **Reescribir la copia** al nivel del original. Es lo que ya se hizo una vez,
   y esta ficha existe porque volvió a pasar.

La 1 es la única que quita el problema en lugar de vigilarlo.

### Qué lo sujeta

**Nada.** El repositorio del curso no está en el gate, y añadirlo es parte de la
decisión.

---

## Sobre la clase 1, que sigue sin aparecer

Ninguna entrada de la clase **1** —los tres coinciden y los tres están mal— se
ha encontrado todavía, y eso no es tranquilizador: sólo la ve un oráculo o un
`expect`. Hoy los ejes con oráculo son `arithmetic` (4 celdas) y `numerals`
(69). La columna `oracled` de `zyddt axis` es el recuento honesto de dónde el
acuerdo **no** es la única prueba, y vale 73 sobre 394.

Dicho de otra forma: de las 394 celdas, 321 están verdes por acuerdo y nada más.
Si alguna esconde un error de los tres, ZyDDT no puede verlo hoy, y ésa es la
lectura correcta de la ausencia en este fichero.


---

## GLB-007 — Un rechazo dentro de un bloque de una línea se lleva por delante la llave que lo cierra

**Estado:** **corregido 2026-09-07**
**Encontrado por:** `chained-index/array-in-loop` y `chained-index/deep-in-loop`
**Motores:** `zytw` y `zyvm` (comparten parser). `zyjs` da un solo error.
**Clase:** la **1** — dos motores contra uno, y el que se sale son los dos.

### Qué se observa

Cualquier rechazo del parser dentro de un bloque escrito en una línea sale
**dos** veces: el rechazo real, y detrás un `expected '}' to close block` que
habla de una llave que sí estaba.

```zymbol
m = [[1,2],[3,4]]
@ i:1..2 { >> m[i][1] ¶ }
```

```
error: chained index does not exist: 'm[…][…]' is not a form of Zymbol
  --> 2:15
error: expected '}' to close block          ← no falta ninguna llave
  --> 3:1
```

### No es del rechazo nuevo — es de `skip_statement`

Se vio con `chained index` porque ese eje es el que lo cruzó con un bucle, pero
el rechazo **preexistente** hace lo mismo, medido el mismo día:

```zymbol
@ i:1..2 { m[i][1] = 7 }     // `indexed assignment` + `expected '}'`
```

La causa está en `zymbol-parser/src/lib.rs`. Un rechazo que ya ha decidido que
la sentencia entera está mal llama a `skip_statement()`, que para **en** el `}`
sin consumirlo — correcto. Después `parse_block` recibe el `Err` y llama a
`skip_statement()` **otra vez** como recuperación, y esa segunda llamada avanza
un token incondicionalmente («a skip that can consume nothing turns recovery
into a loop»). Ese token es la llave.

### La ironía, que es lo que la hace digna de un número

`skip_statement` existe **exactamente** para esto. Su propio comentario lo dice:

> so `a[2] = 99` reported the real refusal … and then `unexpected token:
> Integer(99)`, a second error about the leftovers of the first … A reader
> cannot act on that, and it buries the message that matters.

Arregló la cascada de los restos de la sentencia y abrió otra, un token más
allá, con la llave del bloque. El aviso es la forma del defecto, no su tamaño:
**una recuperación tiene que saber si alguien ya recuperó.**

### Cómo se corrigió, y el intento que hubo que descartar

**Lo primero que probé no valía, y el modo de fallar es la parte útil.** Guardé
en el parser dónde había terminado el último `skip_statement` y no avanzaba si
se le llamaba otra vez en la misma posición sobre un `}`. Cerró la cascada y
abrió un **bucle infinito**: un fichero de `}` sueltos colgaba `zymbol check`
para siempre, porque la posición no distingue «alguien ya saltó» de «el salto
anterior me dejó aquí». Medido contra la línea base — que no cuelga — antes de
descartarlo.

La corrección es más simple y va a la causa: **un rechazo no salta la
sentencia**. Los dos bucles de recuperación —el de `parse_block` y el de nivel
de fichero— ya llaman a `skip_statement` en su rama `Err`, así que hacerlo
también en el rechazo lo ejecutaba dos veces, y el `advance()` incondicional de
la segunda vez se comía la llave. Se retiraron las tres llamadas: las dos de
`variables.rs` y la de `reject_chained_index`.

**Y faltaba una segunda mitad**, que el eje siguió señalando: cuando el rechazo
cae en la CONDICIÓN de un `?`, no hay ningún `parse_block` corriendo que sea
dueño del `{ … }`, así que el salto se paraba en la llave de cierre y la vuelta
siguiente leía una llave suelta como sentencia. Ahora `skip_statement` cuenta
llaves: salta el cuerpo entero, y al cerrarlo consume esa llave y sigue la regla
de línea desde ella —lo que mantiene dentro del salto lo que continúe la
sentencia, como un `?? { … }`—. Un `}` con `depth == 0` es de un bloque que nos
envuelve y se deja intacto, que es lo que evita el bucle del primer intento.

Verificado en las dos formas y en las dos posiciones: `?` y `@`, de una línea y
de varias, con `??` y sin él, más un fichero de llaves sueltas, que sigue
terminando.

---

## GLB-008 — Usar un nombre tras `\` se rechaza en los tres, en momentos distintos y diciendo cosas distintas

**Estado:** **corregido el 2026-09-13.** Los tres rechazan, en ejecución y con la
misma frase. Y el arreglo acabó siendo **el contrario del que esta ficha
proponía** — ver «Lo que la medición cambió»
**Encontrado por:** `lifetime/use-after-destruction`, la primera vez que se preguntó
**Familia:** `AGENTIC.md` G4, que lo tenía anotado como «solo en ejecución» sin saber que zyjs ya lo hacía antes

### Qué se observa

```zymbol
x = "dato"
>> x ¶
\ x
>> x ¶
```

| motor | cuándo | qué dice |
|---|---|---|
| `zytw`, `zyvm` | **en ejecución**, con «dato» ya impreso | `use after destruction: variable 'x' was destroyed after its last use` |
| `zyjs` | **antes de ejecutar** | `undefined variable 'x'` — y su ayuda dice «variables must be defined before use» |

`zymbol check` no dice nada por el lado de Rust.

**Cada motor tiene una mitad distinta bien.** El del navegador rechaza en el
momento correcto —antes de escribir media salida— y el mensaje no menciona que
hubo una destrucción, así que manda al lector a buscar una definición que existe.
Los de Rust nombran exactamente lo que pasó y llegan cuando el programa ya
imprimió.

### Por qué no lo había visto nadie

El corpus tiene dos ficheros que usan `\` —`bug_mm3_destroy_frame_local.zy` y
`gap01_lifetime_end_noop.zy`— y **los dos destruyen un nombre y no vuelven a
tocarlo**. El caso del que trata la regla no lo escribía ninguno, así que
`zyq consensus` nunca lo comparó. Apareció al declarar MEM-8 y escribir su
primera celda.

Es el argumento de la capa de celdas en una línea: la pregunta no estaba
esperando a que alguien tropezara con ella, estaba esperando a que alguien la
hiciera.

### Lo que la medición cambió

La propuesta era llevar la comprobación a `zymbol-semantic`, porque «un motor ya
lo hace antes». Al escribir la celda que faltaba apareció por qué ningún motor
Rust lo hacía:

```zymbol
x = 1
? #0 { \ x }      // la rama NO se ejecuta
>> x ¶            // zytw: 1   ·   zyjs: error
```

**zyjs rechazaba un programa correcto.** Una comprobación estática sin análisis
de flujo no puede distinguir una destrucción que **ocurrió** de una que sólo está
**escrita**, así que la respuesta en ejecución no es la tardía: es la única
correcta. La propuesta iba al revés y habría convertido el falso positivo de un
motor en el comportamiento de los tres.

Es `lifetime/destroy-in-a-branch-not-taken`, y se escribió después de que el
arreglo propuesto empezara a parecer obvio.

### Qué se arregló, y dónde

**El navegador** — el `Checker` borraba el nombre del marco al ver `\`, así que
cualquier uso posterior era `undefined variable`, mirara o no el flujo. Ya no lo
borra. La comprobación vive donde los motores Rust la tienen: en ejecución, en
`Env`, que sabe lo que de verdad pasó. Y `Env` recuerda ahora **qué** nombre se
destruyó, para poder decirlo — antes contestaba `'x' is undefined — did you mean
'x°'`, que manda a buscar una definición que estaba ahí y sugiere un mecanismo de
ámbito de bucle que no tiene nada que ver.

**La VM** — y aquí había un tercer defecto que esta ficha no vio, porque la
primera medición miró sólo la primera línea de la salida: **`\` no hacía nada**
sobre una variable de archivo. El compilador quitaba la ligadura del registro,
pero una variable de archivo vive también en `global_vars`, así que la siguiente
lectura la encontraba allí y `>> x` volvía a imprimir el valor. Instrucción nueva
`DestroyGlobal(gvar, nombre)`: termina la ranura y guarda el nombre para el
mensaje; `StoreGlobal` la revive, porque `\` acaba una vida y no quema el nombre.

### Lo que queda

En la VM, destruir un **local de función** da todavía `'y' is undefined — did you
mean 'y°'` en vez de la frase de destrucción. El mecanismo de arriba no llega
ahí: un registro no lleva nombre en ejecución. Es el mismo defecto de redacción
que se acaba de cerrar para el archivo, en el otro sitio.

### Qué lo sujeta

El eje `lifetime` entero, **5 de 5 en verde**: el uso tras destruir, la rama que
no se ejecuta, que reasignar revive el nombre, que destruir lo terminado sea lo
corriente y que una función pueda destruir su propio local.

---

## GLB-009 — El estado de un módulo sale al exterior en la VM y en el navegador

**Estado:** **cerrado en lo que importa el 2026-09-13** — el estado ya no sale en
ningún motor. Queda abierta la mitad de menor peso: **cuándo** se detecta
**Encontrado por:** `modularity/module-state-is-not-exportable`, la primera celda que preguntó por MEM-4
**Gravedad:** **alta.** Es el cerrojo que impide que el estado de módulo sea una variable global, y **la VM es el futuro motor por defecto**

### Qué se observa

```zymbol
// m/exporta_var.zy
# exporta_var {
    #> { n, sube }      // `n` es una VARIABLE, no una constante
    n = 0
    sube() { n = n + 1 }
}
```

```zymbol
<# ./m/exporta_var => E
>> E.n ¶
```

| | |
|---|---|
| `zymbol check` | `error: E005: Item 'n' not found in module` ✔ |
| `zytw` | `Runtime error: Module 'E' has no constant 'n'` ✔ |
| `zyvm` | **imprime `0`** ✘ |
| `zyjs` | **imprime `0`** ✘ |

### Por qué importa

`MEM-4` dice que las variables de un módulo las escriben y leen **sus propias
funciones, y sólo ellas**. Lo que hace que eso sea un entorno cerrado en vez de
una variable global es precisamente que una variable no se pueda exportar. En dos
de los tres motores ese cerrojo no existe en ejecución: basta declararla en el
`#>` y el estado queda legible desde fuera.

### Cómo se coló

Está anotado porque es el método lo que falló, no la atención. El 2026-09-12
verifiqué MEM-4 y escribí *«holds, and the fence is enforced: `#> { n }` where
`n` is a variable is E005»*. Lo comprobé **con `zymbol check`** y no ejecutando.
Es literalmente el error que `DM-05` cometió —comprobar el diagnóstico en vez de
la consecuencia— y que está escrito en
`zymbol-design/HOW_TO_CHANGE_ZYMBOL.md` § 2 como la salida número 3.

Un aviso estático que dos motores no respetan en ejecución no es un cerrojo: es
un aviso.

### Arreglo propuesto

Que la construcción de la tabla de exportación rechace una ligadura mutable en
el mismo sitio donde ya lo hace el análisis estático, en la VM y en `zyjs`. La
pregunta previa —¿debe `E.n` ser error, o debe `#>` rechazar la declaración?— la
responde el análisis de Rust: rechaza la **declaración**, en el módulo, que es
donde está el defecto.

**Es propuesta, no decisión.**

### Qué se arregló, y dónde

**La VM** — `crates/zymbol-compiler/src/lib.rs`. Al construir la tabla de
exportación aceptaba `Statement::Assignment` además de `ConstDecl` como origen
de una constante exportada, así que `#> { n }` con `n = 0` exportaba el valor
inicial de la variable como si fuera constante. Quitado el brazo. Y un segundo
arreglo de camino: un alias conocido con un campo desconocido caía a compilar
`E` como expresión y contestaba `undefined variable 'E'`, que manda al lector a
buscar una definición que está delante. Ahora dice lo que dice el tree-walker,
con la lista de lo que el módulo sí tiene.

**El navegador** — `web/src/zymbol/zymbol.js`. La tabla de exportación entregaba
lo que el nombre tuviera, fuera lo que fuera. Ahora sale una constante o una
función, y nada más. Su mensaje para `E.n` decía «does not export **function**»,
que nombraba lo que no era: `.` lee una constante, y ahí es donde acaba quien
intenta alcanzar el estado de un módulo desde fuera.

### Lo que queda

Los tres motores rechazan y **dicen exactamente la misma frase**. Lo que aún
diverge es el momento: `zyvm` lo detecta al **compilar**, `zytw` y `zyjs` al
**ejecutar**. Es la misma familia que `GLB-008` — un motor llega antes que los
otros a la misma conclusión — y cerrarla es mover la comprobación al análisis
previo, que es donde `zymbol check` ya la tiene (`E005`).

### Qué lo sujeta

`modularity/module-state-is-not-exportable`: pasó de **WRONG** —un motor aceptaba
el programa— a **DIVERGE** por el momento. La diferencia entre esos dos
veredictos es exactamente lo que se arregló. A su lado
`modularity/module-functions-own-the-state`, verde, sujeta la mitad legítima: el
estado persiste entre llamadas y lo llevan las funciones del módulo.

---

## GLB-010 — En la VM, un `:!` tipado que no coincide hace desaparecer el error

**Estado:** **corregido 2026-09-14** — pila de manejadores, errores pendientes y salidas por salto en la VM; el clasificador de kind compartido por los tres motores
**Encontrado por:** `runtime-errors/type-is-catchable`, la primera celda que preguntó por `##Type`
**Gravedad:** **alta.** Es la forma más cara que puede tomar un fallo: sin salida, sin código de salida, sin rastro — y **`zyvm` es el futuro motor por defecto**

### Qué se observa

```zymbol
!? {
    >> (1 / 0) ¶
} :! ##Index {          // no coincide: esto es un ##Div
    >> "index" ¶
}
>> "sigue" ¶
```

| motor | |
|---|---|
| `zytw` | `Runtime error: division by zero` — el error no fue atendido y sale |
| `zyvm` | **imprime `sigue`** |

Un `:!` tipado **filtra**; un error que no pasa el filtro no ha sido atendido y
tiene que salir del `!?` exactamente como si no se hubiera escrito ningún catch.
En la VM desaparece, y el programa continúa con el estado que dejó el fallo.

Se comprobó en las dos direcciones —un `##Div` contra `:! ##Index` y un
`##Index` contra `:! ##Div`— porque una sola dirección la cumpliría un motor que
sencillamente no case nunca.

### Y una segunda mitad, que es la que lo destapó

```zymbol
<# std/math => m
!? { >> m::sqrt("a") ¶ } :! { >> (_err#?)[1] ¶ }
```

| motor | kind |
|---|---|
| `zytw` | `##Type` |
| `zyvm` | **`##_`** |

La VM no lleva el tipo de un error nativo, así que `:! ##Type` no podía casar
nunca — y al no casar, por el defecto de arriba, el error se perdía. Los dos
juntos convierten un `!? … :! ##Type` en un tragaerrores silencioso.

`zyjs` tiene el tercer comportamiento: no captura por tipo y deja salir el error,
que es incorrecto de otra manera pero al menos es ruidoso.

### No era un caso: era el mecanismo

Siguiendo el defecto aparecieron **veintitrés** programas más en los que la VM
no hace lo que hacen los otros dos motores, y todos tienen la misma forma: un
error que viaja por un `!?` y llega a un sitio que no es el suyo. Están
declarados en `axes/error-flow.toml` (25 celdas) y las agrupo por lo que falla:

| la VM… | ejemplo |
|---|---|
| **no anida**: un `!?` interior que ya terminó sigue armado | `!? { !? {…} :! {…}  >> 10/0 } :! ##Div {…}` entra en el catch **interior** |
| **no relanza**: un filtro que no coincide, un `:>` sin catch | `!? { >> 10/0 } :> { >> "f" }` imprime `f` y **sigue** |
| **no respeta al de fuera**: un error dentro de `:!` o `:>` no llega al `!?` exterior | aborta el programa aunque haya un `:! ##Index` esperándolo |
| **no desarma al salir por un salto** | `@ { !? { @! } :! {…} }` y después del bucle cualquier error entra en ese catch — con `@ {}` es un **bucle infinito** |
| **no ejecuta `:>` al salir por `@!`/`@>`** | `@ { !? { @! } :> { >> "f" } }` no imprime `f` |
| **confunde el `<~` de una lambda con el de su `!?`** | una lambda escrita dentro de un `!?` con `:>` ejecuta ese `:>` al retornar; una escrita dentro de `:>` no retorna |
| **mete el `:>` alcanzado por `<~` dentro de su propio `:!`** | `!? { <~ 1 } :! {…} :> { >> 10/0 }` lo captura su propio catch |
| **no ve un `!?` dentro de una función de `$>`** | ni el de dentro de la lambda ni el de fuera del `$>` — ver `ZYVM-004` |

El tree-walker y `zyjs` coinciden en 23 de las 25. Las otras dos no son de la
VM y tienen ficha propia: en una se equivoca `zyjs` —un `@>` dentro de `@ N`
termina el programa, `ZYJS-017`— y en la otra el tree-walker, que se salta el
`:>` cuando el `:!` falla, contra Python y contra `REFERENCE.md` («`:>` always
executes»): `ZYTW-002`.

### Causa

Tres, y la tercera es la que las junta:

1. **Un solo manejador por marco.** `FrameInfo` tiene un `catch_ip` y un
   `try_depth`. `TryBegin` sobrescribe el `catch_ip` sin guardar el de fuera, y
   `TryEnd` sólo lo borra cuando la profundidad llega a cero. Al entrar en el
   catch, `raise!` pone la profundidad a **cero** —la de todos los `!?` del
   marco, no la de uno—.
2. **Ninguna noción de «error pendiente».** El compilador
   (`compile_try`, `zymbol-compiler/src/lib.rs`) cae al final del despacho tipado
   cuando no coincide nada, y un `:>` sin catch usa la etiqueta del `:>` como
   destino del error: se ejecuta la limpieza y **no queda nada que relanzar**.
3. **Los saltos no saben que cruzan un `!?`.** `@!`, `@>` y `<~` emiten un
   `Jump` o un `Return` sin desarmar el manejador ni ejecutar el `:>`. El único
   rastro de esto era `pending_finally`, que vive en el `Compiler` y no en el
   contexto de la función, así que **se hereda dentro de una lambda**.

La mitad del kind es independiente: la VM clasifica por variante de `VmError`,
y un error nativo llega como `Generic` con un mensaje; el tree-walker lo
clasifica por el texto. Mismo mensaje, dos clasificaciones.

### Arreglo

1. **Pila de manejadores**, sin asignaciones en el camino sin error: `TryBegin`
   guarda el manejador de fuera en un registro que el compilador reserva, y lo
   restauran `TryEnd` y la entrada al catch.
2. **Errores pendientes por marco**, etiquetados por el `!?` que los recibió:
   la entrada al catch guarda el error; una cláusula que coincide lo **consume**;
   al final de `:>` —o de la cadena de cláusulas si no hay `:>`— una instrucción
   lo **relanza** si sigue ahí, restaurando la posición donde nació.
3. **El compilador lleva la pila de `!?` en el contexto de la función**, y cada
   `@!`, `@>` y `<~` que la cruza desarma, ejecuta el `:>` que le toca o relanza
   el error que ese `:>` llevaba.
4. **Un solo clasificador de kind por texto**, usado por los dos motores Rust
   para los errores que no traen variante propia, y portado a `zyjs`.

### Verificación

`error-flow` 28/28 (21 contra Python), `runtime-errors` 8/8, `callable-body`
84/84; `zyq consensus` 660 de acuerdo y 0 divergiendo; `cargo test` 1038 sin
fallos. Los benchmarks de la VM, medidos antes y después en la misma máquina,
entre −9 % y +3 %.

Tres cosas salieron al arreglarlo y tienen celda: `$!!` también se saltaba el
`:>` (`propagate-runs-finally`); un fin de entrada dentro de `!?` no se capturaba,
porque `raise!` estaba dentro del bucle de lectura y su `continue` continuaba
ESE bucle (`input-eof-is-catchable`); y la llamada de cola dentro de `!?` se
suprime ahora siempre (`tail-call-inside-try-is-caught`).

### Qué lo sujeta

`axes/error-flow.toml` (28 celdas; las 23 con oráculo en Python salvo las que
dicen por qué no lo llevan) y las cuatro de `runtime-errors`:
`unmatched-catch-propagates-div`, `unmatched-catch-propagates-index`,
`a-native-type-error-knows-its-kind` y `type-is-catchable`.

---

## GLB-011 — Los operadores `$` con un operando del tipo equivocado: el TW rechaza, la VM y `zyjs` a veces contestan, y los tres dan kinds distintos

**Estado:** **corregido 2026-09-22 (paso G1).** La parte «colecciones tolerantes» quedó **derogada** el 2026-09-20: son ESTRICTAS ([[GLB-046]]), y el paso 4.3 lo implementó en la VM y en `zyjs`. Lo que faltaba —las celdas `-met` cuyo TW contestaba `##_`— se cerró anotando los 22 sitios que quedaban en el tree-walker
**Encontrado por:** `axes/runtime-collection-ops.toml`, paso C3 del plan de cobertura de diagnósticos, 2026-09-14
**Gravedad:** media-alta: el mismo programa falla en un motor y contesta un valor en otro

### Qué se observa

50 diagnósticos de ejecución de los operadores `$`, provocados cada uno con el
operando equivocado entrando por un parámetro (así no los para el analizador).
El tree-walker da error en los 50. Los otros dos no siempre:

**A. La VM contesta en 11**, donde el TW da error. Ejemplos: `"ab"$+ 5` → `ab5`;
`5 $++ "a"` → `5a`; `[1, 2, 3]$-[3..1]` → `[1, 2, 3]`; `[1, 2]$[1..9]` → `[1, 2]`;
`"aa"$~~["a":"b":-1]` → `bb`; `"ab"$? 5` → `#0`.

**B. `zyjs` contesta en 30.** Además de los de la VM: índices fuera de rango de
`$+[i]` que insertan igualmente, `$*` con cuenta no entera o negativa,
`$~~`/`$/`/`$??` con patrón o delimitador que no es cadena, `$-[..]` con
límites que no son enteros.

**C. El kind con que se captura no coincide.** De los 50 `-met`, sólo 2 dan el
mismo kind en los tres. El reparto más común: TW `##_`, VM `##Type` (27 casos).
El TW clasifica por palabras del mensaje (`zymbol_common::errkind`) y estos
mensajes no dicen «type»; la VM los lanza como `VmError::TypeError`.

**D. Texto distinto entre TW y VM en 37** de los que fallan en los dos.

### Qué hay que decidir

1. ¿Estas operaciones con un tipo equivocado **son error** (lo que hace el TW)
   o tienen significado (`"ab"$+ 5` → `ab5`, lo que hacen VM y `zyjs`)?
2. ¿De qué **familia** es un operando de tipo equivocado en una operación `$`:
   `##Type` (VM) o `##_` (TW)?

Sin esas dos respuestas, arreglar sería elegir por el autor.

### Decidido — 2026-09-15

1. **Familia (D1):** un operando del **tipo** equivocado es `##Type`, en los
   tres motores. El TW deja de clasificar estos casos por las palabras del
   mensaje.
2. **¿Error o significado? (D2):** las colecciones son **tolerantes**. En
   palabras del autor:

   > «Creo que las colecciones deben de ser mas flexibles, si a cada borde nos da
   > un error seran inutilizables en el tiempo ya que son sistemas dinamicos, que
   > creceran y seatortaran con el paso de las repeticiones y si son tan
   > extrictos no tendran sentido para muchas casuisticas. Asi que me parece
   > correcto que se deban controlar por validas estos retornos realizando los
   > cambios de tipos y permitiendo las tolerancias del espacio acotado a los
   > valores que tengamos. asi como permitir busquedas de valores en texto.»

   Es un **principio, no todavía una tabla.** Antes de tocar un motor se
   escribe, forma por forma, qué devuelve cada una de las 50 (conversión de
   tipo, recorte al espacio acotado, búsqueda en texto, o error donde ninguna
   tolerancia tiene sentido, por ejemplo donde chocaría con `COL-3`), y el autor
   la valida. Las celdas `expect = "error"` de este eje cambian su verde con esa
   tabla, no antes. Y `LLM.md` § 9 («type/arity mistakes raise») deja de ser
   cierto para estas formas: se corrige cuando la tabla esté validada.

### Corregido — 2026-09-22 (paso G1)

El paso 4.3 hizo estrictos a la VM y a `zyjs`, y al hacerlo **convirtió celdas
de comportamiento en celdas de familia**: 22 de este eje y 1 de `runtime-index-nav`
pasaron a diferir sólo en el kind, porque su sitio en el tree-walker seguía
construyendo `RuntimeError::Generic` y el clasificador por palabras
(`zymbol_common::errkind`) no encontraba «type» en el mensaje, así que contestaba
`##_`.

**Qué se midió antes de tocar.** Las 23 celdas `-met`, corriendo el programa
generado en los tres motores: el TW contestaba `##_` en las 23, y la VM y `zyjs`
coincidían entre sí en las 23 — `##Type` en 17, `##Index` en 6. Los 6 `##Index`
son todos «el tipo es Int y el valor no vale» (`-1`, `0`, `start > end`), que es
lo que D1 manda. Después, cada texto se buscó en el crate del tree-walker: **23
textos, 23 sitios, ninguno duplicado** — 17 en `collection_ops.rs`, 6 en
`string_ops.rs`, todos de la forma `RuntimeError::Generic { message, span: op.span }`,
ninguno con la forma abreviada de campo.

**Qué se cambió.** Esos 23 sitios pasan a `RuntimeError::kinded(kind, message, span)`,
que **envuelve** el error en vez de añadirle un campo: el texto impreso no cambia,
y por eso `zyq consensus`, `zyq expect` y el inventario de mensajes no ven nada.

**Resultado.** 23 celdas en verde, ninguna roja nueva; la matriz completa pasó de
**76 a 53 ids rojos**. `runtime-collection-ops` de 75 a 97 de acuerdo,
`runtime-index-nav` de 38 a 39.

### Qué lo sujeta

`axes/runtime-collection-ops.toml`: 50 celdas `expect = "error"` y 50 `-met`.
97 de 103 verdes; las 6 rojas que quedan son de texto o de comportamiento
(`cannot-index-into-during-deep-update` y su `-met`,
`named-tuple-update-index-must-be-an`, `tuple-update-index-must-be-an-integer`,
y dos `WORDING`), y son del grupo D del plan.

---

## GLB-012 — Índices y navegación con un valor inválido: `zyjs` contesta donde los Rust fallan, y el kind se reparte entre `##_`, `##Index` y `##Type`

**Estado:** **cerrado el 2026-09-22 (pasos G1 y G2).** Decidido el 2026-09-15 (tipo `##Type`, valor `##Index`; el rango invertido selecciona en orden descendente, D3). La familia se cerró en G1 anotando el sitio del tree-walker; D3 se completó en G2, llevando a la navegación la inversión que el paso 4.4 sólo había construido para el corte
**Encontrado por:** `axes/runtime-index-nav.toml`, paso C4 del plan de cobertura de diagnósticos, 2026-09-14
**Familia:** `GLB-011` (la misma pregunta de kind, en otra familia de operaciones)

### Qué se observa

22 diagnósticos de indexación, navegación y direccionamiento de diccionario,
provocados con el valor inválido entrando por un parámetro.

**A. `zyjs` no da error en 8** donde los dos Rust fallan: `$-[9]` sobre array,
cadena y tupla devuelve el valor intacto; `v[1>"a"]` sobre un array devuelve
vacío; `[1, 2][1.5]` devuelve vacío; `#(a: 1)$? 5` responde `#0`; un rango de
navegación invertido `v[1>3..1]` y uno con límite decimal devuelven `[]`.

**B. La VM no da error en 1**: `v[1>3..1]` → `[]`, donde el TW rechaza el
rango invertido.

**C. El kind no coincide en 11.** El TW dice `##Index` para «cannot index» e
«index must be an integer», y la VM `##Type` para los mismos; «a navigation step
is a position (Int) or a key» es `##_` en el TW y `##Type` en la VM; «range
indices in nav path must be positive» es `##_` en el TW y `##Index` en los otros
dos.

### Qué hay que decidir

Lo mismo que en `GLB-011`: la familia de un valor del **tipo** equivocado
usado como índice o paso — `##Type` o `##Index`. Y si un rango de navegación
invertido es error (TW) o vacío (VM, `zyjs`).

### Decidido — 2026-09-15

1. **Familia (D1):** la da **qué** está mal, no **dónde** aparece. Un índice o
   paso del tipo equivocado (`[1, 2][1.5]`, `v[1>"a"]`, indexar un Int, «a
   navigation step is a position (Int) or a key») es `##Type`. Un valor
   inválido del tipo correcto (una posición 0, negativa o fuera de límites,
   «range indices in nav path must be positive») es `##Index`.
2. **Rango invertido (D3): ni error ni vacío, sino selección descendente.** Es
   una forma **nueva**, que hoy no implementa ningún motor:
   - `[10, 20, 30, 40]$[3..1]` → `[30, 20, 10]`, y `v[1>3..1]` invierte igual,
     dando un array. El ejemplo del autor: `"hola mundo"$[-1..1]` →
     `odnum aloh`.
   - **Construye**: el slice sigue en la mitad «Consulta» de `COLLECTIONS.md`
     § 1, y `COL-1` no cambia. Guardar el resultado es `valor = valor$[-1..1]`.
   - **Borde:** sólo invierte un inicio que está **dentro** de los límites. Un
     inicio más allá del final da vacío, así que el modismo «el resto»
     `s$[p+1..-1]` sigue dando `""` cuando `p` es la última posición
     (`corpus/gaps/gap001_slice_arith_bounds.zy`).

Medido al preguntar: `$[3..1]` tiene el mismo reparto que `v[1>3..1]`. El TW
dice `slice start (2) cannot be greater than end (1)`, un texto que filtra el
índice interno que empieza en 0, y la VM y `zyjs` dan `[]`. `valor[-1..1]` falla
hoy de tres maneras: el TW dice `range indices in nav path must be positive
integers`, la VM `index 0 is invalid` y `zyjs` `Expected RBRACKET, got '..'`.
`$-[9]` y `#(a: 1)$? 5` de la parte A son operaciones `$`, así que entran en la
tabla de tolerancias de `GLB-011`.

### Corregido la familia — 2026-09-22 (paso G1)

De este eje quedaba **una** celda `-met` contestando `##_` en el tree-walker:
`a-dictionary-is-asked-about-a-key-met` (`#(a: 1)$? 5`). Su sitio,
`collection_ops.rs:284`, pasó a `RuntimeError::kinded("Type", …)` — el tipo es el
que está mal, D1 punto 1 — y la celda cerró. El método y la medida completa están
en [[GLB-011]], que es donde se anotaron los 23 sitios de una vez.

### Corregido el punto 2 (D3) — 2026-09-22 (paso G2)

El paso 4.4 construyó D3 para el **corte** y dejó fuera la **navegación**. Medido
al empezar G2: ningún motor hacía lo que D3 dice — el TW refusaba `v[1>3..1]` y
la VM y `zyjs` contestaban `[]`. El autor confirmó D3 tal como está escrita, así
que la inversión se llevó a los tres:

| | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| **antes** | error `invalid nav range 3..1 …` | `[]` | `[]` |
| **ahora** | `[30, 20, 10]` | `[30, 20, 10]` | `[30, 20, 10]` |

Cada motor por su camino: el tree-walker construye la lista de posiciones y la
recorre; el compilador de la VM cambió el incremento fijo del bucle por un
**paso** de +1 o −1 decidido en ejecución, y sale cuando `(i − fin) × paso > 0`,
una sola prueba que lee las dos direcciones porque el paso lleva el signo;
`zyjs` hace lo mismo en `evalNavPath`. Ninguno necesitó una instrucción nueva,
que era lo que [[GLB-048]] temía.

Comprobado además que coinciden en lo anidado y en las demás colecciones:
`m[3..1>3..1]`, `m[3..1>1..3]`, la tupla y la cadena dan lo mismo en los tres.

**Los bordes se leen como en el corte, no aparte.** Una posición fuera de la
colección se sigue refusando (`v[1>9..1]` da fuera de límites en los tres, igual
que `a$[9..1]`), y un límite 0 sigue siendo error. Lo que cambió del mensaje es
que perdió su segunda mitad: era `invalid nav range {}..{} — indices are 1-based
and start must be ≤ end`, y «start must be ≤ end» dejó de ser verdad. Ahora dice
`invalid nav range {}..{} — indices are 1-based`. La línea base de mensajes se
editó a mano, cerrando el viejo y abriendo el nuevo en su sitio.

### Corregido en `zyjs` lo que no es `$` — 2026-09-15 (paso 2.9)

`navGetAt` recibía el valor JavaScript ya sin tipo, y `v[0.5]` o `v["a" - 1]` eran
`undefined`, que se imprimía como una línea vacía. Ahora el tipo se mira donde aún
se tiene, con los textos del TW:
- índice simple: `index must be an integer, got Float`;
- paso de ruta: `a navigation step is a position (Int) or a dictionary key
  (String), got Float`;
- clave sobre algo que no es diccionario: `a String navigation step addresses a
  dictionary key, and this is ##[]`, con el nombre de tipo antiguo del TW
  (`twTypeName`), que el paso 3.5 unificará;
- límite de rango: `navigation index must be an integer, got Float`.

`runtime-index-nav` pasa de 8 `WRONG` a 5. Las que quedan son `$-[9]` sobre array,
cadena y tupla, y `$?` con una clave Int (tabla de `GLB-011`), y el rango invertido
(D3, paso 4.4).

### Qué lo sujeta

`axes/runtime-index-nav.toml`: 22 celdas `expect = "error"` y 22 `-met`. 18
verdes, 26 rojas.

---

## GLB-013 — Conversiones y formatos con un valor inválido: `zyjs` inventa un número, y el kind vuelve a ser `##_` contra `##Type`

**Estado:** abierto — **A corregido en `zyjs` el 2026-09-15** (paso 2.8); la parte del kind decidida (`##Type`), pendiente en 4.1
**Encontrado por:** `axes/runtime-format-convert.toml`, paso C5 del plan de cobertura de diagnósticos, 2026-09-14

### Qué se observa

13 programas (14 diagnósticos: `0x|"zz"|` da uno por motor Rust).

**A. `zyjs` no da error en 6** y contesta un valor que nadie calculó:
`0x|1.5|` → `0x0001`; `0x|"zz"|` → `0x0000`; `0x|"D800"|` (un sustituto, no un
carácter) → `0x0000`; `#,|"x"|` → `0`; `#.2|#1|` → `0`; `#!2|#1|` → `0`.

**B. El kind no coincide en 8:** `###`, `##!`, `0x||` con un Float, `#.n||` con
una cuenta decimal inválida, `#,||`, `#.2||` y `#!2||` con un Bool — el TW dice
`##_`, la VM `##Type`.

Donde los tres coinciden: `### 1.0e300` es `##Range` y `0x|"zz"|` es `##Parse`.

### Qué hay que decidir

La familia de un valor del tipo equivocado — la pregunta de `GLB-011`. Lo de
`zyjs` no tiene decisión pendiente: los dos Rust fallan, y un `0` inventado es la
respuesta que ningún motor debería dar.

### Decidido — 2026-09-15

**Familia (D1):** los 8 de la parte B son `##Type` en los tres motores.

### Corregido A en `zyjs` — 2026-09-15 (paso 2.8)

La medición destapó más de lo que decía la ficha: **`0x|"41"|` significaba otra
cosa en `zyjs`**. Los dos Rust leen la cadena como un código escrito en la base del
operador y devuelven el carácter (`A`); `zyjs` la leía como un número decimal e
imprimía su hexadecimal (`0x0029`), y convertía en 0 lo que no podía leer. Ahora
sigue `data_ops.rs`: quita los prefijos, lee los dígitos en su base
(`failed to parse 'zz' as hexadecimal number`, que es `##Parse`), rechaza un valor
fuera de rango (`character code must be in range 0..0x10FFFF, got 1114112`, el
caso F de `GLB-014`) y un sustituto (`invalid Unicode character code: 55296`), y
rechaza un Float o un Bool con el texto del TW. En los formatos, una cadena que no
es un número o un Bool son error con las palabras de cada operador del TW (`format
expressions only work with numbers`, `cannot convert string 'x' to number for
rounding`, `round/truncate expressions only work with numbers or numeric
strings`). La cadena numérica queda como está, porque el TW y la VM no coinciden
(`GLB-029`). `runtime-format-convert` pasa de 6 `WRONG` a 0. Ningún documento ni
ejemplo usaba `0x|"…"|`.

### Qué lo sujeta

`axes/runtime-format-convert.toml`: 13 pares. 7 verdes, 19 rojas.

---

## GLB-014 — Rangos, pasos y `@~` con valores inválidos: la VM entra en bucle infinito con paso 0, y el bucle que desestructura un rango sólo existe en el TW

**Estado:** abierto — **A, B, E, F y H corregidos el 2026-09-15** (pasos 1.3, 1.4, 2.7 y 2.8); C, D y G **decididos** (error estático; `##Type`), pendientes en F4/F5
**Encontrado por:** `axes/runtime-loops-ranges.toml`, paso C6 del plan de cobertura de diagnósticos, 2026-09-14
**Gravedad:** alta por la parte A: un bucle infinito donde los otros dos motores fallan

### Qué se observa

**A. La VM entra en bucle infinito con paso 0.** `@ i:1..9:v` con `v = 0`
imprime `1` sin fin; el TW y `zyjs` dan error. En ZyDDT la celda
`step-must-be-positive-got-met` queda sin veredicto por timeout (30 s por
corrida, dos veces).

**B. La VM acepta límites y pasos decimales:** `@ i:1.5..3` imprime `1.5 2.5`;
`@ i:1..9:1.5` imprime `1 2.5`. `zyjs` los trunca: `1 2`. El TW da error. Medido el 2026-09-15: con un paso
decimal `0.0` o negativo (`-2.5`) la VM **tampoco termina**; eso se cierra con B,
porque depende de qué se haga con un paso decimal.

**C. El bucle que desestructura un rango sólo existe en el tree-walker.**
`@ (a, b):1..v { }`: la VM responde `unsupported construct: range outside loop`
al compilar y `zyjs` `Expected LBRACE, got '..'` al parsear.

**D. Un rango suelto (`v..3` fuera de un bucle)** falla en tres momentos: en
ejecución en el TW, al compilar en la VM, al parsear en `zyjs`. Misma familia
que `GLB-008`: un rechazo que debería ser uno solo y estático.

**E. `zyjs` no valida `@~`:** `@~ "x"` y `@~ -1` no dan error, y además avisa
`unused variable 'v'` porque el analizador no cuenta el operando de `@~` como
uso (familia `ZYJS-018`).

**F. `zyjs` no valida los códigos de carácter:** `0x|"110000"|` → `0x1ADB0`
donde los dos Rust fallan. **Y un patrón de rango de `??` sobre una cadena** da
`b` en `zyjs` (cae al comodín) donde los Rust fallan.

**G. Kinds y textos:** TW `##_` contra VM `##Type` en `@~`, iteración y patrón de
rango; textos distintos en `@~ -1` (`duration` / `ms`) y en paso 0.

**H. `zyjs` acepta un paso negativo** (medido el 2026-09-15, paso 1.3). `@ i:1..3:v`
con `v = -1` imprime `1 2 3`, y con `-2.5` imprime `1`; los dos Rust rechazan
(`step must be positive, got -1`) y `LLM.md` dice *«a negative step is a runtime
error»*. Con 0 rechaza, pero con otra frase: `Loop step cannot be zero`. Celda
nueva `runtime-loops-ranges/step-must-be-positive-got-negative`, roja por `zyjs`.

### Qué hay que decidir

C y D sí: si `@ (a, b):rango` es forma del lenguaje (sólo la ejecuta el TW) y
dónde se rechaza un rango suelto. A, B, E y F no necesitan decisión: los dos Rust
—o el TW— rechazan.

### Decidido — 2026-09-15

1. **C y D (D4): error estático, los dos**, en el analizador, en los tres
   motores y con el mismo texto, de modo que `zymbol check` lo ve. Un patrón en
   un bucle sobre un rango y un rango fuera de un bucle, slice, navegación o
   patrón son sintácticos, así que el rechazo no depende del flujo y no tiene el
   falso positivo de `GLB-008`.

   La medición del 2026-09-15 corrige la parte C: el TW **tampoco** ejecuta
   `@ (a, b):1..v`. Lo parsea y falla en el primer elemento con
   `tuple pattern '( … )' requires a tuple, got ###`. Ningún patrón desestructura
   un Int, así que esa forma nunca puede salir bien en ningún motor.
2. **G (D1):** los kinds de `@~`, de la iteración y del patrón de rango con un
   valor del tipo equivocado son `##Type`.

### Corregido A en la VM — 2026-09-15

`compile_range_loop` copiaba el paso a su registro y sumaba su magnitud en la
dirección del rango sin mirarlo. Con 0 no avanzaba nunca, y con un paso
**negativo** —también escrito como literal, `@ i:1..3:-1`, algo que la ficha no
había medido— se alejaba del final para siempre. Instrucción nueva
`LoopStepCheck(reg)`: si el paso es un Int menor o igual que 0, lanza
`step must be positive, got {n}`, el texto y el kind (`##_`) del TW. No se emite
cuando el paso es un literal entero positivo. La celda base pasa de «sin
veredicto» a `WORDING` (sólo difiere la frase de `zyjs`) y la `-met` a `AGREE`.
`zyq consensus` sigue en 660 de acuerdo y 0 divergiendo.

### Corregido en `zyjs` — 2026-09-15 (paso 2.7)

- **Bucle de rango:** `zyjs` tomaba `.v` de cualquier valor y daba la vuelta en
  silencio a un paso negativo. Ahora sigue las comprobaciones y el orden del TW:
  `step must be an integer, got Float`, `step must be positive, got -1` (también
  con 0, que antes decía `Loop step cannot be zero`) y `range bounds must be
  integers, got Float and Int`. La magnitud del paso va en la dirección del rango.
- **`@~`:** `@~ requires integer milliseconds, got ##"` y `@~ requires non-negative
  duration, got -1`, como el TW; el checker cuenta el operando como uso y deja de
  avisar `unused variable 'v'`.
- **Patrón de rango:** Ints contra Int y Chars contra Char, o `range pattern type
  mismatch`; una cadena caía al comodín.
- **Iteración:** el texto del TW, `can only iterate over ranges, arrays, strings,
  tuples and dictionaries, got Bool`.

Los textos siguen la plantilla del TW con el nombre del tipo, que es lo que dejará
el paso 3.5 y lo que casa con el inventario. `runtime-loops-ranges` pasa de 11
`WRONG` a 4: la del código de carácter (paso 2.8) y las tres de desestructurar un
rango (D4, F5). Las `WORDING` y las `-met` que quedan son la diferencia de texto y
de kind entre el TW y la VM (pasos 3.5 y 4.1). Ningún programa del workspace usa
pasos negativos ni decimales.

### Decidido B y corregido en la VM — 2026-09-15

**Decisión del autor:** un límite o un paso decimal es **error `##Type`**. Un
bucle no es una colección, así que la tolerancia de `GLB-011` no lo alcanza, y
`zyjs` deja de truncar.

`LoopStepCheck` rechaza también un paso que no es Int, y la instrucción nueva
`LoopBoundsCheck(inicio, fin)` rechaza unos límites que no son los dos Int. Se
comprueba en el orden del TW, primero el paso y luego los límites, y la
comprobación de límites no se emite cuando los dos se saben Int al compilar.
Barrido de tipos, los tres motores dentro de `!?`:

| caso | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| inicio `1.5` | error `##_` | error `##Type` | `1 2` |
| fin `3.5` | error `##_` | error `##Type` | `1 2 3` |
| paso `1.5` | error `##_` | error `##Type` | `1 2 4 5 7 8` |
| paso `0.0` | error `##_` | error `##Type` (antes, sin fin) | `Loop step cannot be zero` |
| inicio `1.5`, paso `-2.5` | error `##_` | error `##Type` (antes, sin fin) | `1 4 6 9` |
| inicio `"a"` | error `##_` | error `##Type` | ninguna vuelta, sin error |

La VM toma ya la rama del TW en los seis. Quedan el kind del TW (paso 4.1), los
textos (el TW enseña `Float(1.5)`, familia de `ZYTW-004`) y `zyjs` (F2). Las
siete aplicaciones LDV mantienen sus goldens.

### Qué lo sujeta

`axes/runtime-loops-ranges.toml`: 11 pares (12 diagnósticos: `@~ -1` da uno por
motor Rust). Tres `-met` esperan `warn`: el aviso de dirección de rango con un
límite variable es cierto y no es lo que preguntan.

---

## GLB-015 — Llamadas y funciones de orden superior con algo que no es lo que necesitan: kinds `##_` contra `##Type`, y un `$<` con lambda de un parámetro que la VM y `zyjs` aceptan

**Estado:** abierto — la parte del kind **decidida el 2026-09-15** (`##Type`); **A y B corregidos el 2026-09-15** (pasos 1.10 y 2.10); el kind, pendiente en 4.1
**Encontrado por:** `axes/runtime-functions-hof.toml`, paso C7 del plan de cobertura de diagnósticos, 2026-09-14

### Qué se observa

12 diagnósticos provocados.

**A. `$<` con una lambda de un solo parámetro:** `[1, 2]$< (0, x -> x)` — el TW
da error («reduce lambda requires 2 parameters»), la VM y `zyjs` responden `0`.

**B. `zyjs` acepta un pipe hacia un número:** `5 |> v` con `v = 5` responde `5`.

**C. El kind:** en 9 de los 12 el TW dice `##_` y la VM `##Type` (`map`/`filter`/
`reduce`/`sort` sobre algo que no es array ni lambda, llamar a algo que no es
función). En «lambda expects N arguments» y «member function calls» los tres
dicen `##_`.

**D. Textos distintos entre TW y VM en 8** (la VM dice `this needs Function and
got Int` donde el TW nombra la operación).

### Decidido — 2026-09-15

**A:** un `$<` con una lambda de un solo parámetro es un **error de aridad**, no
un borde de la colección, así que no entra en la tabla de tolerancias de
`GLB-011`. Se corrige en la VM en el paso 1.10 y en `zyjs` en la F2.

### Corregido A en la VM — 2026-09-15

`ArrayReduce` llamaba al callable con `(acumulador, elemento)` sin mirar su
aridad, y una lambda de un parámetro devolvía el valor inicial. Ahora, antes de
mirar el array y como hace el TW, una `Function` o una `Closure` cuya aridad no
es 2 lanzan `reduce lambda requires 2 parameters (accumulator, element), got {n}`.
La aridad de una `Closure` no cuenta sus capturas. Barrido TW contra VM,
idéntico: lambda y función con nombre de 1, 2, 3 y 0 parámetros, array vacío y
una lambda con captura (`R 23`). `zyjs` devuelve todavía `0` o `1`.

### Corregido A y B en `zyjs` — 2026-09-15 (paso 2.10)

- **A:** `$<` evalúa el valor inicial y después la lambda, en el orden del TW, y
  una lambda escrita en Zymbol cuya aridad no es 2 lanza `reduce lambda requires 2
  parameters (accumulator, element), got 1`. Las nativas no declaran parámetros y
  no se comprueban. `evaluation-order` sigue en 13 de 13.
- **B:** un pipe cuyo destino no es una llamada escrita en su sitio (`f(_, 1)`)
  tiene que dar una función; si no, `pipe operator requires a callable function or
  lambda`. `5 |> v` con `v = 5` respondía `5`.

`runtime-functions-hof` pasa de 3 `WRONG` a 1, la del comparador (`GLB-024`, paso 2.13).

**C (D1):** los 9 son `##Type` en los tres motores: algo que no es array ni
lambda, o llamar a algo que no es función.

### Qué lo sujeta

`axes/runtime-functions-hof.toml`: 12 pares. 2 verdes, 22 rojas.

---

## GLB-016 — Un `??` sin brazo que case: el TW aborta, la VM y `zyjs` devuelven `##_` en silencio

**Estado:** abierto — sin decisión pendiente: `LLM.md` dice *«an unmatched `??` aborts»*. **corregido el 2026-09-15** en los tres motores (pasos 1.1, 1.2 y 2.6)
**Encontrado por:** `axes/runtime-match-patterns.toml`, paso C8 del plan de cobertura de diagnósticos, 2026-09-14
**Gravedad:** **alta**: un valor que nadie calculó sigue su camino por el programa, sin error ni aviso

### Qué se observa

```zymbol
t(v) {
    <~ ?? v { 1 => "uno" }
}
>> t(2) ¶
```

| motor | |
|---|---|
| `zytw` | `Runtime error: no pattern matched in match expression` |
| `zyvm` | una línea vacía — el `??` vale `##_` |
| `zyjs` | una línea vacía |

Y la segunda mitad, en el mismo paso: un `??` cuyos brazos dan valores, usado
como sentencia, lo avisa el tree-walker **en ejecución**
(`warning: match expression returns values but result is unused`) y los otros
dos no dicen nada. Un aviso de ese tipo es del analizador, no de un motor.

### Qué lo sujeta

`runtime-match-patterns/no-pattern-matched-in-match-expression` (+ `-met`) y
`runtime-match-patterns/match-with-values-used-as-a-statement`.

### Corregido en la VM — 2026-09-15

`compile_match_expr` (`zymbol-compiler`) cargaba `##_` en el destino y, si
ningún brazo casaba, caía al final. Ahora, cuando el `??` no tiene comodín,
emite `RaiseError("no pattern matched in match expression")` detrás del último
brazo: el mismo texto que el TW, y el mismo kind (`##_`) en la celda `-met`. La
forma de sentencia pasa por el mismo camino, igual que en el TW, donde también
aborta. `zyq consensus` sigue en 660 de acuerdo y 0 divergiendo.

### Corregido en `zyjs` — 2026-09-15 (paso 2.6)

El `Match` sin brazo que case devolvía `mkUnit()`; ahora lanza `no pattern matched
in match expression`, y el nodo lleva su línea. El `Checker` da el aviso de un
`??` usado como sentencia con algún brazo `=> valor`, con el texto y la ayuda del
analizador Rust, bajo el código `W_UNUSED_MATCH`, traducido en los catálogos
inglés y español. `runtime-match-patterns`: 7 de 7 en `AGREE`.

### Corregido el aviso en los dos Rust — 2026-09-15

El aviso lo imprimía el TW con `eprintln!` al **ejecutar** la sentencia, y sólo
si esa línea llegaba a correr. Ahora lo da el analizador
(`zymbol-semantic`, `Statement::Match`) para cualquier `??` sentencia con algún
brazo `=> valor`: el TW, la VM, `zymbol check` y el LSP lo ven antes de
ejecutar, con `help:` y posición. Se comprobó dentro de una función, de una
lambda de bloque y de un bucle, y que un `??` con brazos de bloque no lo dispara.
Ningún fichero de las aplicaciones LDV ni de `web/examples` lo dispara. El
inventario de mensajes cambia una línea por otra: el mismo texto, ya sin el
prefijo `warning:` dentro de la plantilla. Los dos patrones
de desestructuración del mismo paso coinciden en los tres motores.

---

## GLB-017 — Módulos, subscripts y shell: la VM pasa una función al shell, el TW enseña un `Located { … }` de Rust, y cada motor cuenta distinto un módulo que no compila

**Estado:** abierto — **A y G corregidos el 2026-09-15** (pasos 1.5 y 1.5b); **B corregido el 2026-09-16** (paso 3.3); C–F e I abiertos
**Encontrado por:** `axes/runtime-modules-scripts.toml`, paso C9 del plan de cobertura de diagnósticos, 2026-09-14

### Qué se observa

**A. La VM manda una función al shell.** `<\ "echo " g \>` con `g` una lambda:
el TW rechaza (`cannot use function in bash command interpolation`); la VM
convierte la función en texto y ejecuta el comando, que falla en `sh` —
`sh: 1: Syntax error` por stderr— con **estado 0**.

**B. El TW enseña la estructura de Rust** cuando falla un subscript:
`error executing falla.zy: Located { message: "division by zero", file:
"falla.zy", line: 1, column: 0 }`. La VM dice `Runtime error: division by zero`.

**C. Un subscript que no compila:** el TW resume (`1 lexer errors in lexico.zy`,
`1 parser errors in sintaxis.zy`) y la VM reenvía el diagnóstico completo del
subscript.

**D. Un módulo que no compila** se cuenta distinto: con una cadena sin cerrar,
el TW informa `1 lexer error(s)`, la VM `2 parse error(s)` y `zyjs` sólo el
primer error, sin la cabecera.

**E. Texto de «función no exportada» como valor de `_err`:** TW
`function 'priv' not exported from module 'o'`, VM y `zyjs`
`module 'o' does not export function 'priv'`.

**F. `v.f(1)` sobre un número:** TW `undefined module alias: 'v'`; VM y `zyjs`
`the dot reaches a dictionary key, and this is ###`.

**G. Una colección dentro de `<\ \>`** (medido el 2026-09-15, paso 1.5). El TW
une los elementos con espacios; la VM escribía su representación:

| valor | `zytw` | `zyvm` |
|---|---|---|
| `[1, 2]` | `1 2` | `[1, 2]` |
| `(3, "x")` | `3 x` | `(3, x)`, y `sh` falla: `Syntax error: "(" unexpected` |
| `#(k: 1, j: "z")` | `1 z` | nada: `sh` lee `#(…` como comentario |

**Ningún documento dice cuál es la forma correcta**, así que no se toca sin
decisión. La celda `runtime-modules-scripts/bash-collection-interpolation`
pregunta sólo que coincidan (`expect = "ok"`), y su verde no elige entre las dos.

*Decidido el 2026-09-15:* **se une con espacios**, lo del TW. Un argumento de
shell son palabras, y la representación de Zymbol rompe `sh`.

### Corregido A en la VM — 2026-09-15

`BashExec` convertía cada valor con `to_string_repr()` y mandaba `<lambd/1>` al
shell. Ahora, antes de construir el comando, rechaza con
`cannot use function in bash command interpolation`, el texto y el kind (`##_`)
del TW, un valor que sea o contenga una función o una lambda a cualquier
profundidad (`[g]`, `(1, k)`, `#(f: g)`), igual que el `value_to_bash_str`
recursivo del TW. Las dos celdas pasan a `AGREE [2/3]` (`zyjs` excluido por
`BASH_EXEC`).

### Corregido G en la VM — 2026-09-15

`BashExec` usa ahora `shell_text`, el `value_to_bash_str` del TW portado: un
array, una tupla o un diccionario son sus elementos unidos con espacios a
cualquier profundidad, y el resto conserva su texto de siempre. Barrido TW contra
VM, idéntico en todo: Bool `#1`, Float `3.0` → `3`, `1.0e20`, Char, Unit vacío,
`[[1, 2], [3]]` → `1 2 3`, `(1, (2.0, "a b"))` → `1 2 a b`, un diccionario con
colecciones dentro, un error como valor (`##Div(division by zero)`) y el modo de
cifras `#०९#`, que en el shell sigue en ASCII. `GUIDE.md` § BashExec lo documenta.
La celda pasa a `AGREE [2/3]`.

### Corregido B — 2026-09-16 (paso 3.3)

Medido antes, B no era sólo del TW: los dos imprimían mal.

| motor | antes |
|---|---|
| `zytw` | `Runtime error: error executing ./sub/falla.zy: Located { message: "division by zero", file: "./sub/falla.zy", line: 1, column: 0 }` y `--> main.zy:4` |
| `zyvm` | `Runtime error: Runtime error: division by zero`, `--> ./sub/falla.zy:1` y `--> main.zy:4` |

Las dos arquitecturas explican la diferencia: el TW ejecuta el subscript dentro
del mismo proceso, con un intérprete que captura la salida, y la VM lo lanza como
un proceso aparte y toma como mensaje lo que ese proceso escribió en stderr —el
informe de la CLI hija, con su `Runtime error:` y su `-->`—.

La corrección no elige entre las dos: el TW formatea el error del subscript **como
lo escribe la CLI**, el mensaje y su línea, que es exactamente el texto que la VM
reenvía. Los dos dicen ahora, byte a byte:

```
Runtime error: Runtime error: division by zero
  --> ./sub/falla.zy:1
  --> main.zy:4
```

y el `_err` de la celda `-met` es el mismo en los dos. El `Runtime error:` repetido
es el informe de la hija anidado en el de la madre; si debe decirse de otra forma
es cosa de C–F, que no se tocan.

`runtime-modules-scripts/subscript-runtime-error` pasa a `AGREE [2/3]`.

**I. Un subscript con avisos que falla** (medido en el paso 3.3). Como la VM
reenvía todo el stderr de la hija, los avisos del subscript entran en el error y
en `_err`: `##Div(warning: unused variable 'aviso' … Runtime error: division by
zero …)`. El TW, que no analiza el subscript, informa sólo del fallo. Misma raíz
que C. Celda `subscript-with-warnings-that-fails`, que sólo pide que coincidan,
roja.

### Qué lo sujeta

`axes/runtime-modules-scripts.toml`: 14 celdas, 4 verdes, 10 rojas, más
`bash-collection-interpolation` (G), añadida el 2026-09-15, y
`subscript-with-warnings-that-fails` (I), añadida el 2026-09-16. Los errores
de carga de módulo no tienen `-met`: una importación va antes de cualquier
sentencia y no hay `!?` que la rodee.

---

## GLB-018 — Entrada y salida: la VM y `zyjs` no interpolan el prompt de `<<`, ignoran un hueco inválido de `>>~`, y `zyjs` abre `>>|` sin terminal

**Estado:** abierto — **A decidido y corregido en los tres motores el 2026-09-15** (paso 1.6); **B y C corregidos el 2026-09-15** (pasos 1.7 y 2.11); **H decidido y corregido el 2026-09-15** (paso 1.11)
**Encontrado por:** `axes/runtime-io.toml`, paso C12 del plan de cobertura de diagnósticos, 2026-09-14

### Qué se observa

**A. El prompt de `<<` no se interpola en la VM ni en `zyjs`.**
`<< "Nombre {nadie}: " n` — el TW interpola el prompt y falla porque `nadie` no
existe; la VM y `zyjs` imprimen **`Nombre {nadie}: `** literal. Con una variable
que sí existe, esos dos motores tampoco la sustituirían.

> **Medición del 2026-09-15 (paso 1.6), que corrige lo de arriba.** Con una
> variable que existe, global o local de función, la VM y `zyjs` **sí**
> interpolan el prompt (`Hola Ana: `, `Local 7: `). Sólo divergen con un nombre
> que **no existe**. Y en una cadena normal los tres motores hacen lo que hacen
> la VM y `zyjs` en el prompt: `>> "x {nadie}" ¶`, `s = "y {nadie}"` y
> `<~ "z {nadie} {v}"` imprimen `{nadie}` literal, sin error y sin aviso, y
> `zymbol check` no dice nada. **Ningún documento dice qué pasa con un nombre
> que no existe dentro de `{…}`** (`GUIDE.md` § String interpolation). El error
> del TW en el prompt no es «lo documentado», sino la única excepción, así que
> A **necesita decisión**: ¿error estático, error en ejecución o texto literal,
> en toda cadena y en todo prompt?

**H. Una función con nombre dentro de `{…}`** (medido el 2026-09-15, paso 1.6).
`f(p) { <~ p }` y `>> "f={f}" ¶`: los dos Rust imprimen **`f={f}`** tal como está
escrito, y `zyjs` `f=<funct/1>`. Una lambda (`"{g}"`) y la yuxtaposición
(`>> f`) dan `<…/1>` en los tres. El nombre existe, así que la regla de A no lo
alcanza. Celda `runtime-io/named-function-in-interpolation`, que pregunta sólo
que coincidan.

*Decidido el 2026-09-15:* **se interpola** (`f=<funct/1>`), como la lambda, la
yuxtaposición y `zyjs`: `{f}` se lee como `f`. Cambian los dos Rust (paso 1.11).

*Corregido el 2026-09-15 (paso 1.11).* El TW busca, tras las variables, la
función con nombre, igual que `eval_identifier`. La VM compila el nombre por el
camino del identificador (`compile_expr`), el que ya resuelve capturas y
funciones hermanas de un módulo (BUG-ZYB-005), en vez de caer a la rama del texto
literal. Los tres motores coinciden en `{f}` a nivel de archivo, dentro de una
función, dentro de una lambda y con una función privada hermana dentro de un
módulo. La celda pasa a `AGREE`.

**B. `>>~` con un hueco que no es entero:** `>>~ ("a", 1) > "x"` — el TW rechaza;
la VM imprime `x1` como salida normal; `zyjs` no da error y además avisa
`unused variable 'v'` (su analizador no cuenta los huecos de `>>~` como uso,
familia `ZYJS-018`).

**C. `>>|` sin terminal:** el TW y la VM fallan (`failed to enable raw mode`),
como dice `LLM.md` (*«errors without a tty»*); `zyjs` entra y sale del bloque.

### Corregido B y C en `zyjs` — 2026-09-15 (paso 2.11)

- **B:** un hueco escrito de `>>~` tiene que ser Int, comprobado al evaluarlo, con
  el texto del TW (`>>~ slot expects Int, got a`); un hueco solitario que no es una
  tupla se trata como hueco escrito. El checker cuenta los huecos como uso y deja
  de avisar `unused variable 'v'`.
- **C:** sin pantalla no hay `>>|`. El motor lanza `failed to enable raw mode: …`
  cuando no tiene contexto de terminal, o cuando el contexto no puede tomar la
  pantalla. El adaptador de pruebas `web/tests/run_one.mjs` le daba a `zyjs` una
  TUI de imitación (secuencias ANSI, como la CLI) cuyo `enter()` no hacía nada;
  ahora falla cuando stdin o stdout no son una terminal, que es lo que le pasa a la
  CLI por una tubería. El playground tiene su TUI real y no cambia. La celda queda
  en `WORDING` sólo por el detalle del sistema operativo (`No such device or
  address (os error 6)` frente a `not a terminal`), y su `-met` en `AGREE`.

### Corregido B en la VM — 2026-09-15

La VM metía los huecos en una tupla y los leía con `vm_extract_pos`, que
convierte en «sin tocar» todo lo que no es Int, así que `>>~ ("a", 1) > "x"`
imprimía `x1`. Instrucción nueva `OutputSlotCheck(reg, admite_tupla)`, emitida
detrás de cada hueco escrito en cuanto se evalúa, en el orden del TW. Rechaza con
`>>~ slot expects Int, got …`, el texto y el kind (`##_`) del TW, y sólo un hueco
solitario puede llevar la tupla densa (`>>~ p > …`), que sigue ignorando lo que no
es Int, igual que el TW. Barrido TW contra VM, idéntico byte a byte con las
secuencias ANSI: String, Float, Bool, array y `##_` rechazados en el primer y en
el cuarto hueco, la tupla densa con un String dentro y la forma dispersa
`(,,,196)`. Pasan `tui` (3 de 3 por pty) y las siete aplicaciones. Las dos celdas
quedan rojas sólo por `zyjs`.

### Decidido A y corregido — 2026-09-15

**Decisión del autor:** `{nombre}` de un nombre que no es nada (ni variable, ni
función, ni alias de módulo) es **error estático**, en toda cadena y en todo
prompt, en los tres motores.

- **Rust** (`zymbol-semantic`): `check_interpolated_name` en `type_check.rs`, para
  `Literal::InterpolatedString` y para `InputPrompt::Interpolated`. Un nombre que
  sí existe se lee como un identificador, también para MEM-2: `"{k}"` con `k` de
  archivo dentro de una función es `'k' is read from outside this function`,
  igual que `k` suelto. Antes seguía imprimiendo `{k}`. El escáner de nombres es
  uno solo (`interpolation.rs`), compartido con `variable_analysis`, con la regla
  de identificador del lexer.
- **`zyjs`** (hecho en el mismo paso, no en la F2): el `Checker` da
  `E_VAR_INTERP` con el mismo texto y la misma ayuda, y los catálogos inglés y
  español del playground lo traducen. Los nodos `Literal` de cadena llevan ya su
  línea, que antes no tenían. Si se hubiera dejado para la F2, el inventario de
  mensajes habría fallado con dos textos nuevos de un solo lado, y la forma de
  `reject/` no se habría podido añadir.

**Impacto medido antes de dar el paso por hecho.** `zymbol check` sobre 1380
`.zy` del workspace dio **un** fichero: `corpus/modules_scope/interp_global_const.zy`,
cuyas dos últimas líneas afirmaban a propósito la forma literal. Salen del
corpus, con la razón escrita, y la forma pasa a `reject/variables/02_interpolate_undefined.zy`
y a `refusal/undefined-name-in-string-interpolation`. El barrido no veía los
ejemplos de los documentos. El verificador de `GUIDE.md` encontró dos cadenas
ODBC, `"Driver={SQLite3};…"`, que funcionaban gracias al silencio; el
proyecto ya tenía escrito que eso era suerte (`corpus/stdlib/README-odbc.md`,
`WINDOWS_V009.md`), y ZyBank, SPRE y `DESIGN_STD_DB.md` usan `\{…\}`. Se
migraron esas dos y el snippet `dbconnect` de `vscode/`, que además cortaba su
placeholder en la primera `}`. Los manuales (66), el skill publicado y los
ejemplos del playground siguen en verde.

El mensaje de ejecución `undefined variable in input prompt` del TW queda como
red de seguridad inalcanzable (`messages/queue/runtime.tsv`). Las celdas
`runtime-io/undefined-variable-in-input-prompt` y su `-met` —que ahora afirma el
rechazo, porque un error estático no lo atrapa ningún `!?`— pasan a `AGREE`.
`GUIDE.md` § String interpolation documenta la regla.

Dos más se reprodujeron a mano, sin celda posible (ZyDDT no da stdin ni cierra
stdout): un stdin con UTF-8 inválido es `input read error` en el TW y **fin de
entrada** en la VM; un stdout cerrado es `io error: Broken pipe` en el TW.

### Qué lo sujeta

`axes/runtime-io.toml`: 7 celdas, 1 verde (fin de entrada, igual en los tres), 6
rojas.

---

## GLB-019 — Operadores con un operando inválido: la VM responde `!5` → `#0` y `+"a"` → `a`, y dos motores redeclaran una constante

**Estado:** **cerrado el 2026-09-21** — A y B el 2026-09-15 (pasos 1.8, 1.9 y 2.12); **C con D5 (F5)**: `C := 1` seguido de `C := 2` es error estático en los tres analizadores, y `check` lo ve
**Encontrado por:** `axes/runtime-operators.toml`, paso C13 del plan de cobertura de diagnósticos, 2026-09-14

### Qué se observa

El valor inválido sale de `json::decode`, porque por parámetro el analizador lo
rechaza antes (infiere el tipo del parámetro por su uso).

**A. `!v` con `v = 5`:** TW y `zyjs` rechazan (`logical NOT requires boolean
operand`); la VM responde **`#0`**.

**B. `(+v)` con `v = "a"`:** el TW rechaza (`unary plus requires numeric
operand`); la VM responde **`a`**; `zyjs` no parsea el `+` unario
(`expected expression, found Plus`).

*Decidido el 2026-09-15:* el `+` unario **es forma del lenguaje**. `zyjs` lo
implementa (`+5` → `5`, `+"a"` → error) y se documenta en `GUIDE.md` junto a
`-x`.

**C. `C := 1` y luego `C := 2`:** el TW rechaza (`constant 'C' already
declared`); la VM y `zyjs` imprimen **`2`**. Dentro de un `!?`, la VM vuelve a
declararla y `zyjs` la trata como un nombre nuevo del bloque.

Lo que coincide en los tres: comparar un Float con una String, negar una String y
`5 % 0`.

### Corregido A en la VM — 2026-09-15

`Instruction::Not` calculaba `!is_truthy()`: truthiness, que la v0.0.9 retiró
(`GUIDE.md`: *«`!7` and `-"a"` are refused, not coerced»*). Ahora sólo acepta un
Bool y, con cualquier otra cosa, lanza `logical NOT requires boolean operand, got
{tipo}`, con el mismo texto y el mismo nombre de tipo que el TW (`Int`, `String`…).
El compilador sólo emite `Not` para el `!` unario. Barrido con `5`, `0`, `""`,
`[]`, `null` y `1.5` sacados de `json::decode`, más `#1`, `#0` y `!(1 == 2)`, en
expresión y como condición de `?`: los tres motores dan exactamente la misma
salida. Las dos celdas pasan a `AGREE`.

### Corregido B en la VM — 2026-09-15

`compile_unary` compilaba `+x` como una copia del registro. Ahora sólo copia
cuando el tipo estático del operando es Int o Float; si no, emite la instrucción
nueva `Pos(dst, src)`, que deja pasar un Int o un Float y rechaza lo demás con
`unary plus requires numeric operand, got {tipo}`. En el mismo paso, el texto del
TW para **este** diagnóstico dejó de volcar el `Debug` de Rust (`got String("a")`)
y usa `type_ident()`, como su hermano `negation requires numeric operand`. Barrido
TW contra VM, idéntico: String, Bool, array y `null` rechazados; `5`, `1.5`,
`+x` con `x = 3` y `+x + 1` pasan. La celda base queda en `DIVERGE` y la `-met` en
`WRONG`, las dos sólo por `zyjs`, que no parsea `+`.

### Corregido B en `zyjs` — 2026-09-15 (paso 2.12)

`parseUnary` lee `+` como lee `-`, y la evaluación deja pasar un Int o un Float y
rechaza lo demás con `unary plus requires numeric operand, got String`. El checker
ya contemplaba el `+` en su aviso de tipo. `GUIDE.md` lo documenta junto a `-a`.
Barrido idéntico en los tres motores. `runtime-operators`: 12 de 14 en `AGREE`;
las dos que quedan son la constante redeclarada (C, F5).

### Qué lo sujeta

`axes/runtime-operators.toml`: 7 pares. 8 verdes, 6 rojas.

---

## GLB-020 — Una constante varía: `<< C` y `@ C:1..2` la sobrescriben en el TW y en la VM

**Estado:** **cerrado el 2026-09-21 (F5)** — decidido el 2026-09-15 (error estático), implementado en los tres analizadores
**Encontrado por:** buscando cómo alcanzar `cannot reassign constant '{}' (declared with :=)` en tiempo de ejecución, paso C13, 2026-09-14
**Gravedad:** **alta**: incumple `MEM-1`, *las constantes son globales pero nunca varían*

### Qué se observa

La reasignación directa está bien cerrada: `C = 2` y `(C, d) = (5, 6)` los
rechaza el analizador en los tres motores. Pero hay otras dos formas de
escribir un nombre, y ninguna mira si es una constante:

```zymbol
C := 1
<< C              // con 7 en la entrada
>> C ¶            // zytw 7 · zyvm 7 · zyjs: Runtime error: Cannot reassign constant 'C'
```

```zymbol
C := 1
@ C:1..2 {
    >> C ¶
}
>> C ¶            // zytw 2 · zyvm 2 · zyjs 1
```

En los dos, el TW y la VM dejan la constante con otro valor **después**.

### Qué hay que decidir

Si `<< C` y `@ C:…` sobre una constante son un error estático (como `C = 2`) o
si el iterador puede sombrear la constante dentro del bucle sin cambiarla fuera.
Una celda ahora tendría que elegir por el autor cuál es su verde, y un rojo sin
verde posible es un defecto del arnés.

### Decidido — 2026-09-15

**D5: error estático, los dos.** `<< C` y `@ C:…` sobre una constante se
rechazan en el analizador de los tres motores, igual que `C = 2`. Es lo que
exigen `MEM-1` («reassignment is a static error») y `MEM-7` (un entorno ligero
no puede tener otra cosa bajo un nombre que su entorno fuerte ya usa), así que
no cambia ninguna premisa. La celda ya tiene un verde posible y se puede
escribir.

### Implementado — 2026-09-21 (F5)

Las tres formas de la constante y las dos del rango viven en el analizador
compartido, así que `zymbol check` las ve y los tres motores las heredan. Los
seis textos coinciden palabra por palabra.

| forma | antes | ahora |
|---|---|---|
| `C := 1` / `C := 2` | TW error en ejecución, VM y `zyjs` imprimen `2` | `constant 'C' already declared`, estático |
| `<< C` | TW y VM **sobrescriben** la constante en silencio | `cannot reassign constant 'C'`, estático |
| `@ C:1..2` | TW y VM dejan el último valor; `zyjs` itera una copia | igual, estático |
| `@ (a, b):1..3` | TW falla en el primer elemento, VM dice `range outside loop`, `zyjs` no parsea | `tuple pattern '( … )' requires a tuple, got Int`, estático |
| `v..3` suelto | tres textos distintos | `ranges can only be used in for-each loops`, estático |

En `zyjs` hizo falta el parser: no tiene VALOR de rango, así que las dos formas
de D4 eran errores de parseo —refusadas por no parsear, no por lo que son—. La
cabecera del bucle lee ahora el rango tras un patrón para poder refusarlo con la
frase compartida, y el parser de expresiones dice lo mismo ante un `..` suelto
en vez de nombrar el token. Sin producción nueva y sin gramática más ancha: el
barrido de parseo sobre los 2810 `.zy` sale idéntico.

**Un falso positivo que destapó la primera forma:** `C := 1  C := 2  >> C ¶`
avisaba de que `C` no se usaba mientras la imprimía dos líneas más abajo. El
paso de variables no usadas registraba la segunda declaración, que jubilaba a la
primera, y una jubilada que nadie usó se informa como no usada. Ahora la
declaración se refusa y no desplaza nada.

Matriz: **5 celdas en verde, ninguna nueva roja**, 81 → **76** ids rojos.
`runtime-operators` queda en 14 de 14.

---

## GLB-021 — La ayuda de `#.|x|` enseña `#..2|value|`, con dos puntos

**Estado:** **corregido el 2026-09-16** (paso 3.1)
**Encontrado por:** `syntax-format-convert/round-expects-a-decimal-count`, paso B6, 2026-09-14
**Gravedad:** baja, pero es una ayuda que enseña una forma que no existe

`x = #.|5|` en los dos motores Rust:

```
error: expected a decimal count after '#.'
  = help: write the count or the name of a variable holding it: #..2|value| or #..n|value|
```

`parse_format_precision(prefix_str)` (`zymbol-parser/src/data_ops.rs`) compone
`{prefix}.2|value|`, y para el redondeo el prefijo que recibe es `"#."`, que ya
termina en punto. Para `#,` sale bien (`#,.2|value|`). `zyjs` no llega a este
mensaje (`ZYJS-021`).

### Corregido el 2026-09-16 (paso 3.1)

Medido en las seis formas, el defecto era de tres ayudas y no de una:

| forma | ayuda de Rust antes | después |
|---|---|---|
| `#.\|5\|` | `#..2\|value\|` | `#.2\|value\|` |
| `#!\|5\|` | `#!.2\|value\|` | `#!2\|value\|` |
| `#,!\|5\|`, `#^!\|5\|` | `#,.2\|value\|` — enseñaba `.` a quien escribió `!` | `#,!2\|value\|`, `#^!2\|value\|` |

`parse_format_precision` recibe ahora dos textos: el operador que nombra el
mensaje, que no cambia, y lo escrito antes de la cuenta, que es lo que la ayuda
repite. La ayuda de `precision must be a non-negative integer` tenía la misma
composición y se corrige igual (hoy no se alcanza: `-1` no llega como un solo
token).

Cada forma que enseñan las ayudas —`#.2`, `#.n`, `#!2`, `#!n`, `#,.2`, `#,.n`,
`#,!2`, `#,!n`, `#^.2`, `#^.n`, `#^!2`, `#^!n`— corre, y da lo mismo en los tres
motores. `zyjs` da ya la ayuda en `#.` y `#!`, donde antes la omitía para no
copiar la mala. `syntax-format-convert/round-expects-a-decimal-count` pasa a
`AGREE`, y el eje queda en 9 de 9.

Por el camino: `#,.|5|` y sus hermanos se refusan en `zyjs` con otro texto,
[[ZYJS-026]].

---

## GLB-022 — La ayuda de los tipos de error lista siete de once

**Estado:** **corregido el 2026-09-16** (paso 3.2)
**Encontrado por:** `syntax-try-catch/error-type-without-a-name`, paso B7, 2026-09-14
**Gravedad:** baja en efecto; alta como documento: es lo que lee quien no sabe qué tipos hay

`:! ## { }` en los dos motores Rust:

```
error: expected error type name after '##'
  = help: valid error types: ##IO, ##Network, ##Parse, ##Index, ##Type, ##Div, ##_
```

Faltan `##Range`, `##Key`, `##DB` y `##Time`, que existen y se capturan
(`runtime-errors`, `LLM.md` § 9). La ayuda de `expected '##' for error type
(missing second #)` enumera todavía menos: `##IO, ##Network, ##Parse`.

Y `zyjs` acepta `:! ## { }` sin nombre y ejecuta el `!?` (añadido a `ZYJS-021`).

### Corregido el 2026-09-16 (paso 3.2)

Medido antes cuál es la lista: once tipos que produce algún motor —`##Div`,
`##Index`, `##Key`, `##Range`, `##Type`, `##Parse`, `##IO`, `##Network`, `##DB`,
`##Time`, `##_`—. Los cinco primeros se lanzan y se capturan con `:! ##Tipo`
igual en los tres motores; `##Parse`, `##IO` y `##Time` llegan como valor blando
de su módulo, también igual en los tres. Un `catch` con cada uno de los once
nombres se parsea y corre en los tres. (`zyjs` tiene además un `##Scope` que no
se alcanza: el analizador refusa antes.)

- Las **tres** ayudas de `parse_error_type` —no dos: también la de
  `expected '##' for error type`— listan los once, en el orden de la tabla del
  manual v009: los que lanza la operación, los de los módulos y `##_`.
- `zyjs` da las mismas dos ayudas donde llega (`:! #Div`, `:! ## { }`); antes no
  daba ninguna para no copiar la lista corta.
- `GUIDE.md` § Error Types completa su tabla (faltaban `##Key`, `##Range` y
  `##Time`) y dice cuáles vienen de dónde, y que el parser acepta cualquier nombre
  tras `##`. `LLM.md` § 9 añade `##Key` y `##Time`.

`syntax-try-catch/error-type-with-one-hash` pasa a `AGREE`.
`error-type-without-a-name` ya coincide en texto y ayuda, y sigue en `DIVERGE`
sólo por la línea en cascada de Rust ([[GLB-028]], paso 3.7).

### Lo que no se toca aquí

- `zymbol-design/SYMBOLS.md` y `SIMBOLOS_ES.md` (§ «Error kinds») listan los
  siete de antes, «six English words plus `##_`». Son documentos de diseño, de
  rango fuente: se pregunta al autor. *Decidido el 2026-09-16: a los once;*
  **actualizados el 2026-09-16 (paso 3.2d)**, en un commit que sólo cambia esa
  fila en los dos idiomas.
- El comentario de la regla `error-types` de `vscode/syntaxes/zymbol.tmGrammar.json`
  lista siete; la regla en sí acepta cualquier nombre y resalta los once.
- Los manuales traducidos (`web/data/manuals/`) se quedan como están: la tabla de
  `v009/manual_en.md` ya tenía los once.
- Por el camino, [[ZYJS-027]] (un `$!!` fuera de una función) y [[GLB-032]] (la
  documentación promete capturar un error blando con `:!`).
- Y un tipo distinto entre motores: `##.("abc")` es `##_` en el TW y en `zyjs` y
  `##Type` en la VM. Es de F4 (4.1, tipos según la decisión D1).

---

## GLB-023 — Una variable leída sólo en el prompt de `<<` se avisa como no usada en los dos motores Rust

**Estado:** **corregido el 2026-09-15** (paso 1.6b)
**Encontrado por:** medición del paso 1.6 (`GLB-018` A), 2026-09-15
**Gravedad:** media: un aviso falso invita a borrar una variable que el programa usa
**Familia:** zonas ciegas del analizador (`ZYJS-013`, `ZYJS-018`), aquí en el analizador compartido de Rust

```zymbol
x = "Ana"
<< "Hola {x}: " n
>> n ¶
```

| motor | |
|---|---|
| `zytw`, `zyvm` | `warning: unused variable 'x'`, y luego imprimen `Hola Ana: ` |
| `zyjs` | sin aviso |

El analizador de `zymbol-semantic` no visita las partes de `InputPrompt::Interpolated`,
así que ni cuenta sus nombres como uso ni puede ver uno que no existe. `zymbol
check` y el LSP heredan los dos defectos.

### Qué lo sujeta

`runtime-io/input-prompt-interpolation-is-a-use`, roja por `zytw` y `zyvm`.

### Corregido — 2026-09-15

`variable_analysis.rs` se saltaba el prompt con el comentario *«InputPrompt is not
an Expr, so we skip analyzing it»*. Ahora cuenta como uso cada
`StringPart::Variable` de `InputPrompt::Interpolated`, antes de declarar la
variable que se lee, porque el prompt se imprime antes de leer. Control negativo
en el mismo fichero: una variable de verdad sin usar sigue avisándose. La celda
pasa a `AGREE`.

---

## GLB-024 — Un comparador de `$^` que no devuelve un Bool: nadie da error y cada motor ordena distinto

**Estado:** abierto — **decidido el 2026-09-15**: error `##Type` en los tres motores. **Corregido en los tres motores el 2026-09-15** (pasos 1.12 y 2.13); queda el kind (4.1)
**Encontrado por:** leyendo `ArraySort` de la VM en el paso 1.10, 2026-09-15
**Gravedad:** media-alta: un programa mal escrito ordena, sin aviso, de una forma que depende del motor
**Familia:** las reglas de la v0.0.9 sin truthiness (`GUIDE.md`: *«There is no truthiness in Zymbol»*)

```zymbol
v = [3, 1, 2]
>> (v$^ (a, b -> a - b)) ¶
>> (v$^ (a, b -> a * 0 + b * 0)) ¶
>> (v$^ (a, b -> "{a}{b}")) ¶
```

| comparador | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| `a < b` (Bool) | `[1, 2, 3]` | `[1, 2, 3]` | `[1, 2, 3]` |
| `a - b` (Int) | `[2, 1, 3]` | `[3, 1, 2]` | `[3, 1, 2]` |
| `a * 0 + b * 0` (siempre 0) | `[2, 1, 3]` | `[2, 1, 3]` | `[2, 1, 3]` |
| `"{a}{b}"` (String) | `[2, 1, 3]` | `[3, 1, 2]` | `[3, 1, 2]` |

Los comparadores usan sus parámetros a propósito: con `(a, b -> 1)`, `zyjs` avisa
`unused variable 'a'` y `'b'` —los Rust no avisan de parámetros de lambda sin
usar— y ese aviso tapaba la pregunta.

El TW trata como falso todo lo que no es `#1`; la VM (`keep.is_truthy()`) y `zyjs`
aplican truthiness. **Nadie da error.** Sin truthiness en el lenguaje, lo
coherente parece que un comparador que no contesta un Bool sea un error, pero
ningún documento lo dice para `$^`. Por eso la celda
`runtime-functions-hof/sort-comparator-that-is-not-a-bool` pregunta sólo que los
motores coincidan (`expect = "ok"`), y su verde no elige.

### Qué hay que decidir

¿Un comparador que no devuelve un Bool es error, y de qué familia (`##Type`, por
D1)? ¿O tiene un significado, y cuál?

*Decidido el 2026-09-15:* **error `##Type`**, coherente con «sin truthiness» y
con D1. Los Rust en el paso 1.12 y `zyjs` en la F2. La celda pasa a
`expect = "error"`.

### Corregido en los dos Rust — 2026-09-15

El TW leía como falso todo lo que no era `#1`, y la VM llamaba a
`keep.is_truthy()`. Los dos lanzan ahora `sort comparator must return a Bool, got
{tipo}` con el mismo texto; en la VM sale del doble bucle con `break 'calls`, no
con `raise!`. Barrido TW contra VM, idéntico: `a < b` y `a > b` ordenan, `a - b`
(Int) y `"{a}{b}"` (String) se rechazan, y `[7]$^ …` no llama al comparador y no
tiene nada que rechazar. El kind sale `##_` en los dos, porque el TW clasifica por
palabras. Llegar a `##Type` es el paso 4.1. `GUIDE.md` lo documenta junto al
comparador. Las siete aplicaciones mantienen sus goldens.

### Corregido en `zyjs` — 2026-09-15 (paso 2.13)

La ordenación por inserción de `zyjs` aplicaba `truthy()` al resultado. Ahora lanza
`sort comparator must return a Bool, got Int`, con el mismo texto que los Rust. El
mismo barrido de cinco casos da la misma salida en los tres motores.

### Qué lo sujeta

`runtime-functions-hof/sort-comparator-that-is-not-a-bool`, roja. Vecina, por el
mismo camino: `syntax-collection-ops/sort-comparator-from-a-variable`. Los Rust
rechazan `a$^ f` con `f` una lambda en una variable (el comparador tiene que ir
escrito en línea), y `zyjs` ordena con ella (`ZYJS-021`).

---

## GLB-025 — Una variable destruida con `\` se lee en `{…}` sin error: los tres imprimen `{x}`

**Estado:** **corregido el 2026-09-15** en los tres motores (paso 2.15)
**Encontrado por:** leyendo `interpolate_string` del TW en el paso 1.11, 2026-09-15
**Gravedad:** media: el silencio que cerró `GLB-018` A, entrando por la destrucción
**Familia:** `GLB-008` (uso tras destruir), `GLB-018` A

```zymbol
x = "dato"
>> x ¶
\ x
>> "leo {x}" ¶
```

| forma | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| `>> x ¶` tras `\ x` | `use after destruction` | `use after destruction` | `use after destruction` |
| `>> "leo {x}" ¶` tras `\ x` | `leo {x}` | `leo {x}` | `leo {x}` |

`eval_identifier` llama a `check_variable_alive` antes de leer; `interpolate_string`
no, y un nombre destruido cae a la rama del texto literal. El analizador no puede
rechazarlo (lo que enseñó `GLB-008`: una destrucción escrita en una rama que no se
ejecuta no ha ocurrido), así que el rechazo tiene que ser en ejecución, como el del
identificador.

### Por qué se pregunta aunque parece no necesitar decisión

`GUIDE.md` dice desde el paso 1.6 que `{name}` se lee como `name`, y `GLB-008`
decidió que leer un nombre destruido es error en ejecución. Juntas dan la
respuesta, pero ninguna de las dos lo dice de la interpolación.

### Qué lo sujeta

`runtime-io/destroyed-name-in-interpolation`, `expect = "error"`, roja en los
tres.

### Corregido — 2026-09-15 (paso 2.15)

Cada motor hace ahora con `{x}` lo mismo que con `x`:
- **TW:** `interpolate_string` consulta `dead_variables` y lanza `use after
  destruction`.
- **VM:** la interpolación tenía la cadena de resolución del identificador sin la
  rama de las variables de archivo (`file_var_map` → `LoadGlobal`, que es lo que
  rechaza una destruida), y en un cuerpo de función terminaba en texto literal
  donde el identificador lanza `'y' is undefined`.
- **`zyjs`:** `evalStr` atrapaba cualquier error de una parte `{…}` y escribía el
  nombre, así que también se tragaba la destrucción. Ahora deja pasar ese error y
  el de «indefinido».

La celda pasa a `AGREE`. Por el camino salieron tres defectos que el `catch` y el
literal escondían: las capturas de lambda de `zyjs` no veían los nombres de una
interpolación (arreglado aquí, porque sin eso divergía un fichero del corpus); el
TW tiene el mismo defecto (`ZYTW-005`); y la VM rechaza leer un local destruido en
una rama que no se ejecuta (`ZYVM-005`). Dentro de una función, la VM y `zyjs`
dicen `'y' is undefined` donde el TW dice `use after destruction`, igual que con el
identificador: es el resto de `GLB-008`.

---

## GLB-026 — Un fichero con BOM no corre en Rust, y los caracteres raros son identificador en Rust y ruido en `zyjs`

**Estado:** **corregido el 2026-09-15** (paso 2.17), A y B
**Encontrado por:** midiendo el paso 2.1 (`ZYJS-020`), 2026-09-15

### A. La marca de orden de bytes (BOM)

Un `.zy` guardado con BOM, como hacen algunos editores de Windows:

| motor | |
|---|---|
| `zytw`, `zyvm` | `warning: unused variable '\ufeffx'` y `error: undefined variable 'x'`: el lexer pega la marca al primer identificador |
| `zyjs` | `1` |

`is_whitespace('\u{FEFF}')` es falso en Rust, y `is_ident_start` acepta todo lo
que no es espacio, cifra ni operador. Celda `syntax-lexer/byte-order-mark`,
`expect = "ok"`, roja por los dos Rust.

### B. Caracteres que ningún documento clasifica

| carácter | Rust | `zyjs` |
|---|---|---|
| `` ` `` (`` >> `x ``) | parte del identificador: `` undefined variable '`x' `` | lo descarta: imprime `1` |
| U+200B, espacio de ancho cero (`x = 1\u200b`) | identificador: `undefined variable '\u200b'` | lo descarta |
| `€` (`€ = 5`) | identificador: imprime `5` | `expected expression, found Assign` |

Rust sigue su regla (`is_ident_start`: todo lo que no es espacio, cifra ni
carácter de operador) y `zyjs` la suya (`\p{L}\p{M}\p{So}\p{Co}` para empezar,
y lo demás cae al `consume()` final). `GUIDE.md` § String interpolation dice que
un identificador es «any Unicode letter, `_`, and any non-operator symbol», que
es la regla de Rust para `€`, pero no dice nada de la comilla invertida ni de
un carácter de formato invisible.

### Qué hay que decidir

¿Un carácter de formato invisible (U+200B) o la comilla invertida pueden formar
parte de un nombre, o son un error? Hasta decidirlo no hay celda: cualquier verde
elegiría por el autor.

*Decidido el 2026-09-15:* **los símbolos visibles sí** pueden ir en un nombre
(`€`, como dice `GUIDE.md`), y **un carácter invisible o la comilla invertida
son error** en los tres motores. Queda una pregunta antes de implementarlo:
U+200C y U+200D (ZWNJ/ZWJ) son invisibles, pero hacen falta para escribir bien
palabras en devanagari y otras escrituras índicas, y `zyjs` los admite a
propósito dentro de un nombre. Se medirá su uso en las aplicaciones LDV y se
preguntará antes de tocarlos.

*Medido y decidido el 2026-09-15.* ZWNJ aparece 44 veces en nombres de la capa
persa de Chaturanga y de ejemplos en kannada, telugu y persa, y ZWJ 12 veces en el
ejemplo en cingalés. U+200B y el BOM no aparecen en ningún fichero, y las 2567
comillas invertidas del workspace están en comentarios. **ZWJ y ZWNJ se permiten
dentro de un nombre, nunca al principio**; los demás invisibles y la comilla
invertida son error en los tres motores (paso 2.17).

**Un ejemplo del playground que no carga** (medido el 2026-09-15, paso 2.5):
`web/examples/graphics/mandelbrot/emoji.zy` escribe `<<| _🔑`. Tras un `_`, el
lexer de `zyjs` sólo sigue leyendo el nombre si viene letra, uso privado, cifra o
`_` (`[\p{L}\p{Co}0-9_]`), y un emoji es `\p{So}`; el `_` se queda solo y el
parser falla. Rust lo lee como un nombre. El ejemplo lleva `@skip-parity`, y por
eso nada lo ejecutaba en `zyjs`. Entra en el paso 2.17.

### Corregido el 2026-09-15 (paso 2.17)

Los dos lexers dicen ahora lo mismo, y lo dicen en una sola regla escrita dos
veces:

- **A.** Una marca de orden de bytes al principio del fichero se salta, en Rust
  y en `zyjs`. En cualquier otra posición es un carácter invisible, y por tanto
  un error.
- **B.** Un símbolo visible que no es operador es una letra del nombre (`€`,
  `±`, `§`, `©`, un emoji, `_🔑`); un carácter invisible o la comilla invertida
  no lo son y se rechazan con `unexpected character`. Un invisible se nombra por
  su punto de código (`U+00AD`) en vez de entrecomillarse, porque entrecomillarlo
  no enseñaría nada. ZWJ y ZWNJ se permiten **dentro** del nombre, nunca al
  principio.

`zymbol-lexer` gana `is_invisible_char` (los `Cf` de formato más los controles) y
`zyjs` exporta `isInvisibleChar`, `isIdentStart`, `isIdentContinue` e
`isIdentName` con la misma tabla. Las veinte formas de la matriz —`€`, `±`, `¿`,
`§`, `¨`, `©`, emoji, combinante, uso privado, `_🔑`, BOM al principio, BOM en
medio, `` ` ``, U+00AD, U+200B, U+2060, U+200F, ZWNJ al principio, ZWNJ y ZWJ en
medio— dan hoy la misma respuesta en los tres motores.

### Qué lo sujeta

`syntax-lexer/byte-order-mark` (verde), y tres celdas nuevas:
`syntax-lexer/visible-symbol-in-a-name`,
`syntax-lexer/invisible-character-in-a-name`,
`syntax-lexer/backtick-is-not-a-name` y
`syntax-lexer/zero-width-joiner-inside-a-name`.

El arnés tenía un defecto que salió aquí: `zyddt gen` antepone un banner de tres
líneas a la fuente de cada celda, así que una marca de orden de bytes declarada
al principio nunca lo estaba, y la celda no podía llegar a verde. El generador
escribe ahora la marca delante del banner.

---

## GLB-027 — La ayuda de Rust para `x°[1] 5` enseña `arr[i] = val`, una forma que no existe

**Estado:** **corregido 2026-09-19 (paso 3.6)** — la ayuda era el síntoma
**Encontrado por:** paso 2.3, 2026-09-15, al portar el rechazo a `zyjs`
**Familia:** `GLB-021`, `GLB-022` (ayudas que enseñan lo que no es)
**Decisión del autor (2026-09-19):** implementar — un nombre caliente es un ancla
de edición como cualquier otro.

`x = [1, 2]` y luego `x°[1] 5`, o `x°[1]$~ 5`, en los dos motores Rust:

```
error: expected '=' after index expression for indexed assignment
  = help: syntax: arr[i] = val  or  arr[i] += val
```

`COL-2` dice que `arr[i] = v` no existe, y el propio parser rechaza `arr[i] = v`
dos líneas antes con `indexed assignment does not exist`. La ayuda enseña
justo la forma retirada. `zyjs` rechaza igual desde el paso 2.3, **sin** esa
ayuda.

### Lo que se midió antes de tocar nada

A ese mensaje se llegaba por **una sola puerta**, y no era la redacción. El
despachador de sentencias trataba los dos nombres de forma distinta: `x[` sólo
entraba en `parse_assignment` si `is_indexed_assignment` veía un operador de
asignación tras el grupo de corchetes, mientras que `x°[` entraba **siempre**.
Y dentro de esa rama todo era ya un rechazo: el `matches!` que refusa la
asignación indexada cubría exactamente el mismo conjunto de tokens que el
`match` de debajo, así que el único brazo alcanzable del segundo era el `_`, y
las cuarenta líneas que le seguían — el desazucarado `arr[i] = val` →
`CollectionUpdate` — eran código muerto desde la decisión 6.

Lo que la asimetría le costaba al nombre caliente, medido en los tres motores:

| forma | antes | ahora |
|---|---|---|
| `x°[1]$~ 5` | **rechazada en los tres** | `[5, 2]` en los tres |
| `x°[1]` como sentencia | **rechazada en los tres**, señalando la línea siguiente | `[1, 2]`, como `x[1]` |
| `acc°[1]$~ 99` dentro de `@` | rechazada | `[99, 20]`, escribiendo en el `acc` del bucle |
| `>> x°[1] ¶`, `y = x°[1]` | ya funcionaban | sin cambio |
| `x°[1] = 5`, `x°[1] += 5` | «indexed assignment does not exist» | igual |

O sea: `x°[1]$~ 5` es la forma que declara `COLLECTIONS.md` y estaba rechazada
para nombres calientes en los tres motores, mientras la misma lectura funcionaba
en cualquier posición de expresión. `zymbol check` daba el mismo mensaje, así que
el LSP también. Uso real de `°[` en todo el workspace: **cero**.

### Lo que se hizo

Rust — `zymbol-parser`:
1. La rama `HotIdent` pide el mismo `is_indexed_assignment` que la rama `Ident`.
2. La rama de expresión de las dos comparte un método, `parse_expr_or_edit_statement`:
   la caliente devolvía un `Statement::Expr` pelado, así que darle la puerta sin
   esto le habría comprado a `x°[1]$~ 5` un parseo y **DI-01** otra vez — correr y
   no hacer nada en silencio.
3. El desazucarado lleva el anclaje: `flatten_receiver` devuelve un `EditRoot`
   (nombre + `hot` + `pre_hot`) en vez de un nombre pelado, y tanto el
   `Assignment` como el identificador raíz de `rewrite_edit_at_path` se
   construyen con él. `°` no es adorno sobre el receptor: dice en qué ámbito
   vive el nombre, y el desazucarado asigna a ese nombre.
4. El mensaje y su ayuda se borraron con el código muerto que los sostenía.

`zyjs` — la misma forma: fuera el rechazo que sólo miraba `hot`, y el receptor
lleva `hot` hasta `InPlaceEdit`, que define con `hotDef` cuando no hay nada que
actualizar, igual que `VarAssign`.

### Un texto por fallo, de propina

Al quitar la puerta, `x°[1 = 2` dejó de ir a `parse_assignment` y pasó a fallar
donde falla su gemelo frío — y ahí se vio que el corchete de índice sin cerrar
tenía **tres** redacciones repartidas entre los dos motores: la de
`expressions.rs`/`closeNav` con su ayuda, y sendos textos privados en la rama de
sentencia de cada motor, sin ayuda. El privado de Rust seguía vivo para
`x[1 2] = 5`. Los dos se retiraron: ahora las siete formas —`x[1 = 2`,
`x°[1 = 2`, `x°[1`, `x[1 2] = 5`, `x[1 2] $~ 5`, `x°[1 2] = 5`, `x[1>2 3] = 5`—
dan el mismo texto y la misma ayuda en los tres motores, y la ayuda del
navegador aparece cuando el índice trae un `>`, que es lo que decide
`is_nav_index` en Rust.

### Lo que queda rojo, y por qué no es esto

`syntax-variables/hot-index-without-operator` (`x°[1] 5`) pasa de `WORDING` a
`WRONG`, y el rojo **es ahora el mismo** que el de
`refusal/stray-literal-statement` (`x[1] 5`): los dos motores Rust refusan el
`5` suelto y `zyjs` lo ejecuta sin decir nada (ZYJS-021, registrado en el paso
2.3). La celda dejó de medir GLB-027 y mide un hallazgo que ya tiene el suyo.

**Puertas:** `cargo test` 1040/0; consensus 660/0; reject 42/42; expect 634+26,
0 stale; messages verde (línea base 618→616 de 934: dos textos retirados);
project, fmt y guide en línea base; barrido de parseo de `zyjs` idéntico sobre
2810 `.zy`. Matriz: 177 ids rojos, los mismos de antes.

---

## GLB-028 — Los parsers Rust añaden errores falsos en cascada y enseñan sus tokens internos

**Estado:** **la cascada corregida 2026-09-19 (paso 3.7)**; los nombres de token
siguen abiertos y son de los DOS motores
**Encontrado por:** pasos 2.1 y 2.3, 2026-09-15
**Gravedad:** media: el lector recibe dos errores donde hay uno, y el segundo nombra el lexer por dentro
**Decisión del autor (2026-09-19):** las tres causas, sólo la cascada.

Tras el error real, los dos Rust siguen leyendo e informan de algo que no está mal:

| forma | error real | lo que añaden |
|---|---|---|
| `?? c { 'a'..5 => "x" _ => "y" }` | `expected char after '..' in range pattern` | `unexpected token: RBrace` |
| `:! ## { … }` | `expected error type name after '##'` | `unexpected token: RBrace` |
| `>> "a{b" ¶` | `unterminated string interpolation` | `unterminated string literal` (vuelven a leer la comilla de cierre como apertura) |
| `b = #2` | `invalid boolean literal: digit 2 …` | `expected expression, found Error("invalid boolean literal")` |
| `x[1] 5` | — | `unexpected token: Integer(5)`, el nombre de la variante de Rust |

`zyjs` para en el primer error. En varias celdas de `syntax-*` el mensaje ya es
el mismo en los tres y quedan en `DIVERGE` sólo por esa línea de más: los dos
patrones de rango de `syntax-control-flow`, `syntax-lexer/unterminated-string-interpolation`,
`syntax-try-catch/error-type-without-a-name`.

### Lo que se midió antes de tocar nada

Barrido de los 1258 programas mal escritos que hay (`ZyDDT/generated/` más
`zyquality/reject/`), contando diagnósticos por motor:

| superficie | programas con 2+ errores |
|---|---|
| `zymbol run`, `zytw` y `zyvm` idénticos | 12 |
| `zymbol check` — lo que ve el LSP | **41** |
| `zyjs` | 1, y es correcto |

El analizador cascadeaba **tres veces más** que el ejecutor, que es justo la
superficie donde un lector lo encuentra. Y no era una causa: eran **cinco**.

### Las cinco causas

**1 — `skip_statement` contaba las llaves desde donde falló.** La `{` que abrió
el cuerpo ya quedaba detrás, así que `depth` arrancaba en 0 y el salto **se
paraba en la `}` de cierre** en vez de tragarla. Es el escenario que el propio
comentario de la función decía haber arreglado en GLB-007 — sólo se había
arreglado el caso en que el fallo ocurre ANTES de la `{`, en la condición. El
salto recibe ahora el token donde empezó la sentencia y cuenta desde ahí.

**2 — y se comía la `}` del bloque que lo contiene.** El avance obligatorio del
principio tomaba la `}` sobre la que había fallado la sentencia, así que
`parse_block` tomaba por suya la del bloque de fuera y el módulo quedaba sin
cerrar: «expected '}' to close module body». Ahora no toca una `}` de nivel 0
cuando hay un `parse_block` esperándola y la sentencia ya avanzó algo; en el
nivel superior, donde nadie la espera, se sigue consumiendo o la recuperación no
avanzaría.

**3 — el lexer releía la comilla de cierre.** Tras «unterminated string
interpolation» no consumía la `"` que había parado la lectura, así que el token
siguiente empezaba una segunda cadena ahí y esa corría hasta el final del
fichero: «unterminated string literal», y una ayuda que manda cerrar con una
comilla que ya está escrita.

**4 — el bucle de imports avanzaba un solo token.** Los otros dos bucles de
recuperación saltan la sentencia entera desde GLB-007; éste se quedó atrás, así
que `<# ./2malo => m` informaba del `=>` que el primer error ya había dado por
inalcanzable.

**5 — el parser hablaba del token que el lexer ya había refusado.** El lexer
emite su diagnóstico y devuelve un `TokenKind::Error` con su carga dentro;
`run` y `build` paran ahí, pero `check` y el LSP siguen a propósito, y el parser
decía `expected expression, found Error("invalid float: '1.0e+'")` — la cadena
interna del lexer, en la grafía `Debug` de Rust, a un lector que no la pidió. Un
diagnóstico del parser que señala un token que el lexer ya refusó es siempre un
duplicado, y se descarta. **Ésta sola explica 26 de los 41.**

### Antes y después

| | antes | ahora |
|---|---|---|
| `run` con 2+ errores | 12 | **1** |
| `check` con 2+ errores | 41 | **4** |
| celdas | — | **5 verdes, 0 nuevas rojas** (176 → 171 ids rojos) |
| goldens | — | 4 encogen: 2→1, 13→7, 6→3, 6→3 |

El único que queda en `run` es `refusal/undefined-name-in-string-interpolation`,
y son dos errores **reales**, uno por cada nombre indefinido: `zyjs` da los dos
también. Ningún programa pasó de tener un error a no tener ninguno.

### Lo que NO se arregló, y por qué

**Los nombres de token internos los enseñan los DOS motores.** La ficha sólo
acusaba a Rust y eso era la mitad de la medida:

| | |
|---|---|
| Rust | `unexpected token: RBrace`, `expected pattern, found Star`, `unexpected token: FatArrow`, `expected expression, found Error(…)` |
| `zyjs` | `Expected FAT_ARROW, got 'string'`, `expected expression, found FatArrow`, `expected expression, found LBrace`, `Expected IDENT, got '2'` |

Decidido por el autor: fuera de este paso. Son decenas de sitios en cada motor y
cada uno pide decidir cómo se llama ese token en el idioma del lenguaje.

**Cortar la cascada puso 4 celdas en verde, no 11.** Tres de `syntax-control-flow`
pasaron de `DIVERGE` a `WORDING`: ya no sobra ninguna línea, y lo que queda es
que `zyjs` **no tiene** los tres mensajes, que son los buenos —
`expected '=>' after pattern`, `expected ']' to close list pattern`,
`'_?' requires a condition` con su ayuda — y contesta con nombres de token. Eso
lo cuenta el inventario de `zyquality/messages/` y no es esta cascada.

**Y una quinta celda se puso verde de propina**, `runtime-modules-scripts/module-with-parse-errors`,
por la causa 2.

---

## GLB-029 — Formatear una cadena que parece un número: el TW la rechaza y la VM la formatea

**Estado:** **corregido el 2026-09-15** (paso 2.15e): se acepta en los tres motores
**Encontrado por:** paso 2.8, 2026-09-15, al portar a `zyjs` las comprobaciones de los formatos

| forma, con `v = "12.5"` | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| `#,\|v\|` | error: `format expressions only work with numbers, got String("12.5")` | `12.5` | `12.5` |
| `#.2\|v\|` | `12.5` | `12.5` | `12.5` |
| `#!2\|v\|` | `12.5` | `12.5` | `12.5` |

El TW acepta una cadena numérica al redondear y al truncar (su texto dice «numbers
or numeric strings») y la rechaza al dar formato con separadores; la VM la acepta
en los tres. Una cadena que no es un número (`"x"`) y un Bool son error en los tres
motores desde el paso 2.8.

### Qué hay que decidir

¿Los operadores de formato (`#,`, `#^` y sus variantes) aceptan una cadena que se
lee como número, como ya hacen `#.` y `#!`? ¿O ninguno la acepta?

*Decidido el 2026-09-15:* **se acepta en todos los motores**, como ya hacen `#.` y
`#!`. Cambia el TW (paso 2.15e).

*Corregido el 2026-09-15 (paso 2.15e).* `eval_format` del TW acepta una cadena que
se lee como número, con la misma lectura que el redondeo: recortada y con cifras de
cualquier escritura. Los tres motores dan la misma salida con `"1234.5"`, `"1234"`,
`" 42 "`, `"१२३४"` y `"1e3"` en `#,`, `#,.2`, `#^` y `#.1`. Una cadena que no es un
número sigue siendo error en los tres, con texto y kind pendientes de 3.5 y 4.1. La
celda pasa a `AGREE`.

### Qué lo sujeta

`runtime-format-convert/format-a-numeric-string`, que sólo pide que coincidan.

---

## GLB-030 — Dentro de un bloque TUI (`>>| { … }`) el analizador de Rust no comprueba nada

**Estado:** **corregido 2026-09-19 (paso 3.8)** — y eran tres huecos, no uno
**Encontrado por:** el paso 2.17, 2026-09-15, al cargar `emoji.zy` en `zyjs`

`TypeChecker` de `zymbol-semantic` no desciende al cuerpo de un `>>| { … }`: su
único brazo para `Statement::TuiBlock` es `check_top_level_exit`. Todo lo que ese
paso comprueba queda apagado dentro del bloque. Medido con el mismo programa,
dentro y fuera:

| forma | fuera del bloque | dentro de `>>\| { … }` | `zyjs` |
|---|---|---|---|
| `x = f(1)` con `f(a, b)` | `error: function 'f' expects 2 argument(s), but 1 were provided` | nada | error |
| `a $+ "t"` con `a = [1, 2]` | `error: cannot append String to [Int]: type mismatch` | nada | error |
| `>> "{nada}" ¶` | `error: undefined variable 'nada' in string interpolation` | nada | error |
| `@ i:1..c` con `c` calculada | `warning: range direction is decided at runtime…` | nada | aviso |

Es la cuarta vez que aparece la misma forma de fallo: un brazo que no desciende
apaga TODAS las comprobaciones de ese paso, no una. `variable_analysis`,
`last_use`, `loop_context` y `def_use` sí bajan al cuerpo, y por eso los avisos
de variable no usada sí salen dentro del bloque — que es lo que hace difícil de
ver el hueco.

Sale a la luz porque `web/examples/graphics/mandelbrot/emoji.zy` es un programa
TUI entero: `zyjs` da allí dos avisos de dirección de rango correctos y Rust
ninguno, y `web/tests/test_check.mjs` lo cuenta como regresión de paridad
(0/1 → 0/2) desde que `zyjs` sabe leer `_🔑` (paso 2.17).

### Qué hay que decidir

¿Se hace descender al analizador de tipos por el cuerpo del bloque TUI —un
`self.check_block(&tb.body)` en ese brazo—, con lo que aparecerán diagnósticos
nuevos en los programas TUI del corpus y de los ejemplos? ¿O el bloque TUI queda
declarado como zona sin comprobar?

*Decidido el 2026-09-15:* **se corrige en F3**, con los demás textos y
comprobaciones de Rust, midiendo antes cuántos diagnósticos nuevos aparecen en el
corpus, en los ejemplos y en las aplicaciones LDV — un bloque TUI es el cuerpo
entero de varios programas.

La línea base de `web/tests/test_check.mjs` se regraba a `0 2` para `emoji.zy`
en el mismo paso 2.17, con esta causa escrita: los dos avisos son de `zyjs` y son
correctos; lo que falta es el lado Rust. La divergencia la sujetan esta ficha y
su celda, no un número en un fichero.

### Qué lo sujeta

`refusal/undefined-name-inside-a-tui-block`, roja: `zyjs` la refusa en estático y
los dos motores Rust llegan a intentar abrir la pantalla alterna.

### Lo que se midió antes de tocar nada: eran TRES huecos

`check_statement` no tenía brazo para `TuiBlock` —lo que decía la ficha— **ni
para `OutputPos` (`>>~`) ni para `Sleep` (`@~`)**. Los tres caían en el mismo
`_ => {}`. `>>~` se escribe **539 veces** en el corpus y los ejemplos y no había
nada mirando ni sus posiciones ni lo que imprime. `zyjs` comprueba los tres.

| forma | `zytw` antes | `zyjs` | `zytw` ahora |
|---|---|---|---|
| `>>\| { x = f(1) }` con `f(a,b)` | nada | error | error |
| `>>\| { >> "{nada}" ¶ }` | nada | error | error |
| `>>~ (nada, 1) > "A"` | nada | error | error |
| `>>~ (1,1) > f(1)` | nada | error | error |
| `@~ nada` | nada | error | error |
| `@~ f(1)` | nada | error | error |

El cuerpo del bloque entra con ámbito propio, porque `execute_block` empuja uno:
un nombre definido dentro no existe después, y este paso tiene que decir lo
mismo que los demás.

### Lo que apareció al encenderlo

Barrido de los 154 ficheros con `>>|`, `>>~` o `@~` (corpus, `project`,
ejemplos, generados de ZyDDT y las ocho aplicaciones): de 15 líneas de
diagnóstico a **239**, ninguna perdida. Son **tres hechos**:

**1. Los 110 ficheros de `mandelbrot`, dos avisos de dirección de rango cada
uno.** Es exactamente para lo que era el paso: `@ y:1..medio` con `medio`
sacado del tamaño del terminal. `zyjs` ya los daba y Rust no. **Ahora
coinciden**, que es lo que la ficha pedía.

**2. Los mismos 110, un `type mismatch: 'marca' was String but assigned Char`.**
También cierto: `trazo = " .:-=+*#%"` es String y `trazo[paso]` es Char. Ver
[[GLB-043]]: `zyjs` tiene la regla y no la dispara aquí porque sólo compara
literal contra literal.

**3. Un fallo real en ZyBank, a la primera.** `pantalla/tui.zy:595` escribía
`@! principal` donde el salto con etiqueta se escribe `@:principal!`. Ver
[[GLB-041]]. Corregido en el mismo paso, por decisión del autor.

Ningún fichero del corpus y ninguna otra aplicación cambian.

**Puertas:** `cargo test` 1040/0; consensus 660/0; reject 42/42; expect 634+26,
0 stale; messages, project, fmt y guide en línea base; las seis suites de `web/`
en verde. Matriz: 171 → 170 ids rojos, y la celda que sujetaba esta ficha en
verde.

---

## GLB-031 — Espacios dentro de un operador de formato: Rust los acepta y `zyjs` los refusa

**Estado:** **decidido y corregido el 2026-09-16** (paso 3.1c): el operador va junto
**Encontrado por:** el paso 3.1b, 2026-09-16, midiendo los vecinos de [[ZYJS-026]]

Con `v = 1234.5678`:

| forma | `zytw`, `zyvm` | `zyjs` |
|---|---|---|
| `#,. 2\|v\|` | `1,234.57` | refusa |
| `#. 2\|v\|` | `1234.57` | refusa (`expected a decimal count after '#.'`) |
| `#, .2\|v\|` | `1,234.57` | refusa (`expected '\|' after format operator '#,'`) |
| `#,.2 \|v\|` | `1,234.57` | refusa |
| `#.2 \|v\|` | `1234.57` | refusa (`expected '\|' after precision`) |

El lexer de Rust lee `#,`, `.`, `2` y `|` como tokens separados y el parser los
junta, así que cualquier espacio entre ellos pasa. El de `zyjs` lee el operador
entero, con su cuenta, de una pasada y sin espacios. Ningún documento dice si
`#. 2|v|` es una forma del lenguaje o una permisividad del parser: `GUIDE.md`
escribe siempre el operador junto.

No es una diferencia de texto: `zyjs` refusa programas que los dos motores Rust
ejecutan.

### Qué hay que decidir

¿Un operador de formato admite espacios entre sus piezas (`#.`, la cuenta, el
`|`)? Si sí, `zyjs` los salta. Si no, los dos Rust los refusan. Hasta decidirlo no
hay celda: cualquier verde elegiría por el autor.

*Decidido el 2026-09-16:* **no, el operador va junto.** `#.2|v|` es un símbolo,
como `$+` o `>>`.

### Corregido el 2026-09-16 (paso 3.1c)

Medido antes: ningún `.zy` del workspace ni ningún documento escribe un espacio
dentro de un operador de formato, así que nada dependía de la permisividad.

El parser de Rust comprueba ahora que las piezas se tocan —el fin de una en bytes
es el principio de la siguiente—: el operador, el `.` o `!` de la precisión, la
cuenta y el `|` que abre el valor. Un blanco o un comentario entre dos piezas se
refusa con el diagnóstico de la pieza que no está donde debe, que son los mismos
textos que `zyjs` ya daba: ningún mensaje nuevo.

| forma | los tres motores |
|---|---|
| `#. 2\|v\|`, `#! 2\|v\|`, `#./*c*/2\|v\|` | `expected a decimal count after '#.'` (o `'#!'`) |
| `#,. 2\|v\|`, `#^! n\|v\|` | `expected a decimal count after '#,'` (o `'#^'`) |
| `#.2 \|v\|` | `expected '\|' after precision` |
| `#, .2\|v\|`, `#,.2 \|v\|`, `#, \|v\|` | `expected '\|' after format operator '#,'` |
| `#.2\| v \|` | corre: los blancos son del valor |

Texto, ayuda y línea coinciden en los tres; en cinco formas la columna de `zyjs`
es la del operador y no la de la pieza, de la familia registrada en
[[ZYJS-024]]. `GUIDE.md` § Number Formatting lo documenta («An operator is
written together»). Las doce formas correctas —`#.2`, `#.n`, `#!2`, `#!n`,
`#,.2`, `#,.n`, `#,!2`, `#,!n`, `#^.2`, `#^.n`, `#^!2`, `#^!n`— siguen corriendo
igual en los tres. `cargo test` 1039/0, el formateador P1–P4 sin fallos.

### Qué lo sujeta

Cinco celdas en `syntax-format-convert`, verdes: `blank-inside-a-round-operator`,
`blank-before-the-bar-of-a-round`, `blank-inside-a-format-operator`,
`comment-inside-a-round-operator` y `blanks-inside-the-bars-are-the-value`.

---

## GLB-032 — REFERENCE y GUIDE prometen capturar un error blando con `:! ##Tipo`, y ningún motor lo hace

**Estado:** **decidido y corregido el 2026-09-16** (paso 3.2c): estaban mal las frases
**Encontrado por:** el paso 3.2, 2026-09-16

`interpreter/REFERENCE.md` (§ soft errors): *«test it with `$!`, propagate it with
`$!!`, or catch it with `!? … :! ##Kind`»*. `GUIDE.md` (§ standard library):
*«that you test with `$!` or catch with `!?`»*.

Medido en los tres motores, un error blando no se captura nunca con `:!`:

- dentro de un `!?`, el valor no se lanza y el `:!` no se ejecuta;
- con `v$!!` dentro de una función, el error vuelve al llamante **como valor**
  (`>> f()` imprime `##IO(…)`), y el `:!` que rodea la llamada no lo ve;
- con `v$!!` en el nivel superior, el programa termina ([[ZYJS-027]]).

`LLM.md` § 9 y la cabecera de `axes/runtime-errors.toml` (medida el 2026-09-14)
dicen lo contrario que las dos frases: un error blando es un valor, «a `:!`
never sees them, because nothing was thrown».

### Qué hay que decidir

¿Están mal las dos frases —se corrigen para decir que un error blando se
comprueba con `$!` y se propaga con `$!!`, pero no se captura con `:!`— o está mal
el comportamiento, y un `$!!` debería **lanzar** el error para que un `:!` lo
capture?

*Decidido el 2026-09-16:* **están mal las frases.** El comportamiento de los tres
motores es el del lenguaje, y es lo que ya decía `LLM.md` § 9.

### Corregido el 2026-09-16 (paso 3.2c)

Buscadas todas antes de tocar ninguna, eran **tres** y no dos:

- `REFERENCE.md` § soft errors: *«or catch it with `!? … :! ##Kind`»* → se
  comprueba con `$!` y se propaga con `$!!`; es un valor, así que un `:!` no lo ve,
  ni siquiera uno que rodee la llamada.
- `GUIDE.md` § convención de errores de la biblioteca: *«that you test with `$!` or
  catch with `!?`»* → se comprueba con `$!`; `!? … :!` no lo captura.
- `GUIDE.md` § `std/db`: *«catchable with `!? … :! ##DB`»*, la misma promesa para
  `##DB`, que no nombraba la ficha.

`REFERENCE.md` línea 526 dice que un error *lanzado* se captura con `!?`, y es
verdad; no se toca. El ejemplo de § Try / Catch / Finally tiene un `:! ##IO` entre
varios `catch` tipados: es sintaxis válida y no afirma nada sobre errores blandos.
La suite de GUIDE sigue con sus tres fallos de siempre.

---

## GLB-033 — Los mensajes de error nombran los tipos con un vocabulario que `#?` ya no usa

**Estado:** **corregido el 2026-09-18** (paso 3.5, en cinco sub-pasos)
**Encontrado por:** el paso 3.4, 2026-09-16, cerrando [[ZYTW-004]]

`#?` nombra los tipos igual en los tres motores. Los mensajes de la biblioteca
estándar y de varios operadores los nombran con otro vocabulario, también igual
en los tres:

| valor | `#?` | mensajes de error |
|---|---|---|
| `[1, 2]` | `##]` | `##[]` |
| `#[1, "x"]` | `##[` | `##[]` |
| `(1, 2)` | `##)` | `##()` |
| `#(k: 1)` | `##(` | `##(name:)` |
| `x -> x` | `##->` | `##fn` |

Los escalares (`###`, `##.`, `##"`, `##'`, `##?`, `##_`) coinciden. La diferencia
está en las colecciones y las funciones: la taxonomía de `#?` es la de v0.0.9
(`zymbol-design/COLLECTIONS.md`) y los helpers que construyen los mensajes
—`Value::type_name()` en el TW, `Value::zymbol_type_name()` en la VM, y seis
literales en `zyjs`— son anteriores. Se usan en unos 90 sitios de Rust.

No es una divergencia entre motores —las celdas están de acuerdo—, así que el
gate no lo ve. Es un diagnóstico que dice `cannot bind ##[]` a quien, preguntando
con `#?`, oye `##]`.

### Qué hay que decidir

¿Los mensajes pasan a nombrar los tipos como `#?` (`##]`, `##[`, `##)`, `##(`,
`##->`), en los tres motores? ¿O se quedan como están?

*Decidido el 2026-09-16:* **con nombres, como el analizador** —ni los símbolos
de `#?` ni los antiguos—. Y con él, lo que faltaba para escribirlos en ejecución:

| valor | nombre en un mensaje |
|---|---|
| escalares | `Int` `Float` `String` `Char` `Bool` `Unit` `Error` |
| `[1, 2]` | `[Int]`, calculado de los elementos |
| `#[1, "x"]` | `[Any]` |
| `[]` | `[?]` |
| `[[1], [2, 3]]` | `[[Int]]` |
| `(1, "a")` | `(Int, String)` |
| `#(k: 1)` | `#(k: Int)` — y el analizador pasa a decirlo así también |
| una función o una lambda | `Function` |

Decidido a la vez para el paso 3.5: los mensajes que el TW escribía con `{:?}`
(`got Float(1.5)`) usan **la redacción específica del TW con el nombre del tipo**
en los tres motores (`step must be an integer, got Float`); la VM deja su
genérico `this needs X and got Y`.

Sub-pasos: 3.5a nombrador y los `{:?}` del TW · 3.5b la VM · 3.5c `zyjs` · 3.5d la
biblioteca estándar (`##[]`, `##fn`) · 3.5e el diccionario en el analizador.

### 3.5a — 2026-09-16

`zymbol_common::typeword` guarda la tabla, con las reglas de las colecciones en
un solo sitio; el TW la usa con `Value::type_label()`. Los 39 mensajes del TW que
formateaban un valor con `{:?}` escriben su tipo: `map requires array, got
#(k: Int, j: [Int])`, `$/ requires a string on the left, got [?]`. Los otros
cuatro `{:?}` del TW no formatean un valor (un operador del AST, una ruta, la lista
de tipos de `mat::`, que es del 3.5d).

El TW tenía ya otros dos nombradores, y quedan para los sub-pasos que tocan a su
contraparte: `type_ident` (`Int`, `Array` — el de la VM) y `type_word` (prosa:
`integer`, `lambda`).

Medido: ZyDDT sigue en 258, como se esperaba —la VM aún dice otra cosa—; en tres
celdas `WORDING` el TW y `zyjs` ya dicen lo mismo (`index-must-be-an-integer-got`,
`range-bounds-must-be-integers-got-and`, `step-must-be-an-integer-got`).
`cargo test` 1040/0, consensus 660/0, `reject`, `expect`, el inventario y las
siete aplicaciones, en verde.

### 3.5b — 2026-09-16

La VM deja su genérico `this needs X and got Y` en 50 sitios y dice lo que dice
el TW, con `Value::type_label`. Lleva variante propia, `VmError::TypeMsg`, para
no perder la familia `##Type` que daba `TypeError`. Dos instrucciones nuevas de
comprobación —`CallableCheck`— dan las palabras del TW a `5 |> v` y a `v[1](2)`,
y map/filter/reduce comprueban la función **antes** del array, como el TW: eso
corrigió además un comportamiento, `[] $> 5` respondía `[]` en la VM.

Un texto por fallo (decidido el 2026-09-16): la VM compila `v[1]` y `v[1>1]` a
una sola instrucción, así que los dos textos que tenía el TW para cada fallo
pasan a ser uno —`cannot index into X — expected array, tuple, or string`,
`index must be an integer, got X`— y `a String addresses a dictionary key, and
this is X` cubre ahora también `v["k"]` sobre una lista. ZyDDT 258 → 226.

### 3.5c y 3.5d — 2026-09-18

`zyjs` dice ya, en los mismos términos, lo que dicen los dos Rust en los
operadores de colección y de orden superior: una tabla por operador sustituye a
`${op} not supported on ${tipo}` en veinte sitios, y `typeLabel` nombra el tipo
como el analizador.

Y la barrida de este hallazgo: **ningún mensaje de los tres motores nombra ya un
tipo con un símbolo**. Cambian los patrones de desestructuración (`[ … ]`,
`( … )`, `#(…)`), el punto sobre lo que no es un diccionario, `$~`, `$*`,
`term::width`, `@~`, `db: cannot bind` y `mat::`, que además volcaba el `Debug`
de una lista de símbolos (`["##\""]`). Un golden del corpus lo recogía y se
regrabó: `mat::sqrt: incompatible argument type(s) String`.

Por el camino, dos correcciones de camino y un hallazgo: en `zyjs`, `v[1]$~ 9`
sobre un Int llegaba a la aritmética de índices y decía `tuple index out of
bounds`, y ahora dice lo que dicen los otros dos; y [[ZYJS-028]], que **acepta**
`"ab"$* 1.5` y `"ab"$* -1`, que los dos Rust refusan.

ZyDDT 226 → 202. `cargo test` 1040/0, consensus 660/0, `reject` 42/42, `expect`
634+26 (con ese golden), el inventario sin nada nuevo, las siete aplicaciones,
los 216 ejemplos, `test_check`, `test_agents`, `test_manual` y el barrido de
parseo de los 1189 `.zy`, idéntico.

### 3.5e — 2026-09-18

El analizador nombra el diccionario `#(k: Int)`, como se escribe y como lo
nombran ya los mensajes de ejecución; decía `(k: Int)`, que se lee como una
tupla posicional con etiquetas. Cambia en los dos sitios que lo construyen: el
`ZymbolType::name` de `zymbol-semantic` y el `operandTypeName` de `zyjs`.

Con esto el hallazgo queda cerrado: **un solo vocabulario de tipos en los tres
motores, en los mensajes de ejecución y en los del analizador**. El eje
`operator`, que es el que más los nombra, está en 252 de 252.

Medida final del paso 3.5 completo: la matriz baja de 258 rojas a **198**.

---

## GLB-034 — Llamar a un nombre que no guarda una función: tres textos, y el del TW dice que no existe

**Estado:** abierto — sin decisión
**Encontrado por:** el paso 3.5b, 2026-09-16, dando a la VM los textos del TW

```zymbol
t(v) {
    <~ v(2)
}
>> t(5) ¶
```

| motor | |
|---|---|
| `zytw` | `undefined function: 'v'` |
| `zyvm` | `this needs Function and got Int` |
| `zyjs` | `'v' is not a function` |

`v` sí está definido: es un parámetro, y vale 5. El texto del TW manda a buscar
una función que no falta.

Cuando el callee es una **expresión** (`v[1](2)`) los tres dicen ya
`expression is not callable` (paso 3.5b). Este es el caso del **nombre**, que el
compilador de la VM distingue —no emite `CallableCheck` para él, a propósito—
porque los tres lo dicen de forma distinta y no hay decisión.

### Qué hay que decidir

¿Qué dicen los tres? `'v' is not a function` (lo de `zyjs`, que es lo único
cierto de los tres), `expression is not callable` (un solo texto para llamar a lo
que no es función), u otro.

### Qué lo sujeta

`runtime-functions-hof/a-name-that-holds-something-else-is-called`, roja.

---

## GLB-035 — `°x` indexado: los dos motores Rust hablan del prefijo y `zyjs` de la asignación indexada

**Estado:** abierto — hace falta decisión (F3, encontrado por el paso 3.6)
**Encontrado por:** paso 3.6, 2026-09-19, barriendo las formas vecinas de `GLB-027`
**Familia:** `GLB-027` (el nombre caliente indexado), pero el prefijo, no el sufijo

Con `x = [1, 2]`:

| forma | `zytw` / `zyvm` | `zyjs` |
|---|---|---|
| `°x[1] = 5` | `'°name' is only valid as an assignment target` <br> help: `use '°x += n' to anchor accumulation above the nearest loop` | `indexed assignment does not exist: 'x[…] =' is not a form of Zymbol` <br> help: `use 'x[i]$~ value' to modify in place …` |
| `°x[1] 5` | el mismo rechazo del prefijo | **lo ejecuta** y no dice nada |
| `>> °acc[1] ¶` dentro de `@` | imprime `10` | `` `°` has no effect in output context — use `>> x ¶` `` |

Tres desacuerdos en tres formas. El primero es el que importa: **el de `zyjs` es
el mejor de los dos** —`°x[1] = 5` es la asignación indexada, y lo que hay que
decirle al lector es que esa forma no existe, no dónde puede ir un `°`—, pero
el de Rust tampoco es falso. El segundo es la familia
`refusal/stray-literal-statement`. El tercero es una divergencia de
comportamiento: el TW lee `°acc[1]` y `zyjs` refusa el `°` en `>>`.

El paso 3.6 **no lo tocó**: `°x` no llega a `parse_expr_or_edit_statement` en
Rust —su rama no acepta operadores `$`— y el arreglo del sufijo no lo movió.

### Qué hay que decidir

Si `°x[…]` se rechaza por lo que es (asignación indexada, el texto de `zyjs`) o
por dónde está el `°` (el texto de Rust), y si `>> °x[1] ¶` lee o se rechaza.

### Qué lo sujeta

Nada todavía: no hay celda. Las formas están medidas en los tres motores.

---

## GLB-036 — Un corchete de índice sin cerrar en posición de expresión: Rust y `zyjs` eligen distinta ayuda

**Estado:** abierto — sin decisión pendiente (F3, encontrado por el paso 3.6)
**Encontrado por:** paso 3.6, 2026-09-19
**Gravedad:** baja: el mismo texto, distinta ayuda; ninguna de las dos es falsa

`>> x[1 = 2 ¶` y `y = x[1 = 2` — el índice no trae `>`:

| | texto | ayuda |
|---|---|---|
| `zytw`, `zyvm` | `expected ']' after index` | `array indexing must use brackets: arr[index]` |
| `zyjs` | `expected ']' after index` | `array indexing must use brackets: arr[index] or arr[i>j]` |

Los dos motores tienen las **mismas dos** ayudas y las reparten distinto. Rust
decide con `is_nav_index`, una mirada adelante antes de consumir el `[`, así que
para un índice sin `>` da la ayuda llana; `closeNav` de `zyjs` da la del
navegador siempre que no sea un destino de tubería ni una extracción.

Con un `>` dentro (`>> m[1>1 ¶`) los dos dan la del navegador y coinciden — es
lo que hace verde a `syntax-index-nav/navigation-left-open`.

El paso 3.6 alineó las **rutas de sentencia** de los dos motores con esta misma
regla (`x[1 2] = 5`, `x°[1 = 2`, `x[1>2 3] = 5` coinciden ahora en los tres), y
al hacerlo dejó a la vista que la ruta de expresión no la sigue.

### Qué hay que decidir

Nada de diseño: es cuál de las dos reparte bien. Si la regla es la de Rust
—ayuda del navegador sólo cuando el índice navega—, `closeNav` tiene que
preguntar lo mismo que ya pregunta la rama de sentencia de `zyjs`.

### Qué lo sujeta

Nada todavía: `syntax-index-nav/navigation-left-open` sólo cubre el caso con `>`,
que coincide. Hace falta una celda para el caso sin `>` en posición de expresión.

---

## GLB-037 — El formateador sabe reimprimir `arr[i] = val`, una forma que ya no se puede construir

**Estado:** abierto — sin decisión pendiente (F3, encontrado por el paso 3.6)
**Encontrado por:** paso 3.6, 2026-09-19, al borrar el desazucarado muerto
**Gravedad:** baja: código inalcanzable, pero es la forma retirada escrita en un motor

`AssignSugar::IndexedAssign` y `AssignSugar::IndexedCompound(op)`
(`zymbol-ast/src/variables.rs:29,31`) las construía **sólo** el desazucarado de
la asignación indexada, que el paso 3.6 retiró por muerto: la decisión 6 la había
dejado inalcanzable y nadie la había borrado. Las dos variantes siguen ahí, y
con ellas sus lectores:

- `zymbol-formatter/src/visitor.rs:553,565` — sabe reimprimir un `Assignment`
  marcado así **como `arr[i] = val`**, que es la forma que el parser refusa.
- `zymbol-compiler/src/lib.rs:1516` — las trata aparte.
- `zymbol-bytecode/src/lib.rs:401` — un comentario que explica cómo el TW las
  distingue.

Nada puede construirlas ya, así que no es un fallo observable. Es lo mismo que
GLB-027 una capa más abajo: una regla cuya razón se borró es indistinguible de
una que nadie puede justificar, y aquí lo que quedó escrito es la forma retirada.

### Qué hay que decidir

Si se borran las dos variantes y sus cuatro lectores, o se quedan con una nota
que diga que están muertas. Toca cinco crates, así que no se hizo dentro del
paso 3.6.

### Qué lo sujeta

Nada: no hay forma de provocarlas. `zymbol fmt` sobre el corpus no las alcanza —
`zyq suite --only fmt` da P1–P4 sin fallos.

---

## GLB-038 — La recuperación de cadena del lexer se come el resto del fichero, y el TW y la VM informan de errores distintos del mismo módulo

**Estado:** abierto — hace falta decisión (F3, encontrado por el paso 3.7)
**Encontrado por:** paso 3.7, 2026-09-19, midiendo lo que quedaba de la cascada
**Familia:** `GLB-028`, pero no se arregla con ella

`skip_rest_of_string` corre hasta la comilla de cierre **o hasta el final del
fichero**. Cuando no hay comilla de cierre se lleva todo lo que queda, llaves
incluidas, y el parser se queda sin cerrar bloques que sí estaban cerrados:

```
# lexico {
    #> { f }
    f() {
        <~ "abc
    }
}
```

| | |
|---|---|
| `zytw` | `failed to parse module: 1 lexer error(s)` — `unmatched '}' in string` @4:12 |
| `zyjs` | lo mismo |
| `zyvm` | `failed to parse module: 1 parse error(s)` — `expected '}' to close block` @7:1 |

Los dos diagnósticos existen en los dos motores Rust; lo que difiere es **cuál
informa cada cargador de módulos**. El TW da el del lexer y para; la VM da el del
parser, que es el *segundo*. Con `zymbol check` salen los dos.

No lo cierra el filtro del paso 3.7 (causa 5): ese descarta lo que señala un
token `Error`, y éste señala el final del fichero.

Vecino, con la misma raíz y sin celda: `>> "a{b ¶` — sin comilla de cierre — da
`invalid character in string interpolation` en Rust (por el `¶`) y
`unterminated string interpolation` en `zyjs`.

### Qué hay que decidir

Hasta dónde recupera el lexer cuando una cadena no cierra. El salto de línea no
sirve de tope: una cadena de Zymbol puede abarcar varias líneas a propósito. Y,
aparte, cuál de los dos diagnósticos informa un cargador de módulos, que hoy no
es el mismo en los dos motores Rust.

### Qué lo sujeta

`runtime-modules-scripts/module-with-lexer-errors`, roja — y roja por la
divergencia TW/VM, no por la cascada.

---

## GLB-039 — Dos reglas del analizador sobre el mismo nombre: no puedes verlo, y además no existe

**Estado:** abierto — sin decisión pendiente (F3, encontrado por el paso 3.7)
**Encontrado por:** paso 3.7, 2026-09-19
**Gravedad:** baja: los dos textos son ciertos, pero el segundo desmiente al primero

```
? #1 { _t = 1 }
>> _t ¶
```

| | |
|---|---|
| `zytw`, `zyvm` | `cannot access underscore variable '_t' from outer scope` **y** `undefined variable '_t'` |
| `zyjs` | `undefined variable '_t'` |

El primero dice que el nombre existe y no se alcanza; el segundo, que no existe.
Un lector que arregle el segundo borra la declaración que el primero señala. Es
el analizador, no el parser: la cascada del paso 3.7 no lo toca.

La celda `isolation/underscore-is-invisible-outside` está **verde**: el gate
compara el veredicto y los dos motores llegan a `error`. Lo que no ve es que uno
llega con dos textos y el otro con uno.

### Qué hay que decidir

Cuál de las dos reglas habla cuando las dos aciertan. `zyjs` da la menos precisa
de las dos; el texto bueno es el primero de Rust.

### Qué lo sujeta

Nada: la celda es verde. Haría falta una que compare el número de diagnósticos.

---

## GLB-040 — `wording.baseline` lleva 23 líneas sin decidir

**Estado:** abierto — hace falta decisión (arnés, encontrado por el paso 3.7)
**Encontrado por:** paso 3.7, 2026-09-19

`ZyDDT/wording.baseline` dice de sí mismo que «puede encoger sola, y nunca puede
crecer sola: una línea que aparezca aquí sin haberse escrito a propósito es un
mensaje nuevo de un solo lado». Tiene 9 entradas. Hoy hay **23** celdas en
`WORDING`, y **8** de las 9 registradas ya no lo están.

O sea: el fichero no se regraba desde hace varios pasos, y las 23 «NEW WORDING»
que imprime `zyddt axis` son 23 decisiones que nadie ha tomado. Tres son del
paso 3.7 (las tres de `syntax-control-flow` que pasaron de `DIVERGE` a `WORDING`
al retirarse la cascada); las otras 20 vienen de antes.

No se regrabó en el paso 3.7 **a propósito**: `--regen-baseline` absorbería de
una vez las 20 ajenas, que es exactamente contra lo que el fichero avisa.

### Qué hay que decidir

Si se regraba la línea base entera —y entonces las 23 quedan aceptadas de golpe—
o se repasan una a una. Y, si es lo segundo, si el gate debería quejarse de que
lleva 23 pendientes, porque hoy no se queja de nada.

---

## GLB-041 — `@! etiqueta` parece un salto con etiqueta y es un salto pelado más un nombre tirado

**Estado:** abierto — hace falta decisión (F3, encontrado por el paso 3.8)
**Encontrado por:** paso 3.8, 2026-09-19, al encender el analizador dentro de `>>| { … }`
**Clase:** 1 — los tres coinciden, y los tres se quedan cortos

El salto con etiqueta se escribe **`@:etiqueta!`** y **`@:etiqueta>`**: la
etiqueta va DENTRO del salto, y el lexer la lee como un solo token
(`AtColonLabelBreak`). Escrita aparte, `@! etiqueta` es otra cosa: un `@!`
pelado —que sale sólo del bucle más interno— seguido de un identificador suelto
que se lee y se tira.

| lo escrito | lo que pasa |
|---|---|
| `@:principal!` | sale de los dos bucles. `n` = 1 |
| `@!` | sale sólo del interno; el `@:principal {` sin condición no termina nunca |
| `@! principal`, con `principal` **sin definir** | `undefined variable 'principal'` en ejecución, en los tres motores |
| `@! principal`, con `principal` **definido** | `warning: this statement does nothing: 'principal' is read and discarded`, y corre haciendo lo del `@!` pelado |

La última fila es la que importa: **el programa corre, hace lo que no se quiso,
y el único aviso habla de una lectura inútil sin mencionar que a dos caracteres
de ahí está el salto que el lector creía escribir.** Los tres motores dan el
mismo aviso, así que ningún diferencial lo ve.

Apareció porque `ZyBank/pantalla/tui.zy:595` lo escribía así, en la tecla `q`
de salir y **dentro de un `>>| { … }`**, que es justo donde el analizador de
Rust no entraba ([[GLB-030]]). Corregido allí el 2026-09-19 por decisión del
autor: comprobado que `@:principal!` sale de los dos bucles y que `@!` deja el
exterior girando. Es la **única** ocurrencia en todo el workspace; las otras
cuatro coincidencias son comentarios.

### Qué hay que decidir

Si `@!` o `@>` seguidos de un identificador **en la misma línea** se refusan,
con una ayuda que enseñe `@:nombre!`. Hoy son dos sentencias legales que juntas
no hacen nada de lo que parecen.

### Qué lo sujeta

Nada todavía: no hay celda, y el aviso que sale no distingue este caso de
cualquier otro nombre tirado.

---

## GLB-042 — Los mensajes de `>>~` nombran el valor, y la VM llama «ms» a lo que los otros dos llaman «duration»

**Estado:** abierto — sin decisión pendiente (F3, encontrado por el paso 3.8)
**Encontrado por:** paso 3.8, 2026-09-19, midiendo las formas vecinas de `>>~` y `@~`
**Familia:** `GLB-033` (los tipos en los mensajes), cerrado en el paso 3.5

Dos restos en la misma zona:

| forma | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| `>>~ ("fila", 1) > "A"` | `>>~ slot expects Int, got fila` | igual | igual |
| `>>~ (2.5, 1) > "A"` | `>>~ slot expects Int, got 2.5` | igual | igual |
| `@~ -5` | `@~ requires non-negative **duration**, got -5` | `@~ requires non-negative **ms**, got -5` | como el TW |
| `@~ "medio"` | `@~ requires integer milliseconds, got String` | igual | igual |

1. **`>>~ slot` nombra el valor.** GLB-033 lo dejó escrito: los mensajes dicen el
   tipo, nunca el valor. Debería ser `got String` y `got Float`. Los tres lo
   hacen igual —`to_display_string()`, `{got}`, `this.display(v)`— así que
   ningún diferencial lo ve.
2. **La VM dice «ms» donde el TW y `zyjs` dicen «duration».** Una palabra, en un
   mensaje de ejecución que el gate no compara.

`@~ requires integer milliseconds, got String` sí está bien en los tres.

### Qué hay que decidir

Nada de diseño: es aplicar GLB-033 a `>>~ slot` y que la VM copie la redacción
del TW, que es la regla («un mensaje se redacta como el TW redacta esa
operación»).

### Qué lo sujeta

Nada: no hay celda para ninguna de las cuatro formas.

---

## GLB-043 — El aviso de cambio de tipo: Rust infiere el lado derecho y `zyjs` sólo compara literales

**Estado:** abierto — hace falta decisión (F3, encontrado por el paso 3.8)
**Encontrado por:** paso 3.8, 2026-09-19, al medir el impacto de [[GLB-030]]
**Decisión del autor (2026-09-19):** aceptar y regrabar la línea base de paridad.

```zymbol
trazo = " .:-=+*#%"
marca = "@"
marca = trazo[1]      // String → Char
```

| | |
|---|---|
| `zytw`, `zyvm` | `warning: type mismatch: 'marca' was String but assigned Char` |
| `zyjs` | nada |

Los dos tienen la regla. `zyjs` sólo la aplica **literal contra literal**, y lo
declara en su propio comentario: *«Only literal-to-literal is decided without
inference, which is the same limit the condition check works under»*. Rust
infiere el lado derecho, así que ve el `trazo[1]`.

Sale a la luz con [[GLB-030]]: la asignación vive dentro de un `>>| { … }` en
los **110** ficheros de `mandelbrot`, y al encender el analizador allí la
paridad de cada uno pasa de `0 2` —dos avisos de rango que sólo daba `zyjs`— a
`1 0`, el de cambio de tipo que sólo da Rust. **Por fichero la divergencia baja
de dos a una**, pero `web/tests/test_check.mjs` cuenta cualquier dirección y
cantó 110 regresiones.

La línea base se regrabó el 2026-09-19 con esta causa escrita aquí, igual que se
hizo con `emoji.zy` en el paso 2.17: la divergencia la sujeta esta ficha, no un
número en un fichero. El diff son exactamente 110 filas, todas de `mandelbrot`,
y ninguna otra se movió.

### Qué hay que decidir

Hasta dónde infiere el analizador de `zyjs` en el lado derecho de una
reasignación. Estrechar Rust no se hizo: perdería un aviso cierto que ya daba
fuera de los bloques TUI.

### Qué lo sujeta

`web/tests/check_parity_baseline.txt`, 110 filas en `1 0`. No hay celda.

---

## GLB-044 — La familia `##` de un error: el TW la leía de las palabras y los otros dos la llevaban

**Estado:** **corregido 2026-09-19 (paso 4.1)**
**Encontrado por:** el eje `runtime-collection-ops` lo declaraba en su propia
cabecera desde que se escribió: *«which family these belong to is not decided
(the tree-walker answers `##_`, the VM `##Type`)»*
**Decisión del autor:** D1 — tipo equivocado → `##Type`, valor equivocado →
`##Index`. Y el mandato del paso: **alinear los tres motores**.

### Lo que se midió antes de tocar nada

Las 84 celdas `-met` rojas —la mitad de toda la matriz— no eran un problema sino
**dos**:

| | celdas | |
|---|---|---|
| **A — sólo discrepan en la familia** | **44** | este paso |
| **B — algún motor no falla** (`zyjs` imprime `[1, 2]`, `abc`, `[]`…) | 40 | la tabla de tolerancia de D2, paso 4.3 |

Aplicando D1 a las 44, la tabla sale sin ambigüedad: **41 son `##Type`** —
`filter requires array, got X`, `cannot index into X`, `expression is not
callable`, `index must be an integer, got X`— y **3 son `##Index`**, porque el
tipo es correcto y el valor no: `$* repetition count must be non-negative`,
`decimal count must not be negative`, y `range indices in nav path must be
positive integers` (`v[1>-1..2]`).

Frente a ese objetivo:

| motor | ya correcto | había que cambiar |
|---|---|---|
| `zytw` | **0** | 44 |
| `zyvm` | 40 | 4 |
| `zyjs` | 1 | 43 |

### Por qué el TW estaba a cero

Los tres motores comparten **una regla por palabras** —
`zymbol_common::errkind` y `errorKindOfMessage`— documentada como el único sitio
donde vive esa fragilidad. Pero los otros dos llevan **además** la familia en el
sitio donde se levanta el error: la VM en la variante (`VmError::TypeMsg`) y
`zyjs` en `ZyRuntimeError(msg, kind)`. Cuando hay familia declarada, gana; si no,
se leen las palabras.

**Al TW le faltaba esa mitad entera.** Y la regla por palabras no puede
distinguir `index must be an integer` —un TIPO equivocado— de `index out of
bounds` —un VALOR—: «index» casa antes que «type», y por eso siete celdas de
tipo caían en `##Index` sin que nadie pudiera corregirlas sin romper las otras.

### Lo que se hizo

- **`zytw`**: variante `RuntimeError::Kinded { kind, inner }`, que **envuelve**
  en vez de añadir un campo, para que los ~200 sitios que no tienen nada que
  declarar sigan sin declarar nada y los lea la regla por palabras. Anotados
  **57 sitios**, con `RuntimeError::kinded("Type"|"Index", …)`.
- **`zyvm`**: variante `IndexMsg(String)`, la gemela de `TypeMsg` para el valor
  equivocado — no existía ninguna que llevara un mensaje a `##Index`, así que
  los dos casos de valor contestaban `##Type`. Y cuatro sitios más movidos de
  `Generic` a `TypeMsg`.
- **`zyjs`**: 37 sitios pasan de `ZyError` a `ZyRuntimeError(msg, '##Type')`,
  incluida la tabla `NOT_SUPPORTED` entera, que da trece mensajes desde un solo
  `throw`, y las ocho llamadas a `notPositionalMsg`. Un sitio que ya declaraba
  `'##_'` a mano pasa a `'##Type'`.

### Resultado

**`zytw` 44/44, `zyvm` 44/44, `zyjs` 43/44.** Matriz: **43 celdas en verde,
ninguna nueva roja**, 170 → **127** ids rojos. `runtime-format-convert` pasa de
8 divergencias a **0**.

La que queda es `cannot-index-into-during-deep-update`, y no es de familia: ver
[[GLB-045]].

**Puertas:** `cargo test` 1040/0; consensus 660/0; reject 42/42; expect 634+26,
0 stale; messages, project, fmt y guide en línea base; las seis suites de `web/`
en verde; barrido de parseo de `zyjs` idéntico sobre 2810 `.zy`.

---

## GLB-045 — Escribir en profundidad dentro de algo que no es colección: tres motores, tres mensajes, y el de `zyjs` es falso

**Estado:** abierto — hace falta decisión (F4, encontrado por el paso 4.1)
**Encontrado por:** paso 4.1, 2026-09-19, la única celda `-met` que no se alineó
**Clase:** 2 — los tres difieren entre sí

Con `v = [1, 2]`:

| forma | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| **leer** `>> v[1>1] ¶` | `cannot index into Int — expected array, tuple, or string` | igual | igual |
| **escribir** `v[1>1]$~ 9` | `cannot index into Int during deep update` | `$~ writes into a collection, and this is Int` | `tuple index out of bounds: index 1 for tuple of length 0` |

La lectura la unificó el paso 3.5b y coincide palabra por palabra. La escritura
no la unificó nadie, y **el mensaje de `zyjs` es falso**: habla de una tupla
donde hay un array, de longitud 0 donde hay dos elementos, y de un índice fuera
de rango cuando el índice 1 existe. Lo que pasa es que el segundo paso del
camino (`>1`) cae sobre el `Int` que hay en la posición 1.

Con un `v` realmente anidado (`[[1, 2], [3, 4]]`) los tres escriben igual y bien.

Por eso su celda `-met` es la única de las 44 que no se pudo alinear: no es la
familia lo que difiere, es el fallo.

### Qué hay que decidir

Un texto para el fallo, como ya lo tiene la lectura. El del TW nombra la
operación («during deep update») y el de la VM nombra lo que hace falta
(«writes into a collection»); el de `zyjs` hay que retirarlo en cualquier caso.

### Qué lo sujeta

`runtime-collection-ops/cannot-index-into-during-deep-update` y su `-met`, las
dos rojas.

---

## GLB-046 — Las colecciones pasan a ser ESTRICTAS (D2 derogada), medido

**Estado:** **implementado 2026-09-20 (paso 4.3)**, salvo dos formas — ver [[GLB-048]]
**Encontrado por:** paso 4.2, midiendo las 40 celdas del grupo B
**Deroga:** D2 («colecciones tolerantes»). El autor: *«la permisividad es un
error, debería ser más estricto y solicitar expresiones correctas a sus valores;
eso hará que deban calcular más pero que sean más exactas las solicitudes»*.
**No se tocó ningún motor en este paso.**

### El sistema estricto ya existe: es el tree-walker

| motor | acepta, de las 40 formas |
|---|---|
| **`zytw`** | **0** |
| `zyvm` | 13 |
| `zyjs` | 34 |

Tres veces me engañó el arnés leyendo la PRIMERA línea de la salida: el TW
refusa `@ i:1..1.5` (`range end must be an integer, got Float`) y refusa
`C := 1` seguido de `C := 2` (`constant 'C' already declared`); lo que se veía
delante era un aviso. Con la última línea, el TW refusa las 40.

**Así que «estricto» no es un diseño nuevo: es hacer que la VM y `zyjs` se
comporten como el tree-walker.**

### Impacto en código real: cero

Barrido de **1164 programas** — corpus, ejemplos, `zyquality/project` y las
siete aplicaciones (GO, Chaturanga, serpiente, klingon_galaxy, ZyAudit, ZyBank,
GoL):

| | |
|---|---|
| pasan en el TW y en `zyjs` | 769 |
| pasan en el TW, fallan en `zyjs` por entorno (shell, `std/db`, TUI) | 207 |
| ficheros de módulo | 188 |
| **fallan en el TW** | **0** |
| **pasan en la VM o en `zyjs` y el TW los refusa** | **0** |

Ni un programa del workspace se apoya en la permisividad. Ninguna constante se
redeclara en código real. Ningún bucle real emite el aviso de límites.

### Lo que hay que cambiar, por motor

**`zytw`: nada.** **`zyvm`: 13 formas.** **`zyjs`: 34 formas.**

Las 40, agrupadas por lo que son:

**1 — El índice tiene el tipo equivocado** (8): `[1,2][1.5]$~ 9`,
`[1,2]$+["x"] 9`, `[1,2]$-["x"]`, los cuatro rangos con un extremo `"x"`,
`"abc"$~~["a":"b":"x"]`. La permisividad de `zyjs` aquí **destruye datos**:
`[1,2]$-["x"]` lee `"x"` como 0, resuelve la posición 1 y **borra un elemento**.

**2 — La operación no existe para esa colección** (3): `#(a:1)$+ 5`,
`#(a:1)$+[1] 2`, `#(a:1)$? 5`. `zyjs` **se inventa una clave llamada `null`**.

**3 — El índice está fuera de rango, con el tipo correcto** (7): `[1]$+[9] 2`,
`[1,2]$-[9]`, `[1,2]$[1..9]`, `[1,2]$-[1..9]` y sus gemelos de cadena y tupla.

**4 — El valor está mal con el tipo bien** (4): cuenta negativa, índice 0.
La VM lee `-1` como «todas» y **reemplaza la cadena entera**; lee el `0` como un
inicio válido y **borra todo**.

**5 — El operando tiene el tipo equivocado** (9): tanto las de escritura
(`"ab"$+ 5` → `ab5`) como las de consulta (`"ab"$? 5` → `#0`, `"a,b"$/ 5` →
`[a,b]`). **Las dos mitades pasan a error**: preguntarle a una cadena si
contiene un `5` no es una pregunta bien escrita.

**Y dos que no son tolerancia y entran igual** (decidido por el autor):

- `C := 1` / `C := 2` — el TW refusa, **la VM y `zyjs` imprimen `2`**.
- `@ (a, b):1..3` — desestructurar sobre un rango: la VM dice
  `unsupported construct: range outside loop` sobre un rango que **sí** está en
  un bucle, y **`zyjs` ni lo parsea** (`expected '{' to start block`). Es una
  forma del lenguaje que le falta a dos motores.

### El corte descendente: D3 sigue, sin marca nueva

Decidido: **el reverso es el reverso y el resto es error.** `a$[3..1]` construye
`[30, 20, 10]` en los tres; no se inventa ninguna grafía. El paso 4.4.

Medido en el camino, y hay un choque que decidir al implementarlo:

| forma | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| `a$[2..1]` (fin = inicio−1) | `[]` | `[]` | `[]` |
| `a$[2:0]` (cuenta 0) | `[]` | `[]` | `[]` |
| `a$[3..1]`, `a$[4..2]`, `a$[5..1]` | **error** | `[]` | `[]` |

El TW tiene un caso especial: **`fin = inicio−1` es el modismo de corte vacío**,
y `corpus/collections/16_slice_count_based.zy` lo empareja a propósito con
`$[2:0]` — su cabecera dice *«Every :count scenario is paired with its ..end
equivalent; outputs must match»*. Bajo D3, `a$[2..1]` pasa a `[20, 10]` y ese
par deja de ser equivalente. Los tres cortes descendentes que hay en todo el
código real son ese modismo (`$[2..1]`, `$[2..1]`, `$[4..3]`), así que es **un
fichero del corpus** el que hay que reescribir, no una aplicación.

### El bucle NO se toca

`@ i:3..1` cuenta hacia atrás y está bien. Comprobado: `3 2 1`. Hay seis bucles
descendentes literales en el corpus y ninguno en una aplicación. El autor:
*«ya esto está correctamente implementado»*.

### Implementado (paso 4.3, 2026-09-20)

| motor | aceptaba | acepta | idénticas al TW |
|---|---|---|---|
| `zyvm` | 13 | **2** | 18 → **34** de 40 |
| `zyjs` | 34 | **2** | **35** de 40 |

La segunda tanda cerró las redacciones de la VM: `as_int_for` nombra la
operación que pregunta (siete sitios donde decía `this needs Int and got
String`), la inserción y el borrado recuperan sus dos formas distintas, el
diccionario tiene sus propias palabras para `$+` y `$+[i]`, y `vm_deep_set`
distingue una escritura de UN paso de un camino.

Las dos que quedan son las mismas en los dos motores y están en [[GLB-048]]: el
rango de navegación y la constante redeclarada, que piden decisión y no puerto.

Lo sostienen guardas compartidos en cada motor —`needInt`, `needCharStr`,
`needInBounds` y `rangeBounds` en `zyjs`, `range_bounds` en la VM— para que los
operadores no puedan volver a separarse.

Matriz: **45 celdas en verde, ninguna nueva roja**, 127 → **82** ids rojos.
Puertas: `cargo test` 1040/0, consensus 660/0, reject 42/42, expect 634+26 sin
stale, project 7/7, fmt, examples 216/0, `test_check` sin regresiones, barrido
de parseo de `zyjs` idéntico sobre 2810 `.zy`.

### Qué lo sujeta

Las 40 celdas del grupo B: `runtime-collection-ops` 31, `runtime-index-nav` 5,
`runtime-loops-ranges` 3, `runtime-operators` 1.

---

## GLB-047 — Los mensajes de corte y de borrado por rango imprimían el desplazamiento interno

**Estado:** **corregido 2026-09-20 (paso 4.3)**
**Encontrado por:** paso 4.3, al ir a copiar los textos del TW a los otros dos

Cuatro mensajes del tree-walker nombraban números que el lector no había escrito:

| escrito | decía | dice ahora |
|---|---|---|
| `a$[3..1]` | `slice start (2) cannot be greater than end (1)` | `slice start (3) cannot be greater than end (1)` |
| `a$[4..2]` | `slice start (3) … end (2)` | `slice start (4) … end (2)` |
| `a$[1..9]` | `slice indices out of bounds: [0..9]` | `[1..9]` |
| `a$-[1..9]` | `$-[0..9] out of bounds for collection of length 3` | `$-[1..9] …` |

El **inicio** salía como el desplazamiento 0-based en que la función lo había
convertido y el **fin** salía crudo, así que la pareja mezclaba dos sistemas de
numeración y la relación que afirmaba —«2 no puede ser mayor que 1»— era cierta
sobre valores que no estaban en el programa.

Se corrigió **antes** de copiar los textos a la VM y a `zyjs`, que es lo que el
paso 4.3 hace: alinear sobre el TW habría extendido el defecto a dos motores
más. Los sitios guardan ahora lo escrito antes de normalizar.

Ningún golden los graba: son diagnósticos que ningún programa provoca, que es
para lo que existen los ejes de ZyDDT.

### El hermano que faltaba — 2026-09-22 (paso G3)

Esta corrección tocó la forma de **rango** y dejó intacta la de **cuenta**, que
seguía imprimiéndose con la grafía del rango: quien escribía `a$-[2:3]` leía
`$-[2..3] out of bounds for collection of length 3`, y `[2..3]` son dos
posiciones que sí caben en tres. No era el número lo que mentía esta vez, sino
el **signo entre los números**: `[i:n]` y `[i..j]` piden cosas distintas. Los
tres motores lo escriben ya como el lector lo escribió. Ver [[GLB-048]].

---

## GLB-048 — Lo que falta para que la VM sea estricta: dos formas que piden decisión

**Estado:** **cerrado el 2026-09-22.** Los puntos 1, 2 y 4 en el paso G2; el punto 3 en el G3, donde resultó ser **cinco** defectos y no uno
**Encontrado por:** paso 4.3, 2026-09-20

La VM pasó de aceptar 13 de las 40 formas a aceptar **2**. Las dos que quedan no
son puerto mecánico:

**1 — `v[1>3..1]`, el rango de navegación.** El TW dice
`invalid nav range 3..1 — indices are 1-based and start must be ≤ end`; la VM
devuelve `[]`. El compilador baja el paso con rango a un bucle
`i = inicio … fin` y, si el inicio supera al fin, el bucle sencillamente no
corre. Para refusarlo con el texto del TW hace falta **una instrucción nueva**:
la única que lanza, `RaiseError(StrIdx)`, sólo lleva una cadena fija del pool y
el mensaje necesita los dos números en ejecución.

*Qué hay que decidir:* una instrucción que lance con valores, o un texto sin los
números (y entonces el TW también lo pierde, porque el texto es uno).

**2 — `C := 1` seguido de `C := 2`.** El TW lo refusa en **ejecución**
(`constant 'C' already declared`); la VM y `zyjs` imprimen `2`. El compilador
trata `ConstDecl` como una asignación cualquiera: la constancia no existe en la
VM.

*Qué hay que decidir:* **dónde vive la regla.** Si va a `zymbol-semantic` la
heredan los tres motores y `check` la ve —es lo que se hizo con E014— pero pasa
a ser un error ESTÁTICO, y entonces la celda `-met` deja de poder atraparlo con
`!?`, porque un error estático no se atrapa. Si se queda en ejecución hay que
llevar la constancia hasta la VM.

**3 — `[1,2,3]$-[1:-1]`, la cuenta negativa.** El TW dice
`$-[..] count must be non-negative, got -1`; la VM informa de la otra mitad del
rango (`end must be positive`). El compilador **funde la cuenta en el fin**
(`AddInt` + `SubIntImm`), así que la VM no puede distinguir `$-[1:-1]` de
`$-[1..0]`. Es la misma falta que la 1: un guarda que lance con un valor de
ejecución, o una instrucción propia para la forma con cuenta.

**4 — `@ (a, b):1..3` y `v..3` sueltos.** La VM dice
`unsupported construct: range outside loop` sobre un rango que **sí** está en un
bucle, y `zyjs` ni lo parsea. Es una forma del lenguaje que le falta a dos
motores, no una permisividad.

### Medido en el paso G2 — 2026-09-22

**El punto 4 está cerrado, y el 2 también.** D4 y D5 (F5) hicieron estáticas las
dos formas: `zymbol check` refusa `@ (patrón):rango` en las cuatro grafías
—literal, agrupada, con paso, y con límites enteros válidos— y refusa el rango
suelto y la constante redeclarada. Sus tres celdas `-met` de `runtime-loops-ranges`
pasaron a `expect = "error"` en G2 y están verdes. Lo que ese camino dejó muerto
en el tree-walker es [[ZYTW-006]].

**El punto 1 no es lo que dice esta ficha, y hay que resolver la contradicción
antes de implementar nada.** Medido en los tres motores:

| forma | `zytw` | `zyvm` | `zyjs` |
|---|---|---|---|
| `[10,20,30,40]$[3..1]` corte descendente | `[30, 20, 10]` | `[30, 20, 10]` | `[30, 20, 10]` |
| `v[1>3..1]` navegación descendente | **error** `invalid nav range 3..1 …`, familia `##_` | `[]` | `[]` |
| `v[1>1..3]` navegación ascendente | `[10, 20, 30]` | `[10, 20, 30]` | `[10, 20, 30]` |

**D3 ya decidió esta forma, y dice lo contrario que esta ficha.** [[GLB-012]]
punto 2, decidido el 2026-09-15, en sus palabras: *«ni error ni vacío, sino
selección descendente … `[10, 20, 30, 40]$[3..1]` → `[30, 20, 10]`, **y
`v[1>3..1]` invierte igual, dando un array**»*. El paso 4.4 implementó D3 en el
**corte** y dejó fuera la **navegación**: hoy ningún motor cumple D3 ahí — el TW
la refusa y los otros dos dan vacío.

Así que lo que este punto 1 pide —una instrucción de la VM que lance con los dos
números para copiar el texto del TW— **implementaría un mensaje que D3 dice que
no debe existir**. Y la celda `runtime-index-nav/invalid-nav-range-indices-are-1-based`
pide `expect = "error"`, que es una premisa que D3 retiró: por eso no es del
grupo C del plan (una refusa que pasó a estática) sino una celda cuyo `expect`
contradice una decisión ya tomada.

**Resuelto el mismo día: vale D3 tal como está escrita.** La inversión se
implementó en los tres motores y el punto 1 queda cerrado — sin la instrucción
que lanza con valores que esta ficha pedía, porque con D3 ya no hay nada que
lanzar ahí. El detalle está en [[GLB-012]].

La celda pasó a `nav-range-written-downwards-selects-descending`, que pide `ok`,
y la mitad de la refusa que sobrevive —un límite 0— se quedó en una celda propia,
`nav-range-indices-are-1-based`. Esa nace **roja**, y no es una regresión: cae en
el mismo `WORDING` que `range-indices-in-nav-path-must-be` ya registraba, el TW
diciendo lo suyo y los otros dos `index 0 is invalid`. Es un camino que hasta
ahora no medía nadie.

**El punto 3 se cerró en el paso G3, y medirlo lo multiplicó por cinco.** La
ficha decía «la VM informa de la otra mitad del rango». Barrer las formas
vecinas —inicio y cuenta, en array, cadena y tupla, 23 casos— enseñó que los
**tres** motores estaban mal, cada uno de una manera:

| caso | `zytw` antes | `zyvm` antes | `zyjs` antes |
|---|---|---|---|
| `a$-[1:-1]` | correcto | **A**: dice `end must be positive, got -1` | correcto |
| `a$-[1:0]` | `[1,2,3]` | **B**: error, donde borrar nada es lo que pide | correcto |
| `a$-[2:3]` fuera | **E**: dice `$-[2..3]` | **C**: dice `$-[2..4]` | **D**: contesta `[1]` |
| `a$-[-1:1]` | correcto | correcto | **D**: borra desde el final |
| `a$-[4:1]` | correcto | correcto | **D**: deja el array intacto |

**A, B y C son la misma causa**, la que la ficha nombraba: el compilador fundía
la cuenta en el fin con `AddInt` + `SubIntImm`, así que la VM no podía
distinguir `$-[1:-1]` de `$-[1..0]` ni `$-[1:0]` de `$-[1..0]`. Y `B` dependía
del inicio — `$-[2:0]` pasaba y `$-[1:0]` no—, que es la firma de una cuenta
fundida. Se resolvió como el paso 4.4 resolvió el gemelo del corte: una
instrucción propia, `ArrayRemoveCount`, donde la cuenta viaja **como cuenta**.

**D es la estrictez de [[GLB-046]] sin aplicar**: `zyjs` usaba `splice`, que
recorta en silencio, así que un inicio o una cuenta que se pasan del final no
eran error. Ahora los refusa, con las palabras de los Rust.

**E es [[GLB-047]] sin aplicar a esta forma.** Aquella corrigió el rango; la
cuenta se quedó imprimiéndose con la grafía del rango. Quien escribía
`a$-[2:3]` leía «`$-[2..3]` out of bounds for collection of length 3», y
`[2..3]` son dos posiciones que **sí** caben en tres: el mensaje negaba lo que
el lector podía comprobar. Una cuenta se escribe `[i:n]` y un rango `[i..j]`
porque piden cosas distintas, y ahora el mensaje lo respeta en los tres motores.

Los 23 casos coinciden ahora en los tres.

### Qué lo sujeta

`runtime-collection-ops/remove-range-count-must-be-non-negative` pasó a verde en
G3, y con ella **cinco celdas nuevas** para la forma con cuenta, que no tenía
ninguna: `remove-count-out-of-bounds-for-collection` y su `-met`,
`remove-count-of-zero-removes-nothing`, `remove-count-start-must-be-positive` y
su `-met`. Las cinco nacen verdes, que es lo que se pide de una celda escrita
después de arreglar: sujeta el arreglo, no lo anuncia.

`runtime-index-nav/nav-range-written-downwards-selects-descending` y su `-met`
están verdes desde G2; `runtime-operators/constant-already-declared` y las tres
de `runtime-loops-ranges` también, porque sus formas son estáticas.
