# Hallazgos — índice y regla de encaminamiento

> **Qué es este documento.** Dónde se escribe cada cosa que ZyDDT encuentra, y
> por qué hay un fichero por motor en vez de uno solo.
>
> **Idioma.** Español, como el resto de bugs, huecos, errores e ideas del
> proyecto. El código y su documentación siguen en inglés (`CLAUDE.md`).
>
> **Qué no es.** No es `Divergente_ES/`. Aquello fue un **sondeo**: 106 sondas
> escritas a mano contra las expectativas de la industria, ejecutadas una vez y
> reverificadas tres veces. Esto es la capa **permanente**: cada hallazgo de aquí
> lo produjo una celda o una chincheta que se vuelve a ejecutar en cada commit.
> Se cruzan por referencia, no se fusionan.

---

## 0. Estado — 2026-08-30

**Los nueve hallazgos abiertos están corregidos.** Los ejes declarados van
394 de 394 celdas en verde; las 157 rojas del 2026-08-29 son cero.

Y la validación contra las aplicaciones LDV, hecha después, abrió **seis más**:
**nueve más, todos corregidos**: `ZYJS-007`, `ZYJS-009`, `ZYJS-010`,
`ZYJS-011` y [`GLB-001`](GLOBAL.md) … [`GLB-005`](GLOBAL.md). Tres de ellos
necesitaron una decisión del autor, y las tres se tomaron con la medición
delante — la más cara, `GLB-005`, resultó valer **un fichero de 84**.

| fichero | abiertos | corregidos |
|---|---:|---:|
| [`zytw.md`](zytw.md) | 0 | 0 |
| [`zyvm.md`](zyvm.md) | 0 | 2 |
| [`zyjs.md`](zyjs.md) | 0 | 10 |
| [`GLOBAL.md`](GLOBAL.md) | 0 | 6 |

Los seis dicen lo mismo sobre el método: **una aplicación completa encuentra lo
que ningún corpus puede**, porque un corpus se escribe un fichero cada vez y
estos defectos necesitan que dos partes de un programa se estorben — dos módulos
que comparten un nombre de alias, una variable local que se llama como la
función que la produce, un acumulador escrito con el `°` del lado que el corpus
no usa.

Tres decisiones de diseño las desbloquearon, y las tres son del autor:

1. **`&&` y `||` sobre no booleanos son un error**, en los tres motores. No era
   una decisión nueva: la v0.0.9 ya lo había resuelto para el especificador de
   bucle —*no hay truthiness*— y esto es la misma regla en otro operador.
2. **Las tuplas no se ordenan.** `(1, 2) < (3, 4)` se rechaza. La tupla es
   posicional y heterogénea; `==` no se toca.
3. **Un diagnóstico nombra tipos, no valores.** `String and Char`, no
   `String("ab") and Char('c')`. Es la única forma que los tres motores pueden
   emitir siempre, y de paso cierra [`ZYJS-006`](zyjs.md) por construcción.

Lo que **no** estaba en ninguna ficha y salió de aplicarlas:

- el cortocircuito de la VM decidía por truthiness, así que `0 && #1` seguía
  contestando `#0` con la instrucción ya corregida (nace `RequireBool`);
- `zyjs` acertaba la salida encadenada `>> a >> b ¶` **por accidente**, apoyada
  en el cajón de `parsePrimary`: quitarlo puso 18 ficheros del corpus en rojo de
  golpe y obligó a implementar la regla de verdad;
- los operadores **unarios** de `zyjs` no comprobaban nada: `-"a"` daba `NaN` y
  `!7` daba `#0`. Lo encontró una chincheta al ejecutarse, no una lectura.

### Y lo que sólo apareció al validar contra las aplicaciones LDV

Los 394 verdes, el corpus de 661 y los 222 ejemplos no lo vieron; una aplicación
de verdad, sí. Es `LDV.md` § 1 en dos líneas.

- **`ZYJS-007`** (corregido): el lexer de `zyjs` continuaba un identificador con
  dígitos **ASCII** donde Rust usa `is_alphanumeric()`. Chaturanga está escrito
  en sánscrito y nombra variables como `कार्यस्थितिः२`; el fichero corría aquí con
  un parseo equivocado, correctamente bajo los dos motores Rust, y el cajón de
  `ZYJS-001` era lo que lo tapaba. Ningún fichero del corpus nombra así.
