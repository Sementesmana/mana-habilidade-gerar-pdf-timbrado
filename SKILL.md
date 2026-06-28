---
name: gerar-pdf-timbrado
description: Gera PDF com timbre canônico Maná (cabeçalho verde + ouro, rodapé, tabelas, parágrafos) via reportlab puro. Use SEMPRE que precisar gerar relatório PDF Maná em agente — substitui cabeçalho/rodapé copy-paste de 6 funções espalhadas em produção.
categoria: habilidades
owner: xayer-mana
versao-skill: 1.0.0
ultima-revisao: 2026-06-28
ativacao: [gerar-pdf, pdf-timbrado, pdf-mana, relatorio-pdf, cabecalho-mana, reportlab, pdf-cobrar, pdf-ocorrencia, pdf-variedade]
---

# gerar-pdf-timbrado (PDF Timbrado Maná)

> Habilidade canônica da Maná Builder pra gerar PDFs com **cabeçalho verde Maná**, **subtítulo ouro**, **rodapé com agente + paginação** e **tabelas/parágrafos** padronizados. Stack: `reportlab>=4.2` puro — sem Pillow, sem fonte externa, sem binário do SO.

## Quando usar

Sempre que um agente Maná precisar **gerar PDF** pra enviar via WhatsApp, anexar no SE, salvar no S3 ou disponibilizar via endpoint. Exemplos:

- `agente-gestor-comercial`: relatório de ocorrências por vendedor (botão "Cobrar")
- `agente-gestor-estoque`: PDF de posição de cultivar / resumo
- `agente-comite-credito`: ata de comitê
- `agente-premiacao`: relatório de ranking (futuro)

## O que faz

1. **Cabeçalho canônico** — retângulo verde 30 mm full-width com logo, título "Sementes Maná", subtítulo ouro, e 2 linhas de informação à direita.
2. **Rodapé canônico** — linha ouro 1.5pt + texto cinza "Gerado em DD/MM/YYYY HH:MM - {agente} - Sementes Maná LTDA" + numeração página.
3. **Parágrafos** — quebra de linha automática por largura útil.
4. **Tabelas** — cabeçalho verde + linhas alternadas (cinza claro) + larguras opcionais.
5. **Título de seção** — negrito + cor verde.
6. **Imagens** — `pdf.imagem(caminho, largura, altura)`.
7. **Quebra de página automática** — cursor monitora margem inferior e dispara `showPage` + redesenha cabeçalho.

## Input

```python
PDFMana(
    subtitulo: str,           # ouro abaixo do título
    direita_top: str,         # ex: "Gestor Comercial Mana"
    direita_bot: str,         # ex: "cockpit GRD"
    agente: str,              # vai no rodapé
    titulo: str = "Sementes Mana",
    altura_cabecalho_mm: float = 30,
)
```

## Output

```python
bytes_pdf: bytes = pdf.bytes()
```

PDF binário pronto pra `flask.send_file`, `requests.post(files=...)`, salvar em disco etc.

## Exemplo de uso

```python
from mana_habilidade_gerar_pdf_timbrado import PDFMana, gerar_pdf_tabela

# Caso 1 — atalho direto
pdf_bytes = gerar_pdf_tabela(
    subtitulo="Posição Estoque — 28/06/2026",
    agente="agente-gestor-estoque",
    direita_top="Gestor de Estoque Mana",
    cabecalho=["Cultivar", "Saldo (bag)", "Vendido %"],
    linhas=[
        ["76KA", "1500", "30%"],
        ["78KA", "850", "60%"],
    ],
)

# Caso 2 — classe (controle total)
pdf = PDFMana(
    subtitulo="Pareto Vendedores",
    direita_top="Gestor Comercial Mana",
    direita_bot="cockpit GRD",
    agente="agente-gestor-comercial",
)
pdf.titulo_secao("Resumo")
pdf.paragrafo("47 ocorrencias nos ultimos 7 dias...")
pdf.tabela(["Vendedor", "Casos"], [["Carlos", "12"], ["Ana", "9"]])
pdf.quebra_pagina()
pdf.titulo_secao("Plano de ação")
pdf.paragrafo("Reuniao 1:1 com top 3 ate sexta.")
bytes_pdf = pdf.bytes()
```

