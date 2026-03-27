# GeoQueryCLI

Herramienta de línea de comandos para consultar, validar y exportar archivos GeoJSON desde la terminal. Desarrollada en Python puro, sin dependencias externas como parte de un proyecto de clase.

---

## Requisitos

- Python 3.7 o superior
- No requiere instalar librerías adicionales

Verifica tu versión de Python:

```bash
python3 --version
```

---

## Estructura del proyecto

```
GeoQueryCLI/
├── GeoQuery.py          # Script principal
└── sonsonate.geojson    # Archivo de datos de ejemplo
```

---

## Uso general

```bash
python3 GeoQuery.py [OPCION] <archivo.geojson>
```

---

## Comandos disponibles

### `--count`
Cuenta el total de features en el archivo.

```bash
python3 GeoQuery.py --count sonsonate.geojson
```

---

### `--list`
Lista todos los features con su nombre y coordenadas.

```bash
python3 GeoQuery.py --list sonsonate.geojson
```

---

### `--info <nombre>`
Muestra todas las propiedades y la geometría de un feature específico.

```bash
python3 GeoQuery.py --info Izalco sonsonate.geojson
python3 GeoQuery.py --info "San Julián" sonsonate.geojson
```

> Si el nombre contiene espacios, escríbelo entre comillas.

---

### `--filter <campo>=<valor>`
Filtra features según el valor de un campo en `properties`. Detecta automáticamente el tipo de dato (booleano, número o texto).

```bash
python3 GeoQuery.py --filter categoria=ciudad sonsonate.geojson
python3 GeoQuery.py --filter es_cabecera=true sonsonate.geojson
python3 GeoQuery.py --filter poblacion=71541 sonsonate.geojson
```

---

### `--stats <campo>`
Calcula estadísticas de un campo numérico: suma, promedio, máximo, mínimo, top 3 y bottom 3.

```bash
python3 GeoQuery.py --stats poblacion sonsonate.geojson
python3 GeoQuery.py --stats area_km2 sonsonate.geojson
```

---

### `--sort <campo>`
Ordena los features por un campo numérico. Por defecto muestra de mayor a menor. Usa `--asc` para orden inverso.

```bash
python3 GeoQuery.py --sort poblacion sonsonate.geojson
python3 GeoQuery.py --sort area_km2 --asc sonsonate.geojson
```

---

### `--summary`
Muestra un resumen del archivo: total de features, tipos de geometría presentes y descripción de cada campo (tipo de dato, valores únicos, nulos).

```bash
python3 GeoQuery.py --summary sonsonate.geojson
```

---

### `--validate`
Verifica que el archivo cumpla con la estructura RFC 7946. Revisa que cada feature tenga `type`, `geometry` y `properties` válidos, y que las coordenadas estén dentro del rango correcto.

```bash
python3 GeoQuery.py --validate sonsonate.geojson
```

---

### `--export <campo>=<valor> --output <salida.geojson>`
Filtra features y guarda el resultado en un nuevo archivo GeoJSON válido.

```bash
python3 GeoQuery.py --export categoria=ciudad --output ciudades.geojson sonsonate.geojson
python3 GeoQuery.py --export es_cabecera=true --output cabeceras.geojson sonsonate.geojson
```

---

### `--cabeceras`
Lista los features que tienen el campo `es_cabecera` en `true`.

```bash
python3 GeoQuery.py --cabeceras sonsonate.geojson
```

---

## Estructura del archivo GeoJSON

El archivo debe seguir el estándar **RFC 7946**. La estructura mínima requerida es:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-89.7285, 13.7196]
      },
      "properties": {
        "municipio": "Sonsonate"
      }
    }
  ]
}
```

### Reglas importantes del estándar

| Regla | Detalle |
|---|---|
| El archivo raíz debe ser `FeatureCollection` | Es el contenedor de todos los features |
| Cada elemento debe ser de `type: "Feature"` | No se admiten geometrías sueltas en la colección |
| `geometry` y `properties` son obligatorios | Pueden ser `null` pero deben estar presentes |
| Las coordenadas van como `[longitud, latitud]` | Primero longitud, luego latitud (no al revés) |
| El sistema de referencia es WGS84 (EPSG:4326) | Es el único permitido en RFC 7946 |
| Longitud válida: entre -180 y 180 | |
| Latitud válida: entre -90 y 90 | |

### Tipos de geometría válidos

```
Point              → un punto
MultiPoint         → varios puntos
LineString         → una línea
MultiLineString    → varias líneas
Polygon            → un polígono (área cerrada)
MultiPolygon       → varios polígonos
GeometryCollection → mezcla de geometrías
```

### Estructura del archivo de ejemplo `sonsonate.geojson`

Cada feature representa un municipio del departamento de Sonsonate, El Salvador, con los siguientes campos en `properties`:

| Campo | Tipo | Descripción |
|---|---|---|
| `municipio` | string | Nombre del municipio |
| `codigo` | string | Código municipal (4 dígitos) |
| `poblacion` | integer | Población aproximada |
| `area_km2` | float | Superficie en kilómetros cuadrados |
| `categoria` | string | `"ciudad"` o `"pueblo"` |
| `es_cabecera` | boolean | `true` si es cabecera departamental |

---

## Errores comunes

**El archivo no se encuentra**
```
Error: Archivo 'datos.geojson' no encontrado.
```
Verifica que el nombre del archivo y la ruta sean correctos. Linux distingue mayúsculas de minúsculas.

**JSON inválido**
```
Error: El archivo no es JSON válido.
```
Abre el archivo en un editor y busca comas o llaves faltantes.

**Tipo raíz incorrecto**
```
Error: Se esperaba type='FeatureCollection' (RFC 7946).
```
El archivo debe tener `"type": "FeatureCollection"` en la raíz. Un `Feature` suelto no es válido como archivo completo.

**Campo numérico no encontrado**
```
Error: El campo 'x' no existe o no es numérico.
```
Usa `--summary` para ver los campos disponibles y sus tipos.

---

## Referencia rápida

```bash
python3 GeoQuery.py --count     archivo.geojson
python3 GeoQuery.py --list      archivo.geojson
python3 GeoQuery.py --info      "Nombre" archivo.geojson
python3 GeoQuery.py --filter    campo=valor archivo.geojson
python3 GeoQuery.py --stats     campo_numerico archivo.geojson
python3 GeoQuery.py --sort      campo_numerico archivo.geojson
python3 GeoQuery.py --sort      campo_numerico --asc archivo.geojson
python3 GeoQuery.py --summary   archivo.geojson
python3 GeoQuery.py --validate  archivo.geojson
python3 GeoQuery.py --export    campo=valor --output salida.geojson archivo.geojson
python3 GeoQuery.py --cabeceras archivo.geojson
```
