# Hallazgos — `zytw` (tree-walker)

> Un hallazgo entra aquí cuando el runner nombra a `zytw` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

**Ninguno abierto.** `ZYTW-002` y `ZYTW-003` se corrigieron el día que se encontraron. `ZYTW-001` lo encontró el primer eje que le preguntó por el
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

