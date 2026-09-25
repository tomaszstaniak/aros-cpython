#!/bin/sh
# mksuite.sh RUN - write suite-RUN, an AmigaDOS script for one pass of the
# guest tests. On AROS: copy tests/guest to SYS:pytest, then
#   Assign PYTEST: SYS:pytest
#   Execute PYTEST:suite-RUN
# Each result goes to a new file RAM:RUN-<test>.txt. RUN is written into the
# script rather than passed through .key: the python launcher is itself a
# script, and after it ran, the outer script's argument substitution stopped
# working. Results are written by run11.py itself: a redirection of the
# launcher does not reach the interpreter.
R=$1
[ -n "$R" ] || { echo "usage: mksuite.sh RUN" >&2; exit 1; }
{
  echo "; one pass of the guest tests; results in RAM:$R-*.txt"
  for s in id:idprobe.py imp:imports11.py "p11:probe11.py $R" z:compress11.py \
           h:https11.py t:threads11.py lim:limits.py; do
    echo "python /PYTEST/run11.py /RAM/$R-${s%%:*}.txt /PYTEST/${s#*:}"
  done
  for s in inst:install-test.py whl:wheel-test.py; do
    echo "python /PYTEST/run11.py /RAM/$R-${s%%:*}.txt /Python/tests/${s#*:}"
  done
  echo "Run >NIL: python /PYTEST/run11.py /RAM/$R-c1.txt /PYTEST/conc11.py A"
  echo "python /PYTEST/run11.py /RAM/$R-c2.txt /PYTEST/conc11.py B"
  echo "Wait 15"
  for i in 1 2 3 4 5 6 7 8; do
    echo "python -c \"open('/RAM/$R-r$i.txt', 'w').write('R$i\\\\n')\""
  done
  echo "Echo >RAM:$R-end.txt \"SUITE-END $R\""
} > "suite-$R"
