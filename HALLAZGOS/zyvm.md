# Hallazgos — `zyvm` (VM de registros)

> Un hallazgo entra aquí cuando el runner nombra a `zyvm` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

| | | |
|---|---|---|
| [`ZYVM-001`](#zyvm-001--la-vm-ejecuta-lo-que-el-tree-walker-rechaza-40-celdas) | **corregido 2026-08-30** | ejecutaba y contestaba donde `zytw` rechaza — 40 celdas |
| [`ZYVM-002`](#zyvm-002--el-diagnóstico-de---nombra-al-operador--10-celdas) | **corregido 2026-08-30** | el rechazo de `-` citaba al operador `+` |
| [`ZYVM-003`](#zyvm-003--acumular-en-el-estado-de-un-módulo-es-on-en-la-vm-y-on-en-el-tree-walker) | **abierto** | acumular en el estado de un módulo es cuadrático: 3,3 s donde el TW tarda 0,013 s |
| [`ZYVM-004`](#zyvm-004--una-función-llamada-por----o--corre-en-un-segundo-intérprete-que-se-salta-49-instrucciones) | **corregido 2026-09-14** | una función llamada por `$>`, `$|` o `$<` corría en un segundo intérprete que se saltaba 49 instrucciones |

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

---

## ZYVM-004 — Una función llamada por `$>`, `$|` o `$<` corre en un segundo intérprete que se salta 49 instrucciones

**Estado:** **corregido 2026-09-14** — el segundo intérprete se borró; el bucle de despacho es reentrante (`exec(program, floor)`)
**Encontrado por:** `error-flow/try-inside-a-mapped-lambda` el 2026-09-14 — un `!?` dentro de la lambda de un `$>` no capturaba nada — y medido después por `axes/callable-body.toml`
**Gravedad:** **alta.** No falla: contesta `##_`. Y la VM es el futuro motor por defecto

### Qué se observa

```zymbol
>> ["a,b", "c"]$> (s -> s$/ ',') ¶
```

| motor | |
|---|---|
| `zytw` | `[[a, b], [c]]` |
| `zyjs` | `[[a, b], [c]]` |
| `zyvm` | **`[(), ()]`** |

Lo mismo con una **función con nombre** (`xs$> partir`), con `$|` y con `$<`,
y con veinte operaciones: partir, cortar, formatear (`#,||`, `#^||`), cambiar de
base, quitar, insertar, reemplazar, buscar todas las posiciones, `??` sobre un
rango o una cadena, `$!`, `!?` y la desestructuración con resto. El mismo cuerpo
fuera de un `$>` —o dentro de un `@`— funciona.

### Causa

`crates/zymbol-vm/src/lib.rs`, `call_function`: las funciones que llaman los
operadores de orden superior (`call_callable`) no se ejecutan en el bucle de la
VM sino en un **segundo bucle** escrito aparte, que atiende 96 de las
instrucciones y termina en

```rust
_ => {
    // For unsupported instructions in HOF mini-VM, skip
}
```

Las 49 que no conoce no fallan: no hacen nada, y el registro que tenían que
escribir se queda en `##_`. Tampoco llevan manejadores de error, así que un
`!?` dentro de esa función no existe, y un error que sale de ella lo devuelve
con `?` en vez de con `raise!`, así que **tampoco lo captura un `!?` alrededor
del `$>`**.

Es el mismo patrón que `ZYVM-003` señaló en `LoadGlobal`: dos copias del
intérprete, y cada arreglo aterriza en una.

### Por qué no lo veía nada

`zyq consensus` estaba en 660 de acuerdo y 0 divergiendo. Ningún fichero del
corpus usa una de esas operaciones dentro de una función de orden superior **y**
imprime lo que devolvió. El gate compara salidas; el programa que no se escribió
no tiene salida.

### Arreglo

Borrar el segundo intérprete, no completarlo: completarlo deja dos copias que
vuelven a separarse con la instrucción número 163. El bucle principal sólo
depende de `ip`, `base` y `chunk_idx`, que salen del marco de arriba, así que
puede ejecutarse **reentrante**: el operador empuja el marco de la función y
corre el mismo bucle hasta que ese marco retorna. Un error que no encuentra
manejador por encima de ese suelo vuelve al operador, que lo levanta con
`raise!` en el bucle de fuera.

### El coste que tuvo, y cómo se pagó

Cada llamada de un operador de orden superior vuelve a entrar en el bucle, y el
marco de Rust de ese bucle es grande: unos 14 KB. Con los 8 MiB del hilo
principal, la recursión **a través de `$>`** bajó de más de 1 000 niveles a 593
—menos que los 899 del tree-walker—. El CLI ejecuta ahora el programa en un hilo
de 64 MiB (`PROGRAM_STACK`, reservados y no comprometidos): 4 764 niveles en la
VM, y el tree-walker pasa de 899 a 7 212 a través de `$>` y de 1 099 a 8 828 en
recursión simple. En tiempo, un map/filter/reduce de 300 000 elementos pasó de
0,077 s a 0,085 s.

### Qué lo sujeta

`axes/callable-body.toml`: 21 operaciones × 4 llamadores = 84 celdas. `match-int`
es el control —el segundo bucle sí la conocía— y está verde las cuatro veces;
las otras 80 están rojas. Y `error-flow/try-inside-a-mapped-lambda` y
`error-flow/error-in-a-mapped-lambda-is-catchable`.

---

## ZYVM-005 — Un local destruido en una rama que no se ejecuta deja de poder leerse

**Estado:** **corregido el 2026-09-15** (paso 2.15c)
**Encontrado por:** paso 2.15, 2026-09-15 (`GLB-025`)
**Familia:** `GLB-008` («Lo que queda»: la destrucción de un local de función en la VM)

```zymbol
f() {
    y = 2
    ? #0 { \ y }
    <~ y
}
>> f() ¶
```

| motor | |
|---|---|
| `zytw`, `zyjs` | `2` |
| `zyvm` | `Runtime error: 'y' is undefined — did you mean 'y°' (hot definition)?` |

El compilador quita la ligadura del registro al compilar `\ y`, esté o no en una
rama que se vaya a ejecutar, así que la lectura de después ya no encuentra el
nombre y emite el error de «indefinido». A nivel de archivo no pasa: allí la
variable vive en `global_vars` y `DestroyGlobal` sólo actúa si se ejecuta. Es el
falso positivo que enseñó `GLB-008`, en el sitio que esa ficha dejó pendiente. La
interpolación (`"{y}"`) hace lo mismo desde el paso 2.15, porque sigue el camino
del identificador.

### Qué lo sujeta

`runtime-functions-hof/local-destroyed-in-a-branch-not-taken`, roja por la VM.

### Corregido — 2026-09-15 (paso 2.15c)

La destrucción de un local pasa a ser de ejecución, como la de una variable de
archivo desde `GLB-008`, y sólo para los nombres que algún `\` del cuerpo nombra
(`destroyed_names`, calculado antes de compilar el cuerpo, porque en un bucle la
lectura puede ir antes del `\` en el texto):
- `\ y` emite `DestroyLocal(reg, nombre)`: marca el hueco absoluto de la pila y lo
  vacía, sin quitar la ligadura del registro;
- cada lectura de `y` (identificador o `{y}`) emite antes `CheckAlive`, que lanza
  `use after destruction: variable 'y' was destroyed after its last use`;
- cada asignación a `y` emite después `Revive`, que quita la marca, porque
  reasignar revive el nombre, y lo hace tras calcular el valor para que `y = y + 1`
  siga fallando.

TW y VM dan exactamente la misma salida, texto incluido, en seis casos dentro de
una función: rama no ejecutada, rama ejecutada, reasignación, bucle con la
lectura antes del `\`, `y = y + 1` e interpolación. Eso cierra también **el resto
de `GLB-008`** en la VM (un local destruido decía `'y' is undefined`). `zyjs` sigue
diciendo `'y' is undefined` para un local: es el mismo resto, en su motor. `lifetime`
queda en 5 de 5, y el gate de coste en verde.
