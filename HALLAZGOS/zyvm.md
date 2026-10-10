# Hallazgos — `zyvm` (VM de registros)

> Un hallazgo entra aquí cuando el runner nombra a `zyvm` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

| | | |
|---|---|---|
| [`ZYVM-001`](#zyvm-001--la-vm-ejecuta-lo-que-el-tree-walker-rechaza-40-celdas) | **corregido 2026-08-30** | ejecutaba y contestaba donde `zytw` rechaza — 40 celdas |
| [`ZYVM-002`](#zyvm-002--el-diagnóstico-de---nombra-al-operador--10-celdas) | **corregido 2026-08-30** | el rechazo de `-` citaba al operador `+` |
| [`ZYVM-003`](#zyvm-003--acumular-en-el-estado-de-un-módulo-es-on-en-la-vm-y-on-en-el-tree-walker) | **abierto** | acumular en el estado de un módulo es cuadrático: 3,3 s donde el TW tarda 0,013 s |
| [`ZYVM-004`](#zyvm-004--una-función-llamada-por----o--corre-en-un-segundo-intérprete-que-se-salta-49-instrucciones) | **corregido 2026-09-14** | una función llamada por `$>`, `$|` o `$<` corría en un segundo intérprete que se saltaba 49 instrucciones |
| [`ZYVM-010`](#zyvm-010--soltar-valores-cuesta-entre-el-11-y-el-17--del-tiempo-de-la-vm) | **abierto** | soltar el valor viejo en cada escritura de registro, y desmontar marcos que nunca reutilizan un temporal: 11–17 % del tiempo |

**Dos abiertos: `ZYVM-003` y `ZYVM-010`.**

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

### Medido de nuevo, 2026-10-10 — no es sólo el `$+`

Instrucciones (`perf stat -e instructions:u`, binario de release), con el estado en un módulo y el mismo
programa a N = 4000 y N = 16 000:

| edición sobre el estado del módulo | `zytw` | `zyvm` | crece ×4 en la VM |
|---|---:|---:|---:|
| añadir, `datos$+ i`, N veces | 11 M → 34 M | 304 M → **4 710 M** | ×15,5 |
| actualizar **un** elemento, `tabla[k]$~ i`, 4000 veces sobre un array de N | 25 M → 45 M | 906 M → **7 088 M** | ×7,8 |
| quitar del final, `datos$-[datos$#]`, 2000 veces | 16 M → 40 M | 524 M → **5 794 M** | ×11 |
| control: un contador, `cuenta += 1` | 8 M → 21 M | 7 M → 15 M | ×2,4 |
| control: un diccionario de dos campos, `ficha.a$~ i` | 18 M → 63 M | 13 M → 42 M | ×3,2 |

Toda edición en el sitio copia la colección entera, no sólo la que añade: actualizar una casilla de un tablero
guardado en un módulo cuesta proporcional al tablero. El contador y el diccionario pequeño no lo sufren.

Dos cosas que condicionan el arreglo:

- **El orden.** El TW no copia porque evalúa el operando y después edita en la ranura; la VM lee el receptor antes.
  Cuando el operando escribe el mismo estado las dos respuestas difieren, y eso es
  [`GLB-115`](GLOBAL.md), sin decidir.
- **El fallo.** Varias instrucciones de edición sacan el valor de su registro antes de validar (`ArrayRemove` y
  `DeepSet` hacen `mem::replace` y lanzan el error con el valor ya soltado). Hoy no importa, porque la ranura global
  guarda su propia copia; en cuanto la edición sea la única dueña, una edición fallida perdería el estado. Lo sujeta
  desde hoy `runtime-modules-scripts/module-state-after-a-failed-edit`.

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

---

## ZYVM-006 — La marca de «destruido» sobrevive a la llamada, y el `\` de una lambda acaba con la variable del fichero

**Estado:** **corregido el 2026-09-25** (paso P1, con permiso del autor)
**Encontrado por:** midiendo [`GLB-055`](GLOBAL.md), 2026-09-25
**Familia:** `ZYVM-005`

### Qué se observa

```zymbol
f(p) {
    >> p ¶
    \p
    <~ "hecho"
}
>> f(1) ¶
>> f(2) ¶
```

| motor | |
|---|---|
| `zytw`, `zyjs` | `1`, `hecho`, `2`, `hecho` |
| `zyvm` | `1`, `hecho`, y `use after destruction: variable 'p' was destroyed after its last use` |

Una función que destruye su parámetro falla **la segunda vez que se la llama**.
Las marcas de `ZYVM-005` (`destroyed_slots`) son posiciones absolutas de la pila
de valores y nadie las borraba al terminar un marco: el `>> p` de la segunda
llamada leía la marca de la primera. Con una lambda que captura `x`, la lee y la
destruye pasa lo mismo.

Y un segundo defecto, invisible hasta que `GLB-055` hizo error el doble `\`: dentro
de una lambda escrita en el fichero, `\x` emitía `DestroyGlobal` y acababa con la
`x` **del fichero** (lo mismo que [`ZYJS-029`](zyjs.md) en `zyjs`). No se veía
porque `<main>` lee su propia `x` de un registro. Una escritura a una variable del
fichero sólo se emite desde `<main>` (`ERROR-ZYB-002`); el `\` no seguía esa regla.
Salió a la luz con una lambda que sólo hace `\x` y se llama dos veces: la segunda
llamada destruía otra vez la global.

### Corregido el 2026-09-25

- `forget_destroyed_from(base)`: al abrir un marco se borran las marcas de sus
  huecos, en los tres sitios donde se abre uno (llamada, llamada dinámica y
  retrollamada de HOF). No cuesta nada si ningún programa usa `\`.
- `destroyed_locally` en el compilador: fuera de `<main>`, el nombre es una copia
  local y se sigue en su registro; `DestroyGlobal` sólo se emite desde `<main>`.

### Qué lo sujeta

`lifetime/a-function-that-destroys-its-parameter-called-twice`,
`lifetime/a-lambda-that-reads-then-destroys-called-twice` y
`lifetime/a-lambda-destroys-its-own-copy`, verdes.

---

## ZYVM-007 — Patrones numéricos en la VM: el decimal nunca empareja y el entero grande se trunca

**Estado:** **corregido el 2026-09-26** (paso P4-2, con permiso del autor)
**Encontrado por:** midiendo `-1.5 =>` para [`GLB-062`](GLOBAL.md)

| programa | `zytw`, `zyjs` | `zyvm`, antes |
|---|---|---|
| `x = 1.5`, `?? x { 1.5 => … }` | empareja | **no empareja** |
| `x = -1294967296`, `?? x { 3000000000 => … }` | no empareja | **empareja** |
| `x = 3000000000`, `?? x { 3000000000 => … }` | empareja | **no empareja** |
| `x = [9.9, 2]`, `?? x { [1.5, 2] => … }` | no empareja | **empareja** |

Tres sitios del compilador emparejan un literal: el patrón suelto, el elemento de un
patrón de lista y la pertenencia. En los tres:

- un **decimal** caía en una rama de «no soportado». En el patrón suelto y en la
  pertenencia saltaba siempre, y en la lista **no se comparaba**, así que emparejaba con
  cualquier valor;
- un **entero** se comparaba con `CmpEqImm(*n as i32)`, que **trunca** un literal que no
  cabe en 32 bits.

### Corregido

`emit_int_eq` usa la forma inmediata solo si el número cabe. Si no, lo carga entero
(`LoadInt`) y compara con `CmpEq`. El decimal se carga con `LoadFloat` y se compara igual,
en los tres sitios. Todas las formas quedan iguales en los tres motores. Tres celdas en
`runtime-match-patterns`: decimal negativo, entero de más de 32 bits y decimal dentro de una
lista.

---

## ZYVM-008 — `m.nada` (una constante que el módulo no tiene): la VM lo refusa antes de ejecutar

**Estado:** **corregido el 2026-09-26**: la decisión alcanzó también a las funciones y a `std/`
**Encontrado por:** midiendo [`ZYJS-040`](zyjs.md)

```zymbol
<# ./m/saludo => m
>> m.nada ¶
```

Los tres dicen `Module 'm' has no constant 'nada'. Available constants: none`. La VM lo
dice al compilar (`error:`), y el TW y `zyjs` en ejecución (`Runtime error:`). Es la misma
diferencia de fase que tenía GLB-069 antes de corregirse.

### Lo que salió al medirlo

| programa | TW y `zyjs` | VM | `zymbol check` |
|---|---|---|---|
| `m.nada` dentro de `? #0 { … }` | corre | refusa el programa, sin sitio | nada |
| `m.nada` leído | falla en esa línea | refusa antes, sin sitio | nada |
| `m::nada()` dentro de `? #0 { … }` | corre | corre | nada |
| `mt::nada(1)` de `std/math`, en una rama muerta | corre | corre | **lo refusa** |
| `nada`, un nombre local, en una rama muerta | refusado antes | igual | igual |

### Decisión del autor (2026-09-26)

Un miembro que el módulo no exporta, `m.nada` o `m::nada()`, se refusa **antes de
ejecutar**, en los tres motores y en `zymbol check`, con línea y columna. Es lo que ya
pasaba con un nombre local.

### Qué se cambió

- `call_arity.rs`: `module_exports` es la tabla de lo que exporta cada alias de usuario,
  con las constantes y las funciones separadas. Si el bloque `#>` no se resuelve entero,
  el alias no entra y su uso se deja para la ejecución.
- El comprobador de tipos refusa `m.nada` con `Module 'm' has no constant 'nada'.
  Available constants: …` y `m::nada()` con `module 'm' does not export function
  'nada'`, que son las palabras que ya daban los tres al ejecutar. Si el nombre existe pero
  es del otro tipo, la ayuda dice cómo alcanzarlo, con los textos de `std/`. Una variable
  local con el nombre del alias lo tapa: ver [`GLB-070`](GLOBAL.md).
- `zymbol run` llama a `check_stdlib_access`, como ya hacía `check`.
- `zyjs`: `moduleExportsFor`, `STDLIB_CONSTANTS` (la prueba `test_check.mjs` la compara con
  Rust) y los mismos refusos, con los textos de `std/`. Hay seis códigos nuevos en el
  catálogo del playground.
- LSP: su escaneo de `alias::f` repetía el refuso con otras palabras, y el editor enseñaba
  los dos. Ahora solo mira los reexports del bloque `#>`, que el comprobador no ve.

Medido antes de fijarlo: `zymbol check` sobre los 2926 `.zy`. Caen cuatro ficheros, los
cuatro pruebas escritas para esto. Los dos del corpus (`errors/runtime/E008_private_access`
y `E012_no_export`) cambian de golden, y
`runtime-modules-scripts/unexported-function-as-an-error-value` ahora espera un error: un
refuso hecho antes de ejecutar no lo alcanza ningún `!?`.

### Qué lo sujeta

`runtime-modules-scripts/dot-read-of-a-constant-the-module-does-not-have`, en verde, y
cuatro celdas nuevas: `missing-constant-in-a-branch-that-never-runs`,
`missing-function-in-a-branch-that-never-runs`,
`missing-std-function-in-a-branch-that-never-runs` y
`variable-that-shares-an-alias-name-is-not-a-module`. Esta última está roja, y es
[`GLB-070`](GLOBAL.md).

---

## ZYVM-009 — Un brazo `patrón => valor { bloque }`: la VM se saltaba el bloque

**Estado:** **corregido el 2026-09-26** (paso P4.8)
**Encontrado por:** midiendo [`ZYJS-038`](zyjs.md)

El compilador del `??` escribía `if valor { … } else if bloque { … }`, así que, con un valor,
el bloque no se compilaba nunca, en el brazo normal y en el comodín. Con
`90..100 => 'A' { >> "bien" ¶ }`, el TW imprimía `bien` y devolvía `A`, y la VM devolvía `A`
sin imprimir nada. Ahora son dos pasos: el valor a `dst` y después el bloque.

### Qué lo sujeta

`runtime-match-patterns/match-arm-with-a-value-and-a-block` y
`match-arm-value-comes-before-its-block`, verdes.

---

## ZYVM-010 — Soltar valores cuesta entre el 11 y el 17 % del tiempo de la VM

**Estado:** abierto — la parte del marco (`IDEA-BEN-002`) **aplicada el 2026-10-09** y la escritura de un registro
el **2026-10-10**; queda abierta sólo la reutilización de temporales del compilador, aplazada por el autor (R4)
**Encontrado por:** el perfil de [`IDEA-GOL-007`](../../GoL/HALLAZGOS.md) (el
coste de una llamada por celda), el 2026-10-01, **no por una celda**
**Familia:** ninguna con nombre todavía. Es coste, no semántica: los tres
motores dan la misma salida

### Qué se observa

`zyquality/cost/casos/llamada_por_celda.zy.in` y su control `en_linea.zy.in`
con lado 160 (256 000 llamadas), `perf` sobre un binario de release compilado
aparte con símbolos y punteros de marco:

| | en línea | con llamada |
|---|---:|---:|
| tiempo | 606 ms | 705 ms |
| instrucciones de máquina | 5 136 M | 5 620 M |
| tiempo en `drop_glue<Value>` | ~11 % | ~17 % |
| muestras de liberación | 511 | 730 |

Quién llama a la liberación:

| línea | en línea | con llamada | qué es |
|---|---:|---:|---|
| `lib.rs:1394` `wreg!` | 321 | 354 | escribir un registro suelta el valor anterior |
| `lib.rs:4601` `reg_set` | 114 | 155 | lo mismo, por el auxiliar |
| `mod.rs:823` `drop_in_place` | 8 | **90** | desmontar el marco del llamado al volver (`truncate`) |
| `result.rs:835` | 48 | 97 | liberaciones dentro de caminos de `Result` |

Dos lecturas, y la segunda es la que da nombre a la ficha:

1. **La llamada.** Cada una cuesta ~1 900 instrucciones de máquina y ~1 500
   ciclos más que el mismo trabajo en línea, y desmontar el marco es la partida
   mayor que crece. El marco de `vecinos` — cinco parámetros, cinco locales —
   tiene **34 registros**, porque el compilador nunca reutiliza un temporal:
   `alloc_temp` sólo avanza `next_reg`. Cada llamada hace `resize` de 34 `Unit`
   al entrar y suelta 34 valores al salir.
2. **Todo programa.** Sin llamada alguna, la VM pasa ~11 % de su tiempo en
   `drop_glue<Value>`, y casi todo viene de **escribir un registro**: la
   asignación suelta el valor anterior por una función fuera de línea.

### Causa

`crates/zymbol-vm/src/lib.rs` — `wreg!` y `reg_set` escriben con `*slot = v`,
que llama a la liberación del valor viejo; `Instruction::Return` hace
`value_stack.truncate(base)`, que la llama una vez por registro del marco. Y
`crates/zymbol-compiler/src/lib.rs`, `alloc_temp`, que hace los marcos tan
grandes como el número de temporales de la función entera.

**Sin separar todavía:** qué parte de esas liberaciones es de valores que no
poseen nada (`Int`, `Float`, `Bool`, `Char`, `Unit`) y qué parte decrementa un
`Rc` de verdad (una fila del tablero, el propio `m`). El perfil dice dónde se
llama, no qué se suelta.

### Alcance

Toda ejecución en la VM, que es el futuro motor por defecto. No lo ve nada:
`zyq consensus` compara salidas, `bench/` compara cada programa consigo mismo
contra su línea base, y la celda `call/function-in-hot-loop` sólo sujeta la
diferencia entre llamar y no llamar — no el 11 % que pagan los dos.

### Arreglo propuesto

Dos, independientes, y ninguno decidido:

- **En la VM:** no soltar cuando el valor viejo no posee nada — mirar la
  variante antes de escribir y, si es escalar, sobrescribir sin liberación; y lo
  mismo al desmontar el marco. No cambia la semántica; toca el bucle más
  caliente del intérprete.
- **En el compilador:** reutilizar los temporales cuando la sentencia que los
  pidió termina, para que el marco mida lo que la función necesita a la vez y no
  todo lo que pidió alguna vez. Más invasivo: hace falta saber qué registro
  sigue vivo, y reutilizar uno que lo está es un bug de valores silencioso.

Antes de cualquiera de los dos: separar escalares de `Rc` en las muestras, que
dice cuánto hay que ganar con el primero.

### Qué lo sujeta

Nada todavía. La celda `call/function-in-hot-loop` (`time-ratio`, límite 1,30)
vigila la llamada; el coste de soltar en cada escritura no tiene celda.

### Lo que añadió una medición de fuera (ZyBench, documentado el 2026-10-08)

`IDEA-BEN-002`, de ZyBench —una medición de la VM contra Python hecha en otra
sesión—, perfiló con callgrind sobre `820a60a` (2026-10-04) y aporta el dato que
esta ficha dejaba **sin separar**. En `fib(22)`, ~1 000 instrucciones por
llamada, `Vec::resize` era el 23 % (rellenar con `Unit` el marco de 7 registros:
`resize(n, Value::Unit)` clona el valor en cada hueco) y soltarlo al volver el
19 %; y los 7 registros contienen enteros o `Unit` cuando la función vuelve, es
decir, **todo** ese desmontaje es de valores que no poseen nada. En un programa
que devuelve filas del tablero no tiene por qué serlo; eso no se midió.

Propone cuatro cambios, sólo en `zymbol-vm/src/lib.rs`: `resize_with` en lugar
de `resize` (5 sitios); un `truncate_regs` que suelta sólo lo que posee memoria
(7 sitios, el único `unsafe`); `call_callable` con los argumentos en un array y
no en un `Vec` (los 7 llamadores de `$>`, `$|`, `$<` y `$^`); y `StoreGlobal`, que
hace `destroyed_globals.remove` en cada asignación a una global, sólo cuando el
conjunto no está vacío. Mide un 19–27 % menos de instrucciones (`fib(22)`, un
`reduce` de 50 000 llamadas, un bucle de 200 000 vueltas).

Verificado aquí, en `v0.0.10`, el 2026-10-08: los hechos de código siguen siendo
ciertos —5 `resize(…, Value::Unit)`, 7 `value_stack.truncate`, `call_callable`
con `args: Vec<Value>`, el `remove` incondicional en `StoreGlobal`—. **No**
verificado: las cifras de instrucciones (aquí no hay `valgrind`) y el parche
(`vm_llamadas.patch` no está en este workspace).

Es **la mitad del primer arreglo** de arriba —no soltar lo que no posee nada—, y
sólo al desmontar el marco. No toca la escritura de un registro (`wreg!`,
`reg_set`), que es el ~11 % de todo programa, ni la reutilización de temporales
del compilador: esas dos partes siguen abiertas.

### La parte del marco, aplicada (2026-10-09)

Aprobado por el autor el 2026-10-09 al habilitar `perf` para medirlo (D4 de la ronda de ZyBench y ZyBF), y medido con `perf stat -e
instructions:u` sobre el binario de release (opt-level 3 + LTO), cinco ejecuciones; las instrucciones no varían
entre ejecuciones. Sólo `zymbol-vm/src/lib.rs`, aplicado y medido **de uno en uno**:

| cambio | `fib(22)` | `reduce`, 50 000 llamadas | bucle de 200 000 vueltas | `llamada_por_celda`, lado 160 |
|---|---:|---:|---:|---:|
| antes | 45,79 M | 79,87 M | 229,97 M | 5 707 M |
| 1. `resize_with` en lugar de `resize(…, Value::Unit)` (5 sitios) | −11,5 % | −4,5 % | −1,3 % | −2,8 % |
| 2. `StoreGlobal` sólo quita de `destroyed_globals` si no está vacío; `get_chunk` en línea | 0 | 0 | **−14,3 %** | −0,1 % |
| 3. `call_callable` con los argumentos en un array, no en un `Vec` (7 llamadores) | +0,1 % | **−11,1 %** | 0 | 0 |
| 4. `truncate_regs`: al desmontar el marco suelta sólo lo que posee memoria (7 sitios) | **−10,0 %** | −2,1 % | 0 | −0,9 % |
| después | 36,54 M (**−20,2 %**) | 66,33 M (**−17,0 %**) | 194,58 M (**−15,4 %**) | 5 490 M (**−3,8 %**) |

El bucle de 200 000 vueltas gana con el cambio 2 porque su `s` es una variable global: cada asignación pagaba
un `remove` en un mapa vacío. En `llamada_por_celda`, lo que cuesta llamar —su diferencia con `en_linea`, que hace
el mismo trabajo sin llamar— baja de 479 M a 305 M de instrucciones, un 36 %.

En tiempo de reloj, contra un binario de antes compilado aparte desde el mismo commit (que reproduce las
instrucciones de antes con menos del 0,001 % de diferencia), mediana de 7 ejecuciones alternadas: `fib(30)` 218 →
172 ms (−21 %), el bucle de 2 000 000 de vueltas 221 → 191 ms (−14 %), `llamada_por_celda` 727 → 679 ms (−7 %).
Un `reduce` de 500 000 elementos no cambia (88 ms los dos): ahí domina construir el array.

**El único `unsafe`** está en `truncate_regs`, y es más simple que el del parche de ZyBench, que no se usó (no
está en el workspace). Un bucle sustituye por `Unit` cada valor que posee memoria —una asignación segura, que
lo suelta— y después `set_len` acorta el vector. Acortar nunca deja memoria sin inicializar, así que el peor
caso de un error en `Value::owns_memory` sería una fuga, nunca un comportamiento indefinido. Y `owns_memory`
enumera los escalares, no los dueños: una variante que se añada después se suelta hasta que alguien diga lo
contrario.

Lo que lo comprueba: `cargo test --release` (1060 pasan, 4 ignorados, como antes); el consenso del corpus
(672 de 678 de acuerdo, 0 divergen) y sus goldens (642 + 30); dos sondas de memoria —una función que crea un
array, una cadena larga y un diccionario, llamada 20 000 y 80 000 veces, y 3 000 errores que desmontan 41 marcos
con colecciones dentro— que dan el mismo resultado que el TW y un pico de memoria plano (11,1–11,2 MB).

Lo que **no** se hizo, y mantiene la ficha abierta: escribir un registro (`wreg!`, `reg_set`), el ~11 % de todo
programa, y reutilizar los temporales del compilador (`alloc_temp`).

### Medido de nuevo, 2026-10-10 — con símbolos

Un binario de release compilado aparte con símbolos (`strip = false`, `debug = 1`), `perf record`:

| programa, en la VM | `VM::exec` | `drop_glue<Value>` |
|---|---:|---:|
| `fib(30)` | 85 % | **12 %** |
| una generación de Vida con una llamada por celda, lado 160 | 74 % | **20 %** |
| un bucle de 2 000 000 de vueltas en el nivel de arriba | 84 % | **14 %** |
| GO, una partida contra sí mismo (`自戦試験`) | 49 % | **13 %** |
| Chaturanga, la búsqueda (`गतिपरीक्षा`) | 64 % | **10 %** |

Soltar el valor anterior al escribir un registro sigue costando entre el 10 y el 20 %, también en las
aplicaciones. La llamada en sí (la diferencia entre la versión con llamada y la versión en línea) es ya el 5,5 %
de las instrucciones, así que lo que queda por ganar reutilizando temporales es poco.

### La escritura de un registro, aplicada (2026-10-10)

Decidido por el autor el 2026-10-10 (R3). `wreg!` y `reg_set` escriben ahora por `put_reg`: sustituyen el valor
y sólo llaman a la rutina de soltado si el anterior posee memoria; un escalar se olvida (`mem::forget`). **Sin
`unsafe`**, y `owns_memory` enumera los escalares, así que una variante nueva se suelta por defecto.

Ciclos de CPU de usuario (`perf stat -e cycles:u`, mediana de 5), contra el mismo binario de antes sin símbolos:

| programa, en la VM | antes | ahora | |
|---|---:|---:|---:|
| `fib(30)` | 641,5 M | 618,8 M | −3,5 % |
| un `reduce` de 500 000 | 245,4 M | 237,0 M | −3,4 % |
| un bucle de 2 000 000 de vueltas | 691,3 M | 609,5 M | **−11,8 %** |
| una llamada por celda, lado 160 | 2 720,8 M | 2 272,2 M | **−16,5 %** |
| GO, una partida contra sí mismo | 506,0 M | 486,1 M | −3,9 % |
| Chaturanga, la búsqueda | 521,7 M | 475,3 M | −8,9 % |
| `ZyBF/pesado2.zy` | 1 294,6 M | 1 275,7 M | −1,5 % |

Las instrucciones bajan menos (del 2 al 4 %): lo que se ahorra es la llamada, que costaba en ciclos más que en
instrucciones. El tiempo de reloj no se da: en programas de menos de 100 ms baila un 15 % entre corridas, y el
binario con símbolos que sirvió de «antes» tarda 8 ms más en cargar — comparar contra él inflaba la mejora.

Ninguna salida cambia: `cargo test --release` 1060 y 4 ignorados, el consenso del corpus (673 de 679, 0 divergen),
las nueve aplicaciones, y las dos sondas de memoria con el pico plano (11,2 MB). `zyquality/cost`
`call/function-in-hot-loop` da 1,04 en la VM.

Lo que mantiene la ficha abierta: reutilizar los temporales del compilador (`alloc_temp`). Aplazado: la llamada
entera es el 5,5 % de las instrucciones, y reutilizar un registro que sigue vivo es un error de valores silencioso.

---

## ZYVM-011 — Un `??` de sentencia en el que no encaja ningún brazo: la VM sitúa el error en la última línea de un brazo

**Estado:** **corregido 2026-10-07** — OK del autor el 2026-10-07: la VM da la línea de la sentencia, la regla
de todos los errores de ejecución
**Encontrado por:** al corregir [`ZYJS-051`](zyjs.md) (2026-10-07): la celda lo tapaba mientras `zyjs` seguía
de largo, porque su deuda declarada cubría la celda entera

```zymbol
v = 2
?? v {
    1 => {
        >> "uno" ¶
    }
}
>> "sigue" ¶
```

| motor | error | línea que da |
|---|---|---|
| `zytw` | `no pattern matched in match expression` | `--> …:2`, la del `??` |
| `zyjs` | igual | `2` |
| `zyvm` | igual | `--> …:4`, la del `>>` dentro del último brazo |

Como valor, `r = ?? 2 { 1 => "uno" }`, los tres dan la línea 1. La regla es la de todos los errores de
ejecución: la línea es la de la sentencia. La VM toma la posición de la última instrucción que compiló
dentro de los brazos, que es lo que encuentra cuando lanza al final del `??`.

### Qué hay que decidir

Nada de diseño: la regla de la línea ya está decidida. Lo que queda es la corrección, que la VM dé la línea
del `??`. Pendiente del OK del autor.

### Corrección

El compilador sella cada instrucción con la posición de la sentencia que se está compilando
(`FunctionCtx::cur_src`), y una sentencia anidada la sobrescribe sin restaurarla. El `RaiseError` del final
de un `??` se emite después de los brazos, así que se llevaba la posición de la última sentencia que había
en ellos. `compile_match_expr` guarda ahora la posición al entrar y sella con ella esa única instrucción; lo
que se emite después conserva el sello que tenía, que es también el del TW.

| forma | antes, la VM | ahora, los tres |
|---|---|---|
| `?? v { 1 => { >> "uno" ¶ } }` | la línea del `>>` | la del `??` |
| lo mismo dentro de una función | la del `>>` | la del `??` |
| `r = ?? v { 1 => "x" { >> "a" ¶ } }` | la del `>>` | la de la sentencia |
| el último brazo con un `?` dentro | la del `>>` del último brazo | la del `??` |
| en el cuerpo de un `@` | la del `>>` | la del `??` |
| `x = 1 + (?? v { 1 => 10 { >> "a" ¶ } })` | la del `>>` | la de la sentencia |
| `r = ?? 2 { 1 => "uno" }`, sin bloques (control) | la de la sentencia | la de la sentencia |

Al medirlo apareció lo que queda fuera de esta corrección: un error **posterior** en la misma sentencia,
después de un bloque anidado, sale en TW y VM con la línea de ese bloque —
[`GLB-106`](GLOBAL.md).

### Qué lo sujeta

`runtime-match-patterns/match-statement-no-arm-matches`, ya sin deuda, y tres celdas nuevas para las formas
que la VM también situaba mal: `match-value-no-arm-matches-after-a-block-arm`,
`match-statement-no-arm-matches-past-a-nested-if` y `match-statement-no-arm-matches-in-a-loop`. Con la VM
de antes, las cuatro dan DIVERGE.

---

## ZYVM-012 — Un error dentro de una lambda cuyo cuerpo es una expresión: la VM no dice en qué línea

**Estado:** **corregido 2026-10-07** — decidido por el autor el 2026-10-07: la línea de la sentencia que
llama, como el TW y `zyjs`
**Encontrado por:** al corregir [`GLB-106`](GLOBAL.md) (2026-10-07)

```zymbol
h = (s) -> s + 1
x = h("b")
>> x ¶
```

Los tres motores fallan con `+ is arithmetic only — use juxtaposition to concatenate strings`. El TW y
`zyjs` añaden `--> …:2`, la línea de la sentencia que corre, la que llama a la lambda. La VM no añade nada.

| programa | TW | VM | `zyjs` |
|---|---|---|---|
| el de arriba | 2 | sin línea | 2 |
| `ys = ["a", "b"]$> (x -> x + 1)` | 2 | sin línea | 2 |
| `g() { >> "a" ¶  <~ "b" }` · `h = (s) -> s + 1` · `x = h(g())` | 6 | sin línea | 6 |
| control: `h = (s) -> { <~ s + 1 }`, la lambda de bloque | 2 | 2 | 2 |

Una lambda se compila en su propio `FunctionCtx`, y sólo una sentencia pone posición
(`ctx.cur_src`): un cuerpo que es una expresión no tiene ninguna, así que sus instrucciones llevan la
posición por defecto, la línea 0, y un error de línea 0 se informa sin línea.

### Qué hay que decidir

- que un error sin posición propia dé la de la sentencia que llama, como el TW y `zyjs` (Recomendado): es
  la regla de todos los errores de ejecución —la línea es la de la sentencia que corre—, y una lambda de
  expresión no tiene sentencia;
- que dé la línea en que se escribió la lambda: en la VM sería el sello natural, y cambiarían el TW y `zyjs`.

### Corrección

Dos sitios, uno por cada manera de llegar a la lambda:

- **una llamada escrita** (`h(v)`): `locate`, cuando la instrucción que falló no tiene línea, baja por la
  pila de marcos hasta la llamada que llegó a ella —la instrucción anterior a la dirección de vuelta que
  guardó el marco que llama— y toma su posición;
- **un operador que llama** (`$>`, `$|`, `$<`): la ejecución anidada devuelve sus marcos al fallar, así que
  ahí ya no hay pila que bajar; `call_callable` repone la posición del operador cuando la del fallo no tiene
  línea.

| programa | antes, VM | ahora, los tres |
|---|---|---|
| `h = (s) -> s + 1` · `x = h("b")` | sin línea | 2 |
| `xs$> (x -> x + 1)` | sin línea | 2 |
| `<~ h(v)` dentro de una función | sin línea | 4 |
| `xs$| (x -> x > 1)` dentro de una lambda de bloque | sin línea | 2 |
| `x = h(g())`, con un `>>` antes en `g` | sin línea | 6 |
| control: la lambda de bloque | 2 | 2 |

### Qué lo sujeta

`runtime-errors/error-inside-an-expression-lambda-has-a-line`, ya sin deuda;
`error-inside-an-expression-lambda-given-to-map-has-a-line`,
`error-inside-an-expression-lambda-called-in-a-function-has-a-line` y
`error-inside-a-filter-lambda-in-a-block-lambda-has-a-line`. Con la VM de antes, las cuatro dan DIVERGE.
