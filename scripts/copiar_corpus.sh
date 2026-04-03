#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════
# CecilIA v2 — Copiar Corpus de BaseConocimiento
# Contraloria General de la Republica de Colombia
# ═══════════════════════════════════════════════════════
#
# Uso: bash scripts/copiar_corpus.sh
#
# Copia los documentos desde BaseConocimiento hacia corpus/
# con los nombres de coleccion esperados por el sistema.
# ═══════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ORIGEN="${CORPUS_ORIGEN:-/mnt/c/Users/ThinPad X1/Documents/CGR/BaseConocimiento}"
DESTINO="${SCRIPT_DIR}/../corpus"

echo ""
echo "==================================================="
echo " CecilIA v2 — Copiando Corpus Documental"
echo "==================================================="
echo ""
echo "Origen:  ${ORIGEN}"
echo "Destino: ${DESTINO}"
echo ""

if [ ! -d "${ORIGEN}" ]; then
    echo "ERROR: No se encontro el directorio origen: ${ORIGEN}"
    echo "Puede especificar otra ruta con: CORPUS_ORIGEN=/ruta/al/corpus bash $0"
    exit 1
fi

mkdir -p "${DESTINO}"

# Mapeo: directorio origen -> nombre coleccion
declare -A MAPEO=(
    ["01_normativo"]="normativo"
    ["02_institucional"]="institucional"
    ["03_academico"]="academico"
    ["04_tecnico_tic"]="tecnico_tic"
    ["05_estadistico"]="estadistico"
    ["06_jurisprudencial"]="jurisprudencial"
    ["07_auditoria"]="auditoria"
)

for dir_origen in "${!MAPEO[@]}"; do
    coleccion="${MAPEO[$dir_origen]}"
    ruta_origen="${ORIGEN}/${dir_origen}"

    if [ -d "${ruta_origen}" ]; then
        echo "Copiando ${dir_origen} -> ${coleccion} ..."
        mkdir -p "${DESTINO}/${coleccion}"
        cp -r "${ruta_origen}/"* "${DESTINO}/${coleccion}/" 2>/dev/null || true
        conteo=$(find "${DESTINO}/${coleccion}" -type f | wc -l)
        echo "  OK (${conteo} archivos)"
    else
        echo "AVISO: No se encontro ${ruta_origen}, se omite."
    fi
done

echo ""
echo "==================================================="
echo " Copia completada."
echo "==================================================="
echo ""
echo "Para ingestar el corpus en la base vectorial:"
echo "  docker compose exec backend python -m scripts.ingest_corpus"
echo ""
