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
