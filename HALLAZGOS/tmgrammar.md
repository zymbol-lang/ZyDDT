# Hallazgos — `zymbol.tmGrammar.json` (la gramática de VS Code)

> Un hallazgo entra aquí cuando `zyddt surfaces` dice que la gramática dejó un
> token en el scope pelado `source.zymbol`. La regla y el formato están en
> [`INDICE.md`](INDICE.md).
>
> **Este fichero existe desde el 2026-08-30**, por la misma razón que el de
> `highlight.js`: antes de esa fecha nadie ejecutaba la superficie, y un fichero
> vacío lo habría hecho parecer limpia.

| | | |
|---|---|---|
| [`TM-001`](#tm-001--dos-escrituras-de-unicode-150-que-oniguruma-no-conoce-como-dígitos) | **corregido 2026-08-30** | Kawi y Nag Mundari no casaban `\p{Nd}` |
| [`TM-002`](#tm-002--la-gramática-de-vs-code-no-marcaba-0xn-la-regla-de-enteros-unicode-se-comía-el-0) | **corregido 2026-09-14** | `0x\|n\|` sin marcar: `\p{Nd}+` se comía el `0` |
| [`TM-003`](#tm-003--un-nombre-como-cuenta-de-decimales-vn-quedaba-sin-marcar) | **corregido 2026-09-29** | `#.v\|x\|` sin marcar: la cuenta sólo podía ser dígitos |

---

## Cómo se mide, y por qué así

Con **`vscode-textmate` sobre Oniguruma** — la maquinaria de verdad, no una
aproximación con expresiones regulares. Una gramática es una pila de patrones de
Oniguruma con estados `begin`/`end`, y aproximar eso es escribir una segunda
gramática con sus propios fallos: lo que se graduaría sería la aproximación.

Las dos dependencias están declaradas en `vscode/package.json` como
`devDependencies`, así que un checkout limpio las trae con `npm install` y el
`.vsix` no las empaqueta.

**Los corchetes y las llaves se toleran**, y es la única tolerancia del fichero,
así que dice por qué: no llevan scope propio en esta gramática y un editor no lo
necesita —el emparejado y el coloreado de corchetes en VS Code no los decide la
gramática— y esta superficie **no es el índice del hover**; ese es
[`highlight.js`](highlight.md), donde no se tolera nada.

La regla se escribió después de medir: de **15 760** tramos sin scope sobre el
corpus, **15 745** son corchetes puros. Graduarlos habría enterrado los otros
quince, que son el hallazgo — `0x|…|` y la familia de precisión `#,.n|…|`, dos
operadores que la gramática no conocía. Los dos están corregidos en la versión
que este fichero grada.

---

## TM-001 — Dos escrituras de Unicode 15.0 que Oniguruma no conoce como dígitos

**Estado:** **corregido 2026-08-30**
**Encontrado por:** `zyddt surfaces`, sobre las 69 celdas del eje `numerals`

### Qué se observa

```zymbol
#𑽐𑽙#
```

El modo numeral de **Kawi** (U+11F50) y el de **Nag Mundari** (U+1E4F0) dejaban
su `#` en el scope pelado. Los otros 67 bloques estaban bien — incluidos **29
que también están fuera del BMP**, lo que descarta que fuera un problema de
plano astral.

### Causa

No es la gramática: es la **tabla Unicode de Oniguruma**. El patrón dice
`\p{Nd}`, y esas dos escrituras entraron en Unicode 15.0 (2022), posterior a las
tablas que trae el Oniguruma que VS Code usa. Para su motor esos caracteres no
son dígitos.

Es el mismo caso que el pIqaD klingon, que el patrón ya trataba aparte
(`[-]`) porque el Área de Uso Privado no tiene categoría ninguna.

### Arreglo

Los dos rangos, explícitos, junto al del pIqaD y con el comentario que dice por
qué están ahí. **No es un parche a `\p{Nd}`**: es la lista de lo que `\p{Nd}` no
cubre en este motor, que es información y hay que escribirla.

### Qué lo sujeta

Las 69 celdas del eje `numerals`, que `zyddt surfaces` recorre. Y la forma en
que se encontró es el argumento de la matriz: nadie habría escrito a mano un
fichero de prueba en Kawi.

---

## TM-002 — La gramática de VS Code no marcaba `0x|n|`: la regla de enteros Unicode se comía el `0`

**Estado:** **corregido 2026-09-14**
**Encontrado por:** `callable-body/*-base`, la primera celda de ZyDDT que escribió una conversión de base

### Qué se observa

En `r = 0x|x$# * 30|` las dos barras quedaban sin ámbito. Y en `0x|255|` también:
no dependía de lo que hubiera dentro. El corpus escribe `0x|255|` desde hace
versiones, pero la superficie sólo barre las celdas de ZyDDT, y ninguna tenía una
conversión.

### Causa

`syntaxes/zymbol.tmGrammar.json`: las cuatro reglas `0b|` `0o|` `0d|` `0x|` vivían
en `#format-expressions`, incluido después de `#numbers`. Y `#numbers` tiene la
regla de enteros Unicode `\p{Nd}+`, **sin límite de palabra**, que toma el `0` de
`0x|`: `x` queda como identificador y las barras, sueltas. `#base-literals` ya
estaba delante de `#numbers` por la misma razón, escrita en su comentario.

### Arreglo

Un grupo propio, `#base-conversions`, incluido antes de `#base-literals`.

---

## TM-003 — Un nombre como cuenta de decimales (`#.v|x|`) quedaba sin marcar

**Estado:** **corregido 2026-09-29**
**Encontrado por:** las cuatro celdas `runtime-format-convert/decimal-count-must-*`,
al buscar por qué `zyddt suite` daba RED con todas sus celdas y chinchetas en
AGREE — la tubería de `zyq suite` tapaba el código de `surfaces`, que era el 1.

### Qué se observa

```zymbol
t(v) {
    <~ #.v|1.23|
}
>> t(1.5) ¶
```

El `#`, y las dos barras, sin ámbito. El programa es válido: el lexer acepta un
nombre como cuenta, y el resaltador del playground ya lo marcaba (su comentario lo
dice: *«The count may be a NAME as well as digits»*). El corpus lo escribe en
`casts/precision_en_ejecucion.zy`, que dejaba **24** tokens sin marcar — pero la
superficie sólo barre las celdas de ZyDDT, así que nadie lo veía.

### Causa

`syntaxes/zymbol.tmGrammar.json`, `#format-expressions`: las cuatro reglas
(`#^`, `#,`, `#.`, `#!`) escribían la cuenta como `[0-9]+`.

### Arreglo

La cuenta es `(?:[0-9]+|[\p{L}_][\p{L}_0-9]*)` en las cuatro, la misma regla que
el resaltador. Medido sobre el corpus entero: 24 tokens sin marcar antes, **0**
después, y ninguno nuevo en otro fichero.

### Lo que queda, y no es este hallazgo

`surfaces` sigue en RED con 14 (highlight) y 31 (tmgrammar), y **todos** están en
celdas de programas que el lenguaje rechaza: `#,. 2|v|`, `#2`, `:! #Div`, un `#`
suelto, un `'` sin cerrar.

**Decidido por el autor el 2026-09-29:** `surfaces` excusa un token sin marcar
**sólo en la línea a la que apunta un rechazo estático**, medido preguntando al
analizador del tree-walker (`zymbol check`), no declarado en el eje — `expect =
"error"` no distingue un rechazo estático de un error en ejecución, y
`#.v|x|` con una `v` mala es un programa válido que falla al correr. Marcar lo
inválido con una clase propia se descartó: dejaría ciega a la superficie, porque
todo token desconocido pasaría a ser «inválido». Las 45 caían en esas líneas.
Control: con la gramática anterior a este hallazgo, las 12 de las celdas válidas
vuelven a salir y `surfaces` da RED.

