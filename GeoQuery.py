#!/usr/bin/env python3
"""
GeoQuery.py — CLI para consultar archivos GeoJSON (RFC 7946)
Uso: python3 GeoQuery.py [OPCION] <archivo.geojson>
Dependencias: ninguna (solo librería estándar de Python)
"""

import json
import sys
import argparse
from pathlib import Path

# ── Colores ANSI ──────────────────────────────────────────────────────────────
class Color:
    RED    = "\033[0;31m"
    GREEN  = "\033[0;32m"
    YELLOW = "\033[1;33m"
    CYAN   = "\033[0;36m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

def c(color: str, text: str) -> str:
    return f"{color}{text}{Color.RESET}"

def separador():
    print("─" * 40)

# ── Carga y validación del archivo ────────────────────────────────────────────
def cargar_geojson(ruta: str) -> dict:
    path = Path(ruta)

    if not path.exists():
        print(c(Color.RED, f"Error: Archivo '{ruta}' no encontrado."))
        sys.exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(c(Color.RED, f"Error: El archivo no es JSON válido.\n  {e}"))
        sys.exit(1)

    if data.get("type") != "FeatureCollection":
        print(c(Color.RED, "Error: Se esperaba type='FeatureCollection' (RFC 7946)."))
        sys.exit(1)

    if "features" not in data or not isinstance(data["features"], list):
        print(c(Color.RED, "Error: El archivo no contiene una lista de 'features'."))
        sys.exit(1)

    return data

def get_props(feature: dict) -> dict:
    return feature.get("properties") or {}

def get_nombre(feature: dict) -> str:
    props = get_props(feature)
    return props.get("municipio", props.get("name", "Sin nombre"))

# ── Comandos existentes ───────────────────────────────────────────────────────
def cmd_count(data: dict):
    total = len(data["features"])
    print(c(Color.GREEN, "Total de features: ") + c(Color.BOLD, str(total)))


def cmd_list(data: dict):
    print(c(Color.BOLD, f"{'#':<4} {'Municipio':<28} {'Lon':>10} {'Lat':>10}"))
    separador()
    for i, feature in enumerate(data["features"], 1):
        props = get_props(feature)
        nombre = get_nombre(feature)
        coords = feature.get("geometry", {}).get("coordinates", ["-", "-"])
        lon, lat = coords[0], coords[1]
        print(f"{i:<4} {nombre:<28} {lon:>10} {lat:>10}")


def cmd_info(data: dict, municipio: str):
    encontrado = None
    for feature in data["features"]:
        if get_nombre(feature).lower() == municipio.lower():
            encontrado = feature
            break

    if not encontrado:
        print(c(Color.RED, f"No se encontró: '{municipio}'"))
        print(f"Usa {c(Color.CYAN, '--list')} para ver los nombres disponibles.")
        sys.exit(1)

    props = get_props(encontrado)
    coords = encontrado.get("geometry", {}).get("coordinates", [])
    geom_type = encontrado.get("geometry", {}).get("type", "Desconocido")

    print(c(Color.BOLD + Color.CYAN, f"Información: {municipio}"))
    separador()
    print(c(Color.YELLOW, "  Geometría:"))
    print(f"    Tipo       : {geom_type}")
    if coords:
        print(f"    Longitud   : {coords[0]}")
        print(f"    Latitud    : {coords[1]}")
    print(c(Color.YELLOW, "  Propiedades:"))
    for key, val in props.items():
        print(f"    {key:<20}: {val}")


