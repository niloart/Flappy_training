# Explicação Detalhada do Algoritmo Genético no Flappy Bird AI

Este documento detalha a implementação do Algoritmo Genético (AG) utilizado para treinar os pássaros neste projeto. O objetivo do AG é simular o processo de evolução natural para encontrar uma solução ótima para um problema - neste caso, a "solução ótima" é uma rede neural capaz de jogar Flappy Bird eficientemente.

## Conceitos Fundamentais do Algoritmo Genético

Um Algoritmo Genético opera com base em alguns conceitos-chave, todos presentes nesta implementação:

- **População**: Um conjunto de indivíduos (soluções candidatas). No nosso caso, uma população de pássaros.
- **Cromossomo/Genes**: As características de um indivíduo. Para cada pássaro, seu "cromossomo" é a sua rede neural, e os "genes" são os pesos sinápticos dessa rede.
- **Função de Fitness**: Uma forma de medir quão "boa" é uma solução. Pássaros que sobrevivem por mais tempo têm um fitness maior.
- **Seleção**: O processo de escolher quais indivíduos irão se reproduzir para formar a próxima geração. Os mais "aptos" têm maior probabilidade de serem selecionados.
- **Reprodução (Crossover)**: A combinação de genes de dois ou mais pais para criar descendentes.
- **Mutação**: Pequenas alterações aleatórias nos genes de um descendente, que introduzem nova diversidade na população.

## Implementação no Jogo

Vamos detalhar como cada um desses conceitos foi implementado no código.

### 1. População e Indivíduos

- Quando o treinamento começa, uma população inicial de pássaros é criada. A variável `self.active_birds` armazena essa lista.
- Cada `Bird` é um **indivíduo**. Dentro da classe `Bird` (arquivo `bird.py`), cada pássaro inicializa seu próprio "cérebro", que é uma instância da `NeuralNetwork`.
- Os **genes** de cada pássaro são os pesos nas matrizes `weights_ih` (input-hidden) e `weights_ho` (hidden-output) de sua rede neural.

### 2. Função de Fitness

- Após todos os pássaros de uma geração morrerem (sendo movidos de `active_birds` para `saved_birds`), o fitness de cada um é calculado.
  1.  **Cálculo do Score**: O `score` de cada pássaro é simplesmente o número de frames que ele sobreviveu.
  2.  **Normalização**: Para evitar que scores muito altos dominem completamente a seleção, o `score` é elevado ao quadrado (`score ** 2`). Isso dá um peso maior para os melhores, mas ainda permite que os "medianos" tenham uma chance.
  3.  **Cálculo do Fitness**: O fitness final de um pássaro é o seu score ao quadrado dividido pelo somatório do score ao quadrado de toda a população. Isso normaliza os valores, fazendo com que a soma de todos os fitness seja 1.
  4.  **Fitness Aprimorado (Opcional)**: Se ativado, o cálculo do score é modificado para recompensar pássaros que passam por canos, incentivando um comportamento mais "inteligente" do que apenas sobreviver.

### 3. Seleção (Roleta)

- O método implementa a "Seleção por Roleta". Imagine uma roleta onde cada pássaro da geração anterior ocupa um espaço proporcional ao seu fitness. Pássaros com maior fitness têm um espaço maior.
  - Um número aleatório (`r`) entre 0 e 1 é gerado.
  - O código itera pela lista de pássaros salvos (ordenada por fitness) e subtrai o fitness de cada pássaro de `r`.
  - O primeiro pássaro que faz `r` se tornar menor ou igual a zero é o escolhido.
  - Isso garante que indivíduos com maior fitness tenham uma probabilidade maior de serem selecionados como "pais" para a próxima geração.

### 4. Reprodução e Mutação

- O processo de criação da nova geração é o seguinte:
  1.  Um "pai" é selecionado usando o método `_pick_one`.
  2.  Um novo pássaro ("filho") é criado, recebendo uma **cópia exata** do cérebro do pai. Nesta implementação, não há _crossover_ (combinação de dois pais), a diversidade vem da mutação.
  3.  O cérebro do filho passa por um processo de **mutação**.
  4.  O método `mutate` (em `neural_network.py`) percorre cada peso da rede neural. Para cada peso, há uma chance (definida pela `MUTATION_RATE`) de que ele seja ligeiramente modificado, somando-se a ele um pequeno valor aleatório. É essa mutação que permite a exploração de novas "estratégias" de voo.

