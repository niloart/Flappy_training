import numpy as np
import pickle
import random

class NeuralNetwork:
    def __init__(self, input_nodes, hidden_nodes, output_nodes):
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes
        
        self.weights_ih = np.random.uniform(-1, 1, (self.hidden_nodes, self.input_nodes))
        self.weights_ho = np.random.uniform(-1, 1, (self.output_nodes, self.hidden_nodes))
    
    @staticmethod
    def _sigmoid(x):
        return 1 / (1 + np.exp(-x))

    def predict(self, input_array):
        # Convertendo a lista de entrada para um vetor de coluna numpy
        inputs = np.array(input_array, ndmin=2).T
        
        # Inputs para a camada oculta
        hidden_inputs = np.dot(self.weights_ih, inputs)
        hidden_outputs = self._sigmoid(hidden_inputs)
        
        # Camada oculta para a saída
        final_inputs = np.dot(self.weights_ho, hidden_outputs)
        final_outputs = self._sigmoid(final_inputs)
        
        return final_outputs[0, 0]
    
    def copy(self):
        new_nn = NeuralNetwork(self.input_nodes, self.hidden_nodes, self.output_nodes)
        new_nn.weights_ih = self.weights_ih.copy()
        new_nn.weights_ho = self.weights_ho.copy()
        return new_nn
    
    def mutate(self, rate):
        # Função de mutação que adiciona um pequeno valor aleatório
        def mutate_func(val):
            if random.random() < rate:
                return val + np.random.normal(0, 0.1)
            return val
        
        # Vetorizando a função para aplicar em toda a matriz de pesos
        vectorized_mutate = np.vectorize(mutate_func)
        self.weights_ih = vectorized_mutate(self.weights_ih)
        self.weights_ho = vectorized_mutate(self.weights_ho)
    
    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