- **[`GLB-001`](GLOBAL.md)** (corregido): se archivó primero como `ZYJS-008`
  leyendo el síntoma —`zyjs` rechaza lo que los dos motores Rust aceptan— y la
  lectura estaba **al revés**. `zyjs` tenía razón: el analizador semántico de
  Rust **no descendía al operando de un operador `$`**, así que no comprobaba
  nada escrito ahí dentro. Al arreglarlo aparecieron cuatro llamadas de la suite
  de Chaturanga a las que les faltaba la marca `<~`, y las cuatro estaban dentro
  de un `$#`: el hueco no dejó errores al azar, los dejó **con su forma**.
- **`ZYJS-009`** (corregido): `alias::f()` dentro de un módulo resolvía con la
  tabla de alias **del llamante**. Ámbito dinámico. Hace falta que dos módulos
  distintos compartan un nombre de alias, y eso no lo hace ningún fichero del
  corpus — un corpus se escribe un fichero cada vez. Con el arreglo, **la suite
  entera de Chaturanga pasa también en `zyjs`**, y con ella la de GO y la de
  serpiente.

Las tres comparten una lección sobre el denominador: `project/apps.toml` excluye
a `zyjs` de las suites de aplicación **a propósito** —son programas de línea de
órdenes— así que ese cruce no lo recorre ningún gate. Comprobarlo aquí exigió
comparar `zyjs` **contra su propia versión anterior**, fichero a fichero, que es
el único instrumento que había.

Y una sobre el encaminamiento: `ZYJS-008` se archivó contra el motor equivocado
porque no lo produjo el runner sino una lectura, y § 1 dice que el motor lo nombra
el runner. Cuando no hay runner que lo diga, **«el que se sale» no es lo mismo
que «el que está mal»** — y en una pareja que comparte analizador, el que se sale
es justamente el que mira.

---

## 1. La regla

> Un hallazgo se archiva contra **el motor que tiene que cambiar**, y ese motor
> lo nombra el runner, no una lectura.

`zyddt axis` compara la respuesta de cada motor contra la categoría que el eje
exige (`expect`), **por motor y en toda salida, incluida una divergencia**:

```text
WRONG       refusal/assign-no-rhs  an assignment whose right-hand side is missing
    zytw               error/static           cumple   expect=error
    zyvm               error/static           cumple   expect=error
    zyjs               warn                   INCUMPLE expect=error
    → HALLAZGOS/zyjs.md
```

Esa última línea es el encaminamiento, y sale de la ejecución. Antes el informe
decía sólo `DIVERGE`, que es un hecho sobre **una pareja** y no se archiva en
ningún sitio: «difieren» no dice quién está mal.

### Cuando el eje no tiene `expect`, el encaminamiento lo pone una lectura

Y hay que decir cuál. Un eje puramente diferencial —`operator` es el primero
grande— no declara ninguna categoría, a propósito: escribir la respuesta
correcta de 252 combinaciones sería inventarla (CHARTER § 8.2). Sin `expect` el
runner sólo puede decir `DIVERGE`, que por § 3 encamina a `GLOBAL.md`.

Las seis entradas que salieron del eje `operator` el 2026-08-29 **no** están
todas allí, y la razón es que en cinco de ellas la lectura sí encuentra un
culpable, y encontrarlo es información que se perdería archivándolas juntas:

| entrada | por qué a un fichero de motor |
|---|---|
| `ZYVM-001` | los dos motores Rust emiten **el mismo aviso** y luego uno para y el otro no: el desacuerdo no está en ver el problema, está en qué se hace después |
| `ZYVM-002` | `zytw` y `zyjs` dicen lo mismo; la VM es la que se sale |
| `ZYJS-004` | canal, no contenido: el texto es el correcto en los tres, y sólo uno lo pone en stdout |
| `ZYJS-005` | dos motores avisan, el tercero no tiene la comprobación |
| `ZYJS-006` | el diagnóstico enseña valores del anfitrión JavaScript; ningún otro motor puede tener ese defecto |
| `GLOBAL-001` | **se quedó**: los tres redactaban distinto y ninguno era la referencia. Lo resolvió una decisión del autor, no una lectura del runner |

La regla que sale de eso: *cuando el runner dice `DIVERGE`, el fichero lo elige
quien escribe el hallazgo, y el hallazgo tiene que decir por qué ese fichero.*
Si no puede decirlo, es `GLOBAL.md` — que es lo que significa «sin culpable
único», no «sin culpable evidente».

---

## 2. Por qué un fichero por motor

Porque es donde caen. Clasifiqué las 26 entradas `DM` de
`Divergente_ES/INDICE.md` leyendo su descripción de una línea:

