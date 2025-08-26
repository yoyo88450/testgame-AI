import pygame
import sys
from monster import Monster, Attack
from items import Item
import random

# Initialisation de Pygame
pygame.init()
pygame.font.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MONSTER_SIZE = 200
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 180
BUTTON_MARGIN = 10
INFO_HEIGHT = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Création de la fenêtre
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Monster Battle Game")

# Fonts
FONT = pygame.font.SysFont('Arial', 20)
LARGE_FONT = pygame.font.SysFont('Arial', 32)

class Button:
    def __init__(self, x, y, width, height, text, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False

    def draw(self, surface):
        color = self.color if not self.is_hovered else (min(255, self.color[0] + 30), 
                                                       min(255, self.color[1] + 30),
                                                       min(255, self.color[2] + 30))
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class BattleScene:
    def __init__(self, player_monsters, enemy_monster, inventory):
        self.player_monsters = player_monsters
        self.current_monster = player_monsters[0]
        self.enemy_monster = enemy_monster
        self.inventory = inventory
        self.create_buttons()
        self.message = ""
        self.message_timer = 0
        self.state = "MAIN"  # MAIN, ATTACK, ITEMS, SWITCH
        
    def create_buttons(self):
        self.main_buttons = [
            Button(10, WINDOW_HEIGHT - 180, BUTTON_WIDTH, BUTTON_HEIGHT, "Attaquer"),
            Button(200, WINDOW_HEIGHT - 180, BUTTON_WIDTH, BUTTON_HEIGHT, "Objets"),
            Button(390, WINDOW_HEIGHT - 180, BUTTON_WIDTH, BUTTON_HEIGHT, "Changer"),
        ]
        
        self.back_button = Button(10, WINDOW_HEIGHT - 60, BUTTON_WIDTH, BUTTON_HEIGHT, "Retour")
        
        # Création des boutons d'attaque
        self.attack_buttons = []
        for i, attack in enumerate(self.current_monster.attacks):
            x = 10 + (i % 2) * (BUTTON_WIDTH + 10)
            y = WINDOW_HEIGHT - 180 + (i // 2) * (BUTTON_HEIGHT + 10)
            self.attack_buttons.append(Button(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                                           f"{attack.name} ({attack.damage})"))
    
    def draw_monster_info(self, monster, x, y, is_enemy=False):
        # Dessiner un rectangle pour le monstre
        monster_rect = pygame.Rect(x, y, MONSTER_SIZE, MONSTER_SIZE)
        pygame.draw.rect(screen, GRAY, monster_rect)
        
        # Barre de vie
        health_percent = monster.current_hp / monster.max_hp
        health_width = MONSTER_SIZE * health_percent
        health_rect = pygame.Rect(x, y + MONSTER_SIZE + 10, MONSTER_SIZE, 20)
        pygame.draw.rect(screen, RED, health_rect)
        pygame.draw.rect(screen, GREEN, (x, y + MONSTER_SIZE + 10, health_width, 20))
        
        # Informations du monstre
        name_text = FONT.render(f"{monster.name} Nv.{monster.level}", True, BLACK)
        hp_text = FONT.render(f"PV: {monster.current_hp}/{monster.max_hp}", True, BLACK)
        screen.blit(name_text, (x, y + MONSTER_SIZE + 35))
        screen.blit(hp_text, (x, y + MONSTER_SIZE + 55))

    def show_message(self, message, duration=60):
        self.message = message
        self.message_timer = duration

    def update_message(self):
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""

    def draw(self):
        screen.fill(WHITE)
        
        # Dessiner les monstres
        self.draw_monster_info(self.enemy_monster, WINDOW_WIDTH - MONSTER_SIZE - 50, 50, True)
        self.draw_monster_info(self.current_monster, 50, WINDOW_HEIGHT - MONSTER_SIZE - 150)
        
        # Dessiner le message
        if self.message:
            text = FONT.render(self.message, True, BLACK)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 30))
            screen.blit(text, text_rect)
        
        # Dessiner les boutons selon l'état
        if self.state == "MAIN":
            for button in self.main_buttons:
                button.draw(screen)
        elif self.state == "ATTACK":
            for button in self.attack_buttons:
                button.draw(screen)
            self.back_button.draw(screen)
        
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "QUIT"
            
        if self.state == "MAIN":
            for i, button in enumerate(self.main_buttons):
                if button.handle_event(event):
                    if i == 0:  # Attaquer
                        self.state = "ATTACK"
                    elif i == 1:  # Objets
                        self.state = "ITEMS"
                    elif i == 2:  # Changer
                        self.state = "SWITCH"
                    return None
                    
        elif self.state == "ATTACK":
            for i, button in enumerate(self.attack_buttons):
                if button.handle_event(event):
                    attack = self.current_monster.attacks[i]
                    damage = self.current_monster.get_attack_damage(attack.damage)
                    self.enemy_monster.take_damage(damage)
                    self.current_monster.heal(attack.heal)
                    self.show_message(f"{self.current_monster.name} utilise {attack.name}!")
                    self.state = "MAIN"
                    return "ENEMY_TURN"
                    
            if self.back_button.handle_event(event):
                self.state = "MAIN"
                
        return None

def main():
    from game import create_monster_list, create_enemy_monster, create_items
    
    # Initialisation
    player_monsters = create_monster_list()
    enemy_monster = create_enemy_monster(1)
    items = create_items()
    inventory = {
        'potion': (items['potion'], 3),
        'super_potion': (items['super_potion'], 1),
        'revive': (items['revive'], 1),
        'attack_boost': (items['attack_boost'], 2)
    }
    
    battle_scene = BattleScene(player_monsters, enemy_monster, inventory)
    clock = pygame.time.Clock()
    
    # Boucle principale
    running = True
    while running:
        for event in pygame.event.get():
            result = battle_scene.handle_event(event)
            if result == "QUIT":
                running = False
            elif result == "ENEMY_TURN":
                # Tour de l'ennemi
                attack = random.choice(enemy_monster.attacks)
                damage = enemy_monster.get_attack_damage(attack.damage)
                battle_scene.current_monster.take_damage(damage)
                enemy_monster.heal(attack.heal)
                battle_scene.show_message(f"{enemy_monster.name} utilise {attack.name}!")
        
        battle_scene.update_message()
        battle_scene.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