def cmd_filter(data: dict, filtro: str, exportar: str = None):
    if "=" not in filtro:
        print(c(Color.RED, "Error: Formato inválido. Usa campo=valor"))
        sys.exit(1)

    campo, valor = filtro.split("=", 1)

    valor_real = valor
    if valor.lower() == "true":
        valor_real = True
    elif valor.lower() == "false":
        valor_real = False
    else:
        try:
            valor_real = int(valor)
        except ValueError:
            try:
                valor_real = float(valor)
            except ValueError:
                pass

    print(c(Color.BOLD + Color.CYAN, f"Filtro: {campo} = {valor}"))
    separador()

    features_encontrados = [
        f for f in data["features"]
        if get_props(f).get(campo) == valor_real
    ]

    if not features_encontrados:
        print(c(Color.YELLOW, "  Sin resultados."))
    else:
        for feature in features_encontrados:
            print(f"  • {get_nombre(feature)}")

    print()
    print(c(Color.GREEN, "Resultados: ") + str(len(features_encontrados)))

    if exportar and features_encontrados:
        _exportar_geojson(features_encontrados, exportar)


def cmd_stats(data: dict, campo: str):
    valores = []
    nombres = []

    for feature in data["features"]:
        props = get_props(feature)
        val = props.get(campo)
        if isinstance(val, (int, float)):
            valores.append(val)
            nombres.append((val, get_nombre(feature)))

    if not valores:
        print(c(Color.RED, f"Error: El campo '{campo}' no existe o no es numérico."))
        sys.exit(1)

    total    = sum(valores)
    promedio = total / len(valores)
    maximo   = max(valores)
    minimo   = min(valores)

    print(c(Color.BOLD + Color.CYAN, f"Estadísticas: {campo}"))
    separador()
    print(f"  {'Features analizados':<22}: {len(valores)}")
    print(f"  {'Suma':<22}: {total:,.2f}")
    print(f"  {'Promedio':<22}: {promedio:,.2f}")
    print(f"  {'Máximo':<22}: {maximo:,.2f}")
    print(f"  {'Mínimo':<22}: {minimo:,.2f}")

    print()
    print(c(Color.YELLOW, f"  Top 3 por {campo}:"))
    for val, nombre in sorted(nombres, reverse=True)[:3]:
        print(f"    {nombre:<28}: {val:,.2f}")

    print()
    print(c(Color.YELLOW, f"  Bottom 3 por {campo}:"))
    for val, nombre in sorted(nombres)[:3]:
        print(f"    {nombre:<28}: {val:,.2f}")


def cmd_cabeceras(data: dict):
    print(c(Color.BOLD + Color.CYAN, "Cabeceras departamentales"))
    separador()
    encontradas = 0
    for feature in data["features"]:
        props = get_props(feature)
        if props.get("es_cabecera") is True:
            print(f"  ★ {get_nombre(feature)}")
            encontradas += 1
    if encontradas == 0:
        print(c(Color.YELLOW, "  Ningún feature tiene 'es_cabecera': true"))


# ── Comandos nuevos ───────────────────────────────────────────────────────────
def cmd_validate(data: dict, ruta: str):
    """Valida que cada feature tenga la estructura correcta según RFC 7946."""
    print(c(Color.BOLD + Color.CYAN, f"Validando: {ruta}"))
    separador()

    errores   = []
    warnings  = []
    geom_tipos_validos = {"Point", "MultiPoint", "LineString", "MultiLineString",
                          "Polygon", "MultiPolygon", "GeometryCollection"}

    for i, feature in enumerate(data["features"], 1):
        nombre = get_nombre(feature)
        prefijo = f"  Feature {i} ({nombre})"

        # Debe ser type Feature
        if feature.get("type") != "Feature":
            errores.append(f"{prefijo}: 'type' debe ser 'Feature'")

        # Debe tener geometry
        geom = feature.get("geometry")
        if geom is None:
            errores.append(f"{prefijo}: Sin 'geometry'")
        else:
            tipo_geom = geom.get("type", "")
            if tipo_geom not in geom_tipos_validos:
                errores.append(f"{prefijo}: Tipo de geometría inválido '{tipo_geom}'")

            coords = geom.get("coordinates")
            if coords is None:
                errores.append(f"{prefijo}: 'geometry' sin 'coordinates'")
            elif tipo_geom == "Point":
                if not isinstance(coords, list) or len(coords) < 2:
                    errores.append(f"{prefijo}: Point necesita [longitud, latitud]")
                else:
                    lon, lat = coords[0], coords[1]
                    if not (-180 <= lon <= 180):
                        errores.append(f"{prefijo}: Longitud fuera de rango ({lon})")
                    if not (-90 <= lat <= 90):
                        errores.append(f"{prefijo}: Latitud fuera de rango ({lat})")

        # Debe tener properties
        if "properties" not in feature:
            errores.append(f"{prefijo}: Sin campo 'properties'")
        elif feature["properties"] is None:
            warnings.append(f"{prefijo}: 'properties' es null (válido en RFC 7946 pero no recomendado)")

    # Resultado
    if not errores and not warnings:
        print(c(Color.GREEN, f"  ✔ Archivo válido. {len(data['features'])} features sin errores."))
    else:
        if errores:
            print(c(Color.RED, f"  ✘ {len(errores)} error(es) encontrado(s):"))
            for e in errores:
                print(c(Color.RED, f"    • {e}"))
        if warnings:
            print()
            print(c(Color.YELLOW, f"  ⚠ {len(warnings)} advertencia(s):"))
            for w in warnings:
                print(c(Color.YELLOW, f"    • {w}"))

    print()
    print(f"  Errores  : {len(errores)}")
    print(f"  Warnings : {len(warnings)}")


