# Hallazgos — `zyvm` (VM de registros)

> Un hallazgo entra aquí cuando el runner nombra a `zyvm` como el motor que
> incumple. La regla y el formato están en [`INDICE.md`](INDICE.md).

**Ninguno abierto.** Uno cerrado está sujeto por una chincheta:

| chincheta | qué sujeta |
|---|---|
| [`../cases/pin/DM-02_array_equality.zy`](../cases/pin/DM-02_array_equality.zy) | `DM-02` — `==` entre arrays daba `#0` sólo en la VM. Cerrada el 2026-08-18 |

La VM es el motor con más entradas atribuidas en el sondeo de `Divergente_ES`
después de `zyjs` (seis: `DM-02`, `03`, `08`, `16`, `21`, `24`), y es **el futuro
motor por defecto**. Las otras cinco no están sujetas por nada que se ejecute.
