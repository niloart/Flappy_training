import pygame
import random
import os
from bird import Bird
from neural_network import NeuralNetwork

# --- Configurações e Constantes ---

class Config:
    """Agrupa todas as configurações do jogo e da IA."""
    GAME_WIDTH = 400
    GAME_HEIGHT = 600
    UI_PANEL_WIDTH = 300
    CANVAS_WIDTH = GAME_WIDTH + UI_PANEL_WIDTH
    CANVAS_HEIGHT = GAME_HEIGHT + 100 # Inclui painel inferior

    PIPE_WIDTH = 52
    PIPE_GAP = 180
    PIPE_SPAWN_RATE = 100 # A cada X frames
    GROUND_HEIGHT = 20
    
    POPULATION_SIZE = 50
    MUTATION_RATE = 0.05
    SAVE_FILE = "best_flappy_brain.pkl"

class Colors:
    """Define as cores usadas no jogo."""
    BACKGROUND = (26, 32, 44)
    SKY = (135, 206, 235)
    PIPE = (34, 139, 34)
    GROUND = (222, 184, 135)
    PLAYER = (251, 191, 36)  # Dourado
    AI = (59, 130, 246)      # Azul
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    GREEN = (34, 197, 94)
    RED = (239, 68, 68)

class GameState:
    """Enum para os estados do jogo."""
    START = 'start'
    TRAINING = 'training'
    PLAYING = 'playing'
    GAME_OVER = 'game_over'

# --- Classe Principal do Jogo ---

