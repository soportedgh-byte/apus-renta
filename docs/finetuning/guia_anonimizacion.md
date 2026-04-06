# Guia de Anonimizacion de Datos — Ley 1581/2012

**CecilIA v2 — Contraloria General de la Republica de Colombia**
**Sprint 9 | Abril 2026**

---

## 1. Marco Legal

La anonimizacion de datos en CecilIA v2 cumple con:

- **Ley 1581 de 2012**: Regimen general de proteccion de datos personales
- **Decreto 1377 de 2013**: Reglamentacion parcial de la Ley 1581
- **Ley 1712 de 2014**: Transparencia y acceso a informacion publica
- **Circular 002 de 2015 SIC**: Directrices sobre tratamiento de datos personales

## 2. Tipos de Datos Protegidos

El sistema de anonimizacion de CecilIA detecta y reemplaza:

| Tipo de dato | Patron | Reemplazo |
|-------------|--------|-----------|
| Cedulas de ciudadania | `\d{6,10}` con contexto | `[CEDULA_XXXX]` |
| NIT | `\d{9}-\d` | `[NIT_XXXX]` |
| Correos electronicos | `email@dominio.com` | `[EMAIL_XXXX]` |
| Telefonos | `+57 3XX...`, `(601)...` | `[TELEFONO_XXXX]` |
| Nombres propios | Deteccion por contexto | `[PERSONA_XXXX]` |
| Direcciones | Calle, Carrera, Avenida... | `[DIRECCION_XXXX]` |
| Cuentas bancarias | Numeros de cuenta | `[CUENTA_XXXX]` |

## 3. Proceso de Anonimizacion

### 3.1 Anonimizacion automatica

```python
from app.finetuning.dataset_builder import anonimizar

texto_original = "El senor Juan Carlos Perez, cedula 1.234.567, domiciliado en Calle 45 # 12-34, Bogota."
texto_anonimizado = anonimizar(texto_original)
# Resultado: "El senor [PERSONA_A1B2], cedula [CEDULA_C3D4], domiciliado en [DIRECCION_E5F6], Bogota."
```

### 3.2 Anonimizacion con control granular

```python
from app.utils.anonimizacion import anonimizar_texto

resultado = anonimizar_texto(
    texto,
    anonimizar_cedulas=True,
    anonimizar_nit=True,
    anonimizar_emails=True,
    anonimizar_telefonos=True,
    anonimizar_nombres=True,
    anonimizar_direcciones=True,
    anonimizar_cuentas=True,
)

print(f"Texto: {resultado.texto_anonimizado}")
print(f"Reemplazos: {resultado.total_reemplazos}")
```

### 3.3 En el pipeline de dataset

La anonimizacion se aplica automaticamente al construir el dataset:

```python
from app.finetuning.dataset_builder import construir_dataset

# Los ejemplos se anonimizan antes de escribir el JSONL
stats = construir_dataset(ruta_salida="dataset_anonimizado.jsonl")
```

## 4. Pseudonimos Deterministas

El sistema genera pseudonimos deterministas: el mismo dato de entrada siempre produce el mismo pseudonimo. Esto preserva la coherencia interna del texto (si "Juan Perez" aparece 3 veces, las 3 se reemplazan por el mismo `[PERSONA_A1B2]`).

## 5. Excepciones

**NO se anonimizan:**

- Nombres de entidades publicas (ministerios, contralorias, etc.)
- Nombres de normas y leyes
- Nombres de cargos publicos genericos
- Datos ya publicados en fuentes oficiales (SECOP, BREF)

## 6. Verificacion Post-anonimizacion

Antes de usar el dataset para entrenamiento:

1. Revision manual de una muestra aleatoria (10% del dataset)
2. Busqueda de patrones de cedula/NIT que pudieron escapar
3. Verificacion de que el texto sigue siendo coherente
4. Confirmacion de que no se perdio informacion tecnica relevante

## 7. Registro de Auditoria

Cada operacion de anonimizacion genera un log:

```
2026-04-05 10:30:15 | cecilia.finetuning.dataset | DEBUG | Anonimizados 5 items PII en texto de 432 caracteres
```

## 8. Responsabilidades

- **Equipo tecnico**: Mantener y mejorar los patrones de deteccion
- **Oficial de datos**: Aprobar el dataset antes de su uso en entrenamiento
- **Auditores**: Validar que la anonimizacion no afecta la utilidad de los ejemplos

---

*Documento generado por el equipo tecnico CecilIA — CD-TIC-CGR*
