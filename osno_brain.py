#!/usr/bin/env python3
"""
osno-brain — ferramenta CLI para processar e visualizar memórias do Osno.
Lê os ficheiros ~/mind/ e gera relatórios, summaries, e status do dia.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, date
from urllib.request import urlopen
from urllib.error import URLError
import xml.etree.ElementTree as ET

MIND_DIR = Path.home() / "mind"

def read_file(path: Path) -> str:
    """Lê um ficheiro de forma segura."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except Exception as e:
        return f"[erro ao ler {path}: {e}]"

def status():
    """Mostra o estado actual — memórias, plano de hoje, bounties."""
    print("=" * 60)
    print(f"  OSNO 2PC 7000 — STATUS {date.today().isoformat()}")
    print("=" * 60)

    # Plano de hoje
    today_plan = MIND_DIR / "plans" / "today.md"
    if today_plan.exists():
        print("\n📋 PLANO DE HOJE:")
        print("-" * 40)
        content = read_file(today_plan)
        print(content[:500] + ("..." if len(content) > 500 else ""))
    else:
        print("\n📋 PLANO DE HOJE: (sem plano)")

    # Bounties
    bounties = MIND_DIR / "bounties.md"
    if bounties.exists():
        print("\n💰 BOUNTIES:")
        print("-" * 40)
        print(read_file(bounties))

    # Finanças
    finances_dir = MIND_DIR / "finances"
    if finances_dir.exists():
        files = list(finances_dir.glob("*.md"))
        if files:
            latest = max(files, key=lambda f: f.stat().st_mtime)
            print("\n💳 FINANÇAS (último registo):")
            print("-" * 40)
            print(read_file(latest)[:300])

    print("\n" + "=" * 60)

def memories():
    """Mostra todas as memórias."""
    memories_dir = MIND_DIR / "memories"
    if not memories_dir.exists():
        print("Directório de memórias não encontrado.")
        return

    print("=" * 60)
    print("  OSNO 2PC 7000 — MEMÓRIAS")
    print("=" * 60)

    for mem_file in sorted(memories_dir.glob("*.md")):
        print(f"\n{'=' * 40}")
        print(f"  {mem_file.stem.upper()}")
        print(f"{'=' * 40}")
        print(read_file(mem_file))

def journal(target_date: str = None):
    """Lê o journal de uma data (default: hoje)."""
    if target_date is None:
        target_date = date.today().isoformat()

    journal_file = MIND_DIR / "journal" / f"{target_date}.md"
    if journal_file.exists():
        print(read_file(journal_file))
    else:
        print(f"Sem journal para {target_date}")

def news(limit: int = 10):
    """Fetch headlines dos principais jornais PT via RSS."""
    feeds = [
        ("Público", "https://feeds.feedburner.com/PublicoRSS"),
        ("CM", "https://www.cmjornal.pt/rss"),
        ("Jornal de Negócios", "https://www.jornaldenegocios.pt/rss/ultimas_noticias.xml"),
        ("Sol", "https://sol.iol.pt/rss"),
    ]

    print("=" * 60)
    print(f"  OSNO — NOTÍCIAS PT  {datetime.now().strftime('%H:%M')}")
    print("=" * 60)

    for name, url in feeds:
        print(f"\n📰 {name}")
        print("-" * 40)
        try:
            with urlopen(url, timeout=8) as resp:
                content = resp.read()
            root = ET.fromstring(content)
            ns = ""
            items = root.findall(".//item")
            if not items:
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
                ns = "{http://www.w3.org/2005/Atom}"

            count = 0
            for item in items:
                if count >= limit:
                    break
                title_el = item.find(f"{ns}title")
                if title_el is not None and title_el.text:
                    title = title_el.text.strip()
                    # limpar CDATA se presente
                    if title.startswith("<![CDATA["):
                        title = title[9:-3].strip()
                    if title:
                        print(f"  • {title}")
                        count += 1
        except URLError as e:
            print(f"  [erro de rede: {e}]")
        except ET.ParseError as e:
            print(f"  [erro XML: {e}]")
        except Exception as e:
            print(f"  [erro: {e}]")

    print("\n" + "=" * 60)


def summary():
    """Gera um resumo rápido do estado actual."""
    print("=" * 60)
    print(f"  OSNO — RESUMO RÁPIDO")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Contar journals
    journal_dir = MIND_DIR / "journal"
    n_journals = len(list(journal_dir.glob("*.md"))) if journal_dir.exists() else 0
    print(f"\n📖 Dias de journal: {n_journals}")

    # Memórias
    memories_dir = MIND_DIR / "memories"
    if memories_dir.exists():
        mem_files = list(memories_dir.glob("*.md"))
        print(f"🧠 Ficheiros de memória: {len(mem_files)}")
        for f in sorted(mem_files):
            lines = read_file(f).count('\n')
            print(f"   • {f.stem}: ~{lines} linhas")

    # Projetos
    projects_dir = MIND_DIR / "projects"
    if projects_dir.exists():
        proj_files = list(projects_dir.glob("*.md"))
        print(f"🚀 Projectos documentados: {len(proj_files)}")

    # Logs
    logs_dir = MIND_DIR / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.md"))
        print(f"📝 Logs: {len(log_files)}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="osno-brain — CLI de memória e status do Osno",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
comandos:
  status      mostra plano de hoje, bounties, finanças
  memories    mostra todas as memórias
  journal     lê o journal (default: hoje, ou YYYY-MM-DD)
  summary     resumo rápido de tudo
        """
    )
    parser.add_argument("command", choices=["status", "memories", "journal", "summary", "news"])
    parser.add_argument("arg", nargs="?", help="argumento opcional (ex: data para journal)")

    args = parser.parse_args()

    if args.command == "status":
        status()
    elif args.command == "memories":
        memories()
    elif args.command == "journal":
        journal(args.arg)
    elif args.command == "summary":
        summary()
    elif args.command == "news":
        limit = int(args.arg) if args.arg else 5
        news(limit)


if __name__ == "__main__":
    main()
