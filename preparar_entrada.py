"""Build an explicit, bounded input from an authorized public research repository."""
import argparse
import json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--repo',required=True)
p.add_argument('--issue',required=True,help='UTF-8 text file containing the chosen issue')
p.add_argument('--arquivo',action='append',required=True,help='Relative public source/test file; repeat as needed')
p.add_argument('--criterio',action='append',required=True)
p.add_argument('--saida',default='entradas/caso.json')
a=p.parse_args()
root=Path(a.repo).resolve()
files={}
for name in a.arquivo:
    path=(root/name).resolve()
    if not path.is_relative_to(root) or path.suffix not in ('.py','.md','.txt') or path.name.startswith('.'):
        raise ValueError('Arquivo fora do recorte permitido')
    files[name]=path.read_text()
data=dict(problema=Path(a.issue).read_text(),arquivos=files,criterios=a.criterio,
          origem='Recorte informado pelo operador; confirme licença e ausência de segredos antes de publicar')
text=json.dumps(data,ensure_ascii=False,indent=2)
if len(text.encode())>100000:
    raise ValueError('Recorte excede 100 KB')
Path(a.saida).parent.mkdir(parents=True,exist_ok=True)
Path(a.saida).write_text(text)
print(a.saida)