def cmd_summary(data: dict, ruta: str):
    """Vista general del archivo: campos, tipos, conteos."""
    features = data["features"]
    print(c(Color.BOLD + Color.CYAN, f"Resumen: {ruta}"))
    separador()
    print(f"  {'Total de features':<25}: {len(features)}")

    # Tipos de geometría presentes
    geom_tipos = {}
    for f in features:
        t = f.get("geometry", {}).get("type", "null")
        geom_tipos[t] = geom_tipos.get(t, 0) + 1

    print(f"  {'Tipos de geometría':<25}:")
    for tipo, cantidad in geom_tipos.items():
        print(f"    {'•'} {tipo:<20}: {cantidad}")

    # Campos en properties
    campos = {}
    for feature in features:
        for key, val in get_props(feature).items():
            tipo = type(val).__name__
            if key not in campos:
                campos[key] = {"tipo": tipo, "nulos": 0, "unicos": set()}
            campos[key]["unicos"].add(str(val))
            if val is None:
                campos[key]["nulos"] += 1

    print()
    print(c(Color.YELLOW, f"  Campos en properties ({len(campos)} total):"))
    print(f"    {'Campo':<22} {'Tipo':<10} {'Únicos':<8} {'Nulos'}")
    print("    " + "─" * 46)
    for nombre_campo, info in campos.items():
        print(f"    {nombre_campo:<22} {info['tipo']:<10} {len(info['unicos']):<8} {info['nulos']}")


def cmd_sort(data: dict, campo: str, ascendente: bool = False):
    """Lista features ordenados por un campo numérico."""
    pares = []
    for feature in data["features"]:
        val = get_props(feature).get(campo)
        if isinstance(val, (int, float)):
            pares.append((val, get_nombre(feature)))

    if not pares:
        print(c(Color.RED, f"Error: El campo '{campo}' no existe o no es numérico."))
        sys.exit(1)

    orden = "ascendente" if ascendente else "descendente"
    print(c(Color.BOLD + Color.CYAN, f"Ordenado por '{campo}' ({orden})"))
    separador()

    pares.sort(reverse=not ascendente)
    for i, (val, nombre) in enumerate(pares, 1):
        print(f"  {i:<3} {nombre:<28} {val:,.2f}")


def cmd_export(data: dict, filtro: str, salida: str):
    """Filtra y exporta el resultado a un nuevo GeoJSON."""
    if "=" not in filtro:
        print(c(Color.RED, "Error: Formato inválido. Usa campo=valor"))
        sys.exit(1)

    campo, valor = filtro.split("=", 1)
    valor_real = valor
    if valor.lower() == "true":
        valor_real = True
    elif valor.lower() == "false":
        valor_real = False
    else:
        try:
            valor_real = int(valor)
        except ValueError:
            try:
                valor_real = float(valor)
            except ValueError:
                pass

    features_encontrados = [
        f for f in data["features"]
        if get_props(f).get(campo) == valor_real
    ]

    if not features_encontrados:
        print(c(Color.YELLOW, "Sin resultados. No se exportó ningún archivo."))
        return

    _exportar_geojson(features_encontrados, salida)


