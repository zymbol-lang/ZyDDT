# Hallazgos — `zytw` (tree-walker)

> Un hallazgo entra aquí cuando el runner nombra a `zytw` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

**Uno abierto.** Lo encontró el primer eje que le preguntó por el alcance
(`axes/isolation.toml`, 2026-09-12). Hasta ese día este fichero decía «ninguno
todavía», y decía la verdad por la razón equivocada: nadie le había preguntado
casi nada. La cifra que importa es la tabla de `zyddt axis`, no la longitud de
este fichero.

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
