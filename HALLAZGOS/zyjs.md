# Hallazgos — `zyjs` (motor del navegador)

> Un hallazgo entra aquí cuando el runner nombra a `zyjs` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

| | | |
|---|---|---|
| [`ZYJS-001`](#zyjs-001--el-parser-se-traga-cualquier-token-que-no-reconoce-y-lo-convierte-en-_) | abierto | el parser se traga cualquier token que no reconoce |
| [`ZYJS-002`](#zyjs-002--los-diagnósticos-del-lexer-llegan-sin-línea-y-la-guía-va-entre-paréntesis) | abierto | los diagnósticos del lexer llegan sin línea |
| [`ZYJS-003`](#zyjs-003--un-rangeerror-de-javascript-llega-al-usuario-como-diagnóstico) | abierto | un `RangeError` de JavaScript llega como diagnóstico |
| [`ZYJS-004`](#zyjs-004--el-aviso-de-ejecución-sale-por-stdout-mezclado-con-la-salida-del-programa) | abierto | el aviso de ejecución sale por stdout — 70 celdas |
| [`ZYJS-005`](#zyjs-005---y--sobre-no-booleanos-ni-avisan-ni-rechazan) | abierto | `&&`/`\|\|` sobre no booleanos: ni avisa ni rechaza — 34 celdas |
| [`ZYJS-006`](#zyjs-006--el-diagnóstico-enseña-el-javascript-de-debajo-object-object-undefined-y-un-diccionario-llamado-tuple) | abierto | `[object Object]` y `undefined` dentro del diagnóstico — 54 celdas |

---

## ZYJS-001 — El parser se traga cualquier token que no reconoce y lo convierte en `##_`

**Estado:** abierto — pendiente de tu veredicto
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

### Arreglo propuesto

Sustituir las dos líneas por el error que ya se lanza en el resto del fichero:

```js
    throw new ZyStaticError(`expected expression, found ${t.type}`, t.line);
```

**Dirección: estrechar `zyjs`**, la misma que `DM-06`. El motivo es el mismo que
allí: los dos motores Rust comparten el parser, así que ampliar los otros dos
significa cambiar el lenguaje, y el lenguaje ya decidió que esto es un error.

⚠ **Riesgo, y es el que hundió el primer intento de `DM-06`.** Al estrechar sin
más, `>> 1 == 1 ¶` pasó a imprimir `11` — un resultado *silenciosamente
equivocado*, peor que el bug original. Aquí puede pasar lo mismo por el otro
lado: si alguna ruta del parser depende hoy de que el cajón devuelva `Unit` en
vez de fallar, quitarlo la romperá. **No se implementa sin correr el eje
`refusal` completo más el corpus de `web/` detrás.**

### Qué lo sujeta

`refusal/assign-no-rhs`, celda generada de `axes/refusal.toml`, con
`expect = "error"`. Hoy pone el gate en rojo con `WRONG` y encamina aquí.

Las otras cinco formas de la tabla de alcance **no son celdas todavía**. Cuando
se decida el arreglo van al mismo eje, porque una causa raíz con seis síntomas y
una sola celda es una causa que vuelve por cualquiera de los otros cinco.

---

## ZYJS-002 — Los diagnósticos del lexer llegan sin línea, y la guía va entre paréntesis

**Estado:** abierto — pendiente de tu veredicto
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

### Arreglo propuesto

Dos cambios independientes, y se pueden hacer por separado:

1. Que el diagnóstico del lexer lleve `line` (y `col` si es barato), para que
   `run_one.mjs` lo escriba sin tocar el arnés.
2. Sacar la guía del mensaje a un campo propio que se imprima como `= help:`.

⚠ El orden importa, y es la lección de `DM-07`: unificar la forma **antes** de
emitir. Hacer (1) sin (2) deja cada diagnóstico con dos diferencias a la vez —la
posición y la grafía— y convierte un problema arreglable en dos.

### Qué lo sujeta

`diagnostic/location-on-a-lexer-error` (el literal en la línea **2** a propósito:
una celda cuyo error está en la línea 1 no distingue «dice la línea» de «dice 1
siempre») y `diagnostic/guidance-spelling`.

---

## ZYJS-003 — Un `RangeError` de JavaScript llega al usuario como diagnóstico

**Estado:** abierto — pendiente de tu veredicto
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

### Arreglo propuesto

Comprobar que se consumió al menos un dígito antes de convertir, y lanzar el
diagnóstico del lenguaje que ya usan los otros dos motores:

```js
if (!hex) throw new ZyStaticError('expected hexadecimal digits after base prefix', this.line);
```

Cuatro sitios, uno por prefijo, con el nombre de la base en cada mensaje.

⚠ Hacerlo **después** de `ZYJS-002`, o el mensaje nuevo nacerá también sin línea
y habrá que tocarlo dos veces.

### Qué lo sujeta

`diagnostic/base-prefix-with-no-digits`. Cubre `0x`; las otras tres ramas **no
son celdas todavía**, y deberían serlo en el mismo commit del arreglo: cuatro
sitios idénticos con una sola celda es un arreglo que vuelve por cualquiera de
los otros tres.

---

## ZYJS-004 — El aviso de ejecución sale por stdout, mezclado con la salida del programa

**Estado:** abierto — pendiente de tu veredicto
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

### Qué lo sujeta

Las 70 celdas del eje. No hace falta chincheta: la pregunta es un punto de una
matriz declarada, no un hallazgo con nombre.

---

## ZYJS-005 — `&&` y `||` sobre no booleanos: ni avisan ni rechazan

**Estado:** abierto — pendiente de tu veredicto
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

### Qué lo sujeta

Las 34 celdas. Cuando decidas cuál es la respuesta correcta, la forma pasa a ser
un `expect` del eje o una chincheta con ID, no antes: hoy no hay respuesta
correcta escrita en ningún sitio, y ponerla en un test sería inventarla.

---

## ZYJS-006 — El diagnóstico enseña el JavaScript de debajo: `[object Object]`, `undefined`, y un diccionario llamado `Tuple`

**Estado:** abierto — pendiente de tu veredicto
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

### Qué lo sujeta

Las 54 celdas del eje.
