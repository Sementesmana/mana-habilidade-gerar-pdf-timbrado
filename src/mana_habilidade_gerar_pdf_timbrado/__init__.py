"""
mana-habilidade-gerar-pdf-timbrado — Geração de PDF com timbre Maná.

Habilidade canônica da Maná Builder. Resolve 6 cópias de cabeçalho/rodapé
copy-paste em 2 agentes em produção:

  - agente-gestor-comercial: 4 funções com cabeçalho copy-paste
    (pdf_ocorrencia.py + variantes vendedor/geral/cliente)
  - agente-gestor-estoque: 2 funções com cabeçalho copy-paste
    (pdf_variedade.py + gerar_pdf_resumo)

USO TÍPICO

  Caso 1 — Atalho texto simples
  -----------------------------------------------------------------
  >>> from mana_habilidade_gerar_pdf_timbrado import gerar_pdf_simples
  >>> pdf_bytes = gerar_pdf_simples(
  ...     subtitulo="Pareto · 28/06/2026",
  ...     agente="agente-gestor-comercial",
  ...     paragrafos=["Linha 1...", "Linha 2..."],
  ... )

  Caso 2 — Atalho tabela
  -----------------------------------------------------------------
  >>> from mana_habilidade_gerar_pdf_timbrado import gerar_pdf_tabela
  >>> pdf_bytes = gerar_pdf_tabela(
  ...     subtitulo="Posição Estoque",
  ...     agente="agente-gestor-estoque",
  ...     cabecalho=["Cultivar", "Saldo", "Vendido"],
  ...     linhas=[["76KA", "1500", "30%"]],
  ... )

  Caso 3 — Classe (múltiplas páginas, mistura tipos)
  -----------------------------------------------------------------
  >>> from mana_habilidade_gerar_pdf_timbrado import PDFMana
  >>> pdf = PDFMana(subtitulo="Relatório", agente="agente-X")
  >>> pdf.paragrafo("Resumo do dia...")
  >>> pdf.tabela(["A", "B"], [["x", "y"]])
  >>> pdf.quebra_pagina()
  >>> bytes_pdf = pdf.bytes()
"""

__version__ = "0.2.0"

from .core import (
    CORES_MANA,
    SEVERIDADE_CORES,
    PDFMana,
    gerar_pdf_simples,
    gerar_pdf_tabela,
)

__all__ = [
    "CORES_MANA",
    "SEVERIDADE_CORES",
    "PDFMana",
    "gerar_pdf_simples",
    "gerar_pdf_tabela",
]
