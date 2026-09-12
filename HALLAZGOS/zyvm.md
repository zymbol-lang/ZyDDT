# Hallazgos — `zyvm` (VM de registros)

> Un hallazgo entra aquí cuando el runner nombra a `zyvm` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

| | | |
|---|---|---|
| [`ZYVM-001`](#zyvm-001--la-vm-ejecuta-lo-que-el-tree-walker-rechaza-40-celdas) | **corregido 2026-08-30** | ejecutaba y contestaba donde `zytw` rechaza — 40 celdas |
| [`ZYVM-002`](#zyvm-002--el-diagnóstico-de---nombra-al-operador--10-celdas) | **corregido 2026-08-30** | el rechazo de `-` citaba al operador `+` |
| [`ZYVM-003`](#zyvm-003--acumular-en-el-estado-de-un-módulo-es-on-en-la-vm-y-on-en-el-tree-walker) | **abierto** | acumular en el estado de un módulo es cuadrático: 3,3 s donde el TW tarda 0,013 s |

**Uno abierto: `ZYVM-003`.**

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

---

## ZYVM-003 — Acumular en el estado de un módulo es O(n²) en la VM y O(n) en el tree-walker

**Estado:** abierto
**Encontrado por:** la medición del auto-free del 2026-09-12, **no por una celda** — el programa apareció como control de otro experimento
**Familia:** `HLZ-012` / `HLZ-014` (el copy-on-write de los agregados). Es ese mecanismo funcionando en contra

### Qué se observa

```zymbol
// m/alm.zy
# alm {
    #> { llenar, cuanto }
    datos = []
    llenar(n) { @ i:1..n { datos$+ i } }
    cuanto() { <~ datos$# }
}
```

Segundos de reloj, un solo módulo, misma máquina:

| N | `zytw` | `zyvm` |
|---:|---:|---:|
| 2 000 | 0,006 | 0,010 |
| 8 000 | 0,011 | 0,183 |
| 32 000 | **0,013** | **3,299** |
| 500 000 | 0,10 | **no termina en 60 s** |

De 8 000 a 32 000 el trabajo se multiplica por 4 y el tiempo de la VM por **18**.
El tree-walker es plano. La misma acumulación sobre una **variable local** es
lineal en los dos motores (0,34 s para 2 000 000 en ambos), así que no es el
bucle ni el `$+`: es el estado de módulo.

### Causa

`crates/zymbol-vm/src/lib.rs:3621` y `:4828` — las dos copias del intérprete:

```rust
&Instruction::LoadGlobal(dst, gvar_idx) => {
    let val = self.global_vars.get(gvar_idx as usize).cloned()...
```

El `.cloned()` es barato: desde HLZ-012 un `Value::Array` es un `Rc<Vec<…>>` y
clonarlo clona el puntero. El coste viene después. Tras el `LoadGlobal` hay
**dos** dueños del mismo `Rc` —la ranura global y el registro—, así que el `$+`
siguiente llama a `Rc::make_mut` con un contador de 2 y **copia el vector
entero**. Una copia por iteración: O(n²).

El tree-walker no paga eso porque escribe sobre la ranura sin sacar una segunda
referencia a un registro.

Sin confirmar con un parche: el mecanismo es claro y la curva lo acompaña, pero
nadie ha medido la corrección todavía.

### Alcance

Cualquier módulo que acumule en un agregado, que es el patrón normal de un
módulo con estado — y **la VM es el futuro motor por defecto**. No lo ve nada:
el corpus no escribe programas de 32 000 elementos, `bench/` mide programas
fijos que no tocan estado de módulo, y una divergencia de *tiempo* no es una
divergencia de *salida*, así que `zyq consensus` la atraviesa sin verla.

Queda por medir si afecta igual a las escrituras de módulo que no son
agregados (un contador `n = n + 1` no copia nada) y a las aplicaciones LDV, que
sí guardan tableros y listas en módulos.

### Arreglo propuesto

Que `StoreGlobal`/`LoadGlobal` no dejen dos dueños vivos del mismo `Rc` durante
una modificación en sitio: o el compilador reconoce el patrón
*load–modify–store* sobre una global y emite una modificación directa, o
`LoadGlobal` cede la ranura (`std::mem::take`) cuando el siguiente uso es una
escritura de vuelta.

**Es propuesta, no decisión.**

### Qué lo sujeta

`zyquality/cost/`, caso **`growth/append-module-state`**, desde el 2026-09-12.
Un tiempo no es una celda —el diferencial compara salidas y las dos son
idénticas—, así que la suite mide la **curva**: el mismo programa a N y a 4N,
con el límite entre lineal (4,0) y cuadrático (16,0). Marcado
`open_finding = { zyvm = "ZYVM-003" }`, así que se reporta **KNOWN** en cada
corrida con su ratio y no enrojece el gate: la deuda escrita no es una
regresión. El día que baje de 6,0 el runner pide cerrar la ficha.
