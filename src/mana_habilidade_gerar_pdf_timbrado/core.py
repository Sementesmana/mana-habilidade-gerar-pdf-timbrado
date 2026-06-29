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
    "ouro_claro": Color(0.831, 0.627, 0.090),    # tom usado por agente-gestor-comercial
    "cinza_texto": Color(0.33, 0.33, 0.33),
    "cinza_claro": Color(0.85, 0.85, 0.85),
    "branco": Color(1, 1, 1),
    "preto_texto": Color(0.1, 0.1, 0.1),
}

# Severidade canônica Maná (CRÍTICO/ALTO/MÉDIO/BAIXO).
# Usado por agentes N3 que classificam ocorrências/alertas (gestor-comercial,
# gestor-estoque, futuros).
SEVERIDADE_CORES: dict[str, Color] = {
    "critico": Color(0.749, 0.090, 0.090),   # vermelho fechado
    "alto":    Color(0.831, 0.420, 0.043),   # laranja queimado
    "medio":   Color(0.722, 0.525, 0.043),   # ouro Maná
    "baixo":   Color(0.114, 0.420, 0.243),   # verde Maná
    "reincidencia": Color(0.29, 0.106, 0.047),  # marrom escuro (selo REINC)
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
    subtitulo_cor: Color | None = None,
    direita_top_fonte: str = "Helvetica-Bold",
    direita_top_tamanho: float = 11,
    direita_bot_fonte: str = "Helvetica",
    direita_bot_tamanho: float = 8.5,
    direita_bot_cor: Color | None = None,
    mostrar_logo: bool = True,
    margem_mm: float = 15,
) -> None:
    """Cabeçalho retangular verde no topo da página.

    v0.3.0: ganhou `mostrar_logo`, `margem_mm`, `direita_bot_fonte/tamanho/cor`
    pra migração do agente-gestor-comercial sem regressão visual.
    """
    largura, altura = A4
    h = altura_cabecalho_mm * mm
    y_base = altura - h

    c.setFillColor(CORES_MANA["verde"])
    c.rect(0, y_base, largura, h, stroke=0, fill=1)

    # Logo opcional (alguns agentes preferem só texto)
    if mostrar_logo:
        _desenhar_logo(c, x=margem_mm * mm, y=altura - h / 2)
        x_texto = (margem_mm + 10) * mm   # 10mm de offset pro título depois do logo
    else:
        x_texto = margem_mm * mm

    c.setFillColor(CORES_MANA["branco"])
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x_texto, altura - h / 2 + 1 * mm, titulo)

    c.setFillColor(subtitulo_cor or CORES_MANA["ouro"])
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_texto, altura - h / 2 - 5 * mm, subtitulo)

    if direita_top:
        c.setFillColor(CORES_MANA["branco"])
        c.setFont(direita_top_fonte, direita_top_tamanho)
        c.drawRightString(largura - margem_mm * mm, altura - h / 2 + 1 * mm, direita_top)
    if direita_bot:
        c.setFillColor(direita_bot_cor or CORES_MANA["cinza_claro"])
        c.setFont(direita_bot_fonte, direita_bot_tamanho)
        c.drawRightString(largura - margem_mm * mm, altura - h / 2 - 5 * mm, direita_bot)