### 5. Melhorias Opcionais

- **Elitismo**: Se ativado, uma pequena porcentagem dos melhores indivíduos da geração anterior é copiada para a próxima geração **sem sofrer mutação**. Isso garante que o melhor desempenho alcançado até então nunca seja perdido.
- **Mutação Adaptativa**: Se ativada, a `MUTATION_RATE` não é fixa. Se o melhor score da população não melhora por algumas gerações (estagnação), a taxa de mutação aumenta para incentivar maior exploração. Se o score melhora, a taxa diminui para refinar as boas soluções encontradas.

## O Ciclo Completo

O processo se repete a cada geração, formando um ciclo de evolução:

1.  **Início**: Uma população aleatória é criada.
2.  **Simulação**: Todos os pássaros jogam até morrer.
3.  **Avaliação**: O fitness de cada pássaro é calculado com base em seu desempenho.
4.  **Seleção e Reprodução**: Os melhores pássaros são selecionados para gerar a próxima população. Seus cérebros são copiados e sofrem mutações.
5.  **Repetição**: A nova geração, que é sutilmente diferente e potencialmente melhor que a anterior, inicia a simulação novamente.

Ao longo de centenas de gerações, esse processo de seleção e mutação gradualmente "esculpe" as redes neurais, resultando em pássaros que são especialistas em desviar dos canos.

---

## Perguntas e Respostas sobre a Implementação

Aqui estão as respostas diretas para as perguntas comuns sobre o design deste Algoritmo Genético:

#### O que você está otimizando?

Estamos otimizando a **estratégia de jogo** de um agente (o pássaro). O objetivo final é encontrar a configuração ideal para a rede neural do pássaro, permitindo que ele desvie dos canos de forma eficiente e, consequentemente, sobreviva o maior tempo possível.

#### Qual é a variável que quer maximizar ou minimizar?

A variável principal a ser **maximizada** é a **pontuação (score)** de cada pássaro, que é diretamente proporcional ao seu tempo de sobrevivência em frames. Secundariamente, ao ativar a opção "Fitness Aprimorado", também buscamos maximizar o **número de canos ultrapassados**, o que incentiva um comportamento mais proativo e menos passivo.

#### Qual é a representação da solução (genoma)?

A representação da solução, ou o **genoma** de cada pássaro, é o conjunto de todos os **pesos sinápticos** de sua rede neural. Estes pesos são armazenados em duas matrizes NumPy: `weights_ih` (pesos da camada de entrada para a camada oculta) e `weights_ho` (pesos da camada oculta para a camada de saída).

#### Qual é a função de fitness?

A função de fitness quantifica o sucesso de cada pássaro. O `score` (frames sobrevividos) é elevado ao quadrado para dar mais ênfase aos melhores desempenhos. O fitness final é este valor normalizado pela soma dos scores ao quadrado de toda a população. A fórmula é: `fitness = (score²) / Σ(todos_os_scores²)`.

#### Qual é o método de seleção?

O método de seleção utilizado é a **Seleção por Roleta (Roulette Wheel Selection)**. Cada indivíduo da população ocupa um espaço na "roleta" proporcional ao seu valor de fitness. Isso significa que indivíduos mais aptos têm uma probabilidade maior de serem selecionados para a reprodução, mas não é uma garantia, o que ajuda a manter a diversidade genética.

#### Qual método de crossover você vai implementar?

Nesta implementação, **não há um método de crossover** (reprodução sexuada). A reprodução é assexuada: um único "pai" é selecionado, e seu genoma (os pesos da rede neural) é clonado para criar um "filho". A diversidade genética na nova geração é introduzida exclusivamente através do processo de **mutação**.

#### Qual será o método de inicialização?

O método de inicialização é a **criação de uma população com genomas aleatórios**. Para cada pássaro na primeira geração, as matrizes de pesos de sua rede neural são preenchidas com valores aleatórios uniformemente distribuídos no intervalo [-1, 1].

#### Qual o critério de parada?

O treinamento **não possui um critério de parada automático**. Ele é projetado para rodar indefinidamente, geração após geração, permitindo que o usuário observe a evolução. O critério de parada é **manual**: o usuário decide quando a IA atingiu um nível de desempenho satisfatório e pode então salvar o melhor cérebro (tecla `S`) ou simplesmente fechar o programa (tecla `ESC`).
