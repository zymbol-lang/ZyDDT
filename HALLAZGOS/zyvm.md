# Hallazgos — `zyvm` (VM de registros)

> Un hallazgo entra aquí cuando el runner nombra a `zyvm` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

| | | |
|---|---|---|
| [`ZYVM-001`](#zyvm-001--la-vm-ejecuta-lo-que-el-tree-walker-rechaza-40-celdas) | **corregido 2026-08-30** | ejecutaba y contestaba donde `zytw` rechaza — 40 celdas |
| [`ZYVM-002`](#zyvm-002--el-diagnóstico-de---nombra-al-operador--10-celdas) | **corregido 2026-08-30** | el rechazo de `-` citaba al operador `+` |

**Ninguno abierto.**

Las chinchetas que los sujetan:

| chincheta | qué sujeta |
|---|---|
| [`../cases/pin/DM-02_array_equality.zy`](../cases/pin/DM-02_array_equality.zy) | `DM-02` — `==` entre arrays daba `#0` sólo en la VM. Cerrada el 2026-08-18 |
| [`../cases/pin/ZYVM-001_logical_short_circuit.zy`](../cases/pin/ZYVM-001_logical_short_circuit.zy) | que `&&` y `\|\|` sigan **contestando** sobre booleanos |
| [`../cases/pin/ZYVM-001_logical_falsy_left.zy`](../cases/pin/ZYVM-001_logical_falsy_left.zy) | la mitad que la matriz no alcanza: un no booleano **falsy** a la izquierda |
| [`../cases/pin/ZYVM-002_negation_quotes_plus.zy`](../cases/pin/ZYVM-002_negation_quotes_plus.zy) | el `-` unario, que no está en la matriz de operadores binarios |

Los dos salieron del **primer** cruce del eje `operator`
(`axes/operator.toml`, 252 celdas) el 2026-08-29. Ninguno era visible para
ZyQuality: `>> (7 && 3) ¶` no lo escribe ningún fichero del corpus, y un rechazo
no tiene stdout que comparar (CHARTER § 2.1).

---

## ZYVM-001 — La VM ejecuta lo que el tree-walker rechaza (40 celdas)

**Estado:** **corregido 2026-08-30**
**Veredicto:** error en los tres motores. Es la regla que la v0.0.9 ya había
decidido para el especificador de bucle —*no hay truthiness*— aplicada a los
operadores lógicos.
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

### Qué se decidió, y qué se cambió

**Error en los tres.** `LLM.md:151` ya lo dice —*there is no truthiness*— y la
v0.0.9 lo había cerrado para el especificador de bucle con esas mismas palabras:
*«una cosa es cuenta o condición; cualquier otra se rechaza en ejecución»*. Los
operadores lógicos siguen la misma regla. El tree-walker no cambia.

Tres cambios, los tres en la VM y su compilador:

| celdas | qué se cambió |
|---:|---|
| 34 | `Instruction::And` / `Or` leían los dos operandos con `is_truthy()`. Ahora exigen `Bool` y levantan el mensaje del tree-walker. En los **dos** bucles del intérprete — el principal y el de marcos de llamada |
| 2 | `BinaryOp::Div` compilaba a `StrSplit` si algún operando era estáticamente `String` o `Char`. Eliminado: `/` cae a `DivInt`/`DivFloat` y se rechaza. `$/` sigue compilando a `StrSplit` desde su propio sitio |
| 4 | El brazo `(Tuple, Tuple)` de `cmp_order` comparaba elemento a elemento. Eliminado: la tupla es posicional y heterogénea, y `(1, "a") < (2, #0)` no tiene respuesta defendible. `==` no pasa por ahí y sigue comparando tuplas |

### La mitad que la matriz no veía

El eje cruza `&&` con pares cuyo operando izquierdo es **truthy**, así que todas
sus celdas llegaban a la instrucción `And`. Un no booleano **falsy** no llega
nunca: la VM cortocircuita antes, en `JumpIfNot`, que decide por truthiness — y
`0 && #1` seguía contestando `#0` con la instrucción ya corregida.

El salto no puede hacer la comprobación él mismo: `? 7 { … }` compila al mismo
`JumpIfNot` y ahí es un **aviso**, no un error. Así que la guarda es una
instrucción propia, `RequireBool`, que `compile_and` y `compile_or` emiten antes
del salto. La sujeta
[`ZYVM-001_logical_falsy_left.zy`](../cases/pin/ZYVM-001_logical_falsy_left.zy).

---

## ZYVM-002 — El diagnóstico de `-` nombra al operador `+` (10 celdas)

**Estado:** **corregido 2026-08-30**
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


### Causa, y por qué salían las dos caras

Una sola macro. `ri!` era el único lector de operandos enteros de la VM, y su
rama `String` llevaba la guía de `+` porque `+` era la forma más común de
llegar allí. El mensaje era una propiedad **del camino de código**, no del
operador: `7 - "a"` citaba la guía de `+`, y `'a' + 'b'` —donde esa guía es
exactamente la correcta— caía por otra rama y recibía la genérica.

### Qué se cambió

- `ri!` se queda para las **posiciones**: un índice, una cuenta, una repetición.
  Sin la guía de `+`, que allí nunca fue correcta (`arr["x"]` la habría citado).
- `ri2!` / `rf2!` leen **los dos** operandos aritméticos y, al fallar, llaman a
  `arith_type_error(op, a, b)`, que deletrea el mensaje del tree-walker por
  operador: `+`, `/` y `^` tienen el suyo, el resto comparte el de `eval_arithmetic`.
- `ri_imm!` hace lo mismo para las formas con literal plegado.
- `rn!` para el `-` unario, que decía `+ is arithmetic only` sobre `-"a"`.
- Las comparaciones con literal plegado (`CmpLtImm` y familia) leían el registro
  con `ri!`, así que `'a' < 7` se rechazaba aquí como *«this needs a number»* y
  allí como *«cannot compare values»*: una comparación, dos rechazos, decididos
  por si el lado derecho resultaba ser un literal lo bastante pequeño para
  plegar. Ahora pasan por la misma regla de orden que la forma general, con el
  camino rápido de `Int` intacto.

### Qué lo sujeta

Las 10 celdas del eje, más
[`ZYVM-002_negation_quotes_plus.zy`](../cases/pin/ZYVM-002_negation_quotes_plus.zy)
para el `-` unario, que la matriz de operadores **binarios** no cruza.