def _desenhar_rodape(
    c: rl_canvas.Canvas,
    agente: str,
    pagina: int,
    margem_mm: float = 15,
    mostrar_pagina: bool = True,
) -> None:
    """Rodapé: linha ouro + texto cinza + numeração (opcional).

    v0.3.0: `margem_mm` e `mostrar_pagina` parametrizáveis. Alguns agentes
    (gestor-comercial) usam margem 18mm e não mostram número de página.
    """
    largura, _ = A4

    c.setStrokeColor(CORES_MANA["ouro"])
    c.setLineWidth(1.5)
    c.line(margem_mm * mm, 18 * mm, largura - margem_mm * mm, 18 * mm)

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.setFillColor(CORES_MANA["cinza_texto"])
    c.setFont("Helvetica", 8)
    c.drawString(
        margem_mm * mm,
        13 * mm,
        f"Gerado em {agora} - {agente} - Sementes Mana LTDA",
    )

    if mostrar_pagina:
        c.drawRightString(largura - margem_mm * mm, 13 * mm, f"pagina {pagina}")


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
        subtitulo_cor: Color | None = None,
        direita_top_fonte: str = "Helvetica-Bold",
        direita_top_tamanho: float = 11,
        direita_bot_fonte: str = "Helvetica",
        direita_bot_tamanho: float = 8.5,
        direita_bot_cor: Color | None = None,
        mostrar_logo: bool = True,
        margem_mm: float = 15,
        mostrar_pagina_rodape: bool = True,
    ) -> None:
        self.subtitulo = subtitulo
        self.direita_top = direita_top
        self.direita_bot = direita_bot
        self.agente = agente
        self.titulo = titulo
        self.altura_cabecalho_mm = altura_cabecalho_mm
        self.subtitulo_cor = subtitulo_cor
        self.direita_top_fonte = direita_top_fonte
        self.direita_top_tamanho = direita_top_tamanho
        self.direita_bot_fonte = direita_bot_fonte
        self.direita_bot_tamanho = direita_bot_tamanho
        self.direita_bot_cor = direita_bot_cor
        self.mostrar_logo = mostrar_logo
        self.margem_mm = margem_mm
        self.mostrar_pagina_rodape = mostrar_pagina_rodape

        self._buffer = io.BytesIO()
        self._c = rl_canvas.Canvas(self._buffer, pagesize=A4)
        self._largura, self._altura = A4

        self._y_atual = self._altura - (self.altura_cabecalho_mm + 8) * mm
        self._margem_esquerda = margem_mm * mm
        self._margem_direita = self._largura - margem_mm * mm
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
            subtitulo_cor=self.subtitulo_cor,
            direita_top_fonte=self.direita_top_fonte,
            direita_top_tamanho=self.direita_top_tamanho,
            direita_bot_fonte=self.direita_bot_fonte,
            direita_bot_tamanho=self.direita_bot_tamanho,
            direita_bot_cor=self.direita_bot_cor,
            mostrar_logo=self.mostrar_logo,
            margem_mm=self.margem_mm,
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

    # ── v0.2.0 — primitivos descobertos na migração do agente-gestor-comercial

    def chip(
        self,
        texto: str,
        cor: Color | None = None,
        x_mm: float | None = None,
        largura_mm: float = 30,
        altura_mm: float = 7,
        cor_texto: Color | None = None,
        nao_avancar_y: bool = False,
    ) -> None:
        """
        Desenha chip arredondado colorido com texto centralizado (severidade).

        Padrão Maná: severidade, status, faixa, REINCIDÊNCIA.

        Args:
            texto: conteúdo do chip (uppercase, curto).
            cor: cor de fundo (default = SEVERIDADE_CORES["medio"]).
            x_mm: posição X em mm (default = margem esquerda).
            largura_mm: largura em mm.
            altura_mm: altura em mm.
            cor_texto: cor do texto (default = branco).
            nao_avancar_y: se True, não avança o cursor (chips na mesma linha).
        """
        if not texto:
            return
        cor = cor or SEVERIDADE_CORES["medio"]
        cor_texto = cor_texto or CORES_MANA["branco"]
        x = x_mm * mm if x_mm is not None else self._margem_esquerda

        self._garantir_espaco(altura_mm * mm + 4)
        # Fundo arredondado
        self._c.setFillColor(cor)
        self._c.roundRect(
            x,
            self._y_atual - 1 * mm,
            largura_mm * mm,
            altura_mm * mm,
            2,
            stroke=0,
            fill=1,
        )
        # Texto centralizado
        self._c.setFillColor(cor_texto)
        self._c.setFont("Helvetica-Bold", 9)
        self._c.drawCentredString(
            x + (largura_mm * mm) / 2,
            self._y_atual + 1.2 * mm,
            texto,
        )

        if not nao_avancar_y:
            self._y_atual -= (altura_mm + 5) * mm

    def chip_severidade(
        self,
        severidade: str,
        x_mm: float | None = None,
        largura_mm: float = 30,
        nao_avancar_y: bool = False,
    ) -> None:
        """
        Atalho: chip com cor canônica por severidade (critico/alto/medio/baixo).

        `severidade` é case-insensitive; aceita também forma com acento ("crítico").
        """
        chave = severidade.lower().strip()
        chave = chave.replace("í", "i").replace("é", "e")
        cor = SEVERIDADE_CORES.get(chave, SEVERIDADE_CORES["medio"])
        self.chip(
            texto=severidade.upper(),
            cor=cor,
            x_mm=x_mm,
            largura_mm=largura_mm,
            nao_avancar_y=nao_avancar_y,
        )

    def tabela_rotulo_valor(
        self,
        linhas: list[tuple[str, Any]],
        rotulo_cor: Color | None = None,
        valor_cor: Color | None = None,
        rotulo_x_mm: float | None = None,
        valor_x_mm: float = 75,
        max_chars_valor: int = 70,
    ) -> None:
        """
        Tabela 2 colunas: RÓTULO uppercase à esquerda + valor bold à direita.

        Padrão Maná pra "ficha" de pedido/cliente/ocorrência. Cada linha
        é (rótulo, valor) — rótulo vira UPPERCASE, valor é convertido pra str
        e truncado em `max_chars_valor`.

        Args:
            linhas: lista de tuplas (rotulo, valor).
            rotulo_cor: default = cinza_texto.
            valor_cor: default = preto_texto.
            rotulo_x_mm: X do rótulo (default = margem esquerda).
            valor_x_mm: X do valor em mm (default 75).
            max_chars_valor: trunca valor em N chars.
        """
        if not linhas:
            return
        rotulo_cor = rotulo_cor or CORES_MANA["cinza_texto"]
        valor_cor = valor_cor or CORES_MANA["preto_texto"]
        x_rotulo = rotulo_x_mm * mm if rotulo_x_mm is not None else self._margem_esquerda
        altura_linha = 8 * mm

        self._garantir_espaco(altura_linha * len(linhas) + 2 * mm)

        for rotulo, valor in linhas:
            self._c.setFillColor(rotulo_cor)
            self._c.setFont("Helvetica", 9)
            self._c.drawString(x_rotulo, self._y_atual, str(rotulo).upper())

            self._c.setFillColor(valor_cor)
            self._c.setFont("Helvetica-Bold", 11)
            self._c.drawString(
                valor_x_mm * mm,
                self._y_atual,
                str(valor)[:max_chars_valor],
            )
            self._y_atual -= altura_linha
        self._y_atual -= 2

    def drill_compacto(
        self,
        titulo: str,
        cabecalho: list[str],
        linhas_pai_filhos: list[tuple[str, list[list[Any]]]],
        larguras_mm: list[float] | None = None,
        max_filhos: int = 6,
        max_pais: int = 12,
    ) -> None:
        """
        Tabela compacta com drill: linha pai (1 valor) + N linhas filhos.

        Padrão Maná pra: pedidos x itens, vendedor x ocorrências, cliente x pedidos.

        Args:
            titulo: cabeçalho de seção em verde.
            cabecalho: ['PEDIDO', 'CULTIVAR', 'QTD', 'TOTAL']. 1ª coluna = chave do pai.
            linhas_pai_filhos: lista de (chave_pai, lista_filhos).
                Cada filho é list[Any] alinhado às colunas a partir da 2ª.
            larguras_mm: opcional — larguras por coluna.
            max_filhos: trunca filhos por pai.
            max_pais: trunca número de pais.
        """
        if not cabecalho or not linhas_pai_filhos:
            return

        # Título seção
        self._garantir_espaco(6 * mm)
        self._c.setFillColor(CORES_MANA["verde"])
        self._c.setFont("Helvetica-Bold", 10)
        self._c.drawString(self._margem_esquerda, self._y_atual, titulo)
        self._y_atual -= 6 * mm

        # Cabeçalho
        largura_util_mm = (self._margem_direita - self._margem_esquerda) / mm
        n = len(cabecalho)
        if larguras_mm is None or len(larguras_mm) != n:
            larguras_mm = [largura_util_mm / n] * n

        self._c.setFillColor(CORES_MANA["cinza_texto"])
        self._c.setFont("Helvetica-Bold", 8)
        x_cum = self._margem_esquerda
        for i, h in enumerate(cabecalho):
            if i == 0:
                self._c.drawString(x_cum, self._y_atual, str(h))
            else:
                self._c.drawRightString(x_cum + larguras_mm[i] * mm, self._y_atual, str(h))
            x_cum += larguras_mm[i] * mm
        self._y_atual -= 5 * mm

        # Linhas
        self._c.setFont("Helvetica", 9)
        self._c.setFillColor(CORES_MANA["preto_texto"])
        for pai, filhos in linhas_pai_filhos[:max_pais]:
            filhos = filhos or [[]]
            for idx, filho in enumerate(filhos[:max_filhos]):
                if self._y_atual < self._margem_inferior:
                    break
                x_cum = self._margem_esquerda
                # 1ª coluna = chave do pai (só na 1ª linha do pai)
                self._c.drawString(x_cum, self._y_atual, str(pai) if idx == 0 else "")
                x_cum += larguras_mm[0] * mm
                for i, celula in enumerate(filho[: n - 1]):
                    self._c.drawRightString(
                        x_cum + larguras_mm[i + 1] * mm,
                        self._y_atual,
                        str(celula),
                    )
                    x_cum += larguras_mm[i + 1] * mm
                self._y_atual -= 5 * mm
        self._y_atual -= 2

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
        _desenhar_rodape(
            self._c, self.agente, self._pagina,
            margem_mm=self.margem_mm,
            mostrar_pagina=self.mostrar_pagina_rodape,
        )
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
        _desenhar_rodape(
            self._c, self.agente, self._pagina,
            margem_mm=self.margem_mm,
            mostrar_pagina=self.mostrar_pagina_rodape,
        )
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
