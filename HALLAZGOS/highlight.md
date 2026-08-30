# Hallazgos — `highlight.js` (el resaltador del playground)

> Un hallazgo entra aquí cuando `zyddt surfaces` dice que este fichero dejó algo
> sin marcar. La regla y el formato están en [`INDICE.md`](INDICE.md).
>
> **Este fichero existe desde el 2026-08-30**, que es cuando ZyDDT empezó a
> ejecutar la superficie. Antes no existía a propósito: un fichero vacío
> esperando enseña que la ausencia de hallazgos es un estado normal, y hasta ese
> día significaba que nadie había mirado.

| | | |
|---|---|---|
| [`HL-001`](#hl-001--un-prefijo-de-base-sin-dígitos-deja-los-dígitos-sin-marcar) | **corregido 2026-08-30** | `0b22` marcaba `0b` y dejaba `22` desnudo |

---

## Por qué esta superficie se mide y no se lee

Es también **el índice del hover**: cada span de operador lleva `data-h`, la
clave de su ficha en `src/playground/symbols.js`. Un token que el resaltador no
marca es un token que el lector **no puede preguntar**.

Y se mide barriendo, no leyendo. La auditoría que encontró cinco operadores
rotos en este fichero —`$++` partido en `$+` y `+`, la familia `#|…|` entera sin
marcar, un `x°` postfijo absorbido por el identificador, `</ f.zy />` convertido
en seis signos sueltos— funcionó así: quitar el marcado y mirar lo que queda.
Los cinco habían sobrevivido a que alguien leyera el fichero.

**El listón aquí es que no se tolera nada.** Cualquier carácter no blanco que
salga fuera de un span es un token que no se reconoció, y el corpus demuestra
que ese listón se alcanza: 661 ficheros, cero sin marcar.

---

## HL-001 — Un prefijo de base sin dígitos deja los dígitos sin marcar

**Estado:** **corregido 2026-08-30**
**Encontrado por:** `zyddt surfaces`, sobre las celdas del eje `diagnostic`

### Qué se observa

```zymbol
>> 0b22 ¶
```

`0b` sale marcado como número y `22` sale **de la nada**: fuera de todo span. Lo
mismo con `0o99`. Las formas válidas (`0b11`, `0x41`, `0o17`) están bien, y
`0xZZ` también — ahí las letras las reclama la rama de identificador.

### Causa

La rama de literal de base consume `0b`, no casa ningún dígito binario, y emite
`0b` igualmente. Los `22` que quedan **no son alcanzables** por la rama de
número: exige que el carácter anterior no sea `\w`, y el anterior es la `b`.

### Por qué no lo vio nada

Porque `0b22` es un programa **inválido** —el lexer lo rechaza con
`expected binary digits after base prefix`— y ningún fichero del corpus escribe
uno. Vive en el eje `diagnostic` de ZyDDT, que lo escribe porque cruza, no
porque alguien se acordara.

### Arreglo

Un prefijo que no casó ningún dígito se traga la palabra entera: el literal
malformado es **un** span. Un resaltador no puede rechazar nada, pero tampoco
puede dejar la mitad sin colorear.

### Qué lo sujeta

Las celdas `diagnostic/binary-prefix-with-no-digits` y `octal-…`, que ahora
`zyddt surfaces` recorre además de `zyddt axis`.