class FlappyBirdAI:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.colors = Colors()
        
        self.screen = pygame.display.set_mode((self.config.CANVAS_WIDTH, self.config.CANVAS_HEIGHT))
        pygame.display.set_caption("Flappy Bird: Evolução de IA")
        
        self._init_fonts()
        self._init_game_state()
        self._init_ui_rects()

    def _init_fonts(self):
        """Inicializa as fontes usadas no jogo."""
        self.fonts = {
            'title': pygame.font.Font(None, 42),
            'large': pygame.font.Font(None, 36),
            'medium': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 18),
            'tiny': pygame.font.Font(None, 16),
        }

    def _init_game_state(self):
        """Inicializa as variáveis de estado do jogo."""
        self.game_state = GameState.START
        self.pipes = []
        self.active_birds = []
        self.saved_birds = []
        self.player_bird = None
        self.ai_opponent = None
        self.frame_count = 0
        self.generation = 1
        self.best_score = 0
        self.simulation_speed = 1
        self.draw_all_birds = True
        self.clock = pygame.time.Clock()
        
        # Melhorias do algoritmo genético
        self.ga_enhancements = {
            'enhanced_fitness': False,
            'elitism': False,
            'adaptive_mutation': False,
        }
        self.stagnation_count = 0
        self.previous_best_score = 0

    def _init_ui_rects(self):
        """Define as áreas retangulares da interface."""
        self.game_rect = pygame.Rect(0, 0, self.config.GAME_WIDTH, self.config.GAME_HEIGHT)
        self.ui_panel_rect = pygame.Rect(self.config.GAME_WIDTH, 0, self.config.UI_PANEL_WIDTH, self.config.CANVAS_HEIGHT)
        self.bottom_panel_rect = pygame.Rect(0, self.config.GAME_HEIGHT, self.config.GAME_WIDTH, self.config.CANVAS_HEIGHT - self.config.GAME_HEIGHT)

    # --- Lógica de Eventos e Controles ---

    def handle_events(self):
        """Processa todos os eventos do Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return False
            
            if event.type == pygame.KEYDOWN:
                self._handle_key_press(event.key)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click()
        
        return True

    def _handle_key_press(self, key):
        """Lida com os pressionamentos de tecla."""
        key_actions = {
            pygame.K_SPACE: self._handle_mouse_click,
            pygame.K_t: lambda: self.switch_mode(GameState.TRAINING) if self.game_state in [GameState.START, GameState.GAME_OVER] else None,
            pygame.K_p: lambda: self.switch_mode(GameState.PLAYING) if os.path.exists(self.config.SAVE_FILE) else None,
            pygame.K_s: self.save_best_ai if self.game_state == GameState.TRAINING else lambda: None,
            pygame.K_r: lambda: self.switch_mode(GameState.TRAINING, force_restart=True) if self.game_state == GameState.TRAINING else None,
            pygame.K_d: self._toggle_draw_all_birds,
            pygame.K_f: lambda: self._toggle_ga_enhancement('enhanced_fitness'),
            pygame.K_e: lambda: self._toggle_ga_enhancement('elitism'),
            pygame.K_a: lambda: self._toggle_ga_enhancement('adaptive_mutation'),
            pygame.K_1: lambda: self._change_speed(-1),
            pygame.K_2: lambda: self._change_speed(1),
            pygame.K_UP: lambda: self._change_population(10),
            pygame.K_DOWN: lambda: self._change_population(-10),
            pygame.K_RIGHT: lambda: self._change_mutation_rate(0.01),
            pygame.K_LEFT: lambda: self._change_mutation_rate(-0.01),
        }
        if key in key_actions:
            key_actions[key]()

    def _handle_mouse_click(self):
        """Lida com cliques do mouse ou pressionamento de espaço."""
        if self.game_state == GameState.START:
            self.switch_mode(GameState.TRAINING)
        elif self.game_state == GameState.PLAYING and self.player_bird and not self.player_bird.lost:
            self.player_bird.flap()
        elif self.game_state == GameState.GAME_OVER:
            mode = GameState.PLAYING if self.ai_opponent else GameState.TRAINING
            self.switch_mode(mode)

    def _toggle_draw_all_birds(self):
        if self.game_state == GameState.TRAINING:
            self.draw_all_birds = not self.draw_all_birds

    def _toggle_ga_enhancement(self, enhancement):
        if self.game_state in [GameState.START, GameState.TRAINING, GameState.GAME_OVER]:
            self.ga_enhancements[enhancement] = not self.ga_enhancements[enhancement]

    def _change_speed(self, delta):
        self.simulation_speed = max(1, min(10, self.simulation_speed + delta))

    def _change_population(self, delta):
        if self.game_state in [GameState.START, GameState.TRAINING, GameState.GAME_OVER]:
            self.config.POPULATION_SIZE = max(10, min(500, self.config.POPULATION_SIZE + delta))

    def _change_mutation_rate(self, delta):
        if self.game_state in [GameState.START, GameState.TRAINING, GameState.GAME_OVER]:
            self.config.MUTATION_RATE = max(0.0, min(1.0, round(self.config.MUTATION_RATE + delta, 2)))

    # --- Gerenciamento de Estado do Jogo ---

    def switch_mode(self, mode, force_restart=False):
        """Muda o estado do jogo e reinicia as entidades necessárias."""
        self.pipes = []
        self.frame_count = 0
        self.game_state = mode

        if mode == GameState.TRAINING:
            if force_restart or not self.active_birds and not self.saved_birds:
                self.generation = 1
                self.best_score = 0
                self.active_birds = [Bird() for _ in range(self.config.POPULATION_SIZE)]
                self.saved_birds = []
        elif mode == GameState.PLAYING:
            self._start_player_vs_ai_mode()

    def _start_player_vs_ai_mode(self):
        """Configura o modo Jogador vs. IA."""
        if not os.path.exists(self.config.SAVE_FILE):
            print("Nenhuma IA salva encontrada. Treine uma primeiro!")
            self.game_state = GameState.START
            return
        
        self.player_bird = Bird(is_player=True)
        try:
            saved_brain = NeuralNetwork.load(self.config.SAVE_FILE)
            self.ai_opponent = Bird(saved_brain)
        except Exception as e:
            print(f"Erro ao carregar IA salva: {e}")
            self.game_state = GameState.START
            return
        self.active_birds = []

    # --- Lógica do Algoritmo Genético ---

    def next_generation(self):
        """Cria a próxima geração de pássaros."""
        self.generation += 1
        self._calculate_fitness()
        
        self.saved_birds.sort(key=lambda b: b.fitness, reverse=True)
        
        self.active_birds = []
        
        # Elitismo
        elite_count = 0
        if self.ga_enhancements['elitism']:
            elite_count = max(1, int(self.config.POPULATION_SIZE * 0.1))
            for i in range(elite_count):
                if i < len(self.saved_birds):
                    self.active_birds.append(Bird(self.saved_birds[i].brain))
        
        # Crossover e Mutação
        current_mutation_rate = self._get_adaptive_mutation_rate()
        for _ in range(self.config.POPULATION_SIZE - elite_count):
            parent = self._pick_one()
            child = Bird(parent.brain)
            child.brain.mutate(current_mutation_rate)
            self.active_birds.append(child)
        
        self.saved_birds = []
        self.pipes = []
        self.frame_count = 0

    def _pick_one(self):
        """Seleciona um pássaro da população salva com base no fitness (roleta)."""
        index = 0
        r = random.random()
        while r > 0 and index < len(self.saved_birds):
            r -= self.saved_birds[index].fitness
            index += 1
        index = max(0, min(index - 1, len(self.saved_birds) - 1))
        return self.saved_birds[index]

    def _calculate_fitness(self):
        """Calcula o fitness de cada pássaro na população salva."""
        if self.ga_enhancements['enhanced_fitness']:
            self._calculate_enhanced_fitness()
        else:
            self._calculate_standard_fitness()

    def _calculate_standard_fitness(self):
        """Fitness baseado apenas no score."""
        total_score = sum(bird.score ** 2 for bird in self.saved_birds)
        if total_score == 0:
            for bird in self.saved_birds:
                bird.fitness = 1 / len(self.saved_birds)
        else:
            for bird in self.saved_birds:
                bird.fitness = (bird.score ** 2) / total_score

    def _calculate_enhanced_fitness(self):
        """Fitness com bônus por canos passados."""
        total_enhanced_score = 0
        for bird in self.saved_birds:
            enhanced_score = bird.score + (bird.pipes_passed * 100)
            bird.enhanced_score = enhanced_score
            total_enhanced_score += enhanced_score ** 2
        
        if total_enhanced_score == 0:
            for bird in self.saved_birds:
                bird.fitness = 1 / len(self.saved_birds)
        else:
            for bird in self.saved_birds:
                bird.fitness = (bird.enhanced_score ** 2) / total_enhanced_score

    def _get_adaptive_mutation_rate(self):
        """Ajusta a taxa de mutação com base na estagnação."""
        if not self.ga_enhancements['adaptive_mutation']:
            return self.config.MUTATION_RATE
        
        current_best = self.find_best_bird()
        current_best_score = current_best.score if current_best else 0
        
        if current_best_score <= self.previous_best_score:
            self.stagnation_count += 1
        else:
            self.stagnation_count = 0
            self.previous_best_score = current_best_score
        
        if self.stagnation_count >= 3:
            return min(0.15, self.config.MUTATION_RATE * 2.0)
        elif self.stagnation_count == 0:
            return max(0.01, self.config.MUTATION_RATE * 0.7)
        
        return self.config.MUTATION_RATE

    def find_best_bird(self):
        """Encontra o melhor pássaro na população atual ou salva."""
        population = self.active_birds or self.saved_birds
        return max(population, key=lambda b: b.score) if population else None

    def save_best_ai(self):
        """Salva o cérebro do melhor pássaro em um arquivo."""
        best_bird = self.find_best_bird()
        if best_bird:
            best_bird.brain.save(self.config.SAVE_FILE)
            print(f"Melhor IA salva em '{self.config.SAVE_FILE}'!")

    # --- Lógica de Atualização do Jogo ---

    def update(self):
        """Atualiza o estado do jogo a cada frame."""
        for _ in range(self.simulation_speed):
            self.frame_count += 1
            self._update_pipes()
            
            if self.game_state == GameState.TRAINING:
                self._update_training_mode()
            elif self.game_state == GameState.PLAYING:
                self._update_playing_mode()

    def _update_training_mode(self):
        """Atualiza a lógica para o modo de treinamento."""
        if not self.active_birds:
            self.next_generation()
        
        for i in range(len(self.active_birds) - 1, -1, -1):
            bird = self.active_birds[i]
            bird.think(self.pipes, self.config.GAME_HEIGHT, self.config.GAME_WIDTH)
            bird.update()
            
            if self._check_collision(bird):
                self.saved_birds.append(self.active_birds.pop(i))
            else:
                self._check_pipe_pass(bird)

    def _update_playing_mode(self):
        """Atualiza a lógica para o modo jogador vs. IA."""
        if not self.player_bird.lost:
            self.player_bird.update()
            if self._check_collision(self.player_bird):
                self.player_bird.lost = True
        
        if not self.ai_opponent.lost:
            self.ai_opponent.think(self.pipes, self.config.GAME_HEIGHT, self.config.GAME_WIDTH)
            self.ai_opponent.update()
            if self._check_collision(self.ai_opponent):
                self.ai_opponent.lost = True
        
        if self.player_bird.lost and self.ai_opponent.lost:
            self.game_state = GameState.GAME_OVER

    def _update_pipes(self):
        """Move e cria novos canos."""
        if self.frame_count % self.config.PIPE_SPAWN_RATE == 0:
            top_height = random.randint(50, self.config.GAME_HEIGHT - self.config.PIPE_GAP - 100)
            self.pipes.append({'x': self.config.GAME_WIDTH, 'top_height': top_height, 'birds_passed': set()})
        
        for pipe in self.pipes:
            pipe['x'] -= 2
        
        self.pipes = [p for p in self.pipes if p['x'] + self.config.PIPE_WIDTH > 0]

    def _check_collision(self, bird):
        """Verifica se um pássaro colidiu com o chão, teto ou canos."""
        if bird.is_offscreen(self.config.GAME_HEIGHT, self.config.GROUND_HEIGHT):
            return True
        for pipe in self.pipes:
            if bird.collides_with(pipe, self.config.PIPE_GAP):
                return True
        return False

    def _check_pipe_pass(self, bird):
        """Verifica se um pássaro passou por um cano para o fitness aprimorado."""
        for pipe in self.pipes:
            bird_id = id(bird)
            if pipe['x'] + self.config.PIPE_WIDTH < bird.x and bird_id not in pipe['birds_passed']:
                bird.pipes_passed += 1
                pipe['birds_passed'].add(bird_id)

    # --- Lógica de Desenho ---

    def draw(self):
        """Desenha todos os elementos na tela."""
        self.screen.fill(self.colors.BACKGROUND)
        pygame.draw.rect(self.screen, self.colors.SKY, self.game_rect)

        self._draw_pipes()
        self._draw_birds()
        self._draw_ground()
        
        self._draw_ui_panel()
        self._draw_game_overlays()
        
        pygame.draw.rect(self.screen, self.colors.WHITE, self.game_rect, 2)
        pygame.display.flip()

    def _draw_pipes(self):
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, self.colors.PIPE, (pipe['x'], 0, self.config.PIPE_WIDTH, pipe['top_height']))
            pygame.draw.rect(self.screen, self.colors.PIPE, (pipe['x'], pipe['top_height'] + self.config.PIPE_GAP, self.config.PIPE_WIDTH, self.config.GAME_HEIGHT - pipe['top_height'] - self.config.PIPE_GAP))

    def _draw_ground(self):
        pygame.draw.rect(self.screen, self.colors.GROUND, (0, self.config.GAME_HEIGHT - self.config.GROUND_HEIGHT, self.config.GAME_WIDTH, self.config.GROUND_HEIGHT))

    def _draw_birds(self):
        """Desenha os pássaros na tela."""
        if self.game_state == GameState.TRAINING:
            best_bird = self.find_best_bird()
            birds_to_draw = self.active_birds if self.draw_all_birds else ([best_bird] if best_bird else [])
            for bird in birds_to_draw:
                is_best = bird == best_bird
                color = self.colors.PLAYER if is_best else self.colors.AI
                alpha = 255 if is_best else 100
                
                bird_surface = pygame.Surface((bird.width, bird.height), pygame.SRCALPHA)
                bird_surface.fill((*color, alpha))
                self.screen.blit(bird_surface, (bird.x, bird.y))
                
                if is_best:
                    text = self.fonts['tiny'].render("BEST", True, self.colors.BLACK)
                    text_rect = text.get_rect(center=(bird.x + bird.width // 2, bird.y + bird.height // 2))
                    self.screen.blit(text, text_rect)
        
        elif self.game_state in [GameState.PLAYING, GameState.GAME_OVER]:
            if self.player_bird: self.player_bird.draw(self.screen, self.colors.PLAYER, "JOGADOR")
            if self.ai_opponent: self.ai_opponent.draw(self.screen, self.colors.AI, "IA")

    def _draw_ui_panel(self):
        """Desenha os painéis de UI lateral e inferior."""
        # Painel lateral
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, self.ui_panel_rect)
        pygame.draw.line(self.screen, self.colors.WHITE, (self.config.GAME_WIDTH, 0), (self.config.GAME_WIDTH, self.config.CANVAS_HEIGHT), 2)
        
        title_text = self.fonts['medium'].render("FLAPPY BIRD AI", True, self.colors.WHITE)
        self.screen.blit(title_text, (self.config.GAME_WIDTH + 10, 10))
        
        self._draw_stats_on_panel()

        # Painel inferior
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, self.bottom_panel_rect)
        pygame.draw.line(self.screen, self.colors.WHITE, (0, self.config.GAME_HEIGHT), (self.config.GAME_WIDTH, self.config.GAME_HEIGHT), 2)
        
        self._draw_bottom_panel_info()

    def _draw_stats_on_panel(self):
        """Desenha as estatísticas e controles no painel lateral."""
        stats_y = 50
        stats_map = {
            GameState.TRAINING: self._get_training_stats,
            GameState.PLAYING: self._get_playing_stats,
            GameState.START: self._get_start_stats,
            GameState.GAME_OVER: self._get_start_stats,
        }
        stats = stats_map[self.game_state]()
        
        for i, (stat, color) in enumerate(stats):
            if stat:
                text = self.fonts['small'].render(stat, True, color)
                self.screen.blit(text, (self.config.GAME_WIDTH + 10, stats_y + i * 20))

    def _draw_bottom_panel_info(self):
        """Desenha as informações no painel inferior."""
        if self.game_state == GameState.TRAINING:
            mode_text = self.fonts['medium'].render("MODO: TREINAMENTO", True, self.colors.GREEN)
            info_text = self.fonts['small'].render("IA evoluindo...", True, self.colors.WHITE)
            self.screen.blit(mode_text, (10, self.config.GAME_HEIGHT + 10))
            self.screen.blit(info_text, (10, self.config.GAME_HEIGHT + 40))
            self._draw_progress_bar()
        elif self.game_state == GameState.PLAYING:
            mode_text = self.fonts['medium'].render("MODO: JOGADOR vs IA", True, self.colors.PLAYER)
            info_text = self.fonts['small'].render("Use ESPAÇO para voar!", True, self.colors.WHITE)
            self.screen.blit(mode_text, (10, self.config.GAME_HEIGHT + 10))
            self.screen.blit(info_text, (10, self.config.GAME_HEIGHT + 40))
        elif self.game_state == GameState.GAME_OVER:
            mode_text = self.fonts['medium'].render("JOGO FINALIZADO", True, self.colors.RED)
            info_text = self.fonts['small'].render("Pressione ESPAÇO para jogar novamente", True, self.colors.WHITE)
            self.screen.blit(mode_text, (10, self.config.GAME_HEIGHT + 10))
            self.screen.blit(info_text, (10, self.config.GAME_HEIGHT + 40))
        else: # Start
            mode_text = self.fonts['medium'].render("FLAPPY BIRD - EVOLUÇÃO", True, self.colors.WHITE)
            info_text = self.fonts['small'].render("Pressione T para treinar ou P para jogar", True, self.colors.WHITE)
            self.screen.blit(mode_text, (10, self.config.GAME_HEIGHT + 10))
            self.screen.blit(info_text, (10, self.config.GAME_HEIGHT + 40))

    def _draw_progress_bar(self):
        """Desenha a barra de progresso da geração."""
        if self.active_birds:
            progress = (self.config.POPULATION_SIZE - len(self.active_birds)) / self.config.POPULATION_SIZE
            bar_width, bar_height, bar_x, bar_y = 200, 10, 10, self.config.GAME_HEIGHT + 70
            
            pygame.draw.rect(self.screen, self.colors.GRAY, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, self.colors.GREEN, (bar_x, bar_y, bar_width * progress, bar_height))
            
            progress_text = self.fonts['tiny'].render(f"Progresso: {int(progress * 100)}%", True, self.colors.WHITE)
            self.screen.blit(progress_text, (bar_x + bar_width + 10, bar_y - 2))

    def _draw_game_overlays(self):
        """Desenha overlays como a tela de início e de game over."""
        if self.game_state == GameState.START:
            self._draw_overlay_message("EVOLUÇÃO DE IA", "Pressione T para treinar", "ou P para jogar vs IA")
        elif self.game_state == GameState.GAME_OVER:
            if self.player_bird.score > self.ai_opponent.score:
                winner, color = "JOGADOR VENCEU!", self.colors.PLAYER
            elif self.ai_opponent.score > self.player_bird.score:
                winner, color = "IA VENCEU!", self.colors.AI
            else:
                winner, color = "EMPATE!", self.colors.WHITE
            self._draw_overlay_message(winner, "ESPAÇO para jogar novamente", color=color)

    def _draw_overlay_message(self, line1, line2, line3=None, color=None):
        """Função auxiliar para desenhar mensagens de overlay."""
        color = color or self.colors.WHITE
        overlay = pygame.Surface((self.config.GAME_WIDTH, self.config.GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        text1 = self.fonts['title'].render(line1, True, color)
        text2 = self.fonts['medium'].render(line2, True, self.colors.WHITE)
        
        text1_rect = text1.get_rect(center=(self.config.GAME_WIDTH // 2, self.config.GAME_HEIGHT // 2 - 60))
        text2_rect = text2.get_rect(center=(self.config.GAME_WIDTH // 2, self.config.GAME_HEIGHT // 2))
        
        self.screen.blit(text1, text1_rect)
        self.screen.blit(text2, text2_rect)
        
        if line3:
            text3 = self.fonts['medium'].render(line3, True, self.colors.WHITE)
            text3_rect = text3.get_rect(center=(self.config.GAME_WIDTH // 2, self.config.GAME_HEIGHT // 2 + 30))
            self.screen.blit(text3, text3_rect)

    # --- Funções de Geração de Texto para UI ---

    def _get_training_stats(self):
        current_max_score = self.find_best_bird().score if self.find_best_bird() else 0
        self.best_score = max(self.best_score, current_max_score)
        
        on_off = lambda b: ("ON", self.colors.GREEN) if b else ("OFF", self.colors.RED)
        fit_status, fit_color = on_off(self.ga_enhancements['enhanced_fitness'])
        eli_status, eli_color = on_off(self.ga_enhancements['elitism'])
        ada_status, ada_color = on_off(self.ga_enhancements['adaptive_mutation'])

        return [
            ("ESTATÍSTICAS", self.colors.WHITE),
            (f"Melhor Score: {self.best_score}", self.colors.PLAYER),
            (f"Geração: {self.generation}", self.colors.GREEN),
            (f"Vivos: {len(self.active_birds)}", self.colors.AI),
            (f"Velocidade: {self.simulation_speed}x", self.colors.PLAYER),
            ("", None),
            ("CONTROLES", self.colors.WHITE),
            ("S - Salvar IA", self.colors.GREEN),
            ("R - Reiniciar", self.colors.GREEN),
            ("D - Desenhar Todos/Melhor", self.colors.WHITE),
            ("1/2 - Velocidade", self.colors.WHITE),
            ("", None),
            ("MELHORIAS IA", self.colors.WHITE),
            (f"Fitness Avançado (F): {fit_status}", fit_color),
            (f"Elitismo (E): {eli_status}", eli_color),
            (f"Mutação Adaptativa (A): {ada_status}", ada_color),
            (f"Taxa Mutação: {self._get_adaptive_mutation_rate()*100:.1f}%", self.colors.WHITE),
        ]

    def _get_playing_stats(self):
        player_status, player_color = ("Ativo", self.colors.GREEN) if not self.player_bird.lost else ("Eliminado", self.colors.RED)
        ai_status, ai_color = ("Ativa", self.colors.GREEN) if not self.ai_opponent.lost else ("Eliminada", self.colors.RED)
        return [
            ("PLACAR", self.colors.WHITE),
            (f"Jogador: {self.player_bird.score}", self.colors.PLAYER),
            (f"IA: {self.ai_opponent.score}", self.colors.AI),
            ("", None),
            ("STATUS", self.colors.WHITE),
            (f"Jogador: {player_status}", player_color),
            (f"IA: {ai_status}", ai_color),
            ("", None),
            ("CONTROLES", self.colors.WHITE),
            ("ESPAÇO - Voar", self.colors.WHITE),
            ("T - Treinar IA", self.colors.WHITE),
        ]

    def _get_start_stats(self):
        ia_saved, ia_color = ("Sim", self.colors.GREEN) if os.path.exists(self.config.SAVE_FILE) else ("Não", self.colors.RED)
        on_off = lambda b: ("ON", self.colors.GREEN) if b else ("OFF", self.colors.RED)
        fit_status, fit_color = on_off(self.ga_enhancements['enhanced_fitness'])
        eli_status, eli_color = on_off(self.ga_enhancements['elitism'])
        ada_status, ada_color = on_off(self.ga_enhancements['adaptive_mutation'])
        
        return [
            ("BEM-VINDO!", self.colors.WHITE),
            ("", None),
            ("MODOS", self.colors.WHITE),
            ("T - Treinar IA", self.colors.GREEN),
            ("P - Jogar vs IA", self.colors.PLAYER if ia_saved == "Sim" else self.colors.GRAY),
            ("", None),
            ("CONFIGURAÇÕES IA", self.colors.WHITE),
            (f"População (↑/↓): {self.config.POPULATION_SIZE}", self.colors.WHITE),
            (f"Mutação (←/→): {self.config.MUTATION_RATE*100:.0f}%", self.colors.WHITE),
            (f"Fitness Avançado (F): {fit_status}", fit_color),
            (f"Elitismo (E): {eli_status}", eli_color),
            (f"Mutação Adaptativa (A): {ada_status}", ada_color),
            ("", None),
            (f"IA Salva: {ia_saved}", ia_color),
        ]

    # --- Loop Principal ---

    def run(self):
        """O loop principal do jogo."""
        running = True
        while running:
            running = self.handle_events()
            
            if self.game_state in [GameState.TRAINING, GameState.PLAYING]:
                self.update()
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = FlappyBirdAI()
    game.run()