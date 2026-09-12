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

**Estado:** abierto
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

Sin localizar con precisión. Lo que se sabe: el analizador semántico que
`zymbol check` ejecuta —y que `zytw` y `zyvm` comparten— **no comprueba los
nombres libres del cuerpo de una lambda** contra el alcance de su punto de
creación. La VM lo detecta después, al compilar a bytecode; el tree-walker no
tiene ese paso y llega a la ejecución.

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

### Arreglo propuesto

Que la comprobación viva en `zymbol-semantic`, no en el compilador de la VM: es
lo que `check` ejecuta y lo que el LSP indexa, así que es el único sitio donde
la respuesta es la misma para los tres motores y para el editor. La VM dejaría
de necesitar la suya.

**Es propuesta, no decisión.**

### Qué lo sujeta

Las dos celdas del eje. Vuelven a rojo el día que el tree-walker se adelante o
la VM se retrase.

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
