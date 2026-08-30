# Hallazgos — `zyvm` (VM de registros)

> Un hallazgo entra aquí cuando el runner nombra a `zyvm` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

| | | |
|---|---|---|
| [`ZYVM-001`](#zyvm-001--la-vm-ejecuta-lo-que-el-tree-walker-rechaza-40-celdas) | abierto | ejecuta y contesta donde `zytw` rechaza — 40 celdas |
| [`ZYVM-002`](#zyvm-002--el-diagnóstico-de---nombra-al-operador--10-celdas) | abierto | el rechazo de `-` cita al operador `+` |

Y una cerrada, sujeta por una chincheta:

| chincheta | qué sujeta |
|---|---|
| [`../cases/pin/DM-02_array_equality.zy`](../cases/pin/DM-02_array_equality.zy) | `DM-02` — `==` entre arrays daba `#0` sólo en la VM. Cerrada el 2026-08-18 |

Los dos abiertos salieron del **primer** cruce del eje `operator`
(`axes/operator.toml`, 252 celdas) el 2026-08-29. Ninguno era visible para
ZyQuality: `>> (7 && 3) ¶` no lo escribe ningún fichero del corpus, y un rechazo
no tiene stdout que comparar (CHARTER § 2.1).

---

## ZYVM-001 — La VM ejecuta lo que el tree-walker rechaza (40 celdas)

**Estado:** abierto — pendiente de tu veredicto
**Encontrado por:** eje `operator`, 40 de 252 celdas
**Gravedad:** la VM es **el futuro motor por defecto**. Un programa que
`zymbol run` rechaza, `zymbol run --vm` lo corre y contesta.

### Qué se observa

Tres formas, un mismo patrón: la VM no aplica la comprobación de tipos que el
tree-walker sí aplica, y devuelve un valor.

```zymbol
>> (7 && 3) ¶
```

| motor | qué hace |
|---|---|
| `zytw` | `warning: logical operation on non-boolean type: Int` → **`Runtime error: logical AND requires boolean operands, got Int(7)`** |
| `zyvm` | el mismo aviso → y luego imprime **`#1`** |
| `zyjs` | ni aviso ni error: imprime **`#1`** (→ [`ZYJS-005`](zyjs.md)) |

El aviso es idéntico en los dos motores Rust, así que el analizador semántico
—que comparten— sí ve el problema. Lo que difiere es qué hace cada uno después:
uno para, el otro sigue.

```zymbol
>> ("ab" / "cd") ¶
```

| motor | qué hace |
|---|---|
| `zytw` | `Runtime error: / requires numeric operands — use $/ to split strings` |
| `zyvm` | imprime **`[ab]`** |

Este es el más grave de los tres, porque la VM no *ignora* la comprobación: hace
la operación que el mensaje del tree-walker dice que **no** es ésta. `$/` es
partir cadenas; `/` no lo es. La VM parte la cadena igualmente y devuelve un
array de un elemento.

```zymbol
>> ((1, 2) < (3, 4)) ¶
```

| motor | qué hace |
|---|---|
| `zytw` | `Runtime error: cannot compare values with operator 'Lt': Tuple(…) and Tuple(…)` |
| `zyvm` | imprime **`#1`** |

### El reparto de las 40 celdas

| operador | celdas | qué pasa en la VM |
|---|---:|---|
| `&&` | 17 | contesta `#1`/`#0` con cualquier par de operandos no booleanos |
| `\|\|` | 17 | igual |
| `/` | 2 | `"ab" / "cd"` y `"ab" / 'c'` parten la cadena |
| `<` `<=` `>` `>=` | 4 | comparan tuplas |

Los 17 pares son todos los que el eje declara: la familia lógica falla en **todo**
par que no sea `bool-bool`, no en un caso de borde.

### Por qué el gate nunca lo vio

Las dos razones del CHARTER, las dos a la vez:

1. **Cobertura por procedencia.** El corpus tiene los programas que alguien
   escribió. Nadie escribe `7 && 3` en un programa que funciona, así que nadie
   escribió el fichero, así que la pregunta no estaba hecha. El eje la hace
   porque cruza, no porque alguien se acordara.
2. **`vm_compare` compara stdout.** En `>> (7 && 3) ¶` el tree-walker no imprime
   nada —muere antes—, y la comparación de dos salidas cuando una es un rechazo
   no es una comparación.

### Qué habría que decidir

No es obvio cuál de los dos motores tiene razón, y por eso está abierto y no
corregido:

- Si `&&` sobre no booleanos **debe** ser un error, la VM ha perdido una
  comprobación y hay que devolvérsela.
- Si debe ser *truthiness* (la respuesta de la VM y la de `zyjs`), entonces el
  tree-walker es el que sobra-rechaza, el aviso está bien y el error no.

Lo que no puede quedarse es que dependa del motor. El aviso —presente en los dos
Rust— sugiere que la intención era avisar y seguir, pero eso es una lectura, no
una decisión tuya.

---

## ZYVM-002 — El diagnóstico de `-` nombra al operador `+` (10 celdas)

**Estado:** abierto — pendiente de tu veredicto
**Encontrado por:** eje `operator`, 10 celdas
**Familia:** redacción, no comportamiento — los dos motores rechazan

### Qué se observa

```zymbol
>> (7 - "a") ¶
```

| motor | qué dice |
|---|---|
| `zytw` | `arithmetic requires numeric operands: Int(7), String("a")` |
| `zyvm` | **`+ is arithmetic only — use juxtaposition to concatenate strings: "a" b "c"`** |

El programa no tiene ningún `+`. La VM alcanza el mensaje específico de la suma
por un camino que comparten todas las operaciones aritméticas, y el usuario lee
una guía sobre un operador que no ha escrito.

El reverso también ocurre:

```zymbol
>> ('a' + 'b') ¶
```

| motor | qué dice |
|---|---|
| `zytw` | `+ is arithmetic only — use juxtaposition to concatenate strings: "a" b "c"` |
| `zyvm` | `this needs a number and got Char` |

Aquí el `+` sí está, la guía correcta es la del tree-walker, y la VM da la
genérica. Es el mismo defecto visto del otro lado: **el mensaje no está atado al
operador que lo provoca.**

### Por qué importa más de lo que parece

`mensajes_tres_motores` dio la familia de mensajes por unificada. Lo estaba en la
superficie que el inventario `messages/` recorre, que es la que se puede leer del
código fuente. Estos dos no se leen: se producen al ejecutar, y sólo aparecen si
alguien ejecuta esa combinación. El eje las ejecuta todas.
