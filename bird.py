import pygame
import random
from neural_network import NeuralNetwork

class Bird:
    def __init__(self, brain=None, is_player=False):
        self.x = 50
        self.y = 300
        self.width = 34
        self.height = 24
        self.gravity = 0.25
        self.lift = -6.5
        self.velocity = 0
        self.score = 0
        self.fitness = 0
        self.is_player = is_player
        self.lost = False
        
        if isinstance(brain, NeuralNetwork):
            self.brain = brain.copy()
        elif brain is None:
            self.brain = NeuralNetwork(5, 8, 1)
        else:
            self.brain = brain
    
    def think(self, pipes, canvas_height, canvas_width, pipe_width, pipe_gap):
        if self.is_player:
            return
        
        closest = None
        for pipe in pipes:
            if pipe['x'] + pipe_width > self.x:
                closest = pipe
                break
        
        if closest:
            inputs = [
                self.y / canvas_height,
                self.velocity / 10,
                closest['x'] / canvas_width,
                closest['top_height'] / canvas_height,
                (closest['top_height'] + pipe_gap) / canvas_height
            ]
        else:
            inputs = [self.y / canvas_height, self.velocity / 10, 0.5, 0.5, 0.5]
        
        if self.brain.predict(inputs) > 0.5:
            self.flap()
    
    def flap(self):
        self.velocity = self.lift
    
    def update(self):
        self.score += 1
        self.velocity += self.gravity
        self.y += self.velocity
    
    def draw(self, screen, color, text=''):
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        if text:
            font = pygame.font.Font(None, 16)
            text_color = (0, 0, 0) if color == (251, 191, 36) else (255, 255, 255)
            text_surface = font.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(text_surface, text_rect)
