# Flappy Bird com Evolução de IA

Este projeto é uma implementação do clássico jogo Flappy Bird, com um foco especial em treinar uma Inteligência Artificial (IA) para jogar o jogo de forma autônoma usando um algoritmo genético e redes neurais. Além do modo de treinamento, é possível competir contra a melhor IA já treinada.

## Funcionalidades

- **Modo de Treinamento de IA**: Assista a uma população de pássaros evoluir a cada geração para se tornarem melhores em desviar dos canos.
- **Modo Jogador vs. IA**: Jogue contra a melhor IA que você treinou e salvou.
- **Algoritmo Genético Avançado**:
  - **Elitismo**: Preserva os melhores indivíduos da geração anterior, garantindo que o progresso não seja perdido.
  - **Mutação Adaptativa**: A taxa de mutação se ajusta dinamicamente. Se a população estagnar, a mutação aumenta para explorar novas soluções. Se houver progresso, ela diminui para refinar as soluções existentes.
  - **Fitness Aprimorado**: O cálculo de "quão bom" um pássaro é não se baseia apenas na distância percorrida, mas também recompensa cada cano ultrapassado.
- **Controles Interativos**: Ajuste parâmetros como tamanho da população, taxa de mutação e velocidade da simulação em tempo real.
- **Visualização Clara**: Uma interface gráfica mostra estatísticas detalhadas, controles e o status do treinamento ou do jogo.

## Como Funciona

O núcleo da IA é a combinação de uma **Rede Neural** com um **Algoritmo Genético**.

### 1. Rede Neural

Cada pássaro possui seu próprio "cérebro", que é uma rede neural simples. A rede recebe 5 informações (entradas) sobre o ambiente:

1.  **Posição Y do pássaro**: A altura do pássaro na tela.
2.  **Velocidade vertical do pássaro**: Se está subindo ou descendo e com que rapidez.
3.  **Posição X do próximo cano**: A distância horizontal até o próximo obstáculo.
4.  **Altura do topo do próximo cano**: A posição do obstáculo superior.
5.  **Altura da base do próximo cano**: A posição do obstáculo inferior.

Com base nessas entradas, a rede neural calcula uma única saída: a decisão de pular (`flap`) ou não.

### 2. Algoritmo Genético

O treinamento ocorre através de um processo de seleção natural simulado, geração após geração:

1.  **População Inicial**: O jogo começa com uma população de pássaros (`50` por padrão), cada um com uma rede neural aleatória.
2.  **Avaliação (Fitness)**: Todos os pássaros jogam simultaneamente. A "pontuação de fitness" de cada um é calculada com base em quão longe eles chegaram.
3.  **Seleção**: Quando todos os pássaros morrem, o algoritmo seleciona os "pais" da próxima geração. Pássaros com maior pontuação de fitness têm mais chances de serem escolhidos.
4.  **Reprodução e Mutação**: Uma nova população é criada a partir dos cérebros dos pais selecionados. Cada cérebro copiado passa por um processo de **mutação**, onde pequenos ajustes aleatórios são feitos em seus pesos. É essa mutação que permite que novas "estratégias" de voo surjam.
5.  **Repetição**: O ciclo recomeça com a nova geração. Ao longo de centenas de gerações, os pássaros evoluem para se tornarem especialistas em desviar dos canos.

## Como Executar

### Pré-requisitos

- Python 3.x
- `pip` (gerenciador de pacotes do Python)

### Passos

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/niloart/Flappy_training.git
    cd Flappy_training
    ```

2.  **Instale as dependências:**
    O projeto utiliza `pygame` e `numpy`. Instale-os a partir do arquivo `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute o jogo:**
    ```bash
    python flappy_bird_ai.py
    ```

## Controles

A interface exibe a maioria dos controles, mas aqui está uma lista completa:

### Controles Gerais

- **ESC**: Fecha o jogo.
- **T**: Inicia o modo de **Treinamento de IA**.
- **P**: Inicia o modo **Jogador vs. IA** (requer um arquivo `best_flappy_brain.pkl` salvo).
- **ESPAÇO**: Inicia o jogo (na tela inicial) ou faz o pássaro do jogador pular (no modo de jogo).

### Controles do Modo de Treinamento

- **S**: Salva o cérebro do melhor pássaro da população atual no arquivo `best_flappy_brain.pkl`.
- **R**: Reinicia o treinamento do zero (nova Geração 1).
- **D**: Alterna entre desenhar todos os pássaros ou apenas o melhor da geração atual.
- **1 / 2**: Diminui / Aumenta a velocidade da simulação.

### Ajustes do Algoritmo Genético (em tempo real)

- **F**: Ativa/Desativa o **Fitness Aprimorado**.
- **E**: Ativa/Desativa o **Elitismo**.
- **A**: Ativa/Desativa a **Mutação Adaptativa**.
- **SETA PARA CIMA / BAIXO**: Aumenta / Diminui o tamanho da população.
- **SETA PARA DIREITA / ESQUERDA**: Aumenta / Diminui a taxa de mutação base.

## Estrutura dos Arquivos

- **`flappy_bird_ai.py`**: O arquivo principal que contém a lógica do jogo, a interface gráfica, o loop de eventos e a implementação do algoritmo genético.
- **`bird.py`**: Define a classe `Bird`, que representa um único pássaro (seja IA ou jogador). Contém sua física, estado e a lógica para interagir com sua rede neural.
- **`neural_network.py`**: Define a classe `NeuralNetwork`. É o "cérebro" de cada pássaro, responsável por tomar a decisão de pular.
- **`requirements.txt`**: Lista as bibliotecas Python necessárias para rodar o projeto.
- **`best_flappy_brain.pkl`**: Arquivo gerado quando você salva a melhor IA. Ele armazena o estado da rede neural do melhor pássaro.
- **`README.md`**: Este arquivo.

### Integrantes do Grupo

- João Pedro Noleto – RA: 363789
- Danilo Almeida de Sousa – RA: 362639
- Allan dos Santos – RA: 362388
- Thiago Silva França – RA: 361249
- Emerson Luis Saturnino  – RA: 362286
