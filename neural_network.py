import numpy as np
import pickle
import random

class Matrix:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.data = np.zeros((rows, cols))
    
    @staticmethod
    def from_array(arr):
        m = Matrix(len(arr), 1)
        for i in range(len(arr)):
            m.data[i][0] = arr[i]
        return m
    
    @staticmethod
    def multiply(a, b):
        if a.cols != b.rows:
            raise ValueError("Columns of A must match rows of B")
        result = Matrix(a.rows, b.cols)
        result.data = np.dot(a.data, b.data)
        return result
    
    def randomize(self):
        self.data = np.random.uniform(-1, 1, (self.rows, self.cols))
    
    def map_function(self, func):
        self.data = np.vectorize(func)(self.data)

class NeuralNetwork:
    def __init__(self, input_nodes, hidden_nodes, output_nodes):
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes
        
        self.weights_ih = Matrix(self.hidden_nodes, self.input_nodes)
        self.weights_ho = Matrix(self.output_nodes, self.hidden_nodes)
        
        self.weights_ih.randomize()
        self.weights_ho.randomize()
    
    def predict(self, input_array):
        # Inputs to hidden layer
        inputs = Matrix.from_array(input_array)
        hidden = Matrix.multiply(self.weights_ih, inputs)
        
        # Activation function (sigmoid)
        hidden.map_function(lambda x: 1 / (1 + np.exp(-x)))
        
        # Hidden to output
        output = Matrix.multiply(self.weights_ho, hidden)
        output.map_function(lambda x: 1 / (1 + np.exp(-x)))
        
        return output.data[0][0]
    
    def copy(self):
        new_nn = NeuralNetwork(self.input_nodes, self.hidden_nodes, self.output_nodes)
        new_nn.weights_ih.data = self.weights_ih.data.copy()
        new_nn.weights_ho.data = self.weights_ho.data.copy()
        return new_nn
    
    def mutate(self, rate):
        def mutate_func(val):
            if random.random() < rate:
                return val + random.uniform(-0.1, 0.1)
            return val
        
        self.weights_ih.map_function(mutate_func)
        self.weights_ho.map_function(mutate_func)
    
    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
