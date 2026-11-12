"""Auxiliary secret scanner, not a guarantee. Returns 1 on suspicious files."""
from pathlib import Path
import re
root=Path(__file__).resolve().parent
patterns=[re.compile(r'\bsk-[A-Za-z0-9_-]{20,}'),re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}'),
          re.compile(r'github_pat_[A-Za-z0-9_]{20,}')]
issues=[]
for p in root.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in ('.git','.venv','__pycache__')):
        continue
    if p.name.startswith('.env') and p.name!='.env.example':
        # A local .env is expected, but never belongs in the upload/archive.
        print('Arquivo local a excluir de publicação:',p.relative_to(root))
        continue
    try:
        text=p.read_text()
    except UnicodeError:
        continue
    if any(pattern.search(text) for pattern in patterns):
        issues.append(str(p.relative_to(root)))
if issues:
    print('Revisar possíveis segredos nos arquivos:',', '.join(issues))
    raise SystemExit(1)
print('Nenhum padrão conhecido de token encontrado. Faça também revisão manual.')
