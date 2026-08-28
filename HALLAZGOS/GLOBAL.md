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

**Ninguno.** Los cuatro ejes declarados hoy no han producido ninguno.

Eso no es tranquilizador: la clase 1 sólo aparece donde hay un oráculo, y hoy
sólo `axes/arithmetic.toml` lleva oráculos — cuatro celdas. La columna `oracled`
de `zyddt axis` es el recuento honesto de dónde el acuerdo **no** es la única
prueba, y vale 4 sobre 15 celdas.

Dicho de otra forma: de las quince celdas que hay, once están verdes por acuerdo
y nada más. Si alguna de esas once esconde un error de los tres, ZyDDT no puede
verlo hoy, y esa es la lectura correcta de este fichero vacío.
