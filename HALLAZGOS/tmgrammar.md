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
