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

**Ninguno abierto.**

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
