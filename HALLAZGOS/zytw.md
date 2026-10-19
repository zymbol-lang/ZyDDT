# Hallazgos — `zytw` (tree-walker)

> Un hallazgo entra aquí cuando el runner nombra a `zytw` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

**Uno abierto, `ZYTW-016`**, deuda declarada el 2026-10-16 y mantenida en la v0.0.11. `ZYTW-010` se corrigió el 2026-10-10; esta línea nombró a `ZYTW-004` hasta ese día, corregido desde el 2026-09-16. El estado vivo lo calcula `./bin/zyddt findings` de la línea **Estado** de cada ficha, y pone en rojo (`STALE SUMMARY`) la frase de aquí que la contradiga. `ZYTW-002` y `ZYTW-003` se corrigieron el día que se encontraron. `ZYTW-001` lo encontró el primer eje que le preguntó por el
alcance (`axes/isolation.toml`, 2026-09-12) y está corregido. Hasta ese día este
fichero decía «ninguno todavía», y decía la verdad por la razón equivocada: nadie
le había preguntado casi nada. La cifra que importa es la tabla de `zyddt axis`,
no la longitud de este fichero.

---

## ZYTW-001 — Una lambda que nombra algo fuera de su alcance: `check` calla, la VM lo rechaza y el tree-walker revienta a mitad de la salida