| culpable | entradas | cuántas |
|---|---|---:|
| `zyjs` solo | DM-04, 06, 07, 12, 20, 22, 25 | **7** |
| `zyvm` solo | DM-02, 03, 08, 16, 21, 24 | **6** |
| `zytw` solo | DM-01, 15, 19, 26 | **4** |
| la pareja Rust | DM-23 | 1 |
| los tres difieren, sin culpable único | DM-05, 09, 13, 17 | 4 |
| dos mal, de formas distintas | DM-10, 14, 18 | 3 |
| reclasificada a `DI` | DM-11 | 1 |

**17 de 25 vivas tienen un solo culpable** — el 68 %. Tu intuición es correcta:
la mayoría son de motor, y un fichero por motor es la vista que se lee cuando se
va a arreglar uno.

---

## 3. Por qué `GLOBAL.md` no es un cajón de sastre

Es la tentación obvia —«lo que no encaje, ahí»— y sería un error, porque esa
carpeta tiene **una clase con mecanismo de descubrimiento propio**:

> **Los tres coinciden, y los tres están mal.**

Un diferencial no puede verla nunca: tres motores equivocados igual coinciden
perfectamente. Sólo la encuentra un **oráculo** (una implementación en otro
lenguaje) o un **`expect`** (la categoría que la forma debe alcanzar). Ya existe
en el registro: `DM-17` — *«cada motor inventa una respuesta distinta, y las tres
mal»*.

Y hay un riesgo concreto que justifica separarla: `zytw` y `zyvm` comparten
lexer, parser y analizador semántico, y `zyjs` se portó a mano de ellos. Un
error heredado por los tres **no es improbable, es lo esperable**, y es
exactamente lo que ninguna de las dos vistas por motor mostraría.

Van a `GLOBAL.md`:

- los tres coinciden y el oráculo o el `expect` dicen que la respuesta está mal;
- los tres difieren entre sí (no hay un motor que se salga: se salen todos);
- el culpable es una pareja, no un motor (`DM-23`).

---

## 4. Los ficheros

| fichero | qué guarda |
|---|---|
| [`zytw.md`](zytw.md) | hallazgos cuyo culpable es el tree-walker |
| [`zyvm.md`](zyvm.md) | hallazgos cuyo culpable es la VM de registros |
| [`zyjs.md`](zyjs.md) | hallazgos cuyo culpable es el motor del navegador |
| [`GLOBAL.md`](GLOBAL.md) | sin culpable único — § 3 |

Las otras dos superficies (el resaltador del playground y la gramática de VS
Code, `CHARTER.md` § 4) **no tienen fichero todavía**, porque ZyDDT aún no las
ejecuta. Cuando las ejecute, `highlight.md` y `tmgrammar.md` — no antes: un
fichero vacío esperando enseña que la ausencia de hallazgos es un estado normal,
y aquí significa que nadie ha mirado.

---

## 5. Numeración — **pendiente de tu visto bueno**

Propuesta: el identificador lleva el motor, para que el fichero y el número
digan lo mismo.

```text
ZYJS-001    ZYVM-001    ZYTW-001    GLB-001
```

**No reutilizo la serie `DM-NN`** a propósito, y esta es la parte que decides tú.
El argumento para no hacerlo: `DM` es la numeración de `Divergente_ES`, que es un
sondeo cerrado y reverificado con fechas; meter entradas nuevas ahí rompe la
propiedad que lo hace valioso —que sus 30 entradas son lo que se midió aquellos
tres días—. El argumento en contra, que también es real: dos espacios de
identificadores para la misma clase de cosa obligan a mirar en dos sitios.

Si prefieres una serie única, el cambio es renombrar las cabeceras; nada del
runner depende del formato del identificador.

Un hallazgo que además merezca entrar en `Divergente_ES` lleva las dos
referencias cruzadas, y lo dice en su cabecera.

---

## 6. Qué lleva una ficha

Fijo, para que se puedan leer en diagonal:

```markdown
## ZYJS-001 — <una línea que diga qué pasa>

**Estado:** abierto | corregido AAAA-MM-DD | desestimado
**Encontrado por:** <la celda o chincheta de ZyDDT que lo produce>
**Familia:** <DM-NN u otro hallazgo, si lo hay>

### Qué se observa      ← salida literal de los tres motores
### Causa               ← fichero y línea, o «sin localizar»
### Alcance             ← qué más rompe la misma causa
### Arreglo propuesto   ← y por qué en esa dirección
### Qué lo sujeta       ← la celda que se pone en rojo si vuelve
```

**«Arreglo propuesto» es propuesta, no decisión.** Ninguna ficha se implementa
sin que la valides: implementar, deprecar o desestimar es tuyo.
