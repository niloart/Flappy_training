import pygame
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
        
        # Atributos para fitness aprimorado
        self.pipes_passed = 0
        
        if isinstance(brain, NeuralNetwork):
            self.brain = brain.copy()
        else:
            self.brain = NeuralNetwork(5, 8, 1)

    def think(self, pipes, canvas_height, canvas_width):
        if self.is_player:
            return

        closest_pipe = self._find_closest_pipe(pipes)
        
        if closest_pipe:
            pipe_width = 52 # TODO: Obter de uma config
            pipe_gap = 180 # TODO: Obter de uma config
            inputs = [
                self.y / canvas_height,
                self.velocity / 10,
                closest_pipe['x'] / canvas_width,
                closest_pipe['top_height'] / canvas_height,
                (closest_pipe['top_height'] + pipe_gap) / canvas_height
            ]
        else:
            # Valores padrão quando não há canos
            inputs = [self.y / canvas_height, self.velocity / 10, 0.5, 0.5, 0.5]
        
        if self.brain.predict(inputs) > 0.5:
            self.flap()

    def _find_closest_pipe(self, pipes):
        """Encontra o cano mais próximo à frente do pássaro."""
        for pipe in pipes:
            pipe_width = 52 # TODO: Obter de uma config
            if pipe['x'] + pipe_width > self.x:
                return pipe
        return None

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

    def is_offscreen(self, game_height, ground_height):
        """Verifica se o pássaro saiu da tela (chão ou teto)."""
        return self.y + self.height > game_height - ground_height or self.y < 0

    def collides_with(self, pipe, pipe_gap):
        """Verifica se o pássaro colide com um cano específico."""
        pipe_width = 52 # TODO: Obter de uma config
        if (self.x < pipe['x'] + pipe_width and 
            self.x + self.width > pipe['x'] and
            (self.y < pipe['top_height'] or 
             self.y + self.height > pipe['top_height'] + pipe_gap)):
            return True
        return False