def _exportar_geojson(features: list, salida: str):
    """Escribe una lista de features a un archivo GeoJSON."""
    coleccion = {
        "type": "FeatureCollection",
        "features": features
    }
    path = Path(salida)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(coleccion, f, ensure_ascii=False, indent=2)
    print()
    print(c(Color.GREEN, f"  ✔ Exportado: {salida} ({len(features)} features)"))


# ── CLI con argparse ──────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="GeoQuery",
        description=c(Color.BOLD, "GeoQuery CLI") + " — Consulta archivos GeoJSON desde la terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 GeoQuery.py --count     sonsonate.geojson
  python3 GeoQuery.py --list      sonsonate.geojson
  python3 GeoQuery.py --info      Izalco sonsonate.geojson
  python3 GeoQuery.py --filter    categoria=ciudad sonsonate.geojson
  python3 GeoQuery.py --stats     poblacion sonsonate.geojson
  python3 GeoQuery.py --sort      poblacion sonsonate.geojson
  python3 GeoQuery.py --sort      area_km2 --asc sonsonate.geojson
  python3 GeoQuery.py --summary   sonsonate.geojson
  python3 GeoQuery.py --validate  sonsonate.geojson
  python3 GeoQuery.py --export    categoria=ciudad --output ciudades.geojson sonsonate.geojson
  python3 GeoQuery.py --cabeceras sonsonate.geojson
        """
    )

    parser.add_argument("archivo", help="Ruta al archivo .geojson")

    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--count",    action="store_true",   help="Cuenta el total de features")
    grupo.add_argument("--list",     action="store_true",   help="Lista todos los features con coordenadas")
    grupo.add_argument("--info",     metavar="NOMBRE",      help="Detalle completo de un feature")
    grupo.add_argument("--filter",   metavar="CAMPO=VALOR", help="Filtra features por campo y valor")
    grupo.add_argument("--stats",    metavar="CAMPO",       help="Estadísticas de un campo numérico")
    grupo.add_argument("--sort",     metavar="CAMPO",       help="Ordena features por un campo numérico")
    grupo.add_argument("--summary",  action="store_true",   help="Vista general del archivo (campos, tipos, conteos)")
    grupo.add_argument("--validate", action="store_true",   help="Valida la estructura RFC 7946 del archivo")
    grupo.add_argument("--export",   metavar="CAMPO=VALOR", help="Filtra y exporta resultado a nuevo GeoJSON")
    grupo.add_argument("--cabeceras",action="store_true",   help="Lista features con es_cabecera=true")

    parser.add_argument("--output", metavar="ARCHIVO", help="Archivo de salida para --export")
    parser.add_argument("--asc",    action="store_true",   help="Orden ascendente para --sort")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    data = cargar_geojson(args.archivo)

    if args.count:
        cmd_count(data)
    elif args.list:
        cmd_list(data)
    elif args.info:
        cmd_info(data, args.info)
    elif args.filter:
        cmd_filter(data, args.filter)
    elif args.stats:
        cmd_stats(data, args.stats)
    elif args.sort:
        cmd_sort(data, args.sort, ascendente=args.asc)
    elif args.summary:
        cmd_summary(data, args.archivo)
    elif args.validate:
        cmd_validate(data, args.archivo)
    elif args.export:
        if not args.output:
            print(c(Color.RED, "Error: --export requiere --output <archivo.geojson>"))
            sys.exit(1)
        cmd_export(data, args.export, args.output)
    elif args.cabeceras:
        cmd_cabeceras(data)


if __name__ == "__main__":
    main()
