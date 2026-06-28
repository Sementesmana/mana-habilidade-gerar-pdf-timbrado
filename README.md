# mana-habilidade-gerar-pdf-timbrado

> Habilidade canônica da **Maná Builder** que gera PDFs com **timbre Maná** (cabeçalho verde + ouro + rodapé + tabelas) via `reportlab` puro.

[![status](https://img.shields.io/badge/status-beta-blue)]()
[![version](https://img.shields.io/badge/version-0.1.0-green)]()
[![python](https://img.shields.io/badge/python-%3E%3D3.10-blue)]()

## Por que existe

6 funções de cabeçalho/rodapé copy-paste em 2 agentes hoje:
- `agente-gestor-comercial`: `pdf_ocorrencia.py` com 4 funções (ocorrência, vendedor, geral, cliente)
- `agente-gestor-estoque`: `pdf_variedade.py` com 2 funções (variedade, resumo)

Esta habilidade substitui tudo isso com 1 classe `PDFMana` + 2 atalhos.

## Instalação

```bash
pip install "git+https://github.com/Sementesmana/mana-habilidade-gerar-pdf-timbrado.git@v0.1.0"
```

(GitHub Packages PyPI foi descontinuado em 2024 — padrão Maná é git tag + git+https.)

## Uso rápido

```python
from mana_habilidade_gerar_pdf_timbrado import PDFMana, gerar_pdf_simples, gerar_pdf_tabela

# Atalho 1 — texto
pdf_bytes = gerar_pdf_simples(
    subtitulo="Pareto · 28/06/2026",
    agente="agente-gestor-comercial",
    paragrafos=["Resumo do dia...", "Detalhes adicionais..."],
)

# Atalho 2 — tabela
pdf_bytes = gerar_pdf_tabela(
    subtitulo="Posição Estoque",
    agente="agente-gestor-estoque",
    cabecalho=["Cultivar", "Saldo", "Vendido %"],
    linhas=[["76KA", "1500", "30%"], ["78KA", "850", "60%"]],
)

# Classe (controle fino)
pdf = PDFMana(subtitulo="X", agente="agente-Y")
pdf.titulo_secao("Resumo")
pdf.paragrafo("...")
pdf.tabela(headers, linhas)
pdf.quebra_pagina()
pdf.imagem("chart.png", largura=160, altura=80)
pdf_bytes = pdf.bytes()
```

## API

### `PDFMana(subtitulo, direita_top, direita_bot, agente, titulo, altura_cabecalho_mm)`

- `.paragrafo(texto, fonte="Helvetica", tamanho=10)` — parágrafo com quebra automática
- `.titulo_secao(texto)` — título verde negrito
- `.tabela(cabecalho, linhas, larguras_mm=None)` — tabela com cabeçalho verde + linhas alternadas
- `.imagem(caminho, largura, altura)` — insere imagem (PNG/JPG)
- `.quebra_pagina()` — `showPage` + redesenha cabeçalho
- `.bytes()` — finaliza e retorna `bytes`

### `gerar_pdf_simples(subtitulo, agente, paragrafos, direita_top, direita_bot, titulo)`

Atalho — PDF com cabeçalho + N parágrafos.

### `gerar_pdf_tabela(subtitulo, agente, cabecalho, linhas, larguras_mm, direita_top, direita_bot, titulo, paragrafo_antes)`

Atalho — PDF com (opcional) parágrafo + tabela.

### `CORES_MANA`

Dict com cores reportlab canônicas Maná: `verde`, `verde_escuro`, `ouro`, `cinza_texto`, `cinza_claro`, `branco`.

## Decisões de padronização

Esta habilidade resolve 3 divergências que existiam entre as 6 cópias inline:

| Divergência | Decisão canônica |
|---|---|
| Altura cabeçalho 30 vs 32 mm | **30 mm** (mais elegante) |
| Ouro #B8860B (PDF) vs #B08420 (PNG) | **#B8860B** (CSS oficial Maná) |
| Logo arquivo externo vs inline | **Desenhada inline** (2 anéis brancos) — sem dep de PNG |

## Dependências

Apenas `reportlab>=4.2`. Sem Pillow, sem fonte externa, sem binário do SO. Roda direto no Railway sem buildpack adicional.

## Comportamento defensivo

- **Parágrafo vazio** → no-op (não estoura).
- **Cabeçalho vazio na tabela** → no-op.
- **Quebra de página automática** quando cursor passa da margem inferior (25 mm).
- **None nas células** convertido pra `""` automaticamente.

## Desenvolvimento

```bash
git clone https://github.com/Sementesmana/mana-habilidade-gerar-pdf-timbrado
cd mana-habilidade-gerar-pdf-timbrado
pip install -e ".[dev]"
pytest                 # 24 testes, 93% cobertura
ruff check src tests   # lint limpo
```

## Versionamento

Semver. Bumpar versão em `pyproject.toml`, `__init__.py` e `manifest.yaml`, commitar, taggar e pushar.

## Suporte

- Dono: @xayer-mana
- Issues: https://github.com/Sementesmana/mana-habilidade-gerar-pdf-timbrado/issues
- Skill canônica no Cowork: `gerar-pdf-timbrado` (após merge em `Sementesmana/plugin-mana-skills`)

## ADRs aplicáveis

- [2026-06-24 — plataforma agêntica 5 camadas](https://github.com/Sementesmana/mana-vault/blob/main/08-Decisoes/2026-06-24-plataforma-agentica-mana-5-camadas.md)
- [2026-06-26 — Maná Builder + Matriz](https://github.com/Sementesmana/mana-vault/blob/main/08-Decisoes/2026-06-26-mana-builder-matriz-cobertura.md)
- [2026-06-26 — fluxo de criação de habilidade](https://github.com/Sementesmana/mana-vault/blob/main/08-Decisoes/2026-06-26-fluxo-criacao-habilidade-mana-builder.md)
- [2026-06-26 — distribuição via git tag](https://github.com/Sementesmana/mana-vault/blob/main/08-Decisoes/2026-06-26-distribuicao-via-git-tag-pacotes-mana-builder.md)
- [2026-06-26 — plugin Maná Skills no Cowork](https://github.com/Sementesmana/mana-vault/blob/main/08-Decisoes/2026-06-26-plugin-mana-skills-cowork.md)

---

*Sementes Maná LTDA · 2026*
