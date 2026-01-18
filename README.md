# O Professor — Plataforma de Gerenciamento e Venda de Livros Usados

## Visão Geral

**O Professor** é uma aplicação web desenvolvida para gerenciar e comercializar livros usados a partir de um acervo real, com foco em organização de dados, escalabilidade progressiva e separação clara entre camada de dados, API e interface.

O projeto foi concebido como uma solução prática para digitalizar um catálogo físico de livros, permitindo consulta, filtragem, promoções e simulação de compra em ambiente web.

Além do aspecto funcional, o sistema serve como estudo aplicado de arquitetura web leve, manipulação de dados estruturados e integração entre front-end e back-end.

---

## Objetivos do Projeto

- Digitalizar e estruturar um acervo físico de livros usados
- Implementar um catálogo consultável e dinâmico
- Criar uma API responsável pela entrega de dados
- Desenvolver uma interface funcional e extensível
- Aplicar boas práticas de organização, versionamento e padronização de dados
- Servir como projeto demonstrativo para portfólio técnico

---

## Arquitetura da Solução

A aplicação é organizada em três camadas principais:

### 1. Camada de Dados
Responsável pelo armazenamento e padronização das informações dos livros.

Características:
- Persistência baseada em arquivos JSON
- Estruturação por título, autor, gênero, preço e disponibilidade
- Controle rígido de categorias para evitar inconsistências
- Arquivos independentes para catálogo, promoções e combos

### 2. Camada de API
Responsável por fornecer os dados ao cliente.

Características:
- API REST simples hospedada no Render
- Endpoints para catálogo, promoções e combos
- Atualização manual controlada via repositório
- Estratégia de manutenção ativa em ambiente gratuito

### 3. Camada de Apresentação
Responsável pela experiência do usuário.

Características:
- Interface desenvolvida em HTML, CSS e JavaScript puro
- Renderização dinâmica baseada nos dados da API
- Sistema de carrinho persistente no navegador
- Exibição separada para catálogo e promoções
- Layout planejado para evolução futura

---

## Funcionalidades Implementadas

- Listagem dinâmica de livros disponíveis
- Sistema de carrinho de compras
- Gerenciamento de promoções individuais
- Sistema de combos com desconto percentual
- Persistência local de dados no cliente
- Sincronização manual entre base local e repositório
- Padronização de gêneros literários
- Estrutura preparada para expansão modular

---

## Tecnologias Utilizadas

- HTML5
- CSS3
- JavaScript (Vanilla)
- JSON
- Git
- GitHub Pages (Front-end)
- Render (Back-end)

---


