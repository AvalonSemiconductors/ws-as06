#!/bin/bash
set -e

export PDK=gf180mcuD
export PDK_ROOT=$(pwd)/../gf180mcu/

python3 make_gds.py --cellname td --boundary "0/0" "152/5" --foreground "81/0" --invert-alpha --threshold 196 --pixel-size 0.6 td.png td.gds
klayout -b -r ../gf180mcu/gf180mcuD/libs.tech/klayout/tech/drc/gf180mcu.drc -rd decks="all,-antenna,-density" -rd input=td.gds -rd report=drc_results.lyrdb -rd run_mode=deep
echo "calma read td.gds;load td;lef write;" | magic -dnull -noconsole

python3 make_gds.py --cellname avali --boundary "0/0" "152/5" --foreground "81/0" "46/0" --pixel-size 0.6 Logo_BW.png avali.gds
klayout -b -r ../gf180mcu/gf180mcuD/libs.tech/klayout/tech/scripts/slots.drc -rd input=avali.gds -rd output=avali.gds
klayout -b -r ../gf180mcu/gf180mcuD/libs.tech/klayout/tech/drc/gf180mcu.drc -rd decks="all,-antenna,-density" -rd input=avali.gds -rd report=drc_results.lyrdb -rd run_mode=deep
echo "calma read avali.gds;load avali;lef write;" | magic -dnull -noconsole

python3 make_gds.py --cellname deepai --boundary "0/0" "152/5" --foreground "81/0" --invert-alpha --threshold 196 --pixel-size 0.6 deepai.png deepai.gds
klayout -b -r ../gf180mcu/gf180mcuD/libs.tech/klayout/tech/drc/gf180mcu.drc -rd decks="all,-antenna,-density" -rd input=deepai.gds -rd report=drc_results.lyrdb -rd run_mode=deep
echo "calma read deepai.gds;load deepai;lef write;" | magic -dnull -noconsole
