# Hallazgos — `zytw` (tree-walker)

> Un hallazgo entra aquí cuando el runner nombra a `zytw` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

**Ninguno todavía.** ZyDDT lleva ocho ejes declarados; que este fichero esté
vacío no dice que el tree-walker esté limpio, dice que nadie le ha preguntado
casi nada. La cifra que importa es la tabla de `zyddt axis`, no la longitud de
este fichero.

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
