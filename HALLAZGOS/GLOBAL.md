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

**Estado:** abierto — **necesita decisión del autor** (qué es correcto) antes de arreglar nada
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

### Qué lo sujeta

`axes/runtime-collection-ops.toml`: 50 celdas `expect = "error"` y 50 `-met`.
3 verdes, 97 rojas.
