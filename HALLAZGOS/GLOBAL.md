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

**Estado:** abierto — **decidido el 2026-09-15** (familia `##Type`; colecciones tolerantes). Falta que el autor valide la tabla de tolerancias antes de tocar un motor
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

### Qué lo sujeta

`axes/runtime-collection-ops.toml`: 50 celdas `expect = "error"` y 50 `-met`.
3 verdes, 97 rojas.

---

## GLB-012 — Índices y navegación con un valor inválido: `zyjs` contesta donde los Rust fallan, y el kind se reparte entre `##_`, `##Index` y `##Type`

**Estado:** abierto — **decidido el 2026-09-15** (tipo `##Type`, valor `##Index`; el rango invertido selecciona en orden descendente)
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

### Qué lo sujeta

`axes/runtime-index-nav.toml`: 22 celdas `expect = "error"` y 22 `-met`. 18
verdes, 26 rojas.

---

## GLB-013 — Conversiones y formatos con un valor inválido: `zyjs` inventa un número, y el kind vuelve a ser `##_` contra `##Type`

**Estado:** abierto — la parte del kind **decidida el 2026-09-15** (`##Type`)
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

### Qué lo sujeta

`axes/runtime-format-convert.toml`: 13 pares. 7 verdes, 19 rojas.

---

## GLB-014 — Rangos, pasos y `@~` con valores inválidos: la VM entra en bucle infinito con paso 0, y el bucle que desestructura un rango sólo existe en el TW

**Estado:** abierto — **A y B corregidos en la VM el 2026-09-15** (pasos 1.3 y 1.4); C, D y G **decididos el 2026-09-15** (error estático; `##Type`); E, F, H y la parte `zyjs` de B sin decisión pendiente
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

**Estado:** abierto — la parte del kind **decidida el 2026-09-15** (`##Type`); **A corregido en la VM el 2026-09-15** (paso 1.10), queda `zyjs`
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

**C (D1):** los 9 son `##Type` en los tres motores: algo que no es array ni
lambda, o llamar a algo que no es función.

### Qué lo sujeta

`axes/runtime-functions-hof.toml`: 12 pares. 2 verdes, 22 rojas.

---

## GLB-016 — Un `??` sin brazo que case: el TW aborta, la VM y `zyjs` devuelven `##_` en silencio

**Estado:** abierto — sin decisión pendiente: `LLM.md` dice *«an unmatched `??` aborts»*. **La VM y el aviso en los dos Rust, corregidos el 2026-09-15** (pasos 1.1 y 1.2); queda `zyjs` (paso 2.6)
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

**Estado:** abierto — **A y G corregidos el 2026-09-15** (pasos 1.5 y 1.5b); B–F abiertos
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

### Qué lo sujeta

`axes/runtime-modules-scripts.toml`: 14 celdas, 4 verdes, 10 rojas, más
`bash-collection-interpolation` (G), añadida el 2026-09-15. Los errores
de carga de módulo no tienen `-met`: una importación va antes de cualquier
sentencia y no hay `!?` que la rodee.

---

## GLB-018 — Entrada y salida: la VM y `zyjs` no interpolan el prompt de `<<`, ignoran un hueco inválido de `>>~`, y `zyjs` abre `>>|` sin terminal

**Estado:** abierto — **A decidido y corregido en los tres motores el 2026-09-15** (paso 1.6); **B corregido en la VM el 2026-09-15** (paso 1.7), queda `zyjs`; C sin decisión pendiente; **H decidido y corregido el 2026-09-15** (paso 1.11)
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

**Estado:** abierto — **A y la parte VM de B corregidos el 2026-09-15** (pasos 1.8 y 1.9); falta que `zyjs` implemente el `+` unario (decidido: es forma), y C va con D5 (F5)
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

### Qué lo sujeta

`axes/runtime-operators.toml`: 7 pares. 8 verdes, 6 rojas.

---

## GLB-020 — Una constante varía: `<< C` y `@ C:1..2` la sobrescriben en el TW y en la VM

**Estado:** abierto — **decidido el 2026-09-15** (error estático); sin celda todavía
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

---

## GLB-021 — La ayuda de `#.|x|` enseña `#..2|value|`, con dos puntos

**Estado:** abierto — sin decisión pendiente
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

---

## GLB-022 — La ayuda de los tipos de error lista siete de once

**Estado:** abierto — sin decisión pendiente
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

**Estado:** abierto — **decidido el 2026-09-15**: error `##Type` en los tres motores. **Corregido en los dos Rust el 2026-09-15** (paso 1.12); quedan `zyjs` (F2) y el kind (4.1)
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

### Qué lo sujeta

`runtime-functions-hof/sort-comparator-that-is-not-a-bool`, roja. Vecina, por el
mismo camino: `syntax-collection-ops/sort-comparator-from-a-variable`. Los Rust
rechazan `a$^ f` con `f` una lambda en una variable (el comparador tiene que ir
escrito en línea), y `zyjs` ordena con ella (`ZYJS-021`).

---

## GLB-025 — Una variable destruida con `\` se lee en `{…}` sin error: los tres imprimen `{x}`

**Estado:** abierto — **decidido el 2026-09-15**: el mismo error en ejecución que el identificador, en los tres motores (paso 2.15)
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

---

## GLB-026 — Un fichero con BOM no corre en Rust, y los caracteres raros son identificador en Rust y ruido en `zyjs`

**Estado:** abierto — A sin decisión pendiente; **B decidido el 2026-09-15** (ver abajo)
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

**Un ejemplo del playground que no carga** (medido el 2026-09-15, paso 2.5):
`web/examples/graphics/mandelbrot/emoji.zy` escribe `<<| _🔑`. Tras un `_`, el
lexer de `zyjs` sólo sigue leyendo el nombre si viene letra, uso privado, cifra o
`_` (`[\p{L}\p{Co}0-9_]`), y un emoji es `\p{So}`; el `_` se queda solo y el
parser falla. Rust lo lee como un nombre. El ejemplo lleva `@skip-parity`, y por
eso nada lo ejecutaba en `zyjs`. Entra en el paso 2.17.

---

## GLB-027 — La ayuda de Rust para `x°[1] 5` enseña `arr[i] = val`, una forma que no existe

**Estado:** abierto — sin decisión pendiente (F3)
**Encontrado por:** paso 2.3, 2026-09-15, al portar el rechazo a `zyjs`
**Familia:** `GLB-021`, `GLB-022` (ayudas que enseñan lo que no es)

`x = [1, 2]` y luego `x°[1] 5`, o `x°[1]$~ 5`, en los dos motores Rust:

```
error: expected '=' after index expression for indexed assignment
  = help: syntax: arr[i] = val  or  arr[i] += val
```

`COL-2` dice que `arr[i] = v` no existe, y el propio parser rechaza `arr[i] = v`
dos líneas antes con `indexed assignment does not exist`. La ayuda enseña
justo la forma retirada. `zyjs` rechaza igual desde el paso 2.3, **sin** esa
ayuda. Sujeta la celda `syntax-variables/hot-index-without-operator`, en
`WORDING` por esa línea.

---

## GLB-028 — Los parsers Rust añaden errores falsos en cascada y enseñan sus tokens internos

**Estado:** abierto — sin decisión pendiente (F3)
**Encontrado por:** pasos 2.1 y 2.3, 2026-09-15
**Gravedad:** media: el lector recibe dos errores donde hay uno, y el segundo nombra el lexer por dentro

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
