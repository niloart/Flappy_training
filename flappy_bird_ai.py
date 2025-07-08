import pygame
import random
import math
import os
from bird import Bird
from neural_network import NeuralNetwork

class FlappyBirdAI:
    def __init__(self):
        pygame.init()
        
        # Configurações da tela
        self.GAME_WIDTH = 400
        self.GAME_HEIGHT = 600
        self.UI_PANEL_WIDTH = 300
        self.UI_PANEL_HEIGHT = 100
        self.CANVAS_WIDTH = self.GAME_WIDTH + self.UI_PANEL_WIDTH
        self.CANVAS_HEIGHT = self.GAME_HEIGHT + self.UI_PANEL_HEIGHT
        self.screen = pygame.display.set_mode((self.CANVAS_WIDTH, self.CANVAS_HEIGHT))
        pygame.display.set_caption("Flappy Bird: Evolução de IA vs. Jogador")
        
        # Cores
        self.BACKGROUND_COLOR = (26, 32, 44)
        self.SKY_COLOR = (135, 206, 235)
        self.PIPE_COLOR = (34, 139, 34)
        self.GROUND_COLOR = (222, 184, 135)
        self.PLAYER_COLOR = (251, 191, 36)  # Dourado
        self.AI_COLOR = (59, 130, 246)      # Azul
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.GREEN = (34, 197, 94)
        self.RED = (239, 68, 68)
        
        # Configurações do jogo
        self.POPULATION_SIZE = 50
        self.MUTATION_RATE = 0.05
        self.PIPE_WIDTH = 52
        self.PIPE_GAP = 180
        self.PIPE_SPAWN_RATE = 100
        self.GROUND_HEIGHT = 20
        
        # Áreas da interface
        self.game_rect = pygame.Rect(0, 0, self.GAME_WIDTH, self.GAME_HEIGHT)
        self.ui_panel_rect = pygame.Rect(self.GAME_WIDTH, 0, self.UI_PANEL_WIDTH, self.CANVAS_HEIGHT)
        self.bottom_panel_rect = pygame.Rect(0, self.GAME_HEIGHT, self.GAME_WIDTH, self.UI_PANEL_HEIGHT)
        
        # Estado do jogo
        self.pipes = []
        self.active_birds = []
        self.saved_birds = []
        self.player_bird = None
        self.ai_opponent = None
        self.frame_count = 0
        self.generation = 1
        self.best_score = 0
        self.game_state = 'start'  # 'start', 'training', 'playing', 'game_over'
        self.simulation_speed = 1
        self.draw_all_birds = True
        
        # Fontes
        self.font_title = pygame.font.Font(None, 42)
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 16)
        
        # Clock para controle de FPS
        self.clock = pygame.time.Clock()
        
        # Arquivo para salvar melhor IA
        self.save_file = "best_flappy_brain.pkl"
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.handle_input()
                elif event.key == pygame.K_t and self.game_state in ['start', 'game_over']:
                    self.switch_mode('training')
                elif event.key == pygame.K_p and os.path.exists(self.save_file):
                    self.switch_mode('playing')
                elif event.key == pygame.K_s and self.game_state == 'training':
                    self.save_best_ai()
                elif event.key == pygame.K_r and self.game_state == 'training':
                    self.switch_mode('training', force_restart=True)
                elif event.key == pygame.K_d and self.game_state == 'training':
                    self.draw_all_birds = not self.draw_all_birds
                elif event.key == pygame.K_1:
                    self.simulation_speed = max(1, self.simulation_speed - 1)
                elif event.key == pygame.K_2:
                    self.simulation_speed = min(10, self.simulation_speed + 1)
                elif event.key == pygame.K_UP and self.game_state in ['start', 'training', 'game_over']:
                    self.POPULATION_SIZE = min(500, self.POPULATION_SIZE + 10)
                elif event.key == pygame.K_DOWN and self.game_state in ['start', 'training', 'game_over']:
                    self.POPULATION_SIZE = max(10, self.POPULATION_SIZE - 10)
                elif event.key == pygame.K_RIGHT and self.game_state in ['start', 'training', 'game_over']:
                    self.MUTATION_RATE = min(1.0, round(self.MUTATION_RATE + 0.01, 2))
                elif event.key == pygame.K_LEFT and self.game_state in ['start', 'training', 'game_over']:
                    self.MUTATION_RATE = max(0.0, round(self.MUTATION_RATE - 0.01, 2))
                elif event.key == pygame.K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_input()
        
        return True
    
    def handle_input(self):
        if self.game_state == 'start':
            self.switch_mode('training')
        elif self.game_state == 'playing' and self.player_bird and not self.player_bird.lost:
            self.player_bird.flap()
        elif self.game_state == 'game_over':
            if hasattr(self, 'ai_opponent') and self.ai_opponent:
                self.switch_mode('playing')
            else:
                self.switch_mode('training')
    
    def switch_mode(self, mode, force_restart=False):
        self.pipes = []
        self.frame_count = 0
        
        if mode == 'training':
            self.game_state = 'training'
            if force_restart or (len(self.active_birds) == 0 and len(self.saved_birds) == 0):
                self.generation = 1
                self.best_score = 0
                self.active_birds = [Bird() for _ in range(self.POPULATION_SIZE)]
                self.saved_birds = []
                random.seed(42) # Semente fixa para canos previsíveis
        elif mode == 'playing':
            if not os.path.exists(self.save_file):
                print("Nenhuma IA salva encontrada. Treine uma primeiro!")
                return
            
            self.game_state = 'playing'
            self.player_bird = Bird(is_player=True)
            try:
                saved_brain = NeuralNetwork.load(self.save_file)
                self.ai_opponent = Bird(saved_brain, is_player=False)
            except:
                print("Erro ao carregar IA salva!")
                return
            self.active_birds = []
    
    def save_best_ai(self):
        best_bird = self.find_best_bird()
        if best_bird:
            best_bird.brain.save(self.save_file)
            print("Melhor IA salva!")
    
    def next_generation(self):
        self.generation += 1
        self.calculate_fitness()
        self.active_birds = []
        
        for _ in range(self.POPULATION_SIZE):
            self.active_birds.append(self.pick_one())
        
        self.saved_birds = []
        self.pipes = []
        self.frame_count = 0
    
    def pick_one(self):
        index = 0
        r = random.random()
        
        while r > 0 and index < len(self.saved_birds):
            r -= self.saved_birds[index].fitness
            index += 1
        
        index = max(0, min(index - 1, len(self.saved_birds) - 1))
        bird = self.saved_birds[index]
        child = Bird(bird.brain)
        child.brain.mutate(self.MUTATION_RATE)
        return child
    
    def calculate_fitness(self):
        total_score = sum(bird.score ** 2 for bird in self.saved_birds)
        
        if total_score == 0:
            for bird in self.saved_birds:
                bird.fitness = 1 / len(self.saved_birds)
        else:
            for bird in self.saved_birds:
                bird.fitness = (bird.score ** 2) / total_score
    
    def find_best_bird(self):
        if self.active_birds:
            return max(self.active_birds, key=lambda b: b.score)
        elif self.saved_birds:
            return max(self.saved_birds, key=lambda b: b.score)
        return None
    
    def update_pipes(self):
        if self.frame_count % self.PIPE_SPAWN_RATE == 0:
            top_height = random.randint(50, self.GAME_HEIGHT - self.PIPE_GAP - 100)
            self.pipes.append({'x': self.GAME_WIDTH, 'top_height': top_height})
        
        for pipe in self.pipes:
            pipe['x'] -= 2
        
        self.pipes = [pipe for pipe in self.pipes if pipe['x'] + self.PIPE_WIDTH > 0]
    
    def check_collision(self, bird):
        # Colisão com chão ou teto
        if bird.y + bird.height > self.GAME_HEIGHT - self.GROUND_HEIGHT or bird.y < 0:
            return True
        
        # Colisão com canos
        for pipe in self.pipes:
            if (bird.x < pipe['x'] + self.PIPE_WIDTH and 
                bird.x + bird.width > pipe['x'] and 
                (bird.y < pipe['top_height'] or 
                 bird.y + bird.height > pipe['top_height'] + self.PIPE_GAP)):
                return True
        
        return False
    
    def update_game(self):
        for _ in range(self.simulation_speed):
            self.frame_count += 1
            self.update_pipes()
            
            if self.game_state == 'training':
                if len(self.active_birds) == 0:
                    self.next_generation()
                
                for i in range(len(self.active_birds) - 1, -1, -1):
                    bird = self.active_birds[i]
                    bird.think(self.pipes, self.GAME_HEIGHT, self.GAME_WIDTH, 
                             self.PIPE_WIDTH, self.PIPE_GAP)
                    bird.update()
                    
                    if self.check_collision(bird):
                        self.saved_birds.append(self.active_birds.pop(i))
            
            elif self.game_state == 'playing':
                if not self.player_bird.lost:
                    self.player_bird.update()
                    if self.check_collision(self.player_bird):
                        self.player_bird.lost = True
                
                if not self.ai_opponent.lost:
                    self.ai_opponent.think(self.pipes, self.GAME_HEIGHT, self.GAME_WIDTH,
                                         self.PIPE_WIDTH, self.PIPE_GAP)
                    self.ai_opponent.update()
                    if self.check_collision(self.ai_opponent):
                        self.ai_opponent.lost = True
                
                if self.player_bird.lost and self.ai_opponent.lost:
                    self.game_state = 'game_over'
    
    def draw_pipes(self):
        for pipe in self.pipes:
            # Cano superior
            pygame.draw.rect(self.screen, self.PIPE_COLOR, 
                           (pipe['x'], 0, self.PIPE_WIDTH, pipe['top_height']))
            # Cano inferior
            pygame.draw.rect(self.screen, self.PIPE_COLOR,
                           (pipe['x'], pipe['top_height'] + self.PIPE_GAP, 
                            self.PIPE_WIDTH, self.GAME_HEIGHT - pipe['top_height'] - self.PIPE_GAP))
    
    def draw_ground(self):
        pygame.draw.rect(self.screen, self.GROUND_COLOR,
                        (0, self.GAME_HEIGHT - self.GROUND_HEIGHT, 
                         self.GAME_WIDTH, self.GROUND_HEIGHT))
    
    def draw_ui_panel(self):
        # Painel lateral direito
        pygame.draw.rect(self.screen, self.DARK_GRAY, self.ui_panel_rect)
        pygame.draw.line(self.screen, self.WHITE, (self.GAME_WIDTH, 0), (self.GAME_WIDTH, self.CANVAS_HEIGHT), 2)
        
        # Título do painel
        title_text = self.font_medium.render("FLAPPY BIRD AI", True, self.WHITE)
        self.screen.blit(title_text, (self.GAME_WIDTH + 10, 10))
        
        # Estatísticas
        stats_y = 50
        if self.game_state == 'training':
            current_max_score = self.find_best_bird().score if self.find_best_bird() else 0
            if current_max_score > self.best_score:
                self.best_score = current_max_score
            
            stats = [
                ("ESTATÍSTICAS", self.WHITE),
                ("", self.WHITE),
                (f"Melhor Score: {self.best_score}", self.PLAYER_COLOR),
                (f"Geração: {self.generation}", self.GREEN),
                (f"Vivos: {len(self.active_birds)}", self.AI_COLOR),
                (f"População: {self.POPULATION_SIZE}", self.WHITE),
                (f"Taxa Mutação: {self.MUTATION_RATE*100:.0f}%", self.WHITE),
                ("", self.WHITE),
                ("CONTROLES", self.WHITE),
                ("", self.WHITE),
                ("S - Salvar IA", self.GREEN),
                ("R - Reiniciar Treino", self.GREEN),
                ("P - Jogar vs IA", self.WHITE),
                ("D - Desenhar todos", self.WHITE),
                ("1/2 - Velocidade", self.WHITE),
                ("SETAS - Params IA", self.WHITE),
                ("ESC - Sair", self.RED),
                ("", self.WHITE),
                (f"Velocidade: {self.simulation_speed}x", self.PLAYER_COLOR),
                ("", self.WHITE),
                ("STATUS", self.WHITE),
                ("", self.WHITE),
                ("IA evoluindo...", self.GREEN if len(self.active_birds) > 0 else self.RED),
                ("Desenhando: " + ("Todos" if self.draw_all_birds else "Melhor"), self.WHITE),
            ]
        elif self.game_state == 'playing':
            stats = [
                ("PLACAR", self.WHITE),
                ("", self.WHITE),
                (f"Jogador: {self.player_bird.score if self.player_bird else 0}", self.PLAYER_COLOR),
                (f"IA: {self.ai_opponent.score if self.ai_opponent else 0}", self.AI_COLOR),
                ("", self.WHITE),
                ("STATUS", self.WHITE),
                ("", self.WHITE),
                ("Jogador: " + ("Ativo" if self.player_bird and not self.player_bird.lost else "Eliminado"), 
                 self.GREEN if self.player_bird and not self.player_bird.lost else self.RED),
                ("IA: " + ("Ativa" if self.ai_opponent and not self.ai_opponent.lost else "Eliminada"), 
                 self.GREEN if self.ai_opponent and not self.ai_opponent.lost else self.RED),
                ("", self.WHITE),
                ("CONTROLES", self.WHITE),
                ("", self.WHITE),
                ("ESPAÇO - Voar", self.WHITE),
                ("T - Treinar IA", self.WHITE),
                ("ESC - Sair", self.RED),
            ]
        else:  # start ou game_over
            stats = [
                ("BEM-VINDO!", self.WHITE),
                ("", self.WHITE),
                ("Flappy Bird com", self.WHITE),
                ("Inteligência Artificial", self.WHITE),
                ("", self.WHITE),
                ("MODOS DISPONÍVEIS", self.WHITE),
                ("", self.WHITE),
                ("T - Treinar IA", self.GREEN),
                ("P - Jogar vs IA", self.PLAYER_COLOR if os.path.exists(self.save_file) else self.GRAY),
                ("", self.WHITE),
                ("CONTROLES", self.WHITE),
                ("", self.WHITE),
                ("ESPAÇO - Iniciar", self.WHITE),
                ("SETAS - Params IA", self.WHITE),
                ("ESC - Sair", self.RED),
                ("", self.WHITE),
                (f"População: {self.POPULATION_SIZE}", self.WHITE),
                (f"Mutação: {self.MUTATION_RATE*100:.0f}%", self.WHITE),
                ("", self.WHITE),
                ("IA Salva: " + ("Sim" if os.path.exists(self.save_file) else "Não"), 
                 self.GREEN if os.path.exists(self.save_file) else self.RED),
            ]
        
        for i, (stat, color) in enumerate(stats):
            if stat:  # Não desenhar linhas vazias
                text = self.font_small.render(stat, True, color)
                self.screen.blit(text, (self.GAME_WIDTH + 10, stats_y + i * 20))
        
        # Painel inferior
        pygame.draw.rect(self.screen, self.DARK_GRAY, self.bottom_panel_rect)
        pygame.draw.line(self.screen, self.WHITE, (0, self.GAME_HEIGHT), (self.GAME_WIDTH, self.GAME_HEIGHT), 2)
        
        # Informações do modo atual (apenas modo e dica simples)
        if self.game_state == 'training':
            mode_text = self.font_medium.render("MODO: TREINAMENTO DE IA", True, self.GREEN)
            info_text = self.font_small.render("A IA está evoluindo automaticamente...", True, self.WHITE)
        elif self.game_state == 'playing':
            mode_text = self.font_medium.render("MODO: JOGADOR vs IA", True, self.PLAYER_COLOR)
            info_text = self.font_small.render("Use ESPAÇO para voar e compete contra a IA!", True, self.WHITE)
        elif self.game_state == 'game_over':
            mode_text = self.font_medium.render("JOGO FINALIZADO", True, self.RED)
            info_text = self.font_small.render("Pressione ESPAÇO para jogar novamente", True, self.WHITE)
        else:
            mode_text = self.font_medium.render("FLAPPY BIRD - EVOLUÇÃO DE IA", True, self.WHITE)
            info_text = self.font_small.render("Pressione T para treinar IA ou P para jogar contra uma IA salva", True, self.WHITE)
        
        self.screen.blit(mode_text, (10, self.GAME_HEIGHT + 10))
        self.screen.blit(info_text, (10, self.GAME_HEIGHT + 40))
        
        # Barra de progresso da geração (apenas no modo treinamento)
        if self.game_state == 'training' and self.active_birds:
            progress = (self.POPULATION_SIZE - len(self.active_birds)) / self.POPULATION_SIZE
            bar_width = 200
            bar_height = 10
            bar_x = 10
            bar_y = self.GAME_HEIGHT + 70
            
            pygame.draw.rect(self.screen, self.GRAY, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, self.GREEN, (bar_x, bar_y, bar_width * progress, bar_height))
            
            progress_text = self.font_tiny.render(f"Progresso da Geração: {int(progress * 100)}%", True, self.WHITE)
            self.screen.blit(progress_text, (bar_x + bar_width + 10, bar_y - 2))

    def draw_stats(self):
        # Este método agora é incorporado ao draw_ui_panel()
        pass
    
    def draw_ui(self):
        if self.game_state == 'start':
            # Overlay semi-transparente apenas na área do jogo
            overlay = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(self.BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Mensagem de início centralizada na área do jogo
            title = self.font_title.render("EVOLUÇÃO DE IA", True, self.WHITE)
            subtitle = self.font_medium.render("Pressione T para treinar", True, self.WHITE)
            subtitle2 = self.font_medium.render("ou P para jogar vs IA", True, self.WHITE)
            
            title_rect = title.get_rect(center=(self.GAME_WIDTH // 2, self.GAME_HEIGHT // 2 - 80))
            subtitle_rect = subtitle.get_rect(center=(self.GAME_WIDTH // 2, self.GAME_HEIGHT // 2 - 20))
            subtitle2_rect = subtitle2.get_rect(center=(self.GAME_WIDTH // 2, self.GAME_HEIGHT // 2 + 10))
            
            self.screen.blit(title, title_rect)
            self.screen.blit(subtitle, subtitle_rect)
            self.screen.blit(subtitle2, subtitle2_rect)
        
        elif self.game_state == 'game_over':
            # Overlay semi-transparente apenas na área do jogo
            overlay = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(self.BLACK)
            self.screen.blit(overlay, (0, 0))
            
            if self.player_bird.score > self.ai_opponent.score:
                winner = "JOGADOR VENCEU!"
                winner_color = self.PLAYER_COLOR
            elif self.ai_opponent.score > self.player_bird.score:
                winner = "IA VENCEU!"
                winner_color = self.AI_COLOR
            else:
                winner = "EMPATE!"
                winner_color = self.WHITE
            
            winner_text = self.font_title.render(winner, True, winner_color)
            restart_text = self.font_medium.render("ESPAÇO para jogar novamente", True, self.WHITE)
            
            winner_rect = winner_text.get_rect(center=(self.GAME_WIDTH // 2, self.GAME_HEIGHT // 2 - 50))
            restart_rect = restart_text.get_rect(center=(self.GAME_WIDTH // 2, self.GAME_HEIGHT // 2 + 20))
            
            self.screen.blit(winner_text, winner_rect)
            self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        # Fundo geral
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Área do jogo com fundo de céu
        pygame.draw.rect(self.screen, self.SKY_COLOR, self.game_rect)
        
        # Elementos do jogo
        self.draw_pipes()
        
        if self.game_state == 'training':
            best_bird = self.find_best_bird()
            birds_to_draw = self.active_birds if self.draw_all_birds else ([best_bird] if best_bird else [])

            for bird in birds_to_draw:
                is_best = bird == best_bird
                alpha = 255 if is_best else 100
                color = self.PLAYER_COLOR if is_best else self.AI_COLOR
                
                # Criar superfície com transparência
                bird_surface = pygame.Surface((bird.width, bird.height))
                bird_surface.set_alpha(alpha)
                bird_surface.fill(color)
                self.screen.blit(bird_surface, (bird.x, bird.y))
                
                if is_best:
                    text = self.font_tiny.render("BEST", True, self.BLACK)
                    text_rect = text.get_rect(center=(bird.x + bird.width // 2, bird.y + bird.height // 2))
                    self.screen.blit(text, text_rect)
        
        elif self.game_state in ['playing', 'game_over'] and self.player_bird:
            self.player_bird.draw(self.screen, self.PLAYER_COLOR, "JOGADOR")
            self.ai_opponent.draw(self.screen, self.AI_COLOR, "IA")
        
        self.draw_ground()
        
        # Painéis de UI
        self.draw_ui_panel()
        
        # Overlay da UI (start, game over)
        self.draw_ui()
        
        # Borda da área do jogo
        pygame.draw.rect(self.screen, self.WHITE, self.game_rect, 2)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            
            if self.game_state in ['training', 'playing']:
                self.update_game()
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = FlappyBirdAI()
    game.run()