## Cores canônicas Maná (exportadas)

```python
from mana_habilidade_gerar_pdf_timbrado import CORES_MANA

CORES_MANA["verde"]         # #1D6B3E
CORES_MANA["verde_escuro"]  # #134d2c
CORES_MANA["ouro"]          # #B8860B
CORES_MANA["cinza_texto"]   # #545454
```

Use em qualquer customização interna pra manter coerência.

## Pré-requisitos

- Python ≥3.10
- `pip install "git+https://github.com/Sementesmana/mana-habilidade-gerar-pdf-timbrado.git@v0.1.0"`
- Sem dep de binário do SO (não precisa de poppler, tesseract, libcairo etc.)

## Limitações conhecidas

- **Logo é desenhada via reportlab** (2 anéis brancos concêntricos) — sem dep de arquivo PNG. Se o agente quiser logo customizada, use `pdf.imagem("logo.png", ...)` no corpo.
- **Fonte Helvetica nativa** — sem suporte a fontes customizadas (Poppins, DejaVu) ainda. Adicionar via `pdfmetrics.registerFont` num PR futuro se necessário.
- **Tabelas não suportam células multi-linha** (quebra automática). Pra texto longo, use `pdf.paragrafo()` antes/depois.
- **Sem chart inline** — pra gráficos, gere PNG separado (Pillow / matplotlib) e use `pdf.imagem(...)`.

## Como NÃO usar

- ❌ Não use pra **ler/extrair PDF** — use `mana-habilidade-extrair-pdf`.
- ❌ Não use pra **gerar PNG** (Painel de Vendas estilo gestor-estoque) — esse stack é Pillow, não reportlab.
- ❌ Não cole o cabeçalho copy-paste do PDF antigo no novo agente — use **esta habilidade** como source-of-truth.

## Integrações comuns

| Habilidade/SDK | Como combina |
|---|---|
| `mana-habilidade-pseudonimizar-pii` | Pseudonimizar dados ANTES de embutir no PDF se o PDF for compartilhado externamente. |
| `mana-habilidade-extrair-pdf` | Stack oposto — ler PDF de entrada vs gerar PDF de saída. |
| `WhatsAppClient` (porta única) | `zap.enviar_documento(para=..., url=...)` após salvar o PDF em URL. |

## Pseudonimização e LGPD

**Não toca PII direto** — recebe strings já preparadas pelo consumidor. Se o PDF for sair pra fora da rede Maná, o consumidor decide se pseudonimiza antes.

## Histórico

- **0.1.0** (2026-06-28): publicação inicial. 24 testes, 93% cobertura, ruff limpo. Extraído das 6 cópias inline em gestor-comercial (`pdf_ocorrencia.py` x4) + gestor-estoque (`pdf_variedade.py` x2). Padronizou cabeçalho em 30mm + corrigiu divergência do ouro (#B8860B canônico).

## Plano de migração (Fase 2)

| Agente | Status | Quem migra |
|---|---|---|
| [[../agente-gestor-comercial]] | ⏳ pendente | Xayer |
| [[../agente-gestor-estoque]] | ⏳ pendente | Xayer |
| Agentes futuros (comitê, ata, premiação PDF) | usar desde o início | — |

## Suporte

- Dono: @xayer-mana
- Repo: https://github.com/Sementesmana/mana-habilidade-gerar-pdf-timbrado
- Issues: usar a aba Issues do repo

## ADRs aplicáveis

- [[2026-06-24-plataforma-agentica-mana-5-camadas]]
- [[2026-06-26-mana-builder-matriz-cobertura]]
- [[2026-06-26-fluxo-criacao-habilidade-mana-builder]]
- [[2026-06-26-distribuicao-via-git-tag-pacotes-mana-builder]]
- [[2026-06-26-plugin-mana-skills-cowork]]
