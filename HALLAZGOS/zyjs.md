# Hallazgos — `zyjs` (motor del navegador)

> Un hallazgo entra aquí cuando el runner nombra a `zyjs` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

---

## ZYJS-001 — El parser se traga cualquier token que no reconoce y lo convierte en `##_`

**Estado:** abierto — pendiente de tu veredicto
**Encontrado por:** `refusal/assign-no-rhs`, celda del eje `axes/refusal.toml`
**Familia:** `DM-06` (cerrada el 2026-08-18), misma causa de fondo en otro sitio

### Qué se observa

```zymbol
x = =
```

| motor | veredicto | qué dice |
|---|---|---|
| `zytw` | `error/static` | `error: expected expression, found Assign` |
| `zyvm` | `error/static` | `error: expected expression, found Assign` |
| `zyjs` | **`warn`** | `warning: unused variable 'x'` — y el programa corre entero |

El eje exige `expect = "error"`. `zyjs` es el único que no lo alcanza.

### Causa

`web/src/zymbol/zymbol.js:2548`, las dos últimas líneas de `parsePrimary`:

```js
    this.adv();
    return { type: 'Literal', kind: 'unit' };
```

Es un cajón de sastre: **todo token que ninguna de las ramas anteriores reconoce
se consume y se devuelve como literal Unit**. `x = =` no falla porque el `=`
sobrante se convierte en `##_`, la asignación queda bien formada, y lo único que
queda es que `x` no se usa.

No hace falta para el literal `##_`, que tiene su propia rama explícita
**35 líneas más arriba**, en `zymbol.js:2420`:

```js
    if (t.type === 'UNIT')  { this.adv(); return { type: 'Literal', kind: 'unit' }; }
```

Así que el cajón no construye nada: sólo se traga.

### Alcance

No es del lado derecho de una asignación. Es de **cualquier posición de
expresión**. Seis sondas, `zymbol 0.0.9`, todas rechazadas por los dos motores
Rust y todas aceptadas por `zyjs`:

| programa | `zytw` / `zyvm` | `zyjs` |
|---|---|---|
| `x = =` | `expected expression, found Assign` | corre, avisa de `x` |
| `x = ,` | `expected expression, found Comma` | corre, avisa de `x` |
| `x = )` | `expected expression, found RParen` | corre, avisa de `x` |
| `x = ]` | `expected expression, found RBracket` | corre, avisa de `x` |
| `x = }` | `expected expression, found RBrace` | corre, avisa de `x` |
| `x = 1 + =` | `expected expression, found Assign` | corre, avisa de `x` |

Y en posición de salida el programa **imprime y sigue**:

```zymbol
>> (= ) ¶
>> "sigue" ¶
```

`zyjs` escribe una línea en blanco y luego `sigue`, y sale con 0. Los dos motores
Rust lo rechazan.

Esto es, muy probablemente, el mecanismo de fondo de toda la familia
*«el motor del navegador acepta una gramática más amplia que los otros dos»*.
`DM-06` se cerró estrechando `parseOutput` de `parseExpr` a `parseAdditive`, que
era correcto para aquel sitio y **no toca esta causa**: el estrechamiento decide
qué gramática se invoca, y el cajón está por debajo, en el fondo de
`parsePrimary`.

### Arreglo propuesto

Sustituir las dos líneas por el error que ya se lanza en el resto del fichero:

```js
    throw new ZyStaticError(`expected expression, found ${t.type}`, t.line);
```

**Dirección: estrechar `zyjs`**, la misma que `DM-06`. El motivo es el mismo que
allí: los dos motores Rust comparten el parser, así que ampliar los otros dos
significa cambiar el lenguaje, y el lenguaje ya decidió que esto es un error.

⚠ **Riesgo, y es el que hundió el primer intento de `DM-06`.** Al estrechar sin
más, `>> 1 == 1 ¶` pasó a imprimir `11` — un resultado *silenciosamente
equivocado*, peor que el bug original. Aquí puede pasar lo mismo por el otro
lado: si alguna ruta del parser depende hoy de que el cajón devuelva `Unit` en
vez de fallar, quitarlo la romperá. **No se implementa sin correr el eje
`refusal` completo más el corpus de `web/` detrás.**

### Qué lo sujeta

`refusal/assign-no-rhs`, celda generada de `axes/refusal.toml`, con
`expect = "error"`. Hoy pone el gate en rojo con `WRONG` y encamina aquí.

Las otras cinco formas de la tabla de alcance **no son celdas todavía**. Cuando
se decida el arreglo van al mismo eje, porque una causa raíz con seis síntomas y
una sola celda es una causa que vuelve por cualquiera de los otros cinco.
