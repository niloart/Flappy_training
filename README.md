# Flappy Bird AI - Versão Python

Este projeto é uma conversão do jogo Flappy Bird com IA treinada por algoritmos genéticos, originalmente em HTML/JavaScript, agora implementado em Python usando Pygame.

## 🚀 Instalação

1. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

2. **Execute o jogo:**

```bash
python flappy_bird_ai.py
```

## 🎮 Como Jogar

### Controles:

- **ESPAÇO** - Fazer o pássaro voar / Iniciar jogo
- **T** - Modo de treinamento da IA
- **P** - Jogar contra IA salva (se existir)
- **S** - Salvar a melhor IA atual
- **1/2** - Diminuir/Aumentar velocidade da simulação
- **Mouse** - Clique para interagir

### Modos de Jogo:

#### 🧠 Modo Treinamento:

- 50 pássaros são criados com cérebros aleatórios
- A cada geração, os melhores são selecionados para reprodução
- Use as teclas 1/2 para acelerar o treinamento
- Pressione S para salvar a melhor IA

#### 🎯 Modo Jogador vs IA:

- Compete contra a melhor IA treinada
- Use ESPAÇO para controlar seu pássaro
- Veja quem consegue o melhor score!

## 📁 Estrutura do Projeto

- `flappy_bird_ai.py` - Arquivo principal do jogo
- `neural_network.py` - Implementação da rede neural
- `bird.py` - Classe do pássaro
- `requirements.txt` - Dependências do projeto
- `best_flappy_brain.pkl` - IA salva (criado automaticamente)

## 🧠 Como Funciona a IA

### Rede Neural:

- **5 entradas**: posição Y, velocidade, posição X do cano, altura do cano superior/inferior
- **8 neurônios ocultos**: processamento
- **1 saída**: decisão de voar ou não

### Algoritmo Genético:

- **População**: 50 pássaros por geração
- **Seleção**: Baseada no fitness (score²)
- **Mutação**: 5% de chance de alterar pesos
- **Evolução**: Melhores pássaros geram próxima geração

## 🔧 Diferenças da Versão HTML

### Vantagens do Python:

- ✅ **Melhor Performance**: NumPy para cálculos matemáticos
- ✅ **Persistência**: Salvar/carregar IA em arquivo
- ✅ **Modularidade**: Código bem organizado em classes
- ✅ **Extensibilidade**: Fácil de adicionar novas funcionalidades
- ✅ **Controle de Transparência**: Melhor visualização da população

### Funcionalidades Equivalentes:

- ✅ **Treinamento de IA** com algoritmos genéticos
- ✅ **Modo competitivo** jogador vs IA
- ✅ **Controle de velocidade** da simulação
- ✅ **Interface visual** similar
- ✅ **Estatísticas** em tempo real

## 📊 Estatísticas Exibidas

- **Modo Treinamento**: Melhor Score, Geração, Pássaros Vivos
- **Modo Jogador**: Score do Jogador vs Score da IA
- **Velocidade**: Multiplicador da simulação

## 🎨 Personalização

Você pode facilmente modificar:

- **Cores** das diferentes entidades
- **Tamanho da população** (POPULATION_SIZE)
- **Taxa de mutação** (MUTATION_RATE)
- **Arquitetura da rede neural** (camadas e neurônios)
- **Física do jogo** (gravidade, força do pulo, etc.)

## 🛠️ Requisitos Técnicas

- **Python 3.7+**
- **Pygame 2.0+**
- **NumPy 1.20+**
- **4GB RAM** (recomendado)
- **Placa gráfica** básica para renderização

Divirta-se treinando sua própria IA! 🐦🤖
