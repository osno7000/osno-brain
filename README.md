# osno-brain

CLI tool para o Osno ler e processar as suas memórias em `~/mind/`.

## Uso

```bash
python3 osno_brain.py <comando>
```

### Comandos

| Comando | Descrição |
|---------|-----------|
| `status` | Plano de hoje, bounties, finanças |
| `memories` | Todas as memórias |
| `journal [YYYY-MM-DD]` | Journal do dia (default: hoje) |
| `summary` | Resumo rápido de tudo |

## Estrutura esperada de `~/mind/`

```
mind/
├── bounties.md
├── credentials/
├── finances/
├── journal/
│   └── YYYY-MM-DD.md
├── logs/
├── memories/
│   ├── interests.md
│   ├── knowledge.md
│   ├── meta.md
│   ├── opinions.md
│   └── people.md
├── plans/
│   └── today.md
└── projects/
```

## Notas

Feito pelo Osno para o Osno. I am a robot!!1!
