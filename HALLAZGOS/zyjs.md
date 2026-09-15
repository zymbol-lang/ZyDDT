# Hallazgos — `zyjs` (motor del navegador)

> Un hallazgo entra aquí cuando el runner nombra a `zyjs` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

| | | |
|---|---|---|
| [`ZYJS-001`](#zyjs-001--el-parser-se-traga-cualquier-token-que-no-reconoce-y-lo-convierte-en-_) | **corregido 2026-08-30** | el parser se tragaba cualquier token que no reconocía |
| [`ZYJS-002`](#zyjs-002--los-diagnósticos-del-lexer-llegan-sin-línea-y-la-guía-va-entre-paréntesis) | **corregido 2026-08-30** | los diagnósticos del lexer llegaban sin línea |
| [`ZYJS-003`](#zyjs-003--un-rangeerror-de-javascript-llega-al-usuario-como-diagnóstico) | **corregido 2026-08-30** | un `RangeError` de JavaScript llegaba como diagnóstico |
| [`ZYJS-004`](#zyjs-004--el-aviso-de-ejecución-sale-por-stdout-mezclado-con-la-salida-del-programa) | **corregido 2026-08-30** | el aviso de ejecución salía por stdout — 70 celdas |
| [`ZYJS-005`](#zyjs-005---y--sobre-no-booleanos-ni-avisan-ni-rechazan) | **corregido 2026-08-30** | `&&`/`\|\|` sobre no booleanos: ni avisaba ni rechazaba — 34 celdas |
| [`ZYJS-006`](#zyjs-006--el-diagnóstico-enseña-el-javascript-de-debajo-object-object-undefined-y-un-diccionario-llamado-tuple) | **corregido 2026-08-30** | `[object Object]` y `undefined` dentro del diagnóstico — 54 celdas |
| [`ZYJS-007`](#zyjs-007--un-identificador-no-continúa-con-un-dígito-que-no-sea-ascii) | **corregido 2026-08-30** | un identificador no continuaba con un dígito no ASCII |
| ~~`ZYJS-008`~~ | **reencaminado 2026-08-30** | no era de `zyjs`: los dos motores Rust eran los ciegos → [`GLB-001`](GLOBAL.md) |
| [`ZYJS-009`](#zyjs-009--una-llamada-cualificada-dentro-de-un-módulo-usaba-los-alias-del-llamante) | **corregido 2026-08-30** | `alias::f()` dentro de un módulo resolvía con la tabla del llamante |
| [`ZYJS-010`](#zyjs-010--una-función-de-módulo-corría-en-el-alcance-del-llamante) | **corregido 2026-08-30** | el estado del módulo se copiaba, y el llamante tapaba a sus funciones |
| [`ZYJS-011`](#zyjs-011--el-acumulador-yuxtapuesto-tiraba-el-resto-de-la-concatenación) | **corregido 2026-08-30** | `s = °s "x"` devolvía sólo `°s` |
| [`ZYJS-012`](#zyjs-012--la-escritura-profunda-se-queda-en-dos-pasos-cij-k~-v-no-parsea) | **corregido 2026-09-07** | `c[i>j>k]$~ v` no parsea; la LECTURA de tres pasos sí |
| [`ZYJS-013`](#zyjs-013--los-pasos-del-navegador-no-cuentan-como-uso-de-una-variable) | **corregido 2026-09-07** | `m[i>j]` avisa `unused variable 'i'` |
| [`ZYJS-014`](#zyjs-014---es-on-en-el-motor-del-navegador) | abierto | `$+` es O(n²) |
| [`ZYJS-015`](#zyjs-015--outer-se-aceptaba-y-se-ejecutaba-como-outer) | **corregido 2026-09-13** | `@!outer` se aceptaba como `@:outer!` |
| [`ZYJS-016`](#zyjs-016--elementos-argumentos-y-llamadas-de--se-evalúan-a-la-vez-y-sus-efectos-se-entrelazan) | **corregido 2026-09-14** | elementos, argumentos y llamadas de `$>` se evalúan a la vez: `12a a 12b b` |
| [`ZYJS-017`](#zyjs-017--un--dentro-de--n--termina-el-programa-en-silencio) | **corregido 2026-09-14** | un `@>` dentro de `@ N` termina el programa, con estado 0 |
| [`ZYJS-018`](#zyjs-018--el-analizador-no-cuenta-como-uso-lo-escrito-en-los-límites-de-un-corte-ni-en-un-) | **corregido 2026-09-14** | `a$[n..2]` y `"" $++ m` avisan `unused variable` |
| [`ZYJS-019`](#zyjs-019--termwidth-rechaza-con-otro-texto) | **abierto** | `term::width` con un número rechaza con otro texto |
| [`ZYJS-020`](#zyjs-020--el-lexer-acepta-siete-formas-que-los-dos-rust-rechazan) | **abierto** | el lexer acepta 7 formas que los Rust rechazan, y otras 5 las rechaza el parser con otro mensaje |
| [`ZYJS-021`](#zyjs-021--los-errores-de-sintaxis-de-los-operadores--nombran-tokens-y-dos-dicen-object-object) | **abierto** | los errores de sintaxis de `$` nombran tokens internos, y dos dicen `[object Object]` |
| [`ZYJS-022`](#zyjs-022--un-módulo-importado-con-el-bloque-de-exportación-mal-escrito-se-carga-sin-error) | **abierto** | un módulo importado con el bloque de exportación mal escrito se carga sin error |

**Cinco abiertos: `ZYJS-014`, `ZYJS-019`, `ZYJS-020`, `ZYJS-021` y `ZYJS-022`.** `ZYJS-016`, `ZYJS-017` y `ZYJS-018` salieron el 2026-09-14 de ejes declarados para la VM (`error-flow`) y de los que se escribieron para medir lo que esos encontraron, y se corrigieron ese día.

---

## ZYJS-001 — El parser se traga cualquier token que no reconoce y lo convierte en `##_`

**Estado:** **corregido 2026-08-30**
**Encontrado por:** `refusal/assign-no-rhs`, celda del eje `axes/refusal.toml`
**Familia:** `DM-06` (cerrada el 2026-08-18), misma causa de fondo en otro sitio

### Qué se observa

```zymbol
x = =
```

| motor | veredicto | qué dice |
|---|---|---|
| `zytw` | `error/static` | `error: expected expression, found Assign` |
| `zyvm` | `error/static` | `error: expected expression, found Assign` |
| `zyjs` | **`warn`** | `warning: unused variable 'x'` — y el programa corre entero |

El eje exige `expect = "error"`. `zyjs` es el único que no lo alcanza.

### Causa

`web/src/zymbol/zymbol.js:2548`, las dos últimas líneas de `parsePrimary`:

```js
    this.adv();
    return { type: 'Literal', kind: 'unit' };
```

Es un cajón de sastre: **todo token que ninguna de las ramas anteriores reconoce
se consume y se devuelve como literal Unit**. `x = =` no falla porque el `=`
sobrante se convierte en `##_`, la asignación queda bien formada, y lo único que
queda es que `x` no se usa.

No hace falta para el literal `##_`, que tiene su propia rama explícita
**35 líneas más arriba**, en `zymbol.js:2420`:

```js
    if (t.type === 'UNIT')  { this.adv(); return { type: 'Literal', kind: 'unit' }; }
```

Así que el cajón no construye nada: sólo se traga.

### Alcance

No es del lado derecho de una asignación. Es de **cualquier posición de
expresión**. Seis sondas, `zymbol 0.0.9`, todas rechazadas por los dos motores
Rust y todas aceptadas por `zyjs`:

| programa | `zytw` / `zyvm` | `zyjs` |
|---|---|---|
| `x = =` | `expected expression, found Assign` | corre, avisa de `x` |
| `x = ,` | `expected expression, found Comma` | corre, avisa de `x` |
| `x = )` | `expected expression, found RParen` | corre, avisa de `x` |
| `x = ]` | `expected expression, found RBracket` | corre, avisa de `x` |
| `x = }` | `expected expression, found RBrace` | corre, avisa de `x` |
| `x = 1 + =` | `expected expression, found Assign` | corre, avisa de `x` |

Y en posición de salida el programa **imprime y sigue**:

```zymbol
>> (= ) ¶
>> "sigue" ¶
```

`zyjs` escribe una línea en blanco y luego `sigue`, y sale con 0. Los dos motores
Rust lo rechazan.

Esto es, muy probablemente, el mecanismo de fondo de toda la familia
*«el motor del navegador acepta una gramática más amplia que los otros dos»*.
`DM-06` se cerró estrechando `parseOutput` de `parseExpr` a `parseAdditive`, que
era correcto para aquel sitio y **no toca esta causa**: el estrechamiento decide
qué gramática se invoca, y el cajón está por debajo, en el fondo de
`parsePrimary`.

### Arreglo, y el riesgo que se cumplió

Las dos líneas se sustituyeron por el rechazo que el resto del fichero ya lanza,
nombrando el token **como lo nombra el parser de Rust** (`Assign`, `Comma`,
`RParen`), a través de una tabla `Parser.RUST_TOKEN_NAME`. Sin ella el mensaje
habría dicho `ASSIGN` y la celda habría quedado en rojo de redacción.

**Dirección: estrechar `zyjs`**, la misma que `DM-06`: los dos motores Rust
comparten el parser, así que ampliar los otros dos sería cambiar el lenguaje, y
el lenguaje ya decidió que esto es un error.

⚠ El riesgo que la ficha anunciaba **se cumplió**, y merece leerse porque es el
argumento de por qué se anunciaba. Al quitar el cajón, **18 ficheros del corpus**
se pusieron en rojo de golpe. Todos eran lo mismo:

```zymbol
>> "Test 1: 5 |> (x -> x * 2)(_) = " >> result1 ¶
```

`>> a >> b ¶` en una línea son **dos** sentencias de salida, y los dos motores
Rust cortan en el segundo `>>` (`parse_output`, `io.rs`). `zyjs` no tenía esa
regla y acertaba **por accidente**: el segundo `>>` caía en el cajón, volvía
como literal Unit, y Unit se imprime como nada.

Es decir: el cajón no sólo aceptaba programas malos, también *simulaba* una
regla que el motor no tenía. Quitarlo obligó a implementarla —
`Parser.OUTPUT_END`, el mismo conjunto de terminadores que `parse_output` — y
eso es una mejora que nadie habría pedido, porque nada estaba en rojo.

### Qué lo sujeta

`refusal/assign-no-rhs`, más **las otras cinco formas de la tabla de alcance**,
que ahora son celdas del mismo eje (`expression-is-a-comma`,
`-a-close-paren`, `-a-close-bracket`, `-a-close-brace`,
`operand-missing-after-plus`, `output-is-nothing-at-all`): una causa raíz con
seis síntomas y una sola celda es una causa que vuelve por cualquiera de los
otros cinco.

Y la salida encadenada, que nada sujetaba, es la chincheta
[`ZYJS-001_chained_output.zy`](../cases/pin/ZYJS-001_chained_output.zy). No es un
fichero de corpus a propósito: los que la ejercitan van de lambdas y de tuberías
y sólo *imprimen* así, de modo que una regresión aquí se diagnosticaría como un
fallo de lambdas.

---

## ZYJS-002 — Los diagnósticos del lexer llegan sin línea, y la guía va entre paréntesis

**Estado:** **corregido 2026-08-30**
**Encontrado por:** `arithmetic/i53-literal-out-of-range`, y sujeto por
`diagnostic/location-on-a-lexer-error` y `diagnostic/guidance-spelling`
**Familia:** ninguna. Salió al corregir un oráculo tramposo, no buscándolo

### Qué se observa

```zymbol
x = 1
y = 9007199254740992
```

| motor | qué escribe |
|---|---|
| `zytw` / `zyvm` | `error: integer literal out of range: '9007199254740992'`<br>` --> fichero:2:5`<br>` = help: integers range from -9007199254740991 to 9007199254740991 (±2⁵³−1)` |
| `zyjs` | `error: integer literal out of range: '9007199254740992' (integers range from -9007199254740991 to 9007199254740991)` |

Son **dos diferencias**, y conviene no mezclarlas:

**a) No dice dónde.** Ni línea ni columna. Comprobado con el literal en la línea
1 y en la línea 2: en los dos casos, nada. Un diagnóstico sin posición es un
diagnóstico que el editor no puede señalar, y el playground lee `d.line` como
campo — así que ahí tampoco hay a dónde saltar.

**b) La guía va dentro del mensaje.** `= help:` es la grafía que acordó toda la
cadena de herramientas, y el `=` no es adorno: es lo que permite separar la guía
del mensaje. Metida entre paréntesis no la separa nada.

### Causa

El diagnóstico no lleva campo `line`, y `web/tests/run_one.mjs` escribe la
posición sólo `if (d.line != null)`. Es decir: **el arnés está bien y el motor no
le da el dato**. Falta localizar el punto exacto de `zymbol.js` donde se
construye el diagnóstico del lexer.

### Alcance

Sin acotar. Se sabe que afecta al menos a `integer literal out of range`, en
cualquier línea. Queda por medir si es de **todos** los diagnósticos del lexer o
sólo de algunos — es la primera medida que hay que hacer si se decide arreglar.

### Arreglo, en el orden que la ficha pedía

Los dos cambios, juntos y en un commit, que es la lección de `DM-07`: hacer (1)
sin (2) deja cada diagnóstico con dos diferencias a la vez.

**1. La posición.** `ZyStaticError` tenía el constructor `constructor(msg)` y
**tres sitios ya le estaban pasando una línea** que se tiraba a la basura. Ahora
la guarda en `zyLine`, que es de donde `checkSource` la lee — igual que hace
`ZyError`. Los dos sitios del lexer que no la pasaban ahora la pasan.

**2. La grafía.** La guía es un **campo**, `help`, nunca texto pegado al
mensaje. No es un detalle: `zyquality/messages/` lee el *código fuente* de los
dos motores y compara la prosa, así que una guía concatenada al mensaje se ve
como una cadena aquí contra un mensaje más un `.with_help(…)` allí — una
diferencia que no lo es. El campo llega hasta `formatDiagnostic`, en el
playground y en `run_one.mjs`, que lo pintan como `  = help: …`.

Se le dio el mismo tratamiento a `undefined variable` (a la que le faltaba la
guía entera: `variables must be defined before use`), a `!=` y al rechazo de la
gramática de `>>`, que llevaban la guía metida en el mensaje.

Y una cosa que sólo se ve leyendo el inventario: `integers range from …` está
escrita **con los dos números literales**, en una constante, porque así la
escribe `zymbol_common::num::ZY_INT_RANGE_HELP`. Construida con `${ZY_INT_MIN}`
normaliza a `from § to §` y el inventario la cuenta como un mensaje distinto.

### Qué lo sujeta

`diagnostic/location-on-a-lexer-error` (el literal en la línea **2** a propósito:
una celda cuyo error está en la línea 1 no distingue «dice la línea» de «dice 1
siempre») y `diagnostic/guidance-spelling`.

---

## ZYJS-003 — Un `RangeError` de JavaScript llega al usuario como diagnóstico

**Estado:** **corregido 2026-08-30**
**Encontrado por:** sondeo alrededor de `ZYJS-002`; sujeto por
`diagnostic/base-prefix-with-no-digits`

### Qué se observa

| programa | `zytw` / `zyvm` | `zyjs` |
|---|---|---|
| `>> 0xZZ ¶` | `error: expected hexadecimal digits after base prefix` | `error: Invalid code point NaN` |
| `>> 0b22 ¶` | `error: expected binary digits after base prefix` | `error: Invalid code point NaN` |
| `>> 0o99 ¶` | `error: expected octal digits after base prefix` | `error: Invalid code point NaN` |
| `>> 0dAA ¶` | `error: expected decimal digits after base prefix` | `error: Invalid code point NaN` |
| `>> 0x ¶` | `error: expected hexadecimal digits after base prefix` | `error: Invalid code point NaN` |

`Invalid code point NaN` no es un mensaje del lenguaje. Es el texto de una
excepción de JavaScript, y no le dice nada a quien escribe Zymbol.

### Causa

`web/src/zymbol/zymbol.js:721-751`, las cuatro ramas de prefijo de base, con el
mismo defecto cada una:

```js
let hex = '';
while (/[0-9a-fA-F]/.test(this.ch())) hex += this.consume();
toks.push({ type: 'CHAR', value: String.fromCodePoint(parseInt(hex, 16)), … });
```

El `while` puede no casar ni una vez. Entonces `hex` es `''`, `parseInt('', 16)`
es `NaN`, y `String.fromCodePoint(NaN)` lanza `RangeError: Invalid code point
NaN`. Las cuatro ramas —`0x`, `0b`, `0o`, `0d`— están escritas igual y fallan
igual.

### Alcance

Las cuatro, confirmadas. También con el prefijo solo (`0x` sin nada detrás), que
es el caso que más fácil se escribe por accidente.

### Arreglo

Una guarda por rama, antes de convertir, con el nombre de la base en el mensaje:

```js
if (!hex) throw new ZyStaticError(`expected ${'hexadecimal'} digits after base prefix`, this.line);
```

La plantilla no es un capricho. `literals.rs` lo construye como
`format!("expected {} digits after base prefix", base_name)` — **un** mensaje con
un hueco — así que cuatro literales sueltos aquí serían cuatro mensajes que el
inventario ve como cuatro diferencias frente a uno. Escrito así, los dos lados
normalizan a la misma línea.

Se hizo **después** de `ZYJS-002`, para que naciera con línea y no hubiera que
tocarlo dos veces.

### Qué lo sujeta

`diagnostic/base-prefix-with-no-digits` para `0x`, y —en el mismo commit, como
la ficha pedía— `binary-prefix-with-no-digits`, `octal-…`, `decimal-…` y
`bare-prefix-with-nothing-after-it`, que es el prefijo solo al final de la
expresión: el más fácil de escribir por accidente y aquel donde el `while` no
tiene ninguna posibilidad de casar.

---

## ZYJS-004 — El aviso de ejecución sale por stdout, mezclado con la salida del programa

**Estado:** **corregido 2026-08-30**
**Encontrado por:** eje `operator`, 70 de 252 celdas
**Familia:** canal, no redacción. El texto del aviso es el correcto; va al sitio
equivocado.

### Qué se observa

```zymbol
>> ("a" - 7) ¶
```

```console
$ node web/tests/run_one.mjs cell.zy 2>/dev/null      # solo stdout
warning: arithmetic operation on non-numeric type: String

$ node web/tests/run_one.mjs cell.zy >/dev/null       # solo stderr
Runtime error: arithmetic requires numeric operands: String("a"), Int(7)
```

En `zytw` y `zyvm` ese aviso va a stderr, junto al error. En `zyjs` va **a la
salida del programa**.

### Por qué no es el harness

`web/tests/run_one.mjs` sí separa los canales, y lo hace a propósito y con el
comentario puesto (líneas 149-151 y 163-166): los diagnósticos **estáticos** se
escriben a `process.stderr`, y el motor recibe un `onError` precisamente para que
los de ejecución no acaben «in the middle of the program's output».

El aviso de ejecución no usa ese `onError`: sale por `onOutput`, que es el canal
de `>>`. El harness lo entrega donde el motor lo puso.

### Por qué importa

Un programa correcto que provoque un aviso **imprime el aviso como si fuera su
salida**. En el playground los dos canales caen en el mismo panel y no se nota;
por tubería, un `zyjs … | wc -l` cuenta una línea de más, y cualquier consumidor
de la salida recibe texto que el programa no escribió.

Es además el motivo por el que el eje `operator` tiene 70 celdas rojas de una
sola causa: la comparación de stdout, que es la que un gate hace primero, ve una
diferencia en todas ellas.

### El reparto de las 70 celdas

Los cinco operadores aritméticos (`-`, `*`, `/`, `%`, `^`) contra todo par que
tenga un operando no numérico. `+` no está: tiene su propio camino, que rechaza
antes de avisar.

### Arreglo — el aviso no cambia de canal, cambia de momento

La tentación era pasarlo de `onOutput` a `onError` y ya. Habría sido un parche:
en los dos motores Rust ese aviso **no es de ejecución**, lo emite el analizador
semántico (`type_check.rs`), antes de correr nada, con su span.

Así que se movió al mismo sitio: `Checker.warnBinaryOperandType`, invocado desde
el caso `BinOp` de `checkExpr`. Eso arregla tres cosas de una vez —el canal, la
posición y la ausencia de la comprobación en `&&` ([`ZYJS-005`](#zyjs-005---y--sobre-no-booleanos-ni-avisan-ni-rechazan))—
porque pasa a ser un diagnóstico estático como cualquier otro.

Sólo el operando **izquierdo**, y sólo para `- * / % ^` y `&& ||`, que es lo que
`type_check.rs` hace: `+` calla y las comparaciones también.

Para que el aviso nombrara el tipo igual que Rust hizo falta
`Checker.operandTypeName`, que deletrea `[Int]`, `(Int, Int)`, `(x: Int)` y
`Unit` como `ZymbolType::name()`. Es una función aparte y no una ampliación de
`staticKind` a propósito: `staticKind` alimenta las comprobaciones de arrays y
de `$+`, y enseñarle qué es una tupla cambiaría lo que aquéllas deciden.

Y el nodo `BinOp` **no tenía campo `line`** — se lo dio `parseBinLeft`, del
primer token del operando izquierdo. Sin eso el aviso salía sin posición y las
68 celdas seguían en rojo por la misma razón que `ZYJS-002`, una capa más arriba.

### Qué lo sujeta

Las 70 celdas del eje. No hace falta chincheta: la pregunta es un punto de una
matriz declarada, no un hallazgo con nombre.

---

## ZYJS-005 — `&&` y `||` sobre no booleanos: ni avisan ni rechazan

**Estado:** **corregido 2026-08-30**
**Encontrado por:** eje `operator`, 34 de 252 celdas
**Relacionado:** [`ZYVM-001`](zyvm.md) — la misma forma, tres respuestas distintas

### Qué se observa

```zymbol
>> (7 && 3) ¶
```

| motor | aviso | resultado |
|---|---|---|
| `zytw` | `logical operation on non-boolean type: Int` | **rechaza**: `logical AND requires boolean operands, got Int(7)` |
| `zyvm` | el mismo aviso | imprime `#1` |
| `zyjs` | **ninguno** | imprime `#1` |

Tres motores, tres comportamientos. `zyjs` es el único que no dice nada: el
analizador estático de los dos motores Rust emite el aviso, y el de `zyjs` no
tiene esa comprobación.

### Por qué se separa de `ZYVM-001`

Porque el arreglo es distinto y el culpable también. Si decides que la respuesta
correcta es *truthiness*, `ZYVM-001` se cierra y **esto sigue abierto**: seguiría
faltando el aviso. Si decides que es un error, hay que añadir las dos cosas.

Los 17 pares son todos los que el eje declara excepto `bool-bool`.

### Veredicto y arreglo

**Error en los tres**, la misma decisión que cerró [`ZYVM-001`](zyvm.md): no hay
truthiness en Zymbol. `zyjs` gana las dos cosas que le faltaban:

- el **aviso**, ahora estático, desde `warnBinaryOperandType` (ver
  [`ZYJS-004`](#zyjs-004--el-aviso-de-ejecución-sale-por-stdout-mezclado-con-la-salida-del-programa));
- el **rechazo**, en el caso `BinOp` de `eval`, con el mensaje del tree-walker.

El cortocircuito se mantiene y se comprueba en el orden correcto: el operando
izquierdo primero, y el derecho ni se evalúa ni se comprueba si no se alcanza —
`#0 && f()` sigue sin llamar a `f()`.

La misma regla se llevó a los unarios, donde nadie había mirado: `-"a"` contestaba
`NaN` y `!7` contestaba `#0`. Eso lo encontró la chincheta de
[`ZYVM-002`](zyvm.md) al ejecutarse contra los tres motores, no una lectura.

### Qué lo sujeta

Las 34 celdas, más las chinchetas
[`ZYVM-001_logical_short_circuit.zy`](../cases/pin/ZYVM-001_logical_short_circuit.zy)
y [`ZYVM-001_logical_falsy_left.zy`](../cases/pin/ZYVM-001_logical_falsy_left.zy).

---

## ZYJS-006 — El diagnóstico enseña el JavaScript de debajo: `[object Object]`, `undefined`, y un diccionario llamado `Tuple`

**Estado:** **corregido 2026-08-30**
**Encontrado por:** eje `operator`, 54 de 252 celdas
**Familia:** `ZYJS-003` — la excepción del anfitrión llegando al usuario. Allí
era un `RangeError`; aquí es la interpolación por defecto de un objeto.

### Qué se observa

Tres síntomas, un origen: el mensaje se compone con el valor JavaScript en bruto
en vez de con la representación del lenguaje.

```zymbol
>> ((1, 2) / (3, 4)) ¶
```
```text
Runtime error: arithmetic requires numeric operands:
  tuple([object Object],[object Object]), tuple([object Object],[object Object])
```

```zymbol
>> (##_ < ##_) ¶
```
```text
Runtime error: cannot compare unit undefined with unit undefined using operator 'Lt'
```

```zymbol
>> (#(x: 1) / #(y: 2)) ¶
```
```text
warning: arithmetic operation on non-numeric type: Tuple
Runtime error: arithmetic requires numeric operands: tuple([object Object]), tuple([object Object])
```

El tercero tiene un segundo defecto encima: **un diccionario descrito como
`Tuple`**. No es un fallo de parseo —`(#(x: 1))#?` contesta `##(` en los tres
motores, y las 48 celdas del eje `type-symbol` concuerdan—, es que la rama del
mensaje trata las dos colecciones como una.

Para comparar, lo que dice `zytw` de esa misma línea:

```text
warning: arithmetic operation on non-numeric type: (x: Int)
Runtime error: / requires numeric operands — use $/ to split strings
```

### Alcance

54 celdas: todo par con una tupla, un diccionario o un `##_` dentro de un
operador que rechaza. Es la cota inferior — el eje sólo cruza un valor por
especie, y el defecto es de la interpolación, no del valor.

### Arreglo — cerrado por construcción, no por reparación

No se arregló la interpolación: **se quitó el valor del mensaje**. Es la decisión
de [`GLOBAL-001`](GLOBAL.md) —*un diagnóstico nombra tipos, no valores*— llevada
a toda la familia aritmética y lógica en los tres motores.

Si el mensaje no interpola un valor, ningún `[object Object]` ni ningún
`undefined` puede aparecer en él. El defecto no queda arreglado en un sitio:
queda sin sitio donde ocurrir.

El segundo defecto —**el diccionario descrito como `Tuple`**— sí se arregló, y en
los tres motores, porque los tres lo tenían: el `type_name` de la VM y el
`value_type` del tree-walker también decían `Tuple` para un `#(x: 1)`. Ahora
dicen `Dict`, que es el vocabulario que el propio código ya usaba
(`RequireDict`, `ModuleConst::Dict`, `GlobalInit::Dict`).

### Qué lo sujeta

Las 54 celdas del eje.


---

## ZYJS-007 — Un identificador no continúa con un dígito que no sea ASCII

**Estado:** **corregido 2026-08-30**
**Encontrado por:** la validación contra las aplicaciones LDV, no por el corpus
**Familia:** [`ZYJS-001`](#zyjs-001--el-parser-se-traga-cualquier-token-que-no-reconoce-y-lo-convierte-en-_) — el cajón lo estaba tapando

### Qué se observa

```zymbol
क२ = 5
>> क२ ¶
```

| motor | qué hace |
|---|---|
| `zytw` / `zyvm` | `5` |
| `zyjs` (antes) | corría con un **parseo equivocado** y avisaba `this statement does nothing: 'क' is read and discarded` |
| `zyjs` (al cerrar `ZYJS-001`) | `error: expected expression, found Assign` |

### Causa

`readIdent` continuaba con la clase `[\p{L}\p{M}\p{So}\p{Co}0-9_]` — dígitos
**ASCII y sólo ASCII**. El lexer de Rust continúa con
`is_ident_continue`, que es `is_alphanumeric() || '_'`, y `२`.is_alphanumeric()
es cierto: `\p{N}` entero, no `0-9`.

Así que `कार्यस्थितिः२ = …` daba tres tokens —IDENT, NUMBER, ASSIGN— donde el
lenguaje tiene un nombre. Cinco sitios del fichero llevaban la misma clase; los
cinco corregidos a `[\p{L}\p{M}\p{N}\p{So}\p{Co}_]`.

El **inicio** no cambia: un dígito de cualquiera de las 69 escrituras empieza un
número, nunca un nombre, que es lo que hace Rust (`is_ident_start` exige
`digit_value(ch).is_none()`).

### Por qué nadie lo había visto

Dos capas de silencio, una encima de la otra:

1. **El cajón de `ZYJS-001`** se tragaba el `=` sobrante, así que el programa no
   fallaba: quedaba una sentencia que no hacía nada y un aviso que decía
   exactamente eso, en un fichero de 400 líneas en sánscrito.
2. **El corpus no nombra variables así.** Ningún fichero de `zyquality/corpus/`
   escribe un identificador acabado en dígito devanagari. Lo hace **Chaturanga**,
   que está escrito en sánscrito, y las aplicaciones LDV son justo lo que el
   corpus no puede ser: programas que alguien escribió para usarlos.

Es el argumento de `LDV.md` § 1 en una línea: el corpus verifica lo que ya
existe; una aplicación completa es lo que encuentra lo que nadie había escrito.

### Qué lo sujeta

[`ZYJS-007_ident_unicode_digit.zy`](../cases/pin/ZYJS-007_ident_unicode_digit.zy),
con una escritura por familia —devanagari, árabe-índico, dígitos anchos, ASCII—
porque la regla es sobre la categoría Unicode y no sobre el devanagari.

---

## ZYJS-008 — **Reencaminado.** No era de `zyjs`

**Estado:** **reencaminado el 2026-08-30 a [`GLB-001`](GLOBAL.md)**

Se archivó aquí el 2026-08-30 leyendo el síntoma —`zyjs` rechaza un fichero que
los dos motores Rust aceptan— y la lectura era la equivocada. Medido, el que
tenía razón era `zyjs`: el error existía de verdad en el programa, y lo que
fallaba era que **el analizador semántico de Rust no descendía al operando de un
operador `$`**, así que no lo veía.

Culpable la pareja Rust, que comparten analizador → `GLOBAL.md` por
[`INDICE.md`](INDICE.md) § 3. La ficha vive allí como
[`GLB-001`](GLOBAL.md#glb-001--el-analizador-no-mira-dentro-del-operando-de-un-operador-).

**La entrada se queda aquí en vez de borrarse**, porque el error de
encaminamiento es la parte que enseña algo: `INDICE.md` § 1 dice que el motor lo
nombra el runner y no una lectura, y aquí no hubo runner —lo produjo mirar una
aplicación— así que lo nombró una lectura, y se equivocó. Cuando el eje no
puede decidir, *«el que se sale» no es lo mismo que «el que está mal»*.


---

## ZYJS-009 — Una llamada cualificada dentro de un módulo usaba los alias del llamante

**Estado:** **corregido 2026-08-30**
**Encontrado por:** la validación contra las aplicaciones LDV — Chaturanga, al
destrabar [`GLB-001`](GLOBAL.md)
**Gravedad:** es **ámbito dinámico**. Lo que un módulo llama depende de cómo lo
llame quien lo importe.

### Qué se observa

Cuatro ficheros. `medio.zy` importa `uno` como `A`; el programa principal importa
un módulo **distinto**, `dos`, con ese mismo nombre:

```zymbol
// medio.zy
# .medio {
    <# ./uno => A
    #> { usa }
    usa() { <~ A::saluda() }
}
```
```zymbol
// main.zy
<# ./medio => M
<# ./dos => A
>> M::usa() ¶
```

| motor | qué hace |
|---|---|
| `zytw` / `zyvm` | `soy uno` |
| `zyjs` | `Runtime error: module 'A' does not export function 'saluda'` |

Dentro de `usa()`, `A` tiene que ser el `A` de `medio.zy`. `zyjs` usaba el del
llamante.

### Causa

`this.moduleAliases` es **un mapa por intérprete**, y las funciones de un módulo
se ejecutan sobre el intérprete que las llama —`callFunc` no cambia nada—, así
que la búsqueda era dinámica.

Los dos motores Rust no tienen ese problema porque la solución está en el valor:
un valor función lleva **los alias visibles donde se escribió** (`ModuleAliases`,
`interpreter/CLAUDE.md` § Crate Responsibilities) y cada marco los intercambia.

### Arreglo

Lo mismo: el valor función guarda `moduleAliases` al crearse —función con nombre
y lambda— y `callFunc` los intercambia mientras dura la llamada, restaurándolos
en un `finally`. El cuerpo se movió a `_callFuncBody` para que el `try/finally`
no se enrede con los cinco caminos de salida que ya tenía.

### Por qué no lo vio nada

Hace falta que **dos módulos distintos compartan un nombre de alias**, y ningún
fichero del corpus lo hace: un corpus se escribe un fichero cada vez, y la
colisión sólo aparece cuando un programa crece hasta tener módulos que no se
conocen entre sí. Chaturanga la tiene por una razón perfectamente normal:
`मूल/मतिः.zy` importa `आकलनम्` como `आ` y su fichero de pruebas importa `आकृतिः`
con esa misma letra. Dos palabras que empiezan igual.

### Lo que destrabó

No era sólo Chaturanga. Con el arreglo, **la suite entera de Chaturanga pasa
también en `zyjs`** —los tres motores, por primera vez— y con ella la de GO y la
de serpiente. Quedan dos fallos en `zyjs`, los dos **anteriores** y medidos
contra su versión previa: `klingon_galaxy/mIw/Hol.zy` (`'' is not a function`) y
`ZyBank/pruebas/verificación_dígitos.zy` (`FALLOS: 4`). Sin ficha todavía: hace
falta aislarlos antes.

### Qué lo sujeta

[`ZYJS-009_alias_del_modulo.zy`](../cases/pin/ZYJS-009_alias_del_modulo.zy) y su
directorio de apoyo `cases/pin/alias_scope/`.


---

## ZYJS-010 — Una función de módulo corría en el alcance del llamante

**Estado:** **corregido 2026-08-30**
**Encontrado por:** la validación LDV — `klingon_galaxy` y `ZyBank`
**Familia:** [`ZYJS-009`](#zyjs-009--una-llamada-cualificada-dentro-de-un-módulo-usaba-los-alias-del-llamante),
que era la tabla de alias. Esto es el alcance.

### Qué se observa

Dos síntomas, un defecto.

**a) El llamante tapaba a las funciones del módulo.** `klingon_galaxy/mIw/Hol.zy`
nombra un array de idiomas exactamente como la función del módulo que lo
produce —lo normal— y la llamada moría con `'…' is not a function`. El marco de
la función copiaba las variables **del llamante**, así que el array tapaba a la
función.

**b) Lo que escribía una hermana era invisible.** El despachador de idiomas de
`ZyBank` tiene `texto()` llamando a `_asegurar()`, que construye el catálogo;
`texto()` leía después el `#0` con el que el módulo arranca. El marco llevaba
una **copia** del estado, no el estado. Cuatro idiomas más abajo:
`$? not supported on bool`.

### Causa

`callFunc` construía el marco sobre `this.globalEnv` —**el del intérprete que
llama**— porque las funciones de un módulo se ejecutan sobre él. Y copiaba en
ese marco los nombres libres, que para una función de módulo es exactamente lo
que no hay que hacer: el estado de un módulo es mutable y compartido.

### Arreglo

El valor función guarda `homeEnv`, los globales del fichero donde se escribió, y
`callFunc` distingue dos casos:

| la función es | marco | frontera | copia |
|---|---|---|---|
| de **otro** fichero (un módulo) | sobre `homeEnv` | no | ninguna — lee y escribe en vivo |
| de **este** fichero | sobre `homeEnv` (= el propio) | sí | sí, como siempre |

La segunda fila es literal: una función escrita aquí conserva lo que tenía, así
que un `x = …` dentro sigue muriendo con la llamada (ERROR-ZYB-002). La primera
es la semántica de módulo de los dos motores Rust.

⚠ El primer intento hizo lo primero y no lo segundo —copiar desde `homeEnv`— y
puso dos ficheros de `ZyBank` en rojo, porque copiar el estado del módulo es
tan malo como copiar el del llamante. La distinción **propio / de otro fichero**
es lo que hace falta; una sola de las dos mitades no vale.

### Qué lo sujeta

[`ZYJS-010_alcance_del_modulo.zy`](../cases/pin/ZYJS-010_alcance_del_modulo.zy),
que hace las dos preguntas a la vez y nombra una variable local igual que la
función del módulo, a propósito.

---

## ZYJS-011 — El acumulador yuxtapuesto tiraba el resto de la concatenación

**Estado:** **corregido 2026-08-30**
**Encontrado por:** la validación LDV — `ZyBank/pruebas/verificación_dígitos.zy`

### Qué se observa

```zymbol
s = ""
@ _i:1..3 { s = °s "x" }
>> "[" s "]" ¶
```

| motor | respuesta |
|---|---|
| `zytw` / `zyvm` | `[xxx]` |
| `zyjs` | `[]` |

### Causa

La rama del centinela caliente en `ImplicitConcat` devolvía **`items[1]`** —el
`°s`— y tiraba todo lo que viniera detrás. Así que la expresión valía `s`, el
acumulador no crecía nunca, y el bucle producía la cadena vacía.

### Por qué no lo vio nada

El corpus escribe este acumulador con el `°` a la **izquierda** (`°s = s ch`),
que es la forma que da el GUIDE en su ejemplo de cadenas y que toma otra rama.
La forma con `°` a la derecha es la que usa `transliterar()` de `ZyBank`, y sus
cuatro casos de escritura volvían vacíos.

### Qué lo sujeta

[`ZYJS-011_acumulador_yuxtapuesto.zy`](../cases/pin/ZYJS-011_acumulador_yuxtapuesto.zy),
que además ejercita las tres formas que ya funcionaban para que el arreglo no se
las lleve por delante.


---

## ZYJS-012 — La escritura profunda se queda en dos pasos: `c[i>j>k]$~ v` no parsea

**Estado:** **corregido 2026-09-07**
**Encontrado por:** `addressing/write-navigator-deep`, celda de `axes/addressing.toml`
**Clase:** un motor implementa menos que los otros dos

### Qué se observa

```zymbol
c = [[[1,2],[3,4]], [[5,6],[7,8]]]
>> c[1>2>1] ¶          // los tres: 3
c[1>2>1] $~ 0          // zytw y zyvm: escriben.  zyjs: error
>> c ¶
```

```
zytw, zyvm   3
             [[[1, 2], [0, 4]], [[5, 6], [7, 8]]]
zyjs         error: Expected RBRACKET, got '>'
               --> line 3
```

La **lectura** de tres pasos funciona en los tres (`addressing/navigator-3` está
en verde). Es la **escritura** la que se queda en dos: `parseNavContent` acepta
la ruta larga cuando lo que sigue al `]` no es `$~`, y no cuando lo es.

### Por qué importa más de lo que su tamaño sugiere

Es la dirección permisiva al revés, que es la peor para quien escribe en el
playground: el programa funciona en el CLI y **no** en el navegador. Y llega
justo cuando el navegador `>` acaba de quedarse como la **única** forma de bajar
niveles — `arr[i][j]` se cerró el 2026-09-06 —, así que un programa de tres
niveles que antes se podía escribir encadenando ya no tiene alternativa en zyjs.

### Cómo se encontró

No lo encontró un programa: lo encontró declarar el eje. Cero ficheros del
corpus, de las aplicaciones y de los ejemplos escriben a tres pasos, medido el
2026-09-07 — que es exactamente por qué llevaba ahí sin que nadie tropezara.

---

## ZYJS-013 — Los pasos del navegador no cuentan como uso de una variable

**Estado:** **corregido 2026-09-07**
**Encontrado por:** `addressing/navigator-var` y `addressing/navigator-expr`
**Clase:** un motor avisa donde los otros dos callan

### Qué se observa

```zymbol
m = [[1,2,3],[4,5,6]]
i = 1
j = 2
>> m[i>j] ¶
```

```
zytw, zyvm   No errors or warnings
zyjs         warning: unused variable 'i'
             warning: unused variable 'j'
```

`i` y `j` se usan: son los pasos de la ruta. El recorrido de variables de zyjs no
desciende a `spec.path`, así que un nombre que sólo aparece ahí queda contado
como no usado.

### Por qué es un aviso y no un error, y aun así cuenta

Un falso aviso cuesta más que su ruido: enseña a no leerlos. Y este cae sobre la
forma que el lenguaje acaba de dejar como **única** para navegar, así que su
frecuencia sólo puede subir. Familia de [`GLB-001`](GLOBAL.md) — un brazo del
analizador que no mira dentro de su operando apaga las comprobaciones de todo lo
que se escriba ahí—, en el otro motor y sobre otro nodo.


### Cómo se corrigieron (2026-09-07)

**ZYJS-012.** No era `flattenGtChain`, que ya era recursiva: era el `parseExpr`
de la posición de sentencia. En `name[…]` el corchete se consume antes de que el
parser de navegación lo vea, así que la ruta llega como una comparación `>` que
las ramas de abajo reconstruyen — pero `parseExpr` lee **una** comparación y en
Zymbol `>` no encadena, así que `m[1>2>1]` dejaba un `>` delante del `]` y moría
en `Expected RBRACKET`. Ahora se siguen plegando pasos a la izquierda mientras
haya `>`, que es la forma que `flattenGtChain` ya aplana; el operando se lee con
`parseAdditive`, por lo mismo que `parseNavAtom`: ahí `>` es separador y no
operador. La LECTURA nunca estuvo rota — va por `parseNavContent`, que hace ese
bucle desde siempre.

**ZYJS-013.** `checkExpr` miraba `spec.index`, `spec.from` y `spec.to`, y
`from`/`to` viven en un ÁTOMO, nunca en el spec: sólo `kind: 'simple'` se
recorría. `checkNavSpec` recorre ahora las cuatro formas — `simple`, `path`,
`flat`, `structured` — y los dos tipos de átomo. Escrito sobre las FORMAS y no
sobre `kind`, para que un spec que gane un campo lo recorra la rama que le toque
en vez de caerse por un `switch`: el defecto que se arregla es exactamente un
paso que nadie miraba.

---

## ZYJS-014 — `$+` es O(n²) en el motor del navegador

**Estado:** abierto
**Encontrado por:** la medición del auto-free del 2026-09-12, como control
**Familia:** `HLZ-014` — es la nota de `CLAUDE.md` («the browser engine reaches
the same place by sharing the JavaScript array and **rebuilding it on write**»)
con su consecuencia medida

### Qué se observa

```zymbol
a = []
@ i:1..N { a$+ i }
>> a$# ¶
```

| N | `zytw` | `zyvm` | `zyjs` |
|---:|---:|---:|---:|
| 5 000 | 0,011 | 0,006 | 0,148 |
| 20 000 | 0,019 | 0,011 | **2,111** |
| 200 000 | 0,03 | 0,02 | **no termina en 200 s** |

Cuadruplicar el trabajo multiplica por **14** el tiempo de `zyjs`; los dos
motores Rust son planos. No es el factor constante que se le supone a un
intérprete escrito en JavaScript: es otra curva.

### Causa

Probable, sin parche que lo confirme: el modelo de copia al escribir de `zyjs`
reconstruye el array en cada escritura. Eso da la semántica correcta —y por eso
los tres motores coinciden en la salida— pero cada `$+` copia lo acumulado.

### Alcance

Todo programa que construya una colección elemento a elemento, que en el
playground es casi cualquiera. Invisible para el gate por la misma razón que
`ZYVM-003`: la salida es idéntica en los tres motores, y un diferencial compara
salidas.

Un dato que conviene medir antes de decidir nada: el playground corre programas
pequeños, así que puede que esto no le duela a ningún ejemplo real. Lo que no
puede pasar es que nadie lo sepa.

### Arreglo propuesto

Ninguno todavía: primero medir si algún ejemplo o alguna app LDV alcanza la
escala en que se nota.

### Qué lo sujeta

`zyquality/cost/`, caso **`growth/append-local`**, desde el 2026-09-12, con
`n_by_engine = { zyjs = 5000 }` porque a la escala de los motores Rust este
motor necesita minutos. Marcado `open_finding = { zyjs = "ZYJS-014" }`: se
reporta KNOWN con su ratio en cada corrida y no enrojece el gate.

---

## ZYJS-015 — `@!outer` se aceptaba y se ejecutaba como `@:outer!`

**Estado:** **corregido 2026-09-13**; queda un aviso de más
**Encontrado por:** `refusal/modality-before-its-label`, la primera celda de SYM-8
**Familia:** `ZYJS-001` — el parser aceptando lo que los dos motores Rust rechazan

### Qué se observaba

```zymbol
@:outer _i:1..3 { >> "vuelta" ¶
  @!outer }
>> "fin" ¶
```

| motor | |
|---|---|
| `zytw`, `zyvm` | `error: undefined variable 'outer'` |
| `zyjs` | **imprime `vuelta` y `fin`** — exactamente lo mismo que la forma correcta |

No es que lo tolerase: lo **ejecutaba como si fuera `@:outer!`**, que es la forma
que SYM-8 existe para distinguir.

### Causa

`parseStatement`, en la rama `BREAK`: tras `@!` tomaba un `IDENT` como etiqueta
si lo había. La ruptura etiquetada es `AT_BREAK`, dos líneas más abajo, y se
parsea entera desde el token `@:outer!`.

SYM-8 dice que un `?` o `!` modal es la marca **más a la derecha** del operador y
que nunca le sigue un argumento ni una etiqueta. Aceptar un identificador ahí era
admitir un segundo orden para lo mismo.

### Lo que queda

Ya rechaza, y con el mismo texto: `undefined variable 'outer'`. Antes emite un
aviso que los motores Rust no dan — `this statement does nothing: 'outer' is read
and discarded` — que es cierto y es de la familia de diagnósticos que sobran en
este motor. La celda queda en `DIVERGE` por eso, no por el comportamiento.

---

## ZYJS-016 — Elementos, argumentos y llamadas de `$>` se evalúan a la vez, y sus efectos se entrelazan

**Estado:** **corregido 2026-09-14**
**Encontrado por:** `callable-body/map-lambda-match-str`, 2026-09-14 — imprimía las dos líneas de un `$>` en orden inverso; medido después por `axes/evaluation-order.toml`
**Gravedad:** alta para el playground: la salida de un programa correcto sale revuelta

### Qué se observa

```zymbol
p(x) {
    >> x "a" ¶
    >> x "b" ¶
    <~ x
}
>> [p(1), p(2)] ¶
```

| motor | |
|---|---|
| `zytw`, `zyvm` | `1a` `1b` `2a` `2b` `[1, 2]` |
| `zyjs` | **`12a` `a` `12b` `b`** `[1, 2]` |

El valor es correcto y la salida no. Pasa en seis posiciones: los elementos de
un array, de una tupla y de un diccionario, los argumentos de una llamada, las
partes de un `$++` y las llamadas de `$>`. No pasa en `$|`, `$<`, el comparador
de `$^`, los operandos de `+`, los items de un `>>`, los límites de un corte ni
los pasos de un navegador.

### Causa

`web/src/zymbol/zymbol.js`, siete sitios de la forma

```js
await Promise.all(expr.items.map(i => this.eval(i, env)))
```

`Promise.all` no evalúa en orden: **arranca** todas las evaluaciones, y cada una
corre hasta su primer `await` antes de que empiece la siguiente. Como el motor
es `async` de punta a punta, cualquier llamada con más de un efecto se parte
por la mitad.

Cualquier efecto con orden queda expuesto igual: la salida, la entrada `<<`, y
un parámetro `<~` que un elemento escribe y el siguiente lee.

### Arreglo

Un bucle `for … of` con `await` en cada vuelta, en los siete sitios. No hay
paralelismo real que perder: el motor corre en un solo hilo.

### Qué lo sujeta

`axes/evaluation-order.toml`, 13 posiciones; y
`callable-body/map-lambda-match-str`, `callable-body/map-named-match-str`.

---

## ZYJS-017 — Un `@>` dentro de `@ N` termina el programa en silencio

**Estado:** **corregido 2026-09-14**
**Encontrado por:** `error-flow/continue-disarms-the-catch`, 2026-09-14, por accidente —la celda preguntaba por la VM— y medido después por `axes/loop-jump.toml`
**Gravedad:** **alta**: el resto del programa no se ejecuta, no hay mensaje y el estado de salida es 0

### Qué se observa

```zymbol
@ 2 {
    >> "u" ¶
    @>
}
>> "fin" ¶
```

`zytw` y `zyvm` imprimen `u`, `u`, `fin`. `zyjs` imprime **`u`** y termina, con
estado 0. Dentro de una función, la función devuelve `##_`.

### Causa

`web/src/zymbol/zymbol.js`, `execLoop`, la rama del bucle con cuenta: comprueba
`brk(sig)` y nunca `cnt(sig)`, así que el `@>` cae en

```js
if (sig instanceof ZyBreak || sig instanceof ZyContinue) return sig;
```

y sube hasta que nadie lo toma. Las otras cinco clases de bucle sí lo
comprueban.

### Arreglo

`if (cnt(sig)) continue;` en la rama de la cuenta, como en las otras.

### Qué lo sujeta

`axes/loop-jump.toml`: 6 clases de bucle × `@!`/`@>` × arriba/dentro de una
función = 24 celdas. Rojas exactamente las dos de `@>` en `@ N`.

---

## ZYJS-018 — El analizador no cuenta como uso lo escrito en los límites de un corte ni en un `$++`

**Estado:** **corregido 2026-09-14**
**Encontrado por:** `evaluation-order/slice-bounds` y `evaluation-order/build`, 2026-09-14
**Gravedad:** baja: un aviso falso, en `stderr`. Pero es la misma familia que `ZYJS-013` y que `GLB-001`: un brazo que no desciende apaga todas las comprobaciones de lo que hay debajo

### Qué se observa

```zymbol
n = 1
a = [10, 20, 30]
>> a$[n..2] ¶
m = 2
>> "" $++ m ¶
```

`zyjs` avisa `unused variable 'n'` y `unused variable 'm'`. Los motores Rust no.

### Arreglo

Que el recorrido del analizador de `zyjs` descienda a los límites del corte y a
las partes del `$++`.

### Qué lo sujeta

`evaluation-order/slice-bounds` y `evaluation-order/build`.

---

## ZYJS-019 — `term::width` rechaza con otro texto

**Estado:** abierto
**Encontrado por:** `runtime-std/term-width-expected-a-string-or-char`, paso C10 del plan de cobertura de diagnósticos, 2026-09-14
**Gravedad:** baja: rechaza lo mismo, con otras palabras

`term::width(5)`: los dos Rust dicen
`term::width: expected a String or Char, got ###`; `zyjs` dice

```
Runtime error: term::width: expected a String or Char
```

Las otras 20 funciones de `std/` del mismo paso coinciden palabra por palabra en
los tres motores, y también en el kind.

---

## ZYJS-020 — El lexer acepta siete formas que los dos Rust rechazan

**Estado:** **corregido el 2026-09-15** (paso 2.1): 11 de 13 en verde. Las dos que quedan no son de `zyjs` (ver «Lo que queda»)
**Encontrado por:** `axes/syntax-lexer.toml`, paso B3 del plan de cobertura de diagnósticos, 2026-09-14
**Gravedad:** **alta** en el playground: un programa mal escrito corre y enseña un resultado

### Qué se observa

Los 13 diagnósticos del lexer que nada provocaba. `zytw` y `zyvm` los dan los
13, con las mismas palabras. `zyjs`:

**A. Acepta 7 y ejecuta:**

| forma | `zyjs` |
|---|---|
| `/* abierto` (comentario sin cerrar) | programa vacío, estado 0 |
| `0xD800` (un sustituto no es un carácter) | imprime `�` |
| `"a{1}"` (una interpolación que no es un nombre) | imprime `a1` |
| `'\q'` (escape desconocido en un carácter) | imprime `q` |
| `1٢` (cifras de dos escrituras) | imprime `12` |
| `1 & 2` (un `&` suelto) | imprime `12` |
| `c = '` al final del fichero | sólo avisa `unused variable 'c'` |

**B. Rechaza 5 con otro diagnóstico**, porque su lexer no tiene la comprobación
y el error sale después, en el parser: `#2` → `expected expression, found
Output`; `1.0e+` → lo mismo; `'ab'` → `undefined variable 'b''`; `</ ./a.zy` →
`expected expression, found Lt`; `"a{b"` → `invalid character in string
interpolation`.

Sólo `"a{}b"` coincide en los tres.

### Qué lo sujeta

`axes/syntax-lexer.toml`: 13 celdas, 1 verde.

### Corregido — 2026-09-15

Cada forma, con el texto y la ayuda de los Rust, en `web/src/zymbol/zymbol.js`:

| forma | qué hacía | qué hace |
|---|---|---|
| `/* abierto` | fin de fichero, estado 0 | `Unterminated multi-line comment`. Los comentarios **anidan**, como en Rust: `/* a /* b */ c */` era un error de parser en `zyjs` y `/* a /* b */` pasaba sin cerrar |
| `0xD800`, `0x110000` | `�` | `invalid Unicode code point: 0xD800 (hexadecimal D800)`, en las cuatro bases (`codePointChar`) |
| `"a{1}"` | `a1` | `invalid character in string interpolation`, con la regla de identificador de `readIdent` y del checker |
| `"a{b"` | «carácter inválido» | `unterminated string interpolation` |
| `'\q'` | `q` | `invalid escape sequence: '\q'`: la tabla de Rust (`n t r ' \ 0`) y nada más |
| `'ab'` | `undefined variable 'b''` | `expected closing ' for char literal` |
| `c = '` al final | sólo un aviso | `unterminated char literal` |
| `1٢` | `12` | `mixed digit scripts in numeric literal`, en la parte entera y en la decimal |
| `1.0e+`, `1e` | el parser tropezaba | `invalid float literal: '1.0e+'` |
| `#2` | se descartaba sin ruido | `invalid boolean literal: digit 2 is not valid after '#'` |
| `1 & 2` | `12` | `unexpected character: '&'` |

**Dos cosas que la medición cambió por el camino.**
- El `consume()` final del lexer descarta todo carácter que no reconoce. Al
  convertirlo en error para todos los caracteres de operador, `corpus/functions/param_marks.zy`
  **divergió**: la marca de parámetro `a~` funciona en `zyjs` *porque* el `~`
  desaparece. Rust sólo da `unexpected character` para `&`, que es el único
  carácter de operador sin token; la comprobación se quedó en `&`.
- La expresión regular vieja de la interpolación tenía comillas dentro, y eso
  desemparejaba el escáner de `zyquality/messages/extract.py`. Al quitarla, el
  inventario vio por primera vez entero `unmatched '}' in string` con la ayuda
  pegada al texto, y falló. Ese throw pasó a `ZyStaticError(mensaje, línea,
  ayuda)`, como los demás, y el inventario cerró además 16 mensajes que ahora
  casan con los de Rust.

### Lo que queda

- `unterminated-execute-expression`: `zyjs` no implementa `</ ruta />`; el
  rechazo es otro y la celda queda en `WORDING`.
- `unterminated-string-interpolation`: en `DIVERGE` **por los Rust**, que dan
  un segundo diagnóstico falso (`unterminated string literal @4:8`): tras parar
  en la comilla, la vuelven a leer como apertura de otra cadena. Los Rust también
  añaden `expected expression, found Error("invalid boolean literal")` detrás de
  varios errores de lexer, un token interno a la vista. Es trabajo de la F3.

### Lo que sigue desapareciendo en silencio (registrado, sin tocar)

- `~` fuera de su sitio (`1 ~ 2` imprime `12`; Rust: `unexpected token:
  Tilde`), del que depende `a~`. Celda `refusal/lone-tilde`.
- `0X41`, el prefijo en mayúscula: `zyjs` lo lee como `A`, y Rust sólo acepta
  minúscula (`undefined variable 'X41'`). Celda `syntax-lexer/uppercase-base-prefix`.
- Los caracteres que Rust lee como identificador y `zyjs` descarta o rechaza:
  `` `x `` y un espacio de ancho cero (Rust: parte del nombre; `zyjs`: no están), o
  `€` (Rust: identificador; `zyjs`: error). Necesita decisión: `GLB-026`.


---

## ZYJS-021 — Los errores de sintaxis de los operadores `$` nombran tokens, y dos dicen `[object Object]`

**Estado:** **corregido el 2026-09-15** (pasos 2.3, 2.4 y 2.5). Quedan cinco celdas en `WORDING` que no son de `zyjs` (ver «Textos»)
**Encontrado por:** `axes/syntax-collection-ops.toml`, paso B4 del plan de cobertura de diagnósticos, 2026-09-14
**Gravedad:** media: rechaza lo que debe, con un texto que no ayuda
**Familia:** `ZYJS-006` (`[object Object]` en el diagnóstico, cerrado el 2026-08-30 en otro sitio)

Las 16 formas rotas de los operadores `$` las rechazan los tres motores; los dos
Rust con el mismo texto y su `help:`. `zyjs` nombra el token que esperaba su
parser y el que encontró:

| forma | Rust | `zyjs` |
|---|---|---|
| `a$-[1:2` | `expected ']' after count` + help | `Expected RBRACKET, got '>>'` |
| `a$< (0 (s, x) -> s + x)` | `expected ',' after initial value` + help | `Expected COMMA, got '('` |
| `s$~~["a" "b"]` | `expected ':' after pattern` + help | **`Expected COLON, got '[object Object]'`** |
| `s$~~ "a"` | `expected '[' after $~~` + help | **`Expected LBRACKET, got '[object Object]'`** |
| `5$~ 9` | `collection update ($~) requires a place to write` | `expected expression, found DUPDATE` |
| `a$^ x` | `expected comparator lambda after '$^'` | `undefined variable 'x'` |

El `[object Object]` aparece cuando el token encontrado es una cadena: el mensaje
interpola el objeto del token en vez de su texto.

### Y en los literales (paso B5)

Las 5 formas rotas de array, tupla y diccionario: los tres rechazan, los Rust con
el mismo texto. `zyjs`: `[1, 2` → `expected expression, found Output`;
`#(a: 2` y `(1, 2` → `Expected RPAREN, got '>>'`; `#(a 2)` → `expected a key in
the dictionary` (el mensaje de otra forma); `#(1: 2)` → el mismo diagnóstico con
la guía dentro del mensaje en vez de en `help:`.

### Y en formato y conversión (paso B6)

9 formas rotas. Seis como las anteriores (`Expected VBAR, got '>>'`). Tres son
peores: `#.2 5` y `#.|5|` se rechazan **una línea más abajo**, en el `>>`
siguiente (`expected expression, found Output`); y **`#!2 5` se lee como un `!`
lógico** aplicado a `2`, que falla en ejecución con `logical NOT requires boolean
operand` en vez de rechazarse al parsear.

### Y en los filtros de `:!` (paso B7)

`:! #Div { }` → `Expected LBRACE, got '#'`. Y **`:! ## { }` se acepta**: el `!?`
corre, el filtro sin nombre no casa y el error sale sin capturar.

### Y en funciones y lambdas (paso B8)

**Acepta** `f(a b) { }` —lo lee como dos parámetros y luego la llamada con uno
falla por aridad— y `a$^ (x y -> #1)`. El comparador sin flecha, `a$^ (v)`, lo
deja pasar al parsear y falla **en ejecución** (`Expected a function for
collection operator`). `f(1) + 2` como sentencia: `expected expression, found
Plus`.

### Y en el núcleo de expresiones (paso B9)

La mayoría como las anteriores (`Expected RPAREN, got '>>'`). Dos más:
**un módulo con una sentencia detrás de su bloque** (`# extra { … }` y luego
`x = 1`) se carga sin error, y lo que falla después es `module 'e' does not
export function 'f'`; y `°x` suelto como sentencia es `undefined variable 'x'`
en vez de `'°name' is only valid as an assignment target`.

### Y en `??` y `_?` (paso B10)

**Acepta** un patrón de rango con los extremos de tipos distintos —`'a'..5` y
`1..'z'`— y cae al comodín (`y`). Un brazo sin `=>` vuelve a decir
`Expected FAT_ARROW, got '[object Object]'`.

### Y en navegación y E/S (pasos B11 y B12)

En navegación, `m[(a 1)>1]` se lee como la yuxtaposición `11` y falla en
ejecución. En E/S **acepta** un `<\ "echo"` sin cerrar (sólo avisa de la variable
sin usar) y un `<< #|n` sin cerrar, que se pone a leer la entrada; y
`<< ###(4 "n: " n` vuelve a decir `[object Object]`.

### Y en variables y desestructuración (paso B14)

**Acepta** `\ 5` (destruir algo que no es un nombre; sólo avisa de `x` sin usar)
y `x°[1] 5` (una forma indexada sin operador después de un nombre caliente). Las
formas de desestructuración rotas las rechaza con `Expected IDENT, got '5'` y
`Expected COLON, got 'y'`.

### Dos más, medidas el 2026-09-15 (paso 1.10)

- **`a$^ f` con `f` una lambda en una variable.** Los Rust exigen el comparador
  escrito en línea (`expected comparator lambda after '$^'`), y `zyjs` ordena con
  él. La celda que había, `sort-expects-comparator-lambda`, usaba una `x` sin
  definir, y `zyjs` la rechazaba por eso (`undefined variable 'x'`) y no por la
  forma. Celda nueva `syntax-collection-ops/sort-comparator-from-a-variable`,
  roja.
- **Parámetros de lambda sin usar.** `(a, b -> 1)` avisa `unused variable 'a'` y
  `'b'` en `zyjs`, y en los Rust no. Nada dice cuál es lo correcto; salió al
  escribir la celda de `GLB-024`, donde ese aviso tapaba la pregunta.
  *Decidido el 2026-09-15:* **no se avisa**, como en los Rust: una lambda recibe
  los parámetros que la operación le da, los use o no. **Corregido el 2026-09-15
  (paso 2.13)**, y lo mismo para un alias de módulo sin usar (`ZYJS-022`).
  Medido en el mismo paso: los Rust **tampoco** avisan de un parámetro sin usar
  de una **función con nombre** (`f(a, b) { <~ a }`), y `zyjs` sí lo hace. Como no
  estaba en la decisión, `zyjs` sigue avisando en ese caso hasta que el autor diga.

### Corregido: lo que aceptaba — 2026-09-15 (paso 2.3)

Quince formas que `zyjs` ejecutaba se rechazan ahora al parsear, con el texto de
Rust:

| forma | ahora |
|---|---|
| `a$^ f`, con `f` en una variable | `expected comparator lambda after '$^', e.g. …` |
| `a$^ (v)` | `expected '->' in lambda expression` + ayuda |
| `a$^ (x y -> #1)` | `expected ')' after lambda parameters` + ayuda |
| `f(a b) { }` | `expected ')' after parameters` + ayuda |
| `?? c { 'a'..5 => … }`, `1..'z'` | `expected char / integer after '..' in range pattern` |
| `m::sqrt 4` | `expected '(' for module function call` + ayuda |
| `m[1>-a]` | `expected integer after '-' in nav index` + ayuda |
| `m[1>1.5]` | `expected navigation step: a position …` + ayuda |
| `x = <\ "echo"` sin cerrar | `unterminated bash execute expression` + ayuda |
| `<< #\|n` sin cerrar | `expected '\|' to close #\|variable\|` + ayuda |
| `\ 5` | `expected variable name after \` + ayuda |
| `x°[1] 5`, `x°[1]$~ 5` | `expected '=' after index expression for indexed assignment`, **sin la ayuda de Rust**, que enseña `arr[i] = val` (`GLB-027`) |
| `:! ## { }` | `expected error type name after '##'`, **sin ayuda**: la de Rust lista 7 de los 11 tipos (`GLB-022`) |
| `# m { … }` y una sentencia detrás | `unexpected token after module block` + ayuda, dentro de `failed to parse module` |

Los pasos de una ruta de navegación, después de `>`, `;` o `..`, siguen ahora la
gramática estricta de `parse_nav_atom`: entero, `-`entero, nombre, cadena o
`( expr )`. El primer átomo sigue siendo una expresión, porque el índice simple
la admite. **Barrido de parseo** con el `zyjs` anterior y el nuevo sobre los 1189
`.zy` de los ejemplos, las aplicaciones LDV y el corpus: los mismos 9 errores, y
ningún fichero deja de parsear. Las 10 `WRONG` de los ejes `syntax-*` son 0.

### Corregido: lo que leía como otra cosa — 2026-09-15 (paso 2.4)

- **`#.2 5`, `#.|5|`**: un `#.` incompleto caía a la rama de las cabeceras
  antiguas, que se tragaba el resto de la línea, y el error salía una línea más
  abajo. **`#!2 5`**: el `#` se descartaba y quedaba un NOT lógico, que fallaba
  en ejecución. Ahora `#.` y `#!` son siempre los operadores de redondeo y
  truncado, como en el lexer de Rust: `expected '|' after precision`, con la
  ayuda de cada uno, o `expected a decimal count after '#.'` / `'#!'` **sin
  ayuda**, porque la de Rust enseña `#..2|value|` y `#!.2|value|` (`GLB-021`).
  De paso deja de aceptarse `#.nombre {` sin espacio como módulo, que Rust
  rechaza (el corpus escribe `# .nombre {`).
- **`m[(a 1)>1]`**: el primer paso entre paréntesis se leía como la
  yuxtaposición `11`. Si el `)` que lo cierra va seguido de `>` es un paso
  calculado, como decide `is_nav_index` en Rust, y lleva una expresión y su `)`:
  `expected ')' after computed index`.

El barrido de parseo sobre los 1189 ficheros sigue en los mismos 9 errores.
`syntax-format-convert` pasa de 3 `DIVERGE` a 0 y `syntax-index-nav` de 1 a 0.

### Corregido: los textos — 2026-09-15 (paso 2.5)

De las 64 celdas `WORDING` de los ejes `syntax-*`, **59 dan ya en `zyjs` el
mensaje y la ayuda de Rust, carácter a carácter**. La primera lista sólo tenía 52:
estaba construida con la salida resumida de `zyddt axis`, que no imprime la línea
`WORDING` de las celdas que pasan de su límite de detalle. El barrido completo
enseñó las otras 12, y se sacaron con `--detail 200`. `eat(tipo, mensaje, ayuda)`
lleva el texto de Rust en cada sitio, y la variante de reserva ya no enseña
`[object Object]` cuando el token es una cadena. Donde Rust dice cosas distintas
según el contexto, `zyjs` distingue lo mismo:
- la `)` de una llamada por nombre, de módulo, sobre una expresión, sobre un
  paréntesis o en el destino de `|>`;
- un grupo (`to close grouped expression`) frente a una tupla (`to close tuple`);
- el `]` de un índice, de una extracción plana, de una estructurada o de un grupo
  de extracción.

Además, siguiendo la gramática de Rust: una lista de argumentos o de elementos de
array termina en la primera coma que falta; una sentencia que empieza por una
llamada es sólo la llamada (`f(1) + 2`: `expected function call`); `$--[` es la
forma retirada; y una edición sin destino tiene dos titulares, como en Rust:
`modifying requires a destination with a name` si lo editado es lo que devolvió
una llamada, y `this edit has nothing to write into` si es otra expresión
(`x$+ 1 $+ 2`).

Las cinco que quedan no son de `zyjs`:
- `round-expects-a-decimal-count`, `error-type-with-one-hash` y
  `hot-index-without-operator`: la ayuda de Rust enseña algo que no es
  (`GLB-021`, `GLB-022`, `GLB-027`), y `zyjs` da el mensaje sin ella. Se igualan
  en la F3.
- `execute-without-a-path` y `unterminated-execute-expression`: `zyjs` no
  implementa `</ ruta />`.

Barrido de parseo sobre los 1189 ficheros: los mismos 9 errores, dos con el texto
nuevo. El inventario de mensajes cierra 150. En el barrido completo de ZyDDT los
rojos bajan de 378 a 289, sin ninguna regresión. Sólo tuvo que ajustarse la forma de
tres plantillas, para que coincidiera con la de Rust (`'{}'` con el prefijo, no
`'#,'` escrito).

Registrado por el camino: `x[1] 5` —sin `°`— ejecuta el `5` suelto en `zyjs`
(celda `refusal/stray-literal-statement`), y los Rust añaden errores en cascada
(`GLB-028`).

### Qué lo sujeta

`axes/syntax-collection-ops.toml` (16 celdas), `axes/syntax-literals.toml` (5),
`axes/syntax-format-convert.toml` (9), `axes/syntax-try-catch.toml` (2),
`axes/syntax-functions-lambdas.toml` (6), `axes/syntax-expressions.toml` (15),
`axes/syntax-control-flow.toml` (7), `axes/syntax-index-nav.toml` (8),
`axes/syntax-io.toml` (12) y `axes/syntax-variables.toml` (8).

---

## ZYJS-022 — Un módulo importado con el bloque de exportación mal escrito se carga sin error

**Estado:** **corregido el 2026-09-15** (paso 2.2): los 12 módulos rotos se rechazan. Las 12 celdas siguen en `DIVERGE` por dos cosas que no son este hallazgo (ver «Lo que queda»)
**Encontrado por:** `axes/syntax-modules.toml`, paso B13 del plan de cobertura de diagnósticos, 2026-09-14
**Gravedad:** media-alta: el módulo roto no se nota hasta que alguien use lo que exporta

Doce módulos rotos, cada uno importado por un programa que no llega a usarlo
(`<# ./m/x => md` y `>> "x" ¶`). Los dos Rust fallan en los doce al cargar el
módulo, con el diagnóstico del parser del módulo dentro de `failed to parse
module`. `zyjs`:

- **acepta 6** —dos bloques `#>`, `#> { 5 }`, `#> { mat. }`,
  `#> { mat::sqrt => }`, `#> { f => }` y el separador antiguo `#> { mat::sqrt :
  raiz }`— y sólo avisa `unused variable 'md'`;
- rechaza los otros 6 (inicializador no literal, `<#` sin `=>`, módulo sin `{`,
  bloque de exportación sin cerrar, alias que no es nombre) con otra forma.

Todo lo que acepta está dentro del bloque `#>`: su parser de la lista de
exportación no valida los elementos.

### Qué lo sujeta

`axes/syntax-modules.toml`: 12 celdas, 6 `WRONG` (las aceptadas) y 6 `DIVERGE`.

### Corregido — 2026-09-15

- **El bloque `#>`** se parsea con la gramática y los rechazos de
  `parse_export_block` de `zymbol-parser/src/modules.rs`: identificador o error
  (`expected identifier in export item`, con su ayuda), `::`/`.` seguidos de un
  nombre, `=>` seguido de un nombre (`expected new name after '=>'`, `expected
  public name after '=>'`), el separador antiguo `:` o `<=` (`legacy export rename
  separator`) y `expected '}' to close export block`. El bucle viejo saltaba todo
  token que no esperaba y rellenaba el nombre que faltaba con uno por defecto.
- **Un solo `#>` por módulo**: `duplicate export block in module`, con su ayuda.
- **Un módulo que no se lee** se informa como en Rust:
  `failed to parse module: 1 parse error(s) in '<fichero>'` (o `lexer error(s)`)
  y el error debajo con su línea y su ayuda. Antes salía el error del parser del
  módulo sin cabecera, como si fuera del fichero principal (`GLB-017` D). Se
  construye con las mismas tres piezas que `modules.rs`, y el inventario de
  mensajes pasó de 16 a 28 mensajes cerrados.

Consensus 660/0, las siete aplicaciones (casi todas con módulos), `test_zyp` y
los ejemplos del playground siguen en verde.

### Lo que queda (las 12 celdas en `DIVERGE`)

1. **La columna.** El detalle de Rust es `fichero:3:5:` y el de `zyjs`
   `fichero:3:0:`: los tokens de `zyjs` no llevan columna. ZyDDT compara esas
   líneas al pie de la letra.
2. **Un aviso que sólo da `zyjs`:** `unused variable 'md'` para un alias de
   módulo importado y no usado, también con un módulo correcto. Los Rust no
   avisan, y un alias no es una variable. *Decidido el 2026-09-15: no se avisa.*
   **Corregido el 2026-09-15 (paso 2.13).**
   Y sobre la columna, *decidido el 2026-09-15*: `zyjs` tendrá columnas (paso 2.16).
3. `zyjs` añade `--> main.zy:4` detrás del error de carga; los Rust no.
4. E013 (inicializador no literal) sale como `1 semantic error(s)` en `zyjs`,
   porque lo detecta su checker, y como `1 parse error(s)` en Rust. Paso 2.5.

---

## ZYJS-023 — El panel de problemas del playground enseña la clave en bruto de 19 de los 28 diagnósticos del checker

**Estado:** abierto — sin decisión pendiente
**Encontrado por:** paso 2.6, 2026-09-15, al añadir el aviso `W_UNUSED_MATCH`
**Gravedad:** media en el playground: el lector ve `chk.W_NO_EFFECT` donde debería leer una frase

`src/playground/problems.js` escribe cada diagnóstico con `t(\`chk.${d.code}\`)`, y
`t` devuelve la clave cuando el catálogo no la tiene; no hay reserva al
`d.message` inglés. De los 28 códigos que el `Checker` de `zymbol.js` emite con
`this.warn`/`this.error`, **19 no están** en `data/i18n/playground/english.json`:

`E014`, `E015`, `E016`, `E017`, `E018`, `E019`, `E_ARRAY_MIX`, `E_HOT_AMBIG`,
`E_HOT_OUTPUT`, `E_NAME`, `W_ARITH_TYPE`, `W_COND_TYPE`, `W_DESTRUCT_SHAPE`,
`W_LOGIC_TYPE`, `W_MIX_UNNEEDED`, `W_NO_EFFECT`, `W_RANGE_DIR`, `W_TYPE_CHANGE`,
`W_UNARY_TYPE`.

`tests/test_i18n_playground.mjs` comprueba que los dos catálogos tienen las
mismas claves, pero no que estén las que el motor emite. Sin celda: ZyDDT no ve
el panel. Lo que lo sujetaría es un test en `web/tests/` que cruce los códigos
de `zymbol.js` con el catálogo.
