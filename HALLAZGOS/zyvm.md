# Hallazgos — `zyvm` (VM de registros)

> Un hallazgo entra aquí cuando el runner nombra a `zyvm` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

| | | |
|---|---|---|
| [`ZYVM-001`](#zyvm-001--la-vm-ejecuta-lo-que-el-tree-walker-rechaza-40-celdas) | **corregido 2026-08-30** | ejecutaba y contestaba donde `zytw` rechaza — 40 celdas |
| [`ZYVM-002`](#zyvm-002--el-diagnóstico-de---nombra-al-operador--10-celdas) | **corregido 2026-08-30** | el rechazo de `-` citaba al operador `+` |
| [`ZYVM-003`](#zyvm-003--acumular-en-el-estado-de-un-módulo-es-on-en-la-vm-y-on-en-el-tree-walker) | **corregido 2026-10-10** | acumular en el estado de un módulo era cuadrático: 3,3 s donde el TW tardaba 0,013 s |
| [`ZYVM-004`](#zyvm-004--una-función-llamada-por----o--corre-en-un-segundo-intérprete-que-se-salta-49-instrucciones) | **corregido 2026-09-14** | una función llamada por `$>`, `$|` o `$<` corría en un segundo intérprete que se saltaba 49 instrucciones |
| [`ZYVM-010`](#zyvm-010--soltar-valores-cuesta-entre-el-11-y-el-17--del-tiempo-de-la-vm) | **corregido 2026-10-10** | soltar valores al desmontar el marco y al escribir un registro, y un marco que medía todos los temporales que la función pidió alguna vez |
| [`ZYVM-020`](#zyvm-020--n--sobre-un-nombre-que-es-estado-del-módulo-la-vm-le-da-un-registro-propio) | **corregido 2026-10-10** | `n° = n + i` con `n` estado del módulo: 3 donde los otros dos dan 16 |
| [`ZYVM-021`](#zyvm-021--una-lambda-escrita-en-una-función-de-un-módulo-lee-el-estado-del-módulo-como-está-no-como-lo-capturó) | **corregido 2026-10-10** | una lambda en una función de módulo leía el estado del módulo como estaba, no como lo capturó |
| [`ZYVM-023`](#zyvm-023--s--s-x-copia-el-texto-entero-en-cada-añadido-construir-un-texto-es-cuadrático-en-la-vm) | **corregido 2026-10-16** | `s = s "x"` copiaba el texto entero en cada añadido: construir un texto era cuadrático |

**Uno abierto:** `ZYVM-031`. `ZYVM-022`, que no está en la tabla, se corrigió el 2026-10-19. La tabla no es la lista entera ni el estado vivo: el estado de cada ficha es su línea **Estado**, y `./bin/zyddt findings` lo calcula de ahí — y desde el 2026-10-10 pone en rojo (`STALE SUMMARY`) la fila o la frase de aquí arriba que contradiga a su ficha.

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

**Estado:** **corregido 2026-10-10** — la edición saca el valor de la ranura del módulo y es su única dueña; el
orden lo decidió el autor ese día en [`GLB-115`](GLOBAL.md): de izquierda a derecha
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

### Corrección (2026-10-10)

Una edición cuyo resultado vuelve a su propio receptor —`t[i]$~ v`, `t$-[i]`, `t$+ v`, escrita como sentencia o
como `t = t…`— y cuyo receptor es estado de un módulo se compila así: `LoadGlobal`, los operandos,
`DetachGlobal(g, t)`, la edición sobre `t`, `StoreGlobal(g, t)`.

- **`DetachGlobal`** vacía la ranura **sólo si sigue guardando el mismo valor que se cargó** (`Rc::ptr_eq`). Si un
  operando escribió el estado entre medias, la ranura ya es otro valor: la edición corre sobre lo leído y el
  `StoreGlobal` lo pisa. Es el orden de izquierda a derecha de `GLB-115`, sin ningún caso especial.
- **El fallo:** si la edición lanza un error, el valor vuelve a la ranura antes de que nadie lo capture. Y cada
  instrucción de edición valida entera antes de escribir: `DeepSet` recorre el camino completo primero (una clave
  nueva de un diccionario se añade sólo si el resto del camino existe) y `ArrayRemove` comprueba el índice sobre
  el valor en su sitio.
- **Los temporales de la propia sentencia:** `tabla[k]$~ tabla[k] + 1` y `t$-[t$#]` cargan el estado en un temporal
  para calcular el operando, y ese temporal seguía siendo un segundo dueño. El compilador apunta los temporales en
  que la sentencia cargó ese estado y limpia, justo antes de editar, los que la edición no usa.

Instrucciones en la VM, los mismos programas de la tabla de arriba, N = 4000 → 16 000:

| edición sobre el estado del módulo | antes | ahora | crece ×4, ahora |
|---|---:|---:|---:|
| añadir, `datos$+ i`, N veces | 304 M → 4 710 M | 7,9 M → 20,9 M | ×2,7 |
| actualizar un elemento, 4000 veces | 906 M → 7 088 M | 15,0 M → 28,6 M | ×1,9 |
| quitar del final, 2000 veces | 524 M → 5 794 M | 10,7 M → 23,7 M | ×2,2 |
| control: un contador | 7 M → 15 M | 6,4 M → 15,0 M | ×2,4 |
| control: un diccionario de dos campos | 13 M → 42 M | 10,2 M → 30,4 M | ×3,0 |

El TW, en los mismos: 34 M, 46 M y 40 M a N = 16 000. La VM queda por debajo en los tres.

Una carga real: `ZyBF/pesado2.zy` —419 430 actualizaciones de una cinta de 300 celdas— pasa en la VM de 3 719 M de
instrucciones a 1 190 M (el TW, 6 794 M).

No cambia ninguna salida: el consenso del corpus, las nueve aplicaciones y ZyDDT quedan como estaban.

**Lo que no cubre.** Las ediciones que recorren la colección de todos modos (`$+[i]`, `$- v`, `$-- v`,
`$-[a..b]`) siguen construyendo el resultado: su coste ya es proporcional al tamaño. `$++` es otra cosa —añade
al final y copia—, en los dos motores de Rust: [`GLB-118`](GLOBAL.md).

### Qué lo sujeta ahora

`zyquality/cost`, `growth/append-module-state` y `growth/update-module-state`, ya sin deuda y con la VM medida a
tres veces el tamaño del TW —por debajo de eso su corrida no llega al suelo de 40 ms—;
`runtime-modules-scripts/module-state-after-a-failed-edit` para el fallo, y
`edit-whose-operand-writes-the-same-state` para el orden.

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

**Estado:** **corregido 2026-10-10** — en tres partes: el marco (`IDEA-BEN-002`, 2026-10-09), la escritura de un
registro (2026-10-10) y la reutilización de temporales del compilador, aplazada como R4 y pedida por el autor el
mismo 2026-10-10 al ver lo que costaba en una función larga (ver «La parte que quedaba, corregida»)
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

El 2026-10-01, nada: la celda `call/function-in-hot-loop` (`time-ratio`, límite 1,30)
vigilaba la llamada y el coste de soltar en cada escritura no tenía celda. Desde el
2026-10-10, `zyquality/cost` `call/frame-as-large-as-every-temporary` — ver «La parte
que quedaba», al final de la ficha.

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

### La parte que quedaba: primero sujeta (2026-10-10)

Hasta ese día `zyddt findings` decía de esta ficha *«watched by nothing»*: abierta, y sin nada que la mirara. La
parte aplazada se puede medir sola, con dos programas que **ejecutan las mismas instrucciones**:

```zymbol
paso(x, a, b) {
    ? x < 0 {
        >> ((x + a) * (b + 1) - (a * 2 + b)) % 97 ¶
        // … y 63 sentencias más como esa en el sujeto; sólo esta en el control
    }
    <~ x + a
}

s = 0
@ i:1..N { s = paso(i % 7, s % 3, 2) % 1000 }
>> s ¶
```

`x` nunca es negativo, así que la rama no corre en ninguno de los dos, y ninguna de sus sentencias declara una
variable: lo único que cambia es cuántos temporales pidió el cuerpo. `alloc_temp` sólo avanza `next_reg`, el marco
tiene un registro por cada uno, y cada llamada lo rellena entero al entrar y lo recorre al salir.

| 2 000 000 de llamadas (`zytw` 400 000, `zyjs` 200 000) | control, 1 sentencia | sujeto, 64 | razón |
|---|---:|---:|---:|
| `zyvm` | 295 ms | 816 ms | **2,76** |
| `zytw` | 453 ms | 451 ms | 0,99 |
| `zyjs` | 1 656 ms | 1 685 ms | 1,02 |

Con 16 sentencias y una variable en cada una la VM da 1,6; con 64, 3,3. El 5,5 % de arriba es lo que cuesta la
llamada en una función pequeña (`vecinos`, 34 registros); esto es lo que cuesta en una función **larga**, la
llame quien la llame y corra o no la mayor parte de su cuerpo.

`zyquality/cost`: `call/frame-as-large-as-every-temporary` (`time-ratio`, límite 1,30). Se declaró con
`open_finding = { zyvm = "ZYVM-010" }` y salió `KNOWN`; horas después salió `DEBT PAID`, en rojo, que es lo que
tiene que pasar el día que una deuda se paga.

### La parte que quedaba, corregida (2026-10-10)

Pedido por el autor ese día, con la tabla de arriba delante: el 5,5 % que justificaba aplazarlo era el de una
función pequeña.

`crates/zymbol-compiler/src/lib.rs`. Un temporal pertenece a la sentencia que se está compilando.
`compile_stmt` anota cuántos hay vivos al empezar y, al terminar, devuelve los suyos a un fondo
(`FunctionCtx::free_temps`); `alloc_temp` saca del fondo antes de pedir un registro nuevo. Una sentencia anidada
devuelve sólo los suyos: los del bucle o del `!?` que la contiene —el iterador, el registro del error— siguen
siendo de quien los pidió hasta que esa sentencia acaba.

Lo que hubo que mirar antes, porque reutilizar un registro que sigue vivo es un valor equivocado y callado:

- **Dos registros contiguos.** `ArraySlice`, `StrSlice`, `ArrayRemoveRange` y sus formas de cuenta, y
  `NavRangeCheck`, reciben un registro y leen el siguiente. Dos registros devueltos por separado no son vecinos:
  esos tres sitios piden su pareja con `alloc_temp_pair`, que nunca sale del fondo.
- **Un temporal con nombre.** `<< x` y `<<| x` ligaban un temporal a la variable cuando era nueva. Ahora piden
  un registro de variable; y al devolver, un registro al que algún nombre apunta se salta, lo haya pedido quien
  lo haya pedido.
- **El tipo que se sabía.** `reg_types` guarda lo que el compilador dedujo de un registro, y elige con ello la
  instrucción (`StrLen` o la longitud de un array). Al reutilizar, el tipo vuelve a «desconocido».
- **Encontrar `Unit` sin haberlo escrito.** Un registro nuevo vale `Unit`; uno reutilizado, lo que dejó el
  anterior. La regla queda escrita en `alloc_temp`: un temporal se escribe antes de leerse, siempre.

Las dos últimas no se demuestran leyendo. `ZYMBOL_POISON_TEMPS=1` hace que el compilador escriba un valor que
ningún programa calcula (5 333 666 999) en cada temporal al acabar su sentencia: lo que lea un temporal después
de devolverlo, o cuente con un `Unit` que no escribió, lo saca por la salida en vez de dar una respuesta
verosímil. Con el veneno puesto: el consenso del corpus (673 de 679 de acuerdo, 0 divergen), los goldens bajo la
VM, las nueve aplicaciones y los 45 ejes de ZyDDT, sin una diferencia.

| 2 000 000 de llamadas | control, 1 sentencia | sujeto, 64 | razón |
|---|---:|---:|---:|
| `zyvm`, antes | 295 ms | 816 ms | 2,76 |
| `zyvm`, ahora | 279 ms | 277 ms | **0,99** |

**Lo que no cambia, y no es deuda:** las variables. Un bloque con 64 variables propias las tiene vivas a la vez,
y su marco las necesita: la misma sonda con una variable por sentencia baja de 3,3 a 1,5, no a 1,0. Lo que sí
sería reutilizable —el registro de una variable de un bloque que ya terminó, para el bloque hermano— no se
tocó: una variable se lee por nombre desde más sitios que un temporal (`\`, la marca caliente, el espejo de las
variables del fichero), y no hay medición de que cueste en ningún programa real.

### Qué lo sujeta

`zyquality/cost`: `call/frame-as-large-as-every-temporary`, en verde en los tres y ya sin deuda declarada, y
`call/function-in-hot-loop`. `crates/zymbol-compiler/tests/compile_smoke.rs`:
`a_statement_hands_its_temporaries_back` (64 sentencias caben en el marco de una) y
`a_slice_keeps_its_bounds_adjacent_among_reused_temporaries`. `cargo test --release`: 1062 y 4 ignorados.

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

---

## ZYVM-013 — `t[i]$~ v` y `t$-[i]` copian la colección entera en la VM, también sobre una variable local

**Estado:** **corregido 2026-10-10** — no cambia ninguna salida
**Encontrado por:** el control de una medición de `<~` (2026-10-10): las mismas escrituras **en línea**, sin
ninguna llamada, costaban lo mismo que a través de un parámetro de salida
**Familia:** [`ZYVM-003`](zyvm.md) — el mismo `Rc` con dos dueños en el momento de escribir

```zymbol
correr(n) {
    t = []
    @ i:1..n { t$+ 0 }
    @ k:1..2000 { t[(k % n) + 1]$~ k }
    <~ t$#
}
>> correr(16000) ¶
```

Instrucciones (`perf stat -e instructions:u`), 2000 ediciones sobre 16 000 elementos:

| edición, sobre una variable local | `zytw` | `zyvm` | crece ×4 en la VM |
|---|---:|---:|---:|
| actualizar un elemento, `t[i]$~ k` | 33 M | **1 202 M** | ×3,94 |
| quitar del final, `t$-[t$#]` | 31 M | **1 096 M** | ×4,9 |
| añadir, `t$+ k` | 31 M | 14 M | ×2,6 |

Lo mismo en el nivel de arriba del programa, con un índice literal (`t[1]$~ k`), y escrito como `t = t[i]$~ k`.
Añadir no lo sufre: tiene su propio camino en el compilador (`arr = arr$+ elem → ArrayPush in-place`).

### Causa

`zymbol-compiler/src/lib.rs`, `compile_collection_update_as`: para `t[i]$~ v` emite `CopyReg(dst, r_arr)` y después
`DeepSet(dst, …)`. La copia del registro deja dos dueños del `Rc` —la variable y `dst`—, y `Rc::make_mut` copia el
vector. Es lo correcto para la forma funcional, `u = t[i]$~ v`, donde `t` no puede cambiar; la forma que modifica
(`t[i]$~ v` como sentencia) pasa por el mismo camino. `ArrayRemove` llega igual, sobre una copia.

### Alcance

Todo programa que actualice un tablero, una cinta o una tabla casilla a casilla en la VM, que es el futuro motor
por defecto: GO, Chaturanga, GoL, ZyBF. No lo ve nada: la salida es idéntica.

### Arreglo propuesto

En la forma que modifica, operar sobre el registro de la propia variable, sin `CopyReg`. Exige que la instrucción
sea atómica ante el fallo —validar antes de sacar el valor—: hoy `DeepSet` y `ArrayRemove` hacen `mem::replace` y,
si el índice es malo, lanzan el error con el valor ya soltado, lo que sólo es inocuo porque escriben sobre una
copia.

### Corrección (2026-10-10)

La forma que modifica opera sobre el registro de la propia variable: sin `CopyReg` para `t[i]$~ v` (y sus caminos
`t[i>j]$~ v`, `t.campo$~ v`), y `ArrayRemove` directo para `t$-[i]`. Las dos instrucciones validan antes de
escribir, así que una edición que falla deja la variable como estaba.

Dos cosas que hubo que cuidar:

- **Una variable que la misma sentencia pasa como `<~`** (`d[1]$~ meter(d<~)`) no se edita en el sitio: su lectura
  queda fijada antes de la llamada ([`ZYVM-015`](zyvm.md)) y la edición corre sobre esa copia, como antes. Es el
  orden de izquierda a derecha de [`GLB-115`](GLOBAL.md).
- **El nivel de arriba de un programa.** Cada variable del script tiene una ranura espejo que el cuerpo del
  programa reescribe en cada asignación, y esa ranura era un segundo dueño: la edición copiaba igual. Ahora la
  ranura se suelta durante la edición y se reescribe después, como el estado de un módulo; si la edición falla,
  recibe de vuelta el valor intacto.

Instrucciones en la VM, 2000 ediciones sobre 16 000 elementos:

| edición | receptor | antes | ahora | `zytw` |
|---|---|---:|---:|---:|
| `t[i]$~ k` | variable local | 1 202 M | 16 M | 33 M |
| `t$-[t$#]` | variable local | 1 096 M | 14 M | 31 M |
| `t[i]$~ k` | nivel de arriba | 1 201 M | 16 M | 33 M |
| `t$-[t$#]` | nivel de arriba | 1 097 M | 15 M | 31 M |
| `t$+ k` | cualquiera de las dos | 14 M | 14 M | 31 M |

### Qué lo sujeta

`zyquality/cost` `growth/update-local`, ya sin deuda para la VM (la de `zyjs` sigue: [`ZYJS-014`](zyjs.md)).

---

## ZYVM-014 — La VM pierde lo que una función escribe en un parámetro `<~` cuando el argumento es estado de un módulo

**Estado:** **corregido 2026-10-10** — sin decisión: MEM-5 dice que vuelve modificado
**Encontrado por:** una sonda de `<~` (2026-10-10)

```zymbol
// mod/pres.zy
# pres {
    #> { correr, ver }
    datos = [1, 2, 3]

    tocar(a<~) { a$+ 9 }
    correr() { tocar(datos<~) }
    ver() { <~ datos }
}
```

```zymbol
<# ./mod/pres => P
P::correr()
>> P::ver() ¶
```

`zytw` y `zyjs`: `[1, 2, 3, 9]`. **`zyvm`: `[1, 2, 3]`** — la escritura no llega al estado del módulo, sin aviso.

### Causa

Sin localizar con un parche. La escritura de vuelta de un parámetro de salida lleva pares *(parámetro, registro del
llamante)*; cuando el argumento es una global de módulo, su valor está en un temporal cargado con `LoadGlobal`, y
la vuelta escribe en ese temporal, no en la ranura.

### Corrección (2026-10-10)

La causa era la supuesta. Después de la llamada, por cada argumento de salida que es estado de un módulo y no
tiene registro propio, el compilador emite `StoreGlobal(g, temporal)`: lo que la función escribió en el temporal
llega a la ranura.

| programa | antes, VM | ahora, los tres |
|---|---|---|
| `correr()` · `ver()` | `[1, 2, 3]` | `[1, 2, 3, 9]` |
| dos veces | `[1, 2, 3]` | `[1, 2, 3, 9, 9]` |

### Qué lo sujeta

`runtime-modules-scripts/output-argument-that-is-module-state`, ya sin deuda y con un oráculo en Python. Con la VM
de antes da DIVERGE.

---

## ZYVM-015 — La VM lee una variable cuando se ejecuta el operador, no cuando se evalúa el operando: un `<~` posterior cambia lo ya leído

**Estado:** **corregido 2026-10-10** — sin decisión: el orden es de izquierda a derecha
**Encontrado por:** al medir [`GLB-115`](GLOBAL.md), buscando si la pregunta de las ediciones era más general
**Familia:** el eje `evaluation-order` de ZyDDT — *«sub-expressions with effects run left to right»*

```zymbol
inc(a<~) {
    a = a + 10
    <~ 1
}
x = 5
y = x + inc(x<~)
>> y " " x ¶
```

| programa, con `x = 5` | `zytw` | `zyjs` | `zyvm` |
|---|---|---|---|
| `y = x + inc(x<~)` | `6` | `6` | **`16`** |
| `z = inc(x<~) + x` | `16` | `16` | `16` |
| `t = (x, inc(x<~), x)` | `(5, 1, 15)` | `(5, 1, 15)` | **`(15, 1, 15)`** |
| `>> x " " inc(x<~) " " x ¶` | `5 1 15` | `5 1 15` | `5 1 15` |
| `e = d$+ meter(d<~)`, con `meter` que añade `99` | `[1, 2, 3, 1]` | `[1, 2, 3, 1]` | **`[1, 2, 3, 99, 1]`** |

### Causa

Leer una variable local no copia nada: el operando **es** el registro de la variable, y la instrucción lo lee al
ejecutarse — después de que la escritura de vuelta del `<~` lo haya cambiado. En la salida `>>` cada elemento se
emite al evaluarse, y por eso ahí coincide.

### Arreglo propuesto

Cuando un operando ya evaluado es una variable que un operando posterior de la misma expresión recibe como `<~`,
fijar su valor en un temporal al evaluarlo. El compilador lo sabe: el `<~` está escrito en la llamada.

### Corrección (2026-10-10)

La propuesta, tal cual. Al compilar una sentencia el compilador reúne los nombres que **esa** sentencia pasa como
`<~` (`names_written_through_output`, en `zymbol-semantic`); una lectura de uno de esos nombres copia el registro a
un temporal en el momento de evaluarse. El propio argumento de salida no se fija: ése tiene que ser el registro.
Una sentencia que no pasa nada como `<~` —casi todas— se compila igual que antes, sin una instrucción más.

| programa, con `x = 5` | antes, VM | ahora, los tres |
|---|---|---|
| `y = x + inc(x<~)` | `16` | `6` |
| `t = (x, inc(x<~), x)` | `(15, 1, 15)` | `(5, 1, 15)` |
| `e = d$+ meter(d<~)` | `[1, 2, 3, 99, 1]` | `[1, 2, 3, 1]` |
| control: `z = inc(x<~) + x` | `16` | `16` |

### Qué lo sujeta

`runtime-functions-hof/variable-read-before-a-later-operand-writes-it`, ya sin deuda y con un oráculo en Python.
Con la VM de antes da DIVERGE.

---

## ZYVM-016 — Una tupla guardada como estado de un módulo se edita en el sitio: la VM no la protege

**Estado:** **corregido 2026-10-10**, el día en que se encontró — sin decisión: COL-4, *«a tuple cannot be modified — the check is on
the receiver»*
**Encontrado por:** un barrido de tipos × receptor (local, nivel de arriba, estado de módulo) al corregir
[`ZYVM-003`](zyvm.md); los cambios de ese arreglo no lo causaron: la VM de antes daba lo mismo

```zymbol
// mod/fija.zy
# fija {
    #> { probar }
    t = (1, 2, 3)

    probar() {
        t$+ 4
        >> t ¶
    }
}
```

`zytw` y `zyjs`: `cannot modify tuple 't': tuples are immutable`. **`zyvm`: `(1, 2, 3, 4)`.**

| edición, como sentencia, sobre una tupla | local o nivel de arriba, los tres | estado de módulo: `zytw`, `zyjs` | estado de módulo: `zyvm` |
|---|---|---|---|
| `t$+ 4` · `t$-[1]` · `t$- 1` · `t$-- 1` · `t$+[1] 0` · `t$++ 7 8` · `t$-[1..2]` | rechazada | rechazada | **la aplica** |
| `t[1]$~ 9` | rechazada | rechazada | rechazada |
| control: `u = t$+ 4`, que construye | `(1, 2, 3, 4)` | `(1, 2, 3, 4)` | `(1, 2, 3, 4)` |

### Causa

El compilador emite la comprobación (`AssertMutable`) sobre el **registro** del receptor, dentro de un
`if let Ok(r) = ctx.get_reg(nombre)`. El estado de un módulo no tiene registro, así que la comprobación no se
emitía. `$~` se salvaba porque `DeepSetInPlace` se guarda a sí misma.

### Corrección

Para un receptor que es estado de módulo: `LoadGlobal` a un temporal, `AssertMutable`, y el temporal se limpia en
el acto — una referencia que quedara viva haría copiar a la edición que viene después.

### Qué lo sujeta

`runtime-modules-scripts/tuple-held-as-module-state-is-not-edited`, con un oráculo que dice qué imprime cada
línea: tres motores que dejaran pasar la edición coincidirían entre sí. Con la VM de antes da DIVERGE.

---

## ZYVM-017 — `d$- v` y `d$-- v` sobre un diccionario: la VM los rechaza

**Estado:** **corregido 2026-10-10**, el día en que se encontró — sin decisión: lo dice `COLLECTIONS.md`
**Encontrado por:** el mismo barrido de tipos de [`ZYVM-016`](zyvm.md)

```zymbol
d = #(a: 1, b: 2, c: 2)
>> d$- 2 ¶
>> d$-- 2 ¶
```

| | `zytw`, `zyjs` | `zyvm` |
|---|---|---|
| `d$- 2` | `#(a: 1, c: 2)` | **`$- requires an array, tuple, or string, got #(a: Int, b: Int, c: Int)`** |
| `d$-- 2` | `#(a: 1)` | **`$-- requires an array, tuple, or string, got …`** |
| control: `d$-["b"]`, por su dirección | `#(a: 1, c: 2)` | `#(a: 1, c: 2)` |

`zymbol-design/COLLECTIONS.md`: `$-[…]` quita por dirección, *«which leaves `$- value` free to keep meaning "by
value" in both collections»*. Un programa que quita de un diccionario por valor corría en el TW y en el navegador y
fallaba en la VM, que es el futuro motor por defecto.

### Corrección

`ArrayRemoveValue` y `ArrayRemoveAll` reciben el brazo del diccionario: la primera entrada que guarda el valor, o
todas, en orden de inserción — lo que ya hacían el TW y `zyjs`.

Queda una cosa sin tocar, igual en los tres: el mensaje de las otras colecciones dice *«requires an array, tuple,
or string»* y no nombra al diccionario, que sí vale.

### Qué lo sujeta

`runtime-collection-ops/remove-by-value-from-a-dictionary`, con un diccionario de Python como oráculo (también
guarda el orden de inserción). Con la VM de antes da WRONG.

---

## ZYVM-018 — Un parámetro que se llama como el estado del módulo: la VM lo lee del parámetro y lo escribe en el estado

**Estado:** **corregido 2026-10-10**, el día en que se encontró — sin decisión: un parámetro es de su función
**Encontrado por:** revisando el arreglo de [`ZYVM-003`](zyvm.md), que da prioridad al registro local al editar,
contra `store_to_name`, que daba prioridad al estado del módulo al escribir
**Familia:** [`GLB-119`](GLOBAL.md) (la variable de un bucle y el nombre desestructurado, sin decidir) y
[`ZYTW-008`](zytw.md) (el TW, al llamar)

```zymbol
// mod/sombra.zy
# sombra {
    #> { asignar, ver }
    datos = [1, 2, 3]

    asignar(datos) {
        datos = [0]
        <~ datos
    }
    ver() { <~ datos }
}
```

```zymbol
<# ./mod/sombra => S
>> S::asignar([10, 20]) " " S::ver() ¶
```

`zytw` y `zyjs`: `[0] [1, 2, 3]`. **`zyvm`: `[10, 20] [0]`** — la función devuelve el argumento sin tocar y el
estado del módulo queda reemplazado. Sin aviso.

| en una función del módulo, con un parámetro `datos` o `n` | `zytw`, `zyjs` | `zyvm`, antes |
|---|---|---|
| `datos = [0]` · `<~ datos` | `[0]`, estado intacto | `[10, 20]`, estado `[0]` |
| `n = n + 1` · `n += 1` · `<~ n`, con `n = 1` | `3`, estado `100` | `1`, estado `2` |
| `datos[1]$~ 9` · `<~ datos` | `[9, 20]`, estado intacto | `[10, 20]`, estado `[9, 20]` |
| `datos$-[1]` · `<~ datos` | `[20]`, estado intacto | `[10, 20]`, estado `[20]` |
| una lambda de bloque `(n) -> { n = n + 1  <~ n }`, llamada con `5` | `6`, estado `100` | `5`, estado `6` |
| control: `datos$+ 7` · `<~ datos` | `[10, 20, 7]`, intacto | `[10, 20, 7]`, intacto |

### Causa

Las lecturas buscan primero el registro local y después el estado del módulo; `store_to_name`, por donde pasa toda
escritura, buscaba primero el estado del módulo. Un nombre que es las dos cosas se leía de un sitio y se escribía
en otro. `$+` se salvaba porque su camino rápido escribe en el registro.

### Corrección

El contexto de cada función guarda los nombres de sus parámetros —los de una función, los de una lambda—, y
`store_to_name` no escribe en el estado del módulo un nombre que es parámetro.

No se extiende a los demás nombres con registro —la variable de un bucle, un nombre desestructurado—: ahí los
motores no coinciden y hace falta decidir ([`GLB-119`](GLOBAL.md)). Esos casos quedan exactamente como estaban.

### Qué lo sujeta

`runtime-modules-scripts/parameter-named-like-module-state-is-the-function-s-own`, con un oráculo en Python, donde
un parámetro tapa a una global del mismo modo. Con la VM de antes da DIVERGE.

---

## ZYVM-019 — `t[1]$~ f()` sobre una tupla: la VM llama a `f` y después rechaza

**Estado:** **corregido 2026-10-10**, el día en que se encontró — decidido con [`GLB-115`](GLOBAL.md): el receptor
se lee primero
**Encontrado por:** la sonda de [`ZYTW-011`](zytw.md), que cuenta las llamadas

```zymbol
f() {
    >> "llamada" ¶
    <~ 9
}
t = (1, 2)
!? { t[1]$~ f() } :! { >> "rechazada" ¶ }
```

`zytw` y `zyjs`: `rechazada`. **`zyvm`: `llamada`, `rechazada`.**

### Causa

La comprobación de que el receptor no es una tupla se emitía antes de los operandos para todas las ediciones
menos `$~`, que se dejaba a `DeepSetInPlace` — la instrucción que escribe, que corre después de los operandos.

### Corrección

`AssertMutable` se emite para toda sentencia de edición, antes de sus operandos.

### Qué lo sujeta

`runtime-functions-hof/tuple-edit-is-refused-before-its-operand-runs`. Con la VM de antes da DIVERGE.

---

## ZYVM-020 — `n° = …` sobre un nombre que es estado del módulo: la VM le da un registro propio

**Estado:** **corregido 2026-10-10**, el día en que se encontró — sin decisión: es la regla de [`GLB-119`](GLOBAL.md)
**Encontrado por:** la sonda que comparó el TW antes y después de [`ZYTW-010`](zytw.md), que también corrió en la VM
**Familia:** [`GLB-119`](GLOBAL.md) — dar valor a un nombre del módulo escribe su estado, llegue el valor como llegue

```zymbol
# calor {
    #> { despues, ver }
    n = 10

    despues() {
        @ i:1..3 { n° = n + i }
        <~ n
    }
    ver() { <~ n }
}
```

```zymbol
<# ./mod/calor => C
>> C::despues() " " C::ver() ¶
```

| | salida |
|---|---|
| `zytw`, `zyjs` | `16 16` |
| `zyvm`, antes | `3 3` |

La misma función con `n` local da 16 en los tres, y sin la marca (`n = n + i`) también.

### Causa

Una asignación con marca caliente a un nombre **nuevo** le reserva un registro y lo inicia con el elemento neutro
de la operación. «Nuevo» se decidía con `ctx.get_reg(name).is_err()`, y un nombre que es estado del módulo no
tiene registro: se le daba uno, iniciado a cero, la suma corría sobre él y lo que resultaba se escribía en el
estado. Es la mitad de `GLB-119` que aquel arreglo no alcanzó: allí eran los bucles y la desestructuración.

### Corrección

`Statement::Assignment` no hace esa reserva cuando el nombre es estado del módulo y no un parámetro: la
asignación sigue el camino de cualquier otra, que escribe el estado.

### Qué lo sujeta

`runtime-modules-scripts/hot-assignment-to-a-name-that-is-module-state`, con oráculo: las dos marcas, `n°` y `°n`.

---

## ZYVM-021 — Una lambda escrita en una función de un módulo lee el estado del módulo como está, no como lo capturó

**Estado:** **corregido 2026-10-10** — decidido por el autor ese día: la lambda **captura**, como con cualquier otro nombre
**Encontrado por:** la misma sonda, 2026-10-10
**Familia:** [`ZYVM-020`](zyvm.md), [`GLB-119`](GLOBAL.md) — otra forma en que un nombre que es estado del módulo no sigue en la VM el camino de un nombre cualquiera

```zymbol
# captura {
    #> { captura }
    t = [5, 6]

    captura() {
        f = k -> t[k]
        t[1]$~ 500
        <~ f(1)
    }
}
```

```zymbol
<# ./mod/captura => K
>> K::captura() ¶
```

| | salida |
|---|---|
| `zytw`, `zyjs` | `5` |
| `zyvm`, antes | `500` |

Con `t` local a la función —`u = [5, 6]  f = k -> u[k]  u[1]$~ 500  <~ f(1)`— los tres dan `5`: la lambda
capturó el valor que `u` tenía cuando se escribió.

### Qué pasa

En el TW y en `zyjs` una lambda captura por valor lo que nombra de fuera, y el estado del módulo es una de esas
cosas. En la VM un nombre que es estado del módulo no tiene registro (`GLB-119`); lo que se observa es que la
lambda lee lo que la ranura del módulo tiene cuando corre. El camino exacto en el compilador no se ha leído.

### Qué había que decidir

- **captura**, como un local: es lo que hacen dos motores y lo que hace la VM con cualquier otro nombre. La
  lambda es entonces la misma cosa dentro y fuera de un módulo.
- **el estado vivo**: es lo que hace una *función* del módulo, que lee el estado cuando corre. Una lambda
  guardada y llamada más tarde vería lo que el módulo tenga ese día.

### Decisión y corrección (2026-10-10)

El autor: **captura**.

`compile_lambda` busca las variables libres del cuerpo entre los nombres que tienen registro en la función que
la contiene, y un nombre que es estado del módulo no tiene ninguno. Ahora, mientras dura esa búsqueda, los
nombres del estado del módulo cuentan como si lo tuvieran; los que el cuerpo nombra se cargan de la ranura del
módulo **donde la lambda se escribe** y viajan en la clausura como cualquier otra captura. Dentro de la lambda el
nombre es suyo, como un parámetro: lo lee de su registro y lo escribe en su registro — una lambda sólo escribe
los nombres que declara — , también cuando lo asigna antes de leerlo.

Las ocho formas de la celda, que los tres motores contestan igual: lectura después de
editar el estado, escritura dentro de la lambda, lambda que devuelve otra lambda, parámetro que se llama como el
estado, lambda pasada a `$>`, lambda guardada **en** el estado del módulo y llamada desde otra función, y
asignación antes de la lectura.

### Qué lo sujeta

`runtime-modules-scripts/lambda-in-a-module-function-captures-module-state`, con oráculo.

## ZYVM-022 — Lo que devuelve una llamada y se usa una vez sobrevive en su registro temporal: la VM tiene dos arrays donde el tree-walker tiene uno

**Estado:** **corregido 2026-10-19** — deuda conocida desde la v0.0.8 («VM expression temporaries», `IMPL_V008.md`
§ B.1), archivada el 2026-10-11 y corregida por decisión del autor (grupo 3 del plan de cierre,
`interpreter/ROADMAP_V0011_ES.md`: la opción de liberar sólo lo que puede ser una colección, medida antes, y deuda si
costaba más de un 2 % de pasos). Sujeta por `autofree/call-result` de `zyquality/cost`, que pasa
**Encontrado por:** el plan de lanzamiento de la v0.0.10, paso 3.2: el ROADMAP pedía re-medir la deuda de auto-free
antes de reescribirla y esa medición no tenía dónde vivir
**Familia:** [`ZYVM-010`](zyvm.md) (el marco de llamada: reutiliza los temporales por sentencia, y esa reutilización es
justo lo que deja el valor vivo); la deuda hermana, «regiones planas» (`last_use.rs`), no es un hallazgo

```zymbol
big() {
    a = []
    @ i:1..2000000 { a$+ i }
    <~ a
}
x = big()$#
y = big()$#
>> x + y ¶
```

Dos llamadas seguidas; el array de la primera está muerto en cuanto acaba su sentencia, y la segunda podría
construir el suyo en el mismo sitio. Pico de memoria, mediana de tres, descontados los 8,5 MiB de un proceso vacío:

| forma | `zytw` seq/uno | `zyvm` seq/uno |
|---|---:|---:|
| variables con nombre (`autofree/scale`) | 1,00 | 1,00 |
| los dos vivos a propósito (el control) | 2,01 | 2,05 |
| **el resultado de una llamada, usado una vez** | 1,00 | **2,05** |
| una expresión `(a$+ 0)$#` | 1,00 | 0,98 |

En bruto, como lo imprime el arnés: 1,00 y 1,79. En absoluto, el pico de un proceso con un array de 2 000 000 de
enteros es 37,7 MiB en la VM y 235,9 MiB en el tree-walker: **la VM sigue usando unas seis veces menos**, y con la
deuda (68 MiB) todavía gana por 3,4 a 1. Lo que se pierde es la ventaja *relativa* de liberar a tiempo, no la
absoluta.

### Por qué

`emit_auto_free` limpia el registro de una **variable con nombre**. El resultado de `big()` no se liga a ningún
nombre: cae en un registro temporal, y al acabar la sentencia `release_temps` lo devuelve al *pool* sin tocarlo —
«holds whatever its last user left», dice `alloc_temp`. El valor sigue vivo hasta que otro temporal reutilice el
registro, y para entonces la segunda llamada ya ha construido su array dentro de su marco.

El tree-walker no tiene registros: el valor es un `Value` de Rust sin dueño al acabar la expresión, y se suelta
ahí (1,00, medido).

**La prueba de que es eso y no otra cosa** — `ZYMBOL_POISON_TEMPS=1` hace que `release_temps` escriba un entero en
cada temporal al acabar su sentencia, y con él puesto el mismo programa da:

| `zyvm` | `call_seq` | `call_one` | razón |
|---|---:|---:|---:|
| normal | 68,3 MiB | 37,5 MiB | 1,82 |
| `ZYMBOL_POISON_TEMPS=1` | 37,7 MiB | 39,2 MiB | **0,96** |

### Lo que costaría corregirlo, medido

La corrección obvia es la del veneno, siempre: una instrucción por temporal liberado y por sentencia. Contado con
`--count`, la VM ejecuta entre +7,7 % (`ctl_call`: 1 300 015 → 1 400 023 pasos) y +9,1 % (`ctl_arith`: 3 300 015 →
3 600 023) más. Es el precio máximo y es uniforme, no el de un valor grande. Las salidas son tres, y ninguna se ha
tomado:

- **Dejarla**, escribiendo la razón en `alloc_temp`. La VM gana igual en absoluto.
- **Liberar sólo lo que puede ser un agregado**: el compilador lleva un tipo estático por registro (`reg_types`,
  de mejor esfuerzo), y un temporal que es `Int`/`Float`/`Bool` no pesa. Reduce el coste a las llamadas y a las
  expresiones de tipo desconocido; cuánto, no se ha medido.
- **Liberar en la última lectura** (la receta de `IMPL_V008.md` § B.1): la instrucción que consume el temporal por
  última vez lo toma en vez de copiarlo. Es el cambio de asignador de registros que la v0.0.8 describía.

### Corrección (2026-10-19)

La salida elegida, medida en tres pasos con `--count` sobre los 16 programas de `zyquality/bench/big/` contra el mismo
`HEAD` sin el cambio:

| variante | pasos, media geométrica | el peor | `autofree/call-result` |
|---|---:|---:|---:|
| limpiar al acabar la sentencia todo temporal de tipo desconocido | +18,7 % | `loop_mod` +62,5 % | 68 → 39 MiB |
| sólo los que recibieron el resultado de una llamada | +0,45 % | `match_loop` +6,4 % | 68 → 39 MiB |
| …salvo si una instrucción aritmética los leyó después | **+0,05 %** | `nqueens` +0,8 % | 68 → 39 MiB |

La primera era la opción tal como se escribió y quedaba lejos del 2 %: casi todo temporal tiene tipo desconocido, y se
limpiaba en cada vuelta de cada bucle. La segunda es lo que esta ficha describe —el resultado de una llamada—, pero
`acc = acc + classify(i)` pagaba un paso por vuelta en limpiar un número. La tercera es la que quedó: `emit` apunta en
`call_results` el registro que escribe un `Call`, `CallDynamic` o `CallBuiltin`, y lo quita si una instrucción aritmética
lo lee —si corrió, lo que hay es un número; si no, la sentencia ya terminó con un error—; `release_temps` emite un
`LoadUnit` para los que siguen apuntados. Dejar uno sin limpiar sólo cuesta memoria, como antes; nunca da una respuesta
distinta.

### Qué lo sujeta

`autofree/call-result` en `zyquality/cost/cost.toml`, sin `open_finding` desde la corrección: la VM da ×1,01 (39 MiB
contra 39). Los dos programas son `casos/autofree_resultado_uno.zy` y `casos/autofree_resultado_secuencial.zy`.

---

## ZYVM-023 — `s = s "x"` copia el texto entero en cada añadido: construir un texto es cuadrático en la VM

**Estado:** **corregido 2026-10-16** — no cambia ninguna salida. Reproducido ese día sobre `v0.0.11` y archivado
con sus tres casos de `zyquality/cost` como deuda antes del arreglo. Es el primero de la etapa 2
(`interpreter/ROADMAP_V0011_ES.md`, PERF-06), con la recomendación «implementar» que el autor incorporó al plan el
2026-10-14
**Encontrado por:** ZyBigBench (PERF-06), por curva de crecimiento; traído a `zyquality/bench/big/` el 2026-10-14
**Familia:** [`ZYVM-003`](zyvm.md) y [`ZYVM-013`](zyvm.md) — una edición que se escribe en un registro nuevo en vez
de en su receptor; aquí no hay `Rc` con dos dueños, sino un búfer que nunca se reutiliza

```zymbol
s = ""
@ _i:1..32000 { s = s "x" }
>> s$# ¶
```

`zymbol run --count`, la misma forma con el receptor en sus tres sitios posibles:

| receptor | `zyvm` bytes 2 000 → 8 000 | razón | `zytw` |
|---|---:|---:|---:|
| variable del programa | 4,2 MB → 34,5 MB | **8,12** | 1,89 |
| variable local de una función | 4,3 MB → 34,5 MB | **8,11** | 1,76 |
| estado de un módulo | 4,3 MB → 34,6 MB | **7,97** | 1,26 |

A 32 000 añadidos la VM pide 515 MB al asignador para un texto de 32 KB; el tree-walker, 223 KB. Los pasos
crecen ×4,00 exactos: el coste está dentro de una instrucción, en lo que copia. ZyBigBench lo midió en
instrucciones: 128 000 añadidos, 968 M contra 290 M con la mitad.

### Causa

`zymbol-compiler/src/lib.rs`, `compile_binary`: `BinaryOp::Concat` emite `ConcatStr(dst, r_l, r_r)` con `dst` un
temporal nuevo, y la asignación copia después el temporal a la variable. La VM tiene la vía rápida —`ConcatStr`
reutiliza el búfer del operando izquierdo, con `try_into_string`, cuando `dst == a`—, pero el compilador nunca la
alcanza: destino y operando izquierdo no son el mismo registro, así que cada añadido reserva un texto de la longitud
entera y copia el anterior dentro.

### Alcance

Todo programa que construya un texto por partes: un informe, una línea de tablero, un buffer de pantalla. La salida
es idéntica; sólo lo ve una curva.

### Corrección (2026-10-16)

`compile_assignment_inner` reconoce `s = s x y …` —una cadena de `Concat` cuya hoja de más a la izquierda es el
receptor— y emite `ConcatStr(s, s, x)`, `ConcatStr(s, s, y)` sobre el registro de la propia variable, por los mismos
tres caminos que `ConcatBuild` (GLB-118): la variable local, la del programa con su ranura espejo, y el estado de un
módulo. Lo que hubo que cuidar:

- **Izquierda a derecha.** Todos los operandos se evalúan antes del primer añadido, así que ven el `s` con el que
  empezó la sentencia. Un operando que *es* el registro del receptor (`s = s "-" s`) se copia aparte antes.
- **Un `<~` en la misma sentencia** (`r = r escribe(r<~)`) deja la lectura fijada y sigue por el camino de la copia,
  como en ZYVM-013.
- **La ranura.** El estado de un módulo y la variable espejo de un programa guardan una segunda referencia al
  texto, y con dos dueños `try_into_string` copia. `DetachGlobal` soltaba la ranura sólo para agregados; ahora también
  para un texto que comparte búfer con el registro (`ZyStr::shares_buffer`). Si un operando escribió el estado entre
  la lectura y el añadido, la ranura tiene otro texto y no se toca: `mete()` en el fichero del corpus de abajo.

`zymbol run --count`, `bytes` de 2 000 a 8 000 añadidos:

| receptor | antes | ahora |
|---|---:|---:|
| variable del programa | 4,2 MB → 34,5 MB (×8,12) | 2,26 MB → 2,52 MB (×1,12) |
| variable local de una función | 4,3 MB → 34,5 MB (×8,11) | 2,26 MB → 2,53 MB (×1,12) |
| estado de un módulo | 4,3 MB → 34,6 MB (×7,97) | 2,35 MB → 2,61 MB (×1,11) |

Los pasos bajan un 8 % en las dos primeras (sin el `CopyReg` de vuelta) y suben un 8 % en el estado de un módulo
(`DetachGlobal` y la limpieza de temporales del estado). Sin instrucciones de `perf`: `perf_event_paranoid` está en 3
en esta máquina.

`zyquality/corpus/modules_scope/concat_receptor.zy` (con su módulo `concat_receptor_m.zy`) recoge las formas que el
arreglo podía romper: el receptor como operando, un alias que comparte el texto, números, un receptor que no es
texto, una cadena corta que crece, un alias dentro de una función, el estado de un módulo leído antes y después, un
operando que reescribe el estado, una lambda que captura la variable, paréntesis, texto no ASCII y un `<~` en la
misma sentencia. Da la misma salida en los tres motores y con `ZYMBOL_POISON_TEMPS=1`.

### Qué lo sujeta

`growth/concat-local`, `growth/concat-in-function` y `growth/concat-module-state` en `zyquality/cost/cost.toml`, sin
deuda: la razón contada de `bytes` es exacta. Mientras el hallazgo estuvo abierto los tres llevaban
`open_finding = { zyvm = "ZYVM-023" }`, y por él el corredor de `cost/` aprendió a leer `open_finding` en las
razones contadas: hasta entonces ninguna deuda declarada era de `--count`. Una deuda se da por pagada sólo cuando
pasan **todas** las lecturas de su motor, porque un defecto al que el conteo es ciego pasa todas las razones
contadas mientras sigue abierto.

---

## ZYVM-024 — `@ ch:s` recorre la variable, no el texto que tenía al empezar: si el cuerpo reescribe `s`, la VM lee el texto nuevo y, pasado su final, da el carácter 0

**Estado:** **corregido 2026-10-16** — encontrado y corregido el mismo día, antes que PERF-04
**Encontrado por:** la lectura de `compile_foreach_loop` para el arreglo de PERF-04 (`interpreter/ROADMAP_V0011_ES.md`,
etapa 2), cuya receta dice «sobre la cadena que había al entrar al bucle»: hoy no es así
**Familia:** ninguna abierta. Es el aliasing que el camino genérico de ese mismo bucle ya había resuelto para los
diccionarios («Into a FRESH register, not over `r_coll`»), y que el camino del texto no tiene

```zymbol
s = "abcd"
@ ch:s {
    >> ch
    s = "zz"
}
>> " " s ¶
```

| | salida |
|---|---|
| `zytw`, `zyjs` | `abcd zz` |
| `zyvm` | `az` + dos caracteres 0 + ` zz` |

Lo mismo con un texto más largo (`aYZ` donde los otros dicen `abc`) y con uno no ASCII (`ñaaaa` por `ñandú`). Un
arreglo no lo sufre: el bucle tiene su propia referencia.

### Causa

`zymbol-compiler/src/lib.rs`, `compile_foreach_loop`: cuando el iterable es de tipo estático `String`, el bucle
cuenta los caracteres una vez (`StrLen`) y en cada vuelta emite `StrCharAt(item, r_coll, idx)`. Si el iterable es
un nombre, `r_coll` **es** el registro de la variable, así que cada vuelta lee lo que la variable tiene en ese
momento. Y `StrCharAt` contesta `'\0'` a un índice fuera del texto en vez de fallar, por eso el error no se ve.

### Alcance

Un programa que recorre un texto y lo reescribe dentro del bucle —un analizador que consume su entrada, un
autómata—. Un texto al que sólo se le añade al final (`u = u ch`) da lo mismo por casualidad: el prefijo no cambia.
No lo ve ninguna prueba: ningún fichero del corpus reescribía el texto que recorre.

### Qué lo sujeta

`zyquality/corpus/loops/14_foreach_string_snapshot.zy`, con su golden de `zytw`: seis formas —un texto más corto,
uno más largo, uno que crece al final, uno no ASCII, uno dentro de una función y, para comparar, un arreglo—.
Divergía en la VM en tres de ellas.

### Corrección (2026-10-16)

El camino del texto copia el iterable a un registro propio del bucle antes de contar sus caracteres, como ya
hacía el camino genérico. La copia es un incremento del contador de referencias, no del texto. Con
`ZYMBOL_POISON_TEMPS=1` da el mismo golden.

El `'\0'` de `StrCharAt` deja de alcanzarse, pero sigue ahí: PERF-04 sustituye esa instrucción.

---

## ZYVM-025 — `@ ch:texto` busca cada carácter desde el principio del texto: recorrer un texto es cuadrático en la VM

**Estado:** **corregido 2026-10-16** — no cambia ninguna salida. Reproducido ese día sobre `v0.0.11` y archivado
con `growth/foreach-over-text` de `zyquality/cost` como deuda antes del arreglo. Es PERF-04 de la etapa 2 (`interpreter/ROADMAP_V0011_ES.md`), con la
recomendación «implementar» que el autor incorporó al plan el 2026-10-14
**Encontrado por:** ZyBigBench (PERF-04), por curva de crecimiento
**Familia:** [`ZYVM-024`](zyvm.md), la misma instrucción: aquél era *qué* texto lee cada vuelta, éste *cuánto* le
cuesta leerlo

```zymbol
s = ""
@ _i:1..80000 { s = s "ñ" }
k = 0
@ ch:s { ? ch == 'ñ' { k = k + 1 } }
>> k ¶
```

Reloj, una corrida, binario de release:

| texto | n → 4n | `zyvm` | `zytw` |
|---|---|---:|---:|
| «ñ» | 20 000 → 80 000 | 47 ms → 387 ms | 18 ms → 51 ms |
| «ñ» | 80 000 → 320 000 | 399 ms → 5 933 ms (**×14,9**) | 51 ms → 118 ms |
| «x» | 320 000 → 1 280 000 | 1 257 ms → 21 367 ms (**×17**) | 135 ms → 471 ms |

`--count` no lo ve: `steps` crece ×4,00 exacto, porque cada vuelta es **una** instrucción, recorra lo que recorra.

### Causa

`zymbol-vm/src/lib.rs`, `StrCharAt(dst, s, i)`: el bucle de texto pide el carácter `i` en cada vuelta, y la
instrucción lo busca. Con texto ASCII llama antes a `s.is_ascii()`, que recorre el texto entero (a unos 40 GB/s,
por eso tarda en notarse); con texto no ASCII, además, a `s.chars().nth(i)`, que lo recorre hasta `i`.

### Alcance

Todo programa que recorra un texto carácter a carácter: un analizador, un contador, un cifrado. Con texto ASCII
corto no se nota; con un fichero leído entero, sí.

### Qué lo sujeta

`growth/foreach-over-text` en `zyquality/cost/cost.toml`, por reloj y con texto no ASCII, ya sin deuda. Mientras
estuvo abierto sus razones contadas pasaban y el reloj daba `KNOWN` (×14,87), y el corredor no lo dio por pagado:
fue la primera prueba de que una deuda se paga sólo cuando pasan todas las lecturas de su motor.

### Corrección (2026-10-16)

`StrCharAt(dst, s, i)` —el carácter `i`— se sustituye por `StrCharNext(dst, s, cursor)`: el carácter que empieza en
el byte `cursor`, y el cursor avanza tras él. El bucle de texto guarda el cursor en un registro propio junto al
contador de caracteres, que sigue decidiendo cuándo termina, así que `@>` y `@!` no cambian. Cada vuelta es O(1) y
no reserva nada; es seguro porque desde [`ZYVM-024`](zyvm.md) el bucle recorre una copia del texto que nada puede
modificar. Un cursor fuera del texto o en medio de un carácter es un fallo del compilador, y se rechaza en vez de
contestar `'\0'` como hacía `StrCharAt`.

| texto | n | antes | ahora |
|---|---:|---:|---:|
| «ñ» | 320 000 | 5 933 ms | 58 ms |
| «x» | 1 280 000 | 21 367 ms | 207 ms |

Caracteres de uno a cuatro bytes, `@>`, `@!`, un texto vacío y un bucle anidado dan la misma salida en los tres
motores y con `ZYMBOL_POISON_TEMPS=1`.

---

## ZYVM-026 — Un texto cortado donde su tipo no se conoce al compilar: la VM recortaba el rango como antes de D3

**Estado:** **corregido 2026-10-16** — encontrado y corregido el mismo día, al preparar PERF-05 a
**Encontrado por:** la lectura de las instrucciones de corte para PERF-05 a (`interpreter/ROADMAP_V0011_ES.md`):
`ArraySlice` tenía su propia rama para un texto, con el `.max(0).min(len)` que `StrSlice` había dejado en D3
**Familia:** las reglas estrictas de D3 (pasos 4.3 y 4.4) y la revocación de D2 (2026-09-20): un corte que se sale de
la colección se rechaza, y uno escrito de mayor a menor invierte

```zymbol
hasta(s, a, b) { <~ s$[a..b] }
t = "ñandú"
>> hasta(t, 3, 1) " | " t$[3..1] ¶
>> hasta(t, 2, 9) ¶
```

| | `hasta(t, 3, 1)` | `hasta(t, 2, 9)` |
|---|---|---|
| `zytw`, `zyjs`, y la VM con `t$[…]` | `nañ` | `##Index(slice indices out of bounds: [2..9] …)` |
| `zyvm` con un parámetro | vacío | `andú` |

### Causa

El compilador elige la instrucción por el tipo estático: `StrSlice` si sabe que es un texto, `ArraySlice` si no lo
sabe —un parámetro, el resultado de una llamada—. `ArraySlice` llevaba su propia rama para un texto, escrita «para
módulos» antes de D3, con el rango recortado a la longitud y sin dirección. Las dos instrucciones contestaban cosas
distintas al mismo corte.

### Alcance

Toda función que corte el texto que recibe. Un rango bien escrito dentro del texto daba lo mismo, por eso no se
veía; uno invertido o fuera de rango daba un valor plausible en vez del de los otros dos motores.

### Corrección (2026-10-16)

Una función, `str_slice`, con la regla de `StrSlice`, y las dos instrucciones la llaman.

### Qué lo sujeta

`zyquality/corpus/strings/31_slice_in_a_function.zy`: diez cortes, cada uno escrito por un parámetro y, al lado,
sobre el texto directamente. Divergía en la VM en todos los que invierten el rango o se salen del texto.

---

## ZYVM-027 — Una recursión en cola dentro de un módulo no era una llamada en cola en la VM

**Estado:** **corregido 2026-10-16** — encontrado al alinear la llamada en cola para [`GLB-133`](GLOBAL.md)
**Encontrado por:** `C::baja(30000)`, con `baja` recursiva en cola dentro de un módulo: `modulo` en el tree-walker,
`##Depth` en la VM
**Familia:** [`GLB-133`](GLOBAL.md), [`ZYTW-017`](zytw.md)

### Causa

`zymbol-compiler/src/lib.rs`, la regla que emite `TailCall` en un `Statement::Return`: busca la función llamada sólo
en `function_index`, y una función de un
módulo se resuelve por `module_scope`. Dentro de un módulo la búsqueda fallaba y la llamada se compilaba como una
llamada normal.

### Corrección (2026-10-16)

La misma resolución que `compile_call`: `function_index` primero y `module_scope` después.

### Qué lo sujeta

`zyquality/corpus/errors/runtime/depth_tail_calls.zy`, con su módulo `depth_tail_calls_m.zy`.

---

## ZYVM-028 — `s$#`, `s[i]` y un corte recorrían el texto entero cada vez: cuadráticos dentro de un bucle

**Estado:** **corregido 2026-10-17** — es PERF-05 b de la etapa 2 (`interpreter/ROADMAP_V0011_ES.md`), que D8 había
aplazado y el autor metió en la etapa el 2026-10-17, con Python como oráculo: «debemos acercarnos porque no es una
competencia, es una validación»
**Encontrado por:** ZyBigBench (PERF-05), y `gap.py` en instrucciones el 2026-10-17: `str_len` a ×31 de Python a n y
×61 a 2n; `str_slice_small` a ×42 y ×85 — la distancia crecía
**Familia:** [`GLB-130`](GLOBAL.md), que quitó la copia del corte y dejó el recorrido; [`ZYTW-016`](zytw.md), la mitad
del tree-walker, que sigue abierta

### Causa

Una posición de Zymbol cuenta caracteres y un `str` se direcciona por bytes. `s$#` contaba los caracteres en cada
llamada (`is_ascii()` y, si no, `chars().count()`), `s[i]` contaba y luego avanzaba hasta `i`, y un corte contaba para
validar los límites y recorría hasta ellos.

### Corrección (2026-10-17)

El texto del montón de un `ZyStr` guarda su número de caracteres, calculado la primera vez que alguien lo pide
(`char_len`). Un texto cuyo número de caracteres es su longitud es ASCII, y entonces una posición es un byte:
`s[i]` y un corte no recorren nada. El valor detrás de un `Rc` compartido no cambia nunca —escribir en el sitio saca el
`String` de su único dueño y crea un texto nuevo, con el recuento sin calcular—, así que el recuento no puede quedarse
viejo. `ZyStr` sigue ocupando 8 bytes.

Instrucciones (`perf`, mediana de 7), VM, frente a Python:

| operación | antes, n → 2n | ahora, n → 2n |
|---|---|---|
| `str_len` (`m = s$#`, 20 000 veces) | ×31 → ×61 | ×1,2 → ×1,2 |
| `str_slice_small` (2 000 cortes) | ×42 → ×85 | ×2,1 → ×2,1 |

Un texto no ASCII sigue recorriéndose hasta la posición en `s[i]` y en un corte; `s$#` ya no. Eso tiene ficha propia
desde el 2026-10-19, [`GLB-139`](GLOBAL.md), con su caso en `zyquality/cost/`.

### Qué lo sujeta

`zyquality/corpus/strings/32_char_count_kept.zy` —un texto que crece en el sitio leído entre añadidos, un alias que
lo comparte, ASCII y no ASCII— y la prueba `char_len_is_counted_once_and_stays_true` de `zy_str.rs`.

---

## ZYVM-029 — Un bucle contado que acaba en el entero más grande abortaba en la VM al salir

**Estado:** **corregido 2026-10-17** — encontrado al fundir el control del bucle contado en una instrucción, en la
etapa 2 de la v0.0.11
**Encontrado por:** `@ i:9007199254740989..9007199254740991 { … }`: el tree-walker y zymbol.js corren las tres vueltas y
siguen; la VM corre las tres y para con `integer overflow: 9007199254740991 + 1`
**Familia:** [`GLB-135`](GLOBAL.md), el otro defecto del control de un bucle `@` encontrado en la v0.0.11

### Causa

`zymbol-compiler/src/lib.rs`, `compile_range_loop`: al final de cada vuelta el contador oculto avanzaba con `AddInt`
(o `SubInt`) y la comparación con el límite venía después, en la cabecera. `AddInt` comprueba el entero seguro, así
que el paso que iba a sacar el contador del rango desbordaba antes de que nadie mirase el límite. Con un paso mayor
que 1 bastaba con que el último valor estuviese a menos de un paso del máximo.

### Corrección (2026-10-17)

Una instrucción nueva, `RangeStep`, hace el final de la vuelta entero: calcula el siguiente valor en `i64` —los dos
operandos caben en ±(2^53−1), la suma no sale de un `i64`—, lo compara con el límite y sólo lo guarda si vuelve al
cuerpo. Fuera del rango no escribe nada, así que no hay nada que desbordar. Es también lo que pesaba: el control de
cada vuelta eran nueve despachos (la dirección se preguntaba dos veces en cada una) y ahora son dos.

### Qué lo sujeta

`zyquality/corpus/loops/16_range_ends_at_max_int.zy`: hacia arriba, hacia abajo, y con un paso que salta el límite en
los dos sentidos.

---

## ZYVM-030 — Un parámetro que nada lee no tenía registro: la llamada escribía fuera del marco

**Estado:** **corregido 2026-10-17** — encontrado al quitar los `LoadUnit` que preceden a un `Return`, en la etapa 2
de la v0.0.11; está en la v0.0.10 publicada
**Encontrado por:** `f(a, b, c) { <~ a }`, en una build de depuración de la VM: `unsafe precondition(s) violated:
slice::get_unchecked_mut requires that the index is within the slice`, y el proceso aborta. La build de release
contestaba bien, por suerte

### Causa

`zymbol-compiler/src/lib.rs`, `eliminate_dead_code`: cuando quita instrucciones inalcanzables, vuelve a contar los
registros del trozo con las que quedan, y un parámetro que ninguna instrucción lee no está en ninguna. `f` quedaba
con un registro para tres parámetros. `Call`, `CallDynamic` y `TailCall` escriben cada argumento en el marco con
`get_unchecked_mut` / `ptr::write`, sin comprobar límites, así que `b` y `c` iban más allá del final del `Vec`:
dentro de su capacidad casi siempre, pisando memoria que nadie usaba; fuera de ella, el montón. En la v0.0.10 la
escritura era una asignación, que además soltaba lo que hubiese allí.

Hacía falta código inalcanzable para que el recuento corriese —el `LoadUnit` + `Return` implícito tras un `<~`
final lo es siempre— y un parámetro sin leer, que sólo provoca un aviso.

### Corrección (2026-10-17)

Un trozo nunca tiene menos registros que parámetros.

### Qué lo sujeta

La prueba `a_frame_holds_every_parameter_even_one_nothing_reads` de `zymbol-compiler/tests/compile_smoke.rs`, que
falla sin la corrección (`f: 1 registers for 3 parameters`), y `zyquality/corpus/functions/parametro_sin_leer.zy`, el
programa, que sólo una build de depuración ve fallar.

## ZYVM-031 — El ejecutable de `zymbol build` no tenía `std/net` ni `std/db` aunque el `zymbol` que lo construía sí

**Estado:** **abierto** — encontrado el 2026-10-20 al preparar 3.1 de la v0.0.11, leyendo quién construye una VM. Lo
introdujo la propia rama `v0.0.11`, nunca publicada: `std/db` desde D4 (`interpreter` del 2026-10-19) y `std/net` desde
la build compacta (`17bfdb8`, 2026-10-20)
**Encontrado por:** leer `zymbol-standalone/src/lib.rs`, `write_cargo_toml`, y comprobarlo con dos programas

### Reproducción

Con un `zymbol` de la rama compilado `cargo build --release --features db`:

```text
$ cat nethead.zy
<# std/net => net
r = net::head("http://127.0.0.1:1/")
>> r ¶
$ zymbol run nethead.zy            # y --tw
#0
$ zymbol build nethead.zy -o nethead && ./nethead
Runtime error: std/net is not available in this build (compiled without HTTP support)

$ cat dbconn.zy
<# std/db => db
c = db::connect("sqlite", "Driver=NoSuchDriver")
>> "reached" ¶
$ zymbol run dbconn.zy
reached
$ zymbol build dbconn.zy -o dbconn && ./dbconn
Runtime error: std/db is not available in this build (compiled without ODBC support)
```

`net::head` contra un puerto cerrado contesta `#0` sin red, así que el primero es determinista.

### Causa

`zymbol build` compila el programa con el compilador del propio `zymbol` y genera un proyecto de Cargo que depende de
`zymbol-vm` por ruta, **sin features**: `zymbol-vm = { path = "…" }`. El compilador tiene las del binario que lo
lleva —Cargo las une—, la VM generada sólo las suyas por defecto, que son `[]` desde D4. El compilador emite los ids de
`std/net` y `std/db`, y la VM del ejecutable cae en el `net_dispatch` / `db_dispatch` que existe para lo inalcanzable.
Hasta D4 `db` estaba en los defectos de `zymbol-vm`, y `ureq` era obligatorio en ella hasta `17bfdb8`; por eso antes
funcionaba. Nada de la puerta ejecuta `zymbol build` con un programa que importe uno de los dos.

### Corrección prevista

Que el proyecto generado pida para `zymbol-vm` las mismas features que tiene el compilador que produjo su bytecode:
`zymbol-standalone` gana `http` y `db`, que encienden las de su `zymbol-compiler` y que el CLI le pasa, y
`write_cargo_toml` las escribe.