**Estado:** **CORREGIDO 2026-09-12** — y el hueco era mucho mayor de lo que esta
ficha decía: no era el alcance, era que **el analizador no entraba en el cuerpo
de una lambda de bloque en absoluto**
**Encontrado por:** `isolation/block-var-lambda` y `isolation/caller-local-lambda`
**Familia:** [`ERROR-ZYB-002`](../../ZyBank/HALLAZGOS.md#error-zyb-002) — la sugerencia `°` ya se señaló allí como un empujón hacia el rodeo equivocado, y sigue igual

### Qué se observa

```zymbol
lee = () -> { >> de_bloque ¶ }
? #1 {
    de_bloque = 10
    >> de_bloque ¶
    lee()
}
```

```text
$ zymbol check …          No errors or warnings

zytw   error/runtime   imprime «10» y ENTONCES falla
       error  'de_bloque' is undefined — did you mean 'de_bloque°' (hot definition)?
zyvm   error/static    error  undefined variable 'de_bloque'
zyjs   error/static    error @4  undefined variable 'de_bloque'
                       help: variables must be defined before use
```

Los tres rechazan el programa, así que el `expect = "error"` del eje se cumple y
la celda no es `WRONG`. Es `DIVERGE`, y lo que diverge es **cuándo**: dos motores
lo saben antes de ejecutar y el tercero lo descubre con media salida ya escrita.

### Causa

**Localizada** (`crates/zymbol-semantic/src/type_check.rs`, brazo `Expr::Lambda`).
Un cuerpo de lambda tiene dos formas y sólo una se comprobaba:

| forma | a dónde iba | comprobaba |
|---|---|---|
| `() -> expr` | `infer_expr` | **sí** — `infer_expr` ES lo que comprueba |
| `() -> { … }` | `infer_return_type_from_block` | **no** — sólo recolecta tipos de retorno |

Así que dentro de un `-> { … }` **nada semántico se miraba**. Medido el
2026-09-12, el mismo código dentro y fuera de una lambda de bloque:

| escrito | fuera | dentro |
|---|---|---|
| un nombre que no existe en ninguna parte | error | **silencio** |
| una llamada con la aridad mal | error | **silencio** |
| una llamada a la que le falta la marca `<~` | error | **silencio** |
| `m[i][j]` | error | error — lo rechaza el **parser**, no el analizador |

Esa última fila es la que hacía el hueco pequeño a la vista: algo seguía
fallando ahí dentro, así que no parecía una zona ciega.

Es la misma forma que los operandos de `$#`, `$?` y `$??`, que el comentario
del propio fichero ya describe: *«un sitio que `infer_expr`/`check_statement`
no visita es un sitio donde todas las comprobaciones están apagadas»*.

### Alcance

Cualquier lambda cuyo cuerpo nombre algo que no existe donde la lambda se crea.
Dos cosas lo agravan:

- **`check` es el filtro que usan los envoltorios de las otras repos.** Un
  programa así pasa el gate estático y luego se comporta distinto según el motor
  — y la VM es el futuro motor por defecto, así que la respuesta cambiará sola.
- **La sugerencia engaña.** `de_bloque°` es un mecanismo de ámbito de bucle;
  ofrecerlo aquí empuja a escribir un rodeo en lugar de a pasar el valor. Es
  exactamente la objeción que `ERROR-ZYB-002` levantó en agosto contra el mismo
  mensaje.

### Arreglo aplicado

Recorrer el cuerpo con `check_statement` antes de inferir el tipo de retorno.
Cinco líneas en el brazo `Expr::Lambda`, en el analizador compartido, así que
vale para los dos motores Rust a la vez. `zyjs` ya lo hacía y no necesitó nada.

**Y corrigió un falso positivo de paso.** `corpus/memory_correct_01_lambdas.zy`
—un fichero cuyo título es «uso correcto de lambdas»— tenía grabado como golden
`error: undefined variable 'first'`:

```zymbol
apply_twice = (func, value) -> {
    first = func(value)      // la asignación no se visitaba
    <~ func(first)           // el `<~` sí, para inferir el retorno → 'first' indefinida
}
```

El analizador miraba **sólo los `<~`** del cuerpo y ninguna de las sentencias
anteriores. El golden guardaba ese falso positivo como comportamiento esperado;
ahora el programa imprime lo que él mismo dice esperar (7 y 125).

### Impacto, medido antes de dar por bueno

| | |
|---|---|
| corpus | 1 golden, y era el falso positivo de arriba; `consensus` sigue 660 de acuerdo y 0 divergiendo |
| aplicaciones y ejemplos | **0 causados**. Tres ficheros dan error y ninguno es de este cambio: `GO/集計.zy` no contiene una sola lambda de bloque, `ZethyCLI/main.zy` falla en el lexer por una llave sin cerrar, y `ZethyCLI/config.zy` sólo fallaba por la ruta desde la que se le llamaba |
| `cargo test`, `reject` | sin cambios |

### Qué lo sujeta

Las dos celdas del eje, **verdes desde el 2026-09-12**. Vuelven a rojo el día que
el tree-walker se adelante o la VM se retrase.

Lo que **no** sujeta nada todavía: que el analizador siga entrando en el cuerpo
de una lambda. Las dos celdas preguntan por un nombre fuera de alcance, no por la
aridad ni por la marca `<~` escritas ahí dentro, que eran las otras dos mitades
del hueco. Tres celdas más lo cerrarían.

Y hay una razón estructural para desconfiar del vacío: el tree-walker es **el
banco de diagnósticos**, así que cuando dos motores discrepan en un mensaje la
dirección por defecto es alinear al otro con éste. Eso hace que sus mensajes
salgan «bien» por construcción, no por comprobación. El 2026-08-30 fue así en
ocho de los nueve hallazgos; la excepción fue [`GLOBAL-001`](GLOBAL.md), donde la
forma elegida fue la de la VM y **el que cambió fue el tree-walker**.

Para referencia, el sondeo de `Divergente_ES` le atribuyó cuatro: `DM-01`,
`DM-15`, `DM-19` y `DM-26`. Ninguna está sujeta por una celda de ZyDDT — pasarlas
a chincheta es trabajo pendiente y es la parte arqueológica de
[`../MIGRATION.md`](../MIGRATION.md) § 3, paso 3.

---

## ZYTW-002 — Un `:!` que falla se salta el `:>`, y el error que cruza un `:>` se localiza en el `:>`

**Estado:** **corregido 2026-09-14**
**Encontrado por:** `error-flow/error-in-catch-still-runs-finally` y `error-flow/error-through-finally-keeps-its-line`, 2026-09-14 — el eje se escribió para la VM (`GLB-010`) y el tree-walker era el de referencia
**Gravedad:** media. Un `:>` es donde se cierra lo que se abrió, y es justamente el caso en que algo ya ha ido mal

### Qué se observa

```zymbol
!? {
    !? { >> 10 / 0 ¶ } :! ##Div {
        a = [1]
        >> a[9] ¶                   // el catch falla
    } :> {
        >> "limpieza" ¶
    }
} :! ##Index {
    >> "exterior" ¶
}
```

| | salida |
|---|---|
| `zytw` | `exterior` |
| `zyjs` | `limpieza` · `exterior` |
| Python, mismo flujo | `limpieza` · `exterior` |

`REFERENCE.md`: *«`:> { }` — finally block (always executes, regardless of
error)»*.

Y la segunda mitad, en el mismo sitio: un error que atraviesa un `:>` sale
localizado **en la última línea del `:>`**, no donde ocurrió.

```zymbol
!? {
    >> "a" ¶
    >> 10 / 0 ¶        // línea 3
} :> {
    >> "limpieza" ¶    // línea 5
}
```

`zytw` dice `--> main.zy:5`; `zyjs` dice `:3`.

### Causa

`crates/zymbol-interpreter/src/lib.rs`, `execute_try`:

```rust
self.execute_catch_block(catch_clause, err_val.clone())?;
```

El `?` devuelve antes de llegar al bloque del `:>`. Y la línea: el error del
cuerpo se guarda sin localizar en `try_result`, el `:>` ejecuta sus sentencias
—que actualizan la línea en curso— y el error se localiza al salir, con la
línea que dejó el `:>`.

### Arreglo

Guardar el resultado del catch en vez de propagarlo, ejecutar el `:>` y
propagar después, con la misma precedencia que ya tiene el cuerpo: un error del
`:>` gana. Y localizar el error del cuerpo (y el del catch) **antes** de
ejecutar el `:>`.

### Una tercera mitad, que salió al arreglar las dos

Un `:>` que falla mientras lleva un `<~` pendiente restauraba ese retorno
**antes** de propagar su error, y el retorno seguía viajando con él: cortaba el
`>> f() ¶` del llamador después del valor y antes del `¶`, y llegaba al nivel
superior como estado de salida del programa — `1`. La vio
`error-flow/return-runs-finally-outside-its-own-catch`, que comparaba la salida
y además el código.

### Qué lo sujeta

`error-flow/error-in-catch-still-runs-finally`,
`error-flow/error-through-finally-keeps-its-line` y
`error-flow/return-runs-finally-outside-its-own-catch`.

---

## ZYTW-003 — Cada error capturado deja abiertos los ámbitos donde se lanzó

**Estado:** **corregido 2026-09-14**
**Encontrado por:** leyendo `execute_block` al corregir `ZYTW-002`, y confirmado midiendo antes de tocarlo
**Gravedad:** media: no cambia ninguna salida, pero un bucle que captura errores se vuelve cuadrático

### Qué se observa

```zymbol
c = 0
@ _i:1..80000 {
    !? { >> 10 / 0 ¶ } :! { c += 1 }
}
```

| capturas | `zytw` | `zyvm` |
|---:|---:|---:|
| 20 000 | 0,61 s · 33 MB | 0,02 s |
| 80 000 | **11,9 s · 110 MB** | 0,03 s |

Cuatro veces las capturas, **19,5 veces** el tiempo.

### Causa

`execute_block` hace `push_scope`, recorre las sentencias con `?` y hace
`pop_scope` sólo si ninguna falla. Un error que sale de tres bloques deja tres
ámbitos abiertos, y el `!?` que lo captura sigue ejecutando encima de ellos:
cada búsqueda de un nombre recorre todos los que dejó cada captura anterior. Lo
mismo con los bucles (`push_loop_scope`) y con el bloque del `:!`.

### Arreglo

El `!?` es el único sitio donde un error deja de viajar, así que es el único que
tiene que devolver la pila: guarda la profundidad al entrar y la restaura al
capturar, al fallar el catch y al fallar el `:>` (`unwind_scopes_to`). Una función
ya lo hacía con `restore_call_state`.

### Qué lo sujeta

`zyquality/cost/`, caso `growth/caught-errors`: el mismo programa a N y a 4N, con
el límite entre lineal (4,0) y cuadrático (16,0). Tras el arreglo, `zytw` 3,75,
`zyvm` 3,93, `zyjs` 3,04.

---

## ZYTW-004 — `db: cannot bind` imprime la estructura interna de la lambda, con sus spans

**Estado:** **corregido el 2026-09-16** (paso 3.4) el caso de `db`; el segundo caso pasa al paso 3.5
**Encontrado por:** `runtime-std-db/cannot-bind-a-function`, paso C11 del plan de cobertura de diagnósticos, 2026-09-14
**Gravedad:** baja en efecto, alta en lo que enseña: el mensaje expone el `Debug` de Rust
**Familia:** `GLB-017` B (`error executing … Located { … }`)

`d::exec("c", "select ?", (v,))` con `v` una lambda:

| motor | |
|---|---|
| `zytw` | `db: cannot bind Function(FunctionValue { params: ["x"], body: Expr(Identifier(IdentifierExpr { name: "x", span: Span { start: Position { line: 5, column: 11, byte_offset: 72 }, … module_aliases: {"d": "__stdlib__/std/db"} }) as a parameter` |
| `zyvm` | `db: cannot bind ##fn as a parameter` |

### Causa

`crates/zymbol-interpreter/src/stdlib/db.rs`, `bind_params`: formatea el valor
con `{:?}`. Es el mismo patrón que muchos diagnósticos del tree-walker del paso
C3 (`got Int(5)`, `got String("x")`), aquí con un valor cuyo `Debug` es enorme.

### Qué lo sujeta

`runtime-std-db/cannot-bind-a-function` (NEW WORDING hasta que el texto sea uno).

### Otro caso, medido el 2026-09-15 (paso 1.5)

Indexar una cadena con una lambda, `"echo "[g]` con `g = x -> x`, vuelca lo
mismo en el `_err`: `##Index(index must be an integer, got Function(FunctionValue
{ params: ["x"], body: Expr(Identifier(IdentifierExpr { … span: Span { … } … })`.
La VM dice `##Type(this needs Int and got Function)`. Además del texto, el kind:
un índice del tipo equivocado es `##Type` (decisión D1 del 2026-09-15, `GLB-012`).
Sin celda propia: es el `{:?}` de este mismo hallazgo.

### Corregido el 2026-09-16 (paso 3.4)

`bind_params` escribe el tipo con `Value::type_name()`, el mismo vocabulario que
la VM usa en ese mensaje (`zymbol_type_name()`). Medido con cada tipo que no se
puede enlazar, texto y tipo coinciden en los dos motores:

| valor | los dos motores |
|---|---|
| `[1, 2]` | `##_(db: cannot bind ##[] as a parameter)` |
| `(1, 2)` | `##_(db: cannot bind ##() as a parameter)` |
| `#(a: 1)` | `##_(db: cannot bind ##(name:) as a parameter)` |
| `x -> x` | `##_(db: cannot bind ##fn as a parameter)` |

`runtime-std-db/cannot-bind-a-function` pasa a `AGREE [2/3]` y el eje queda en
16 de 16. El segundo caso —indexar con una lambda— es uno de los `{:?}` del paso
3.5, y su tipo (`##Type`) es de F4.

Por el camino, [[GLB-033]]: esos nombres de tipo (`##[]`, `##fn`) no son los que
da `#?` (`##]`, `##->`).

---

## ZYTW-005 — Una lambda no captura un nombre que sólo lee dentro de una interpolación

**Estado:** **corregido el 2026-09-15** (paso 2.15b), en el TW y en la VM
**Encontrado por:** paso 2.15, 2026-09-15, al arreglar el mismo defecto en `zyjs`
**Gravedad:** media: un valor que nadie calculó, invisible si el programa no lo imprime

```zymbol
log = ""
tag = (s -> { log = "{log}{s}"  <~ log })
>> tag("A") " " tag("B") ¶
```

| motor | |
|---|---|
| `zytw` | `{log}A {log}B` |
| `zyvm`, `zyjs` | `A B` |

La lambda no captura `log`, porque su análisis de capturas no entra en las partes
de una cadena. En la llamada, `{log}` no se resuelve y la interpolación deja el
texto literal. `zyjs` tenía el mismo defecto (`collectIdentNames`), escondido
porque el `catch` de su evaluación de cadenas escribía el nombre tal cual; se
arregló en el paso 2.15, porque sin eso `corpus/lambdas/28_eval_order_and_capture.zy`
divergía. En el TW sigue: `zyq consensus` no lo ve porque ese fichero no imprime
`log`. Desde el paso 1.6 (`GLB-018` A), una interpolación de algo que no existe
debería ser error y no texto.

### Qué lo sujeta

`runtime-functions-hof/lambda-captures-a-name-read-in-a-string`, roja por el TW.

### Corregido — 2026-09-15 (paso 2.15b)

`collect_refs_in_expr` (`functions_lambda.rs`) pasaba de largo por los literales;
ahora cuenta como referencia cada nombre de una cadena interpolada, con el
escáner compartido de `zymbol-semantic` (`interpolated_names`, hecho público). Al
medirlo con una lambda devuelta desde el bloque de otra apareció **el mismo
defecto en la VM**: `collect_free_in_expr` tampoco entraba en las cadenas, y
`(x -> "x={x} m={m}")` imprimía `m={m}`. Se corrigió en el mismo paso. Los tres
motores coinciden con una lambda anidada, un local de función y el iterador de un
bucle. La celda pasa a `AGREE`.

---

## ZYTW-006 — Tres diagnósticos de rango del tree-walker quedaron inalcanzables cuando D4 los hizo estáticos, y dos celdas verdes miden otro mensaje

**Estado:** **corregido el 2026-09-22** (paso G2), decidido por el autor el mismo día
**Encontrado por:** paso G2, 2026-09-22, al medir las celdas del grupo C
**Gravedad:** baja en ejecución (nadie los ve), media en el arnés: dos celdas están verdes midiendo un mensaje distinto del que declaran

### Qué se observa

`eval_iterable` (`crates/zymbol-interpreter/src/expr_eval.rs:16`) tiene un brazo
`Expr::Range` con tres diagnósticos propios:

| línea | mensaje |
|---|---|
| `expr_eval.rs:28` | `range start must be an integer, got {}` |
| `expr_eval.rs:38` | `range end must be an integer, got {}` |
| `expr_eval.rs:~46` | el del paso (`step`) del mismo brazo |

Ese brazo ya no es alcanzable. Sólo hay dos caminos hasta él:

1. `loops.rs:196`, la vía lenta de `@ var:iterable` — pero `loops.rs:147`
   intercepta **todo** `Expr::Range` antes, en la vía rápida, y allí el mensaje
   es otro: `range bounds must be integers, got {} and {}` (`loops.rs:169`), un
   solo texto para los dos bordes.
2. `eval_iterable_pairs` ← `loops.rs:131`, la vía de `@ (patrón):iterable` — y
   **D4 (F5, 2026-09-21) hizo `@ (patrón):rango` un error estático.**

Medido el 2026-09-22 con `zymbol check`: las cuatro formas —`@ (a,b):1..v`,
la agrupada `@ (a,b):(1..v)`, la del paso `@ (a,b):1..v:2` y **la que tiene
límites enteros válidos** `@ (a,b):1..3`— se refusan antes de correr. No queda
ninguna vía a ejecución.

El mensaje vivo, en cambio, sí está en los tres motores y coincide:

```zymbol
t(v) { @ i:1..v { >> i ¶ }  <~ 1 }
>> t(1.5) ¶
```

| motor | |
|---|---|
| `zytw`, `zyvm`, `zyjs` | `range bounds must be integers, got Int and Float` |

(`loops.rs:169`, `zymbol-vm/src/lib.rs:3506`, `web/src/zymbol/zymbol.js:7429`.)

### Lo que esto le hace al arnés

`runtime-loops-ranges/range-start-must-be-an-integer-got` y
`…/range-end-must-be-an-integer-got` declaran
`what = "range start/end must be an integer, got {:?}"` y están **verdes** —
pero lo que los tres motores contestan a su programa es
`tuple pattern '( … )' requires a tuple, got Int`. El veredicto es honesto
(los tres refusan), el `what` no: ningún motor produce ya ese texto.

Y `range bounds must be integers, got {} and {}` —el mensaje que sí sale— **no
lo mide ninguna celda**. Es cobertura perdida, no ganada: las dos celdas que
deberían sujetarlo se quedaron sujetando otra cosa sin que nadie lo notara,
que es el mismo modo de fallo que [[GLB-047]].

Sus `-met` sí se arreglaron en el paso G2: piden `error`, con la razón escrita.

### Decidido y corregido — 2026-09-22 (paso G2)

El autor eligió **borrar el muerto y reapuntar las dos celdas**.

1. **El brazo se borró.** `eval_iterable` ya no hace `match expr`: evalúa la
   expresión y reparte por el valor. Con el brazo se fueron los dos textos de
   rango. El tercero, `step must be positive, got {}`, **no se perdió**: vive en
   `loops.rs:154`, `zymbol-vm/src/lib.rs:3493` y `zymbol.js:7426`, comprobado
   antes de borrar.
2. **Las dos celdas se reapuntaron** a `@ i:` y se renombraron
   `range-bounds-must-be-integers-end` y `…-start`, con la razón escrita en el
   TOML. Las dos miden ahora el texto vivo, y miden cosas distintas: el mismo
   mensaje imprime `Int and Float` en una y `Float and Int` en la otra.
   `tuple pattern '( … )' requires a tuple`, lo que medían sin querer, ya lo
   sujeta `runtime-match-patterns` — comprobado antes de reapuntar, para no
   dejar el mensaje sin celda.
3. **Sus `-met` piden `warn`, no `ok`.** Primero las puse en `ok` y salieron
   rojas: los tres motores contestan `##Type` y lo atrapan, pero el programa
   también emite `range direction is decided at runtime`, porque el límite viene
   de una variable. Ése era el motivo del `warn` que las celdas traían de
   origen, y volverlo a poner es lo correcto, no un apaño.

**El inventario de mensajes se editó a mano**, como manda el método: fuera las
dos líneas de `messages/baseline.txt` (616 de 932 → **614 de 930**: sólo baja, y
baja exactamente por los dos borrados), fuera sus dos filas de
`messages/queue/runtime.tsv`, y de paso se repararon dos filas que ya apuntaban
a sitios muertos — `range bounds…` nombraba una celda inexistente y
`step must be positive` seguía apuntando a `expr_eval.rs:51`.

### Qué lo sujeta

`runtime-loops-ranges/range-bounds-must-be-integers-end` y `…-start`, con sus
`-met`. El eje queda 22 de 23, y ahora ese verde mide lo que dice medir.

---

## ZYTW-007 — Llamar a una lambda destruida dice `undefined function`

**Estado:** **corregido el 2026-09-25** (paso P4.7)
**Encontrado por:** midiendo [`GLB-055`](GLOBAL.md), 2026-09-25

```zymbol
g = () -> 1
\g
>> g() ¶
```

| motor | |
|---|---|
| `zytw` | `Runtime error: undefined function: 'g'` |
| `zyvm`, `zyjs` | `Runtime error: use after destruction: variable 'g' was destroyed after its last use` |

La llamada busca `g` entre las funciones al no encontrarla entre las variables, y
no mira antes si la variable se destruyó.

### Qué lo sujeta

`lifetime/call-a-destroyed-lambda`, roja (`WORDING`).

### Corregido el 2026-09-25 (paso P4.7)

Antes de buscar la función por nombre, la llamada comprueba con
`check_variable_alive` si el nombre es una variable destruida. Solo lo hace cuando
no hay una función con ese nombre. `lifetime` queda 24 de 24.

---

## ZYTW-008 — Una función cuyo parámetro se llama como el estado del módulo llama a otra: el TW escribe el parámetro en el estado

**Estado:** **corregido 2026-10-10** — sin decisión: la VM y `zyjs` coinciden, y un parámetro es de su función
**Encontrado por:** la misma sonda de [`ZYVM-018`](zyvm.md)

```zymbol
// mod/pasa.zy
# pasa {
    #> { d, ver }
    datos = [1, 2, 3]

    lee(v) { <~ v$# }
    d(datos) { <~ lee(datos) }
    ver() { <~ datos }
}
```

```zymbol
<# ./mod/pasa => P
>> P::d([1]) " " P::ver() ¶
```

`zyvm` y `zyjs`: `1 [1, 2, 3]`. **`zytw`: `1 [1]`** — después de la llamada, el estado del módulo es el argumento.
No hay ningún `<~` en el programa.

| `d(datos)` con el argumento `[1]` | `zyvm`, `zyjs` | `zytw` |
|---|---|---|
| `<~ lee(datos)` — llama a otra función del módulo | estado `[1, 2, 3]` | **estado `[1]`** |
| `otro(datos<~)` — la llama con el parámetro como salida | estado `[1, 2, 3]` | **estado `[1]`** |
| control: `datos[1]$~ 9` · `<~ datos` — no llama a nadie | estado `[1, 2, 3]` | estado `[1, 2, 3]` |
| control: el parámetro se llama `p` | estado `[1, 2, 3]` | estado `[1, 2, 3]` |

### Causa

El TW da a cada marco una copia de las variables del módulo que su cuerpo nombra, y al salir —y al entrar en otra
función del mismo módulo— publica las que han cambiado. Un cuerpo «nombra» `datos` también cuando `datos` es su
parámetro: la variable del módulo se inyectaba, el parámetro ocupaba su sitio en el ámbito, y en la siguiente
llamada el vaciado encontraba una «variable de módulo» con otro valor —el argumento— y la publicaba. La escritura
de vuelta al salir ya excluía a los parámetros; el vaciado al entrar, no.

### Corrección (2026-10-10)

Un nombre que es parámetro de la función no se inyecta. Y una función llamada desde otra del mismo módulo toma el
valor vivo del marco que llama sólo si a ese marco se le **dio** la variable del módulo, no si tiene en su ámbito
algo que se llama igual.

| `d(datos)` con el argumento `[1]` | antes, `zytw` | ahora, los tres |
|---|---|---|
| `<~ lee(datos)` | estado `[1]` | estado `[1, 2, 3]` |
| `otro(datos<~)` · `<~ datos` | devuelve `[1, 5]`, estado `[1]` | devuelve `[1, 5]`, estado `[1, 2, 3]` |

### Qué lo sujeta

`runtime-modules-scripts/call-from-a-function-whose-parameter-is-named-like-module-state`, ya sin deuda y con un
oráculo en Python. Con el TW de antes da DIVERGE.

---

## ZYTW-009 — `s = s + t` sobre dos cadenas: el TW las une, donde `+` es sólo aritmético

**Estado:** **corregido 2026-10-10**, el día en que se encontró — sin decisión: la regla ya estaba, y el propio TW
la aplica en cualquier otro sitio
**Encontrado por:** leyendo los atajos de asignación del TW para corregir [`GLB-115`](GLOBAL.md)

```zymbol
s = "a"
s = s + "b"
>> s ¶
```

`zyvm` y `zyjs`: `+ is arithmetic only — use juxtaposition to concatenate strings: "a" b "c"`. **`zytw`: `ab`.**

| programa | `zytw`, antes | `zyvm`, `zyjs` |
|---|---|---|
| `s = s + t`, dos cadenas | **`ab`** | `##Type` |
| `s = s + c`, cadena y carácter | **`abx`** | `##Type` |
| `s += t` | **`abxb`** | `##Type` |
| control: `u = s + t`, a otra variable | `##Type` | `##Type` |

La misma operación se rechazaba o se hacía según a quién se asignara el resultado. Un programa que une texto así
corría en el motor por defecto y en ningún otro; la VM va a ser el motor por defecto. Ningún fichero del corpus ni
de las aplicaciones lo hacía —correría en uno de tres—, y por eso no lo vio nada.

### Causa

El atajo de `x = x OP y` (`variables.rs`, «B12») tenía un tercer brazo, después del entero y el flotante: si `OP`
es `+` y los dos lados son cadenas, `push_str`. Venía de cuando `+` unía cadenas.

### Corrección

El brazo se quita. `s = s + t` llega al operador, que lo rechaza con las palabras de siempre. La forma que une
texto, `s = s x`, gana su propio camino en el sitio (ver [`ZYTW-011`](zytw.md)).

### Qué lo sujeta

`runtime-operators/plus-on-strings-assigned-to-its-own-left-side-is-refused`. La marca se imprime **después** de
la sentencia: un motor que une lo dice. Con el TW de antes da DIVERGE.

---

## ZYTW-010 — Llamar a una función de un módulo cuesta el tamaño del estado del módulo

**Estado:** **corregido 2026-10-10** — la mitad de lectura por la mañana; la de escritura, que el autor había decidido
no corregir ese mismo día, la pidió horas después: el estado de un módulo vive ya en un solo sitio
**Encontrado por:** leyendo cómo sincroniza el TW el estado de un módulo, para [`ZYTW-008`](zytw.md), y midiéndolo
**Familia:** [`ZYVM-003`](zyvm.md), ya cerrado — allí copiaba cada edición; aquí, cada llamada

```zymbol
// mod/mesa.zy
# mesa {
    #> { crear, leer, poner, cuanto }
    t = []

    crear(n) { @ i:1..n { t$+ 0 } }
    leer(i) { <~ t[i] }
    poner(i, v) { t[i]$~ v }
    cuanto() { <~ t$# }
}
```

```zymbol
<# ./mod/mesa => M
M::crear(16000)
@ k:1..2000 { M::poner((k % 16000) + 1, k) }
>> M::cuanto() ¶
```

Es la forma de un módulo con API: el estado se toca una casilla por llamada, desde fuera. Instrucciones, 2000
llamadas, con el estado a 4000 y a 16 000 casillas:

| cada llamada | `zytw`, antes | `zytw`, ahora | `zyvm` |
|---|---:|---:|---:|
| **lee** una casilla, `leer(i)` | 374 M → **1 401 M** | 41 M → 66 M | 9 M → 23 M |
| **escribe** una casilla, `poner(i, v)` | 821 M → **2 905 M** | 822 M → **2 911 M** | 11 M → 25 M |
| control: escribe otra variable del módulo, pequeña | 223 M → 244 M | 224 M → 249 M | 9 M → 23 M |

### Causa

El TW no guarda el estado de un módulo en un solo sitio. Cada marco recibe una **copia** de las variables que su
cuerpo nombra —el almacén del módulo conserva el original— y, al salir, decide cuáles ha cambiado comparando cada
una con la que recibió.

- **Leer:** el 91 % del tiempo estaba en `Value::eq`. Una tabla que nadie tocó se comparaba consigo misma,
  elemento a elemento, en cada llamada.
- **Escribir:** el original sigue en el almacén, así que el marco nunca es el único dueño de la colección: la
  primera edición de cada llamada la copia entera (54 % en `Vec::clone`, 25 % soltándola), y la comparación de
  salida la recorre otra vez.

### Corrección, la mitad de lectura (2026-10-10)

La comparación pregunta primero por la **identidad**: un marco que no escribió una colección sigue teniendo el
mismo `Rc` que recibió. Sólo si los punteros difieren se comparan los valores, como antes — un marco que escribió
de vuelta lo que ya había no ha cambiado nada, y decir que sí dejaría que su copia pisara lo que guardó una
llamada anidada.

### Qué hay que decidir, la mitad de escritura

Quitar la copia por llamada es dejar de inyectar: que el estado de un módulo viva en un solo sitio y las funciones
lo lean y lo escriban ahí, como en la VM y en `zyjs`, que *«never had the question»* (lo dice el propio comentario
del TW). Desaparecen la inyección, la instantánea, el vaciado al entrar y la escritura de vuelta al salir — y con
ellos la clase de fallo de [`ZYTW-008`](zytw.md) y [`ZYTW-013`](zytw.md), que son los dos de esa maquinaria.

- **hacerlo:** es reescribir cómo el TW resuelve una variable dentro de un módulo. Lo sujetan el corpus, las nueve
  aplicaciones y ZyDDT, que hoy están en verde;
- **no hacerlo:** la VM va a ser el motor por defecto y ya no lo tiene; el TW queda con una llamada que cuesta el
  tamaño del estado cuando escribe, declarada.

### Decisión (2026-10-10)

El autor: **no hacerlo**. La VM pasa a ser el motor por defecto —en esta versión o en una próxima, sin fijar— y ya
guarda el estado de un módulo en un solo sitio. Reescribir cómo el TW resuelve nombres dentro de un módulo no
compensa para un motor que deja de ser el de por defecto.

Queda como deuda **declarada**: la ficha sigue abierta, el caso de coste la muestra `KNOWN` en cada corrida con su
ratio, y no enrojece la puerta. Si el relevo no llega, esta ficha es la que hay que reabrir.

### La decisión, revocada, y la mitad de escritura (2026-10-10)

El autor, ese mismo día: **hacerlo**. La deuda había quedado declarada y a la vista — 13,76 con límite 6,00 en
cada corrida — y es así como se vuelve a mirar.

No se reescribió cómo el TW resuelve un nombre. Se cambió **dónde está la tabla**: mientras corre un marco de un
módulo, la tabla de variables de ese módulo (`LoadedModule::all_variables`) *es* el ámbito más externo del marco
—`scope_stack[0]`—, movida fuera del almacén, y los ámbitos propios del marco empiezan en el índice 1. Toda
búsqueda que ya recorría la pila de ámbitos de dentro afuera encuentra el estado del módulo al final, en su único
sitio; una edición es la única dueña de la colección y escribe en el sitio; un parámetro o un local del mismo
nombre lo tapa por estar más adentro.

La tabla está en el marco **sólo mientras ese marco es el que corre**. `take_call_state` la devuelve al almacén
antes de cualquier llamada, y `restore_call_state` la vuelve a sacar: lo que la llamada alcance —el mismo módulo,
directamente o a través de otros tres— la encuentra allí. Mover un `HashMap` son tres palabras de máquina; no hay
copia, ni instantánea, ni comparación al salir.

Lo que desaparece: la inyección de las variables que el cuerpo nombra y su caché (`module_var_mentions`), la
instantánea de cada marco (`frame_module_vars`), el vaciado al entrar en una hermana (`flush_module_frame`,
MM-12), la escritura de vuelta con su comparación (`still_the_injected`, MM-2) y el refresco del llamante: 279
líneas fuera de `functions_lambda.rs` y 70 dentro. Con esa maquinaria se va la clase de fallo de [`ZYTW-008`](zytw.md) y
[`ZYTW-013`](zytw.md).

Lo que hubo que cuidar, porque la tabla del módulo ya no es una copia que se pueda estropear:

- `take_variable` (el `<~ nombre` que mueve en vez de copiar) y el auto-free no alcanzan el índice 0. `\ nombre`
  tampoco lo alcanzaba ese día: daba el nombre por terminado para el marco, como antes. Al día siguiente pasó a
  terminarlo para el módulo ([`GLB-120`](GLOBAL.md)).
- Las constantes del módulo van en el conjunto de constantes del índice 0. `is_const` no las aplica a un
  parámetro o a un local que las tape, y `unmark_const` no las toca: antes cada marco tenía su copia de las marcas.
- La marca caliente sin bucle ancla en el primer ámbito **del marco**, no en la tabla del módulo.
- Un argumento de salida que es estado del módulo sigue sin prestarse (`is_module_state`): prestarlo lo sacaría
  de la tabla mientras dura la llamada, y una función del módulo llamada entretanto no lo encontraría.
- Lo que una función con nombre captura del fichero no tapa una variable del módulo que se llame igual.

| 12 000 llamadas, cada una escribe una casilla de 12 000 | `zytw`, antes | `zytw`, ahora | `zyvm` |
|---|---:|---:|---:|
| tiempo | 1 930 ms | 27 ms | 22 ms |
| razón al cuadruplicar el tamaño | 13,76 | **3,27** | 3,31 |

### Lo que corrigió de paso: lo escrito antes de un fallo

```zymbol
falla(i) {
    t[i]$~ 99
    n += 100
    x = t[1000]        // falla
    <~ x
}
```

```zymbol
!? { A::falla(2) } :! { }
>> A::leer(2) " " A::total() ¶
```

| | salida |
|---|---|
| `zytw`, antes | `0 0` — ninguna de las dos escrituras (en la sonda, `0 1` con el contador en 1 antes de la llamada) |
| `zyvm`, `zyjs`, y `zytw` ahora | `99 100` |

Un marco que fallaba soltaba su copia, y con ella todo lo que había escrito antes de fallar. No lo veía nada: ni
el corpus ni ninguna celda escribían el estado de un módulo y fallaban después. Lo encontró la sonda que comparó
el TW antes y después de este arreglo, con 20 formas de tocar el estado de un módulo, en los tres motores. La
misma sonda abrió [`ZYVM-020`](zyvm.md) y [`ZYVM-021`](zyvm.md), corregidos ese día, y lo que acabó siendo [`GLB-120`](GLOBAL.md), corregido al día siguiente.

### Qué lo sujeta

`zyquality/cost`: `growth/module-call-that-reads-one-cell` y `growth/module-call-that-writes-one-cell`, en verde
en los tres y sin deuda declarada. `runtime-modules-scripts/module-state-written-before-a-failure-stays-written`,
con oráculo. Y lo que ya sujetaba el estado de módulo y siguió en verde sin tocarlo: `modules_scope/` del corpus
(23 ficheros), las celdas de `GLB-119`, `ZYTW-008` y `ZYTW-013`, y las nueve aplicaciones.

---

## ZYTW-011 — Un operando se evalúa dos veces cuando el atajo de la asignación no se puede aplicar

**Estado:** **corregido 2026-10-10**, el día en que se encontró — sin decisión
**Encontrado por:** leyendo los atajos de asignación del TW para corregir [`GLB-115`](GLOBAL.md)

```zymbol
dos() {
    >> "llamada" ¶
    <~ 2
}
n = 10
n = n / dos()
>> n ¶
```

`zyvm` y `zyjs`: `llamada`, `5`. **`zytw`: `llamada`, `llamada`, `5`.**

| sentencia | llamadas a `f` en `zytw`, antes | en `zyvm`, `zyjs` |
|---|---:|---:|
| `n = n / f()` · `n = n % f()` · `n = n ^ f()` | **2** | 1 |
| `x = x / f()`, con `x` flotante | **2** | 1 |
| `s = s f()` — el acumulador de texto | **2** | 1 |
| `n = n == f()` · `n = n > f()` | **2** | 1 |
| `v = v && f()`, con `v` cierto | **2** | 1 |
| `v = v && f()`, con `v` **falso** | **1** | 0 |
| `m = m - f()`, flotante y entero | **2** | 1 |
| `x = t[f()]`, `t$-[f()]`, `t[f()]$~ 0`, con el índice fuera de rango | **2** | 1 |
| `s$+ f()`, con `f` que devuelve una cadena | **2** | 1 |
| control: `n = n + f()`, `u = n / f()` | 1 | 1 |

El valor sale bien, así que ningún fichero con salida grabada podía verlo: sólo un operando con efecto —que
imprima, que cuente, que consuma una cola— distingue una evaluación de dos. Y con `&&`, la que no debía ocurrir.

### Causa

`execute_assignment` tiene atajos para `nombre = nombre OP …`: evalúan el operando y trabajan sobre la variable
en su sitio. Cuando el atajo no se podía aplicar —una división, una comparación, una yuxtaposición, un índice
fuera de rango, un tipo que no es el del atajo— el código *«caía»* al camino general, que es
`eval_expr(&assign.value)`: la expresión entera otra vez, operando incluido.

### Corrección

Ningún atajo devuelve la expresión. El operando se evalúa una vez y la operación se termina **con los valores en
la mano**: cada operación del lenguaje que tenía atajo tiene ahora una forma que recibe valores (`append_in`,
`remove_at_in`, `update_in`, `apply_binary`, `index_into`), y es la misma que usa el camino general. `&&` y `||`
no entran al atajo: quien decide si el lado derecho corre es `eval_binary`.

De paso, lo que el camino en el sitio cubre: `s = s x` añade sobre la cadena, y `d["k"]$~ v` y `d.k$~ v` escriben
en el diccionario donde está.

### Coste

El TW, contra el commit anterior, en instrucciones por vuelta de un bucle mínimo y en los benchmarks del proyecto
(nueve corridas):

| | instrucciones | ciclos |
|---|---:|---:|
| `s = s + i` | +6 % | +5 % |
| `a$+ i` | +8 % | +12 % |
| `x = a[3]` · `s = s + x` | +3 % | +5 % |
| `a[3]$~ i` | −12 % | −12 % |
| `f = f * 1.0000001` | −22 % | −23 % |
| `s = s "a"`, 100 000 veces | −94 % | −97 % |
| los ocho de `zyquality/bench/` | de −10 % a +1,5 % | de −11 % a +3 % |

Las dos primeras filas son un coste que no está localizado: no hay ninguna búsqueda de variable de más, y mover el
código entre funciones lo cambia de sitio sin quitarlo.

### Qué lo sujeta

`runtime-functions-hof/operand-of-a-self-assignment-runs-once`, con un oráculo en Python: once sentencias, cada
una con su llamada contada. Con el TW de antes da DIVERGE.

---

## ZYTW-012 — `t = t[1]$~ 9` sobre una tupla: el TW la rechaza, donde construye una tupla nueva

**Estado:** **corregido 2026-10-10**, el día en que se encontró — sin decisión: COL-4
**Encontrado por:** leyendo los atajos de asignación del TW

```zymbol
t = (1, 2)
t = t[1]$~ 9
>> t ¶
```

`zyvm` y `zyjs`: `(9, 2)`. **`zytw`: `cannot modify tuple 't': tuples are immutable`.**

COL-4: una tupla no se modifica, y `u = t[i]$~ v` *deriva* otra. `t = t[i]$~ v` es esa misma derivación, ligada de
vuelta a `t` — como `t = t$+ 3` y `t = t$-[1]`, que los tres motores ya aceptaban. Lo que se rechaza es la
sentencia `t[1]$~ 9`.

### Causa

El atajo de `nombre = nombre[i]$~ v` comprobaba que el receptor no fuera una tupla sin mirar qué forma se había
escrito. La comprobación general, unas líneas antes, sí lo mira.

### Corrección

El atajo deja de comprobarlo: la sentencia ya llegó rechazada, y la forma funcional construye.

### Qué lo sujeta

`runtime-collection-ops/functional-update-of-a-tuple-bound-to-its-own-name`, con oráculo. Con el TW de antes da
WRONG.

---

## ZYTW-013 — Guardar, llamar, restaurar: el TW pierde la escritura que devuelve el estado a su valor de entrada

**Estado:** **corregido 2026-10-10**, el día en que se encontró — sin decisión
**Encontrado por:** una celda de [`GLB-115`](GLOBAL.md) que dio `15` donde eran `5` con el orden ya corregido

```zymbol
// mod/deshace.zy
# deshace {
    #> { deshacer, ver }
    n = 5

    mover() { n = 99 }
    deshacer() {
        mover()
        n = 5
    }
    ver() { <~ n }
}
```

```zymbol
<# ./mod/deshace => D
D::deshacer()
>> D::ver() ¶
```

`zyvm` y `zyjs`: `5`. **`zytw`: `99`.** Es como una búsqueda deshace una jugada.

| `deshacer()`, con `n = 5` al entrar | `zytw`, antes | `zyvm`, `zyjs` |
|---|---|---|
| `mover()` · `n = 5` — el valor de entrada | **`99`** | `5` |
| `mover()` · `n = 6` — otro valor | `6` | `6` |
| lo mismo con una colección, `t = [1, 2]` | **`[9]`** | `[1, 2]` |

### Causa

Al salir, el marco decide qué variables del módulo ha cambiado comparándolas con las que recibió. Tiene dos
copias de «las que recibió»: una local, tomada al entrar, y la del intérprete, que una llamada anidada mueve
cuando escribe el estado (MM-12). La escritura de vuelta comparaba contra **la de entrada**. `n = 5` es igual a
la de entrada, luego «no cambió», y el módulo se quedaba con lo que guardó `mover`.

### Corrección

La escritura de vuelta compara contra la instantánea del marco, la que se mueve.

### Qué lo sujeta

`runtime-modules-scripts/module-state-written-back-to-its-starting-value-after-a-nested-call`, con oráculo. Con
el TW de antes da DIVERGE.

---

## ZYTW-014 — `d[f()]`, con `f` que escribe `d`: el TW indexa lo que `f` dejó

**Estado:** **corregido 2026-10-10**, el día en que se encontró — decidido con [`GLB-115`](GLOBAL.md): de
izquierda a derecha
**Encontrado por:** barriendo las demás lecturas después de corregir las ediciones

```zymbol
cambia(a<~) {
    a = [7, 8, 9, 6]
    <~ 1
}
d = [10, 20, 30]
x = d[cambia(d<~)]
>> x ¶
```

`zyvm` y `zyjs`: `10`. **`zytw`: `7`.**

| lectura | `zytw`, antes | los tres, ahora |
|---|---|---|
| `d[cambia(d<~)]` | `7` | `10` |
| `datos[meter()]`, estado de módulo | `7` | `10` |
| control: `d[1] + cambia(d<~)` · `d$# + cambia(d<~)` · `(d, cambia(d<~), d)` | de izquierda a derecha | igual |

### Causa

`eval_index` evalúa los índices y **después** toma prestada la colección de la variable, para no copiarla
(`HLZ-012`). Es lo mismo que leerla antes — salvo cuando un índice la escribe.

### Corrección

Cuando un índice puede escribir la colección —lo mismo que se pregunta para una edición—, la lectura va por el
camino general, que evalúa la colección primero. Si no, que es casi siempre, sigue prestada.

### Qué lo sujeta

`runtime-functions-hof/self-assignment-whose-operand-writes-the-receiver` y
`runtime-modules-scripts/module-state-read-before-a-later-operand-writes-it`.

---

## ZYTW-015 — Una lambda de bloque que termina sin `<~`: el TW aborta donde la VM y zyjs dan `##_`

**Estado:** **corregido 2026-10-11** — decidido por el autor ese día: da `##_`, como una función con nombre
**Encontrado por:** la auditoría de `interpreter/LLM.md` del 2026-09-07 (`IMPL_V009.md` § E.1). Estuvo un mes
escrita en un plan y sin ficha: ningún fichero del corpus escribía la forma
**Familia:** [`ZYTW-001`](zytw.md) (el analizador no entraba en el cuerpo de una lambda de bloque)

```zymbol
lam = () -> { >> "efecto" ¶ }
lam()
>> "sigo" ¶
```

| | antes | |
|---|---|---|
| `zytw` | `efecto`, y `Runtime error: block lambda must use <~ to return value` | `rc 1` |
| `zyvm`, `zyjs` | `efecto`, `sigo` | `rc 0` |
| `zymbol check` | *No errors or warnings* | |

Medido con cuatro formas el día de la decisión — la llamada como sentencia, el valor (`v = lam()`), un `<~` en
un solo camino y `xs$> (x -> { >> x ¶ })`—: el TW abortaba en las cuatro, y en las cuatro la VM y zyjs seguían
con `##_`. La misma forma con nombre, `f() { >> "efecto" ¶ }`, da `##_` en los tres.

El 2026-09-07 el TW salía con `rc 0` tras abortar; el 2026-10-11 ya salía con 1. La divergencia era la misma.

### Qué se decidió

Devuelve `##_`. La alternativa —error en los tres— habría hecho a una lambda más estricta que una función con
nombre y habría obligado a todo callback llamado por su efecto a terminar en `<~ ##_`.

### Qué cambió

`functions_lambda.rs`: la rama que distinguía `is_named` desaparece; un cuerpo que termina sin `<~` da
`Value::Unit`, tenga nombre o no. El mensaje `block lambda must use <~ to return value` ya no existe.

### Qué lo sujeta

Cuatro celdas en `axes/runtime-functions-hof.toml` (`block-lambda-called-for-its-effect`,
`…-without-return-is-unit`, `…-returns-on-one-path`, `…-as-a-callback`) y
`zyquality/corpus/lambdas/15_block_without_return.zy` con su golden.

---

## ZYTW-016 — Leer una variable de texto la copia: el texto del tree-walker no tiene `Rc`

**Estado:** **abierto** — deuda declarada el 2026-10-16, y **se mantiene en la v0.0.11** por decisión del autor del
2026-10-19 (grupo 1 del plan de cierre, `interpreter/ROADMAP_V0011_ES.md`), junto con la mitad de [`GLB-139`](GLOBAL.md)
que es del tree-walker. Antes de eso: el mapa de ruta de la v0.0.11
(`interpreter/ROADMAP_V0011_ES.md`, etapa 2, PERF-05 b) dice que se archiva con su caso `KNOWN`, y el rendimiento del
tree-walker no es prioridad salvo donde comparte el defecto con la VM. Sujeto por `growth/read-a-text` de
`zyquality/cost` (`open_finding`)
**Encontrado por:** el control de GLB-130: el mismo bucle sin cortes, sólo con `s$#`, era igual de cuadrático en el
tree-walker
**Familia:** `HLZ-012` y `HLZ-014`, que dieron un `Rc` a `Array`, `Tuple` y `NamedTuple` en el tree-walker y dejaron
fuera el texto

```zymbol
s = ""
@ _i:1..8000 { s = s "ñ" }
k = 0
@ _i:1..8000 { k = k + s$# }
>> k ¶
```

`bytes` de 2 000 a 8 000: `zytw` 8,1 MB → 128 MB (×15,9); `zyvm` 2,29 MB → 2,58 MB.

### Causa

`Value::String(String)`: leer la variable clona el `String`. Cada `s$#`, cada corte, cada argumento de una llamada
copia el texto entero.

### Qué lo sujeta

`growth/read-a-text` en `zyquality/cost/cost.toml`, por `--count` (`clock_off`), con
`open_finding = { zytw = "ZYTW-016" }`. Y `growth/slice-a-text`, que también lo paga en el tree-walker.

---

## ZYTW-017 — Dentro de un `!?`, el tree-walker desactivaba la llamada en cola de todo lo que se llamara desde ahí

**Estado:** **corregido 2026-10-16** — encontrado al alinear la llamada en cola para [`GLB-133`](GLOBAL.md)
**Encontrado por:** la frontera de 10 000 llamadas: `!? { >> cuenta(30000) ¶ }`, con `cuenta` recursiva en cola, daba
`##Depth` en el tree-walker y `cuerpo` en la VM
**Familia:** [`GLB-133`](GLOBAL.md)

```zymbol
cuenta(n) {
    ? n == 0 { <~ "cuerpo" }
    <~ cuenta(n - 1)
}
!? { >> cuenta(30000) ¶ } :! { >> "no: " _err ¶ }
```

### Causa

`try_depth` era un campo del intérprete, no de cada marco. La llamada en cola se desactiva con un `!?` abierto (el
marco debe su manejador o su `:>`), y con el contador global bastaba un `!?` en **quien llama** para desactivarla en
toda la cadena de llamadas de debajo, donde ningún manejador está armado. La VM lo decide por función (`try_stack`
es de cada `FunctionCtx`). Antes del límite no se veía: el tree-walker abortaba hacia los 9 000 niveles por la pila, y
la VM llegaba al final.

Y al revés, el tree-walker sí tomaba la llamada en cola dentro de un `:!` o un `:>` propio, donde la VM no.

### Corrección (2026-10-16)

`try_depth` se guarda y se pone a 0 en `take_call_state`, y se restaura en `restore_call_state`. Y cuenta también
durante la cláusula `:!` y el `:>`, no sólo durante el cuerpo, como el `try_stack` de la VM.

### Qué lo sujeta

`zyquality/corpus/errors/runtime/depth_tail_calls.zy`.

---

## ZYTW-018 — `d[k>c]$~ v` con `c` ausente: el tree-walker abortaba en vez de añadir la clave

**Estado:** **corregido 2026-10-19** — encontrado y corregido el mismo día, al comparar el tree-walker de antes y el de
después de [`GLB-140`](GLOBAL.md)
**Encontrado por:** `zyquality/corpus/collections/edicion_profunda_en_el_sitio.zy`, que el tree-walker de antes no
terminaba
**Familia:** [`GLB-141`](GLOBAL.md), la otra cara de la misma regla

```zymbol
d = #(a: #(b: 1))
d.a["c"]$~ 3
k = "a"
e = d[k>"c"]$~ 4
>> d " " e ¶
```

`zyvm` y `zyjs` dan `#(a: #(b: 1, c: 3)) #(a: #(b: 1, c: 4))`; el tree-walker abortaba en la segunda línea con
`Runtime error: no key 'c' in dictionary — available: b`. Con `d.a` sin `c`, la forma funcional de la cuarta línea
abortaba igual. El control, `d["c"]$~ 3` de un nivel, añade la clave en los tres.

### Causa

`deep_update_value` leía el elemento de **cada** paso antes de escribirlo, también el del último. En un diccionario,
leer una clave ausente es `##Key`, así que no llegaba nunca a `set_at_step`, cuyo comentario dice justo que la añade.

### Corrección (2026-10-19)

El último paso en un diccionario escribe su clave sin leerla antes, en el camino funcional; el camino en el sitio de
`GLB-140` ya lo hacía. La sentencia, la forma funcional y la de claves en variables añaden la clave en los tres motores.

### Qué lo sujeta

`zyquality/corpus/collections/edicion_profunda_en_el_sitio.zy` (`d.a["c"]$~ 3`).

---

## ZYTW-019 — El valor del tree-walker medía 120 bytes: un array de enteros ocupaba seis veces lo de la VM

**Estado:** **corregido 2026-10-19** — medido el 2026-10-19 en la revisión de `zyquality/bench/big/HALLAZGOS.md` y
corregido ese día por decisión del autor (grupo 3 del plan de cierre, `interpreter/ROADMAP_V0011_ES.md`)
**Encontrado por:** la sonda de `$-[1]` por el principio, que en el tree-walker iba 36 veces más lenta que Python y 15
veces más que la VM sin copiar nada
**Familia:** `HLZ-012` y `HLZ-014`, que dieron a las colecciones del tree-walker un `Rc`; [`ZYTW-016`](zytw.md), el texto
que sigue sin él

```zymbol
v = []
@ i:1..40000 { v$+ i }
@ _i:1..40000 { v$-[1] }
>> v$# ¶
```

El control, `v$-[v$#]`, quita el último: no desplaza nada.

### Causa

Todo valor de un `enum` de Rust mide lo que su variante más grande. `Value::Function(FunctionValue)` iba en línea, y un
`FunctionValue` mide 120 bytes (`ErrorValue`, 48; `String`, 24): cada entero de un array ocupaba 120. Quitar el primero
desplaza los que quedan —en cualquier lenguaje—, y el tree-walker desplazaba 7,5 veces la memoria de la VM, cuyo valor
mide 16.

### Corrección (2026-10-19)

`Function(Box<FunctionValue>)` y `Error(Box<ErrorValue>)`, con dos constructores, `Value::function` y `Value::error`. La
variante más grande pasa a ser `String`, y la etiqueta cabe en un hueco de su capacidad: **un valor mide 24 bytes**.
Medido contra el binario anterior, tres corridas:

| programa | antes | ahora |
|---|---:|---:|
| array de 2 000 000 de enteros, pico de memoria | 236,1 MiB | 53,3 MiB |
| ese mismo, tiempo | ~437 ms | ~305 ms |
| el programa de arriba (`$-[1]`, 40 000) | ~2 640 ms | ~313 ms |
| 1 000 000 de llamadas | ~597 ms | ~566 ms |
| 300 000 cierres creados y llamados | ~382 ms | ~388 ms |
| 200 000 errores capturados | ~124 ms | ~131 ms |

Lo que cuesta es una reserva más al crear una función o un error como valor.

### Qué lo sujeta

La prueba `a_value_is_as_large_as_a_string` de `zymbol-interpreter/src/lib.rs`.
