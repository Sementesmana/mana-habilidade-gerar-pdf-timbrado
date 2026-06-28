"""
Geração de PDF com timbre Maná — núcleo.

Padrão canônico extraído das 6 cópias inline em produção. Decisões:

  - Altura cabeçalho:   30 mm  (era 30 vs 32 entre agentes — canônico = 30)
  - Verde primário:     #1D6B3E
  - Ouro:               #B8860B (oficial CSS Maná)
  - Logo:               2 anéis brancos desenhados via reportlab puro
                        (sem dep de arquivo externo)
  - Rodapé:             linha ouro + texto cinza + numeração página
  - Fonte:              Helvetica nativa (sem fonte externa)

Stack: reportlab puro (sem Pillow, sem fonte externa, sem binário do SO).
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas

# ─────────────────────────────────────────────────────────────────────
# Cores canônicas Maná
# ─────────────────────────────────────────────────────────────────────

CORES_MANA: dict[str, Color] = {
    "verde": Color(0.114, 0.420, 0.243),         # #1D6B3E
    "verde_escuro": Color(0.075, 0.302, 0.173),  # #134d2c
    "ouro": Color(0.722, 0.525, 0.043),          # #B8860B
    "cinza_texto": Color(0.33, 0.33, 0.33),
    "cinza_claro": Color(0.85, 0.85, 0.85),
    "branco": Color(1, 1, 1),
}


# ─────────────────────────────────────────────────────────────────────
# Helpers internos — cabeçalho e rodapé
# ─────────────────────────────────────────────────────────────────────


def _desenhar_logo(c: rl_canvas.Canvas, x: float, y: float, raio: float = 4 * mm) -> None:
    """Logo Maná simples — 2 anéis brancos concêntricos."""
    c.setStrokeColor(CORES_MANA["branco"])
    c.setLineWidth(1.3)
    c.circle(x, y, raio, stroke=1, fill=0)
    c.circle(x, y, raio - 1.8, stroke=1, fill=0)


def _desenhar_cabecalho(
    c: rl_canvas.Canvas,
    titulo: str,
    subtitulo: str,
    direita_top: str,
    direita_bot: str,
    altura_cabecalho_mm: float = 30,
) -> None:
    """Cabeçalho retangular verde no topo da página."""
    largura, altura = A4
    h = altura_cabecalho_mm * mm
    y_base = altura - h

    c.setFillColor(CORES_MANA["verde"])
    c.rect(0, y_base, largura, h, stroke=0, fill=1)

    _desenhar_logo(c, x=15 * mm, y=altura - h / 2)

    c.setFillColor(CORES_MANA["branco"])
    c.setFont("Helvetica-Bold", 18)
    c.drawString(25 * mm, altura - h / 2 + 1 * mm, titulo)

    c.setFillColor(CORES_MANA["ouro"])
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25 * mm, altura - h / 2 - 5 * mm, subtitulo)

    if direita_top:
        c.setFillColor(CORES_MANA["branco"])
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(largura - 15 * mm, altura - h / 2 + 1 * mm, direita_top)
    if direita_bot:
        c.setFillColor(CORES_MANA["cinza_claro"])
        c.setFont("Helvetica", 8.5)
        c.drawRightString(largura - 15 * mm, altura - h / 2 - 5 * mm, direita_bot)


def _desenhar_rodape(
    c: rl_canvas.Canvas,
    agente: str,
    pagina: int,
) -> None:
    """Rodapé: linha ouro + texto cinza + numeração."""
    largura, _ = A4

    c.setStrokeColor(CORES_MANA["ouro"])
    c.setLineWidth(1.5)
    c.line(15 * mm, 18 * mm, largura - 15 * mm, 18 * mm)

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.setFillColor(CORES_MANA["cinza_texto"])
    c.setFont("Helvetica", 8)
    c.drawString(
        15 * mm,
        13 * mm,
        f"Gerado em {agora} - {agente} - Sementes Mana LTDA",
    )

    c.drawRightString(largura - 15 * mm, 13 * mm, f"pagina {pagina}")


# ─────────────────────────────────────────────────────────────────────
# Classe principal — PDFMana
# ─────────────────────────────────────────────────────────────────────


class PDFMana:
    """
    Builder pra PDFs com timbre Maná.

    Uso:
        >>> pdf = PDFMana(subtitulo="Relatório", agente="agente-X")
        >>> pdf.paragrafo("Texto...")
        >>> pdf.tabela(["A", "B"], [["x", "y"]])
        >>> pdf.quebra_pagina()
        >>> bytes_pdf = pdf.bytes()
    """

    def __init__(
        self,
        subtitulo: str = "",
        direita_top: str = "",
        direita_bot: str = "",
        agente: str = "agente-template",
        titulo: str = "Sementes Mana",
        altura_cabecalho_mm: float = 30,
    ) -> None:
        self.subtitulo = subtitulo
        self.direita_top = direita_top
        self.direita_bot = direita_bot
        self.agente = agente
        self.titulo = titulo
        self.altura_cabecalho_mm = altura_cabecalho_mm

        self._buffer = io.BytesIO()
        self._c = rl_canvas.Canvas(self._buffer, pagesize=A4)
        self._largura, self._altura = A4

        self._y_atual = self._altura - (self.altura_cabecalho_mm + 8) * mm
        self._margem_esquerda = 15 * mm
        self._margem_direita = self._largura - 15 * mm
        self._margem_inferior = 25 * mm
        self._pagina = 1

        self._desenhar_cabecalho_pagina()

    # ── Helpers internos ───────────────────────────────────────────────

    def _desenhar_cabecalho_pagina(self) -> None:
        _desenhar_cabecalho(
            self._c,
            titulo=self.titulo,
            subtitulo=self.subtitulo,
            direita_top=self.direita_top,
            direita_bot=self.direita_bot,
            altura_cabecalho_mm=self.altura_cabecalho_mm,
        )

    def _garantir_espaco(self, altura_necessaria: float) -> None:
        """Quebra página se não cabe."""
        if self._y_atual - altura_necessaria < self._margem_inferior:
            self.quebra_pagina()

    def _wrap_texto(self, texto: str, fonte: str, tamanho: float) -> list[str]:
        """Quebra texto em linhas que cabem na largura útil."""
        largura_util = self._margem_direita - self._margem_esquerda
        palavras = texto.split()
        linhas: list[str] = []
        atual = ""
        for p in palavras:
            tentativa = f"{atual} {p}".strip()
            if self._c.stringWidth(tentativa, fonte, tamanho) <= largura_util:
                atual = tentativa
            else:
                if atual:
                    linhas.append(atual)
                atual = p
        if atual:
            linhas.append(atual)
        return linhas

    # ── Conteúdo público ───────────────────────────────────────────────

    def paragrafo(self, texto: str, fonte: str = "Helvetica", tamanho: float = 10) -> None:
        """Escreve um parágrafo. Quebra de linha automática por largura."""
        if not texto:
            return
        self._c.setFont(fonte, tamanho)
        self._c.setFillColor(CORES_MANA["cinza_texto"])
        linhas = self._wrap_texto(texto, fonte, tamanho)
        altura_linha = tamanho + 2
        for linha in linhas:
            self._garantir_espaco(altura_linha)
            self._c.drawString(self._margem_esquerda, self._y_atual, linha)
            self._y_atual -= altura_linha
        self._y_atual -= 4

    def titulo_secao(self, texto: str) -> None:
        """Título de seção (negrito + cor verde)."""
        self._garantir_espaco(18)
        self._c.setFont("Helvetica-Bold", 12)
        self._c.setFillColor(CORES_MANA["verde"])
        self._c.drawString(self._margem_esquerda, self._y_atual, texto)
        self._y_atual -= 14

    def tabela(
        self,
        cabecalho: list[str],
        linhas: list[list[Any]],
        larguras_mm: list[float] | None = None,
    ) -> None:
        """
        Tabela com cabeçalho verde + linhas alternadas cinza claro.

        Args:
            cabecalho: lista de strings.
            linhas: lista de linhas; cada linha do mesmo tamanho do cabecalho.
            larguras_mm: opcional — larguras em mm. Default = divide igual.
        """
        if not cabecalho:
            return
        n = len(cabecalho)
        largura_util_mm = (self._margem_direita - self._margem_esquerda) / mm
        if larguras_mm is None or len(larguras_mm) != n:
            larguras_mm = [largura_util_mm / n] * n

        altura_linha = 6 * mm
        self._garantir_espaco(altura_linha * (len(linhas) + 1) + 4 * mm)

        # Cabeçalho
        x = self._margem_esquerda
        self._c.setFillColor(CORES_MANA["verde"])
        self._c.rect(
            self._margem_esquerda,
            self._y_atual - altura_linha + 1,
            largura_util_mm * mm,
            altura_linha,
            stroke=0,
            fill=1,
        )
        self._c.setFillColor(CORES_MANA["branco"])
        self._c.setFont("Helvetica-Bold", 9)
        for i, txt in enumerate(cabecalho):
            self._c.drawString(x + 1.5 * mm, self._y_atual - altura_linha + 3, str(txt))
            x += larguras_mm[i] * mm
        self._y_atual -= altura_linha + 1

        # Linhas alternadas
        self._c.setFont("Helvetica", 9)
        for idx, linha in enumerate(linhas):
            self._garantir_espaco(altura_linha)
            if idx % 2 == 1:
                self._c.setFillColor(CORES_MANA["cinza_claro"])
                self._c.rect(
                    self._margem_esquerda,
                    self._y_atual - altura_linha + 1,
                    largura_util_mm * mm,
                    altura_linha,
                    stroke=0,
                    fill=1,
                )
            self._c.setFillColor(CORES_MANA["cinza_texto"])
            x = self._margem_esquerda
            for i, celula in enumerate(linha):
                self._c.drawString(
                    x + 1.5 * mm,
                    self._y_atual - altura_linha + 3,
                    str(celula),
                )
                x += larguras_mm[i] * mm
            self._y_atual -= altura_linha
        self._y_atual -= 4

    def quebra_pagina(self) -> None:
        """Finaliza página atual e abre nova com cabeçalho."""
        _desenhar_rodape(self._c, self.agente, self._pagina)
        self._c.showPage()
        self._pagina += 1
        self._y_atual = self._altura - (self.altura_cabecalho_mm + 8) * mm
        self._desenhar_cabecalho_pagina()

    def imagem(self, caminho: str, largura: float = 0, altura: float = 0) -> None:
        """Insere imagem (PNG/JPG). Larguras em mm."""
        largura_util_mm = (self._margem_direita - self._margem_esquerda) / mm
        if largura <= 0:
            largura = largura_util_mm
        if altura <= 0:
            altura = largura * 0.5
        self._garantir_espaco(altura * mm + 4)
        self._c.drawImage(
            caminho,
            self._margem_esquerda,
            self._y_atual - altura * mm,
            width=largura * mm,
            height=altura * mm,
            preserveAspectRatio=True,
        )
        self._y_atual -= altura * mm + 4

    def bytes(self) -> bytes:
        """Finaliza o PDF e retorna os bytes."""
        _desenhar_rodape(self._c, self.agente, self._pagina)
        self._c.save()
        return self._buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────
# Funções atalho
# ─────────────────────────────────────────────────────────────────────


def gerar_pdf_simples(
    subtitulo: str,
    agente: str,
    paragrafos: list[str],
    direita_top: str = "",
    direita_bot: str = "",
    titulo: str = "Sementes Mana",
) -> bytes:
    """Atalho — PDF com texto."""
    pdf = PDFMana(
        subtitulo=subtitulo,
        direita_top=direita_top,
        direita_bot=direita_bot,
        agente=agente,
        titulo=titulo,
    )
    for p in paragrafos:
        pdf.paragrafo(p)
    return pdf.bytes()


def gerar_pdf_tabela(
    subtitulo: str,
    agente: str,
    cabecalho: list[str],
    linhas: list[list[Any]],
    larguras_mm: list[float] | None = None,
    direita_top: str = "",
    direita_bot: str = "",
    titulo: str = "Sementes Mana",
    paragrafo_antes: str = "",
) -> bytes:
    """Atalho — PDF com (opcional) parágrafo + tabela."""
    pdf = PDFMana(
        subtitulo=subtitulo,
        direita_top=direita_top,
        direita_bot=direita_bot,
        agente=agente,
        titulo=titulo,
    )
    if paragrafo_antes:
        pdf.paragrafo(paragrafo_antes)
    pdf.tabela(cabecalho, linhas, larguras_mm=larguras_mm)
    return pdf.bytes()
