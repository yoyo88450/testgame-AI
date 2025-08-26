import pygame
import sys
from monster import Monster, Attack
from items import Item
import random
import os
import unicodedata

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
        # Ajout pour gestion objets
        self.item_buttons = []
        self.selected_item = None
        self.target_monster_buttons = []
        self.selected_target = None
        self.switch_monster_buttons = []

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
        # Création des boutons d'objets
        self.item_buttons = []
        y_start = WINDOW_HEIGHT - 180
        for i, (item_name, (item, qty)) in enumerate(self.inventory.items()):
            x = 10 + (i % 2) * (BUTTON_WIDTH + 10)
            y = y_start + (i // 2) * (BUTTON_HEIGHT + 10)
            text = f"{item.name} ({qty}x)"
            self.item_buttons.append(Button(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, text))
        # Boutons pour choisir le monstre cible (pour revive)
        self.target_monster_buttons = []
        y_start = WINDOW_HEIGHT - 180
        for i, monster in enumerate(self.player_monsters):
            if hasattr(monster, 'is_fainted') and monster.is_fainted:
                x = 10 + (i % 2) * (BUTTON_WIDTH + 10)
                y = y_start + (i // 2) * (BUTTON_HEIGHT + 10)
                text = f"{monster.name} (K.O.)"
                self.target_monster_buttons.append(Button(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, text))
    
    def normalize_monster_filename(self, name):
        # Enlève les accents, met en minuscules et remplace les espaces
        name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
        return name.lower().replace(' ', '')

    def load_monster_image(self, monster_name):
        filename = self.normalize_monster_filename(monster_name)
        img_path = os.path.join('assets', f'{filename}.png')
        if os.path.exists(img_path):
            try:
                return pygame.image.load(img_path)
            except Exception as e:
                print(f"Erreur chargement image {img_path}: {e}")
                return None
        else:
            print(f"Image non trouvée : {img_path}")
        return None

    def draw_monster_info(self, monster, x, y, is_enemy=False):
        # Afficher l'image PNG si elle existe
        img = self.load_monster_image(monster.name)
        if img:
            img = pygame.transform.scale(img, (MONSTER_SIZE, MONSTER_SIZE))
            screen.blit(img, (x, y))
        else:
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

    def draw_monster_selection(self):
        # Affiche des petits ronds bien visibles sous les PV du monstre actif
        y = WINDOW_HEIGHT - 120
        for i, monster in enumerate(self.player_monsters):
            x = 40 + i * (MONSTER_SIZE // 2 + 40)
            # Dessin du rond
            circle_color = GREEN if monster == self.current_monster else GRAY
            center_x = x + MONSTER_SIZE // 8
            center_y = y + 60
            pygame.draw.circle(screen, circle_color, (center_x, center_y), 14)

    def draw_menu_zone(self, buttons):
        # Zone fixe pour les boutons menu et sous-menus
        menu_rect = pygame.Rect(0, WINDOW_HEIGHT - 40, WINDOW_WIDTH, 40)
        pygame.draw.rect(screen, GRAY, menu_rect)
        pygame.draw.rect(screen, BLACK, menu_rect, 2)
        # Boutons plus petits
        for i, button in enumerate(buttons):
            button.rect.y = WINDOW_HEIGHT - 35
            button.rect.x = 10 + i * (BUTTON_WIDTH // 1.5 + 10)
            button.rect.width = int(BUTTON_WIDTH // 1.5)
            button.rect.height = int(BUTTON_HEIGHT // 1.5)
            button.draw(screen)

    def draw(self):
        screen.fill(WHITE)
        self.draw_monster_info(self.enemy_monster, WINDOW_WIDTH - MONSTER_SIZE - 50, 50, True)
        self.draw_monster_info(self.current_monster, 50, WINDOW_HEIGHT - MONSTER_SIZE - 150)
        self.draw_monster_selection()
        # Dessiner le message
        if self.message:
            text = FONT.render(self.message, True, BLACK)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 30))
            screen.blit(text, text_rect)
        # Zone fixe pour tous les menus
        if self.state == "MAIN":
            self.draw_menu_zone(self.main_buttons)
        elif self.state == "ATTACK":
            self.draw_menu_zone(self.attack_buttons + [self.back_button])
        elif self.state == "ITEMS":
            self.draw_menu_zone(self.item_buttons + [self.back_button])
            if self.selected_item == 'revive' and self.target_monster_buttons:
                for button in self.target_monster_buttons:
                    button.draw(screen)
        elif self.state == "SWITCH":
            self.draw_menu_zone(self.switch_monster_buttons + [self.back_button])
        pygame.display.flip()

    def set_current_monster(self, monster):
        self.current_monster = monster
        self.create_buttons()

    def set_inventory(self, inventory):
        self.inventory = inventory
        self.create_buttons()

    def create_switch_buttons(self):
        self.switch_monster_buttons = []
        y_start = WINDOW_HEIGHT - 180
        for i, monster in enumerate(self.player_monsters):
            if hasattr(monster, 'is_alive') and monster.is_alive() and monster != self.current_monster:
                x = 10 + (i % 2) * (BUTTON_WIDTH + 10)
                y = y_start + (i // 2) * (BUTTON_HEIGHT + 10)
                text = f"{monster.name} (PV: {monster.current_hp}/{monster.max_hp})"
                self.switch_monster_buttons.append(Button(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, text))

    def show_upgrade_dialog(self):
        dialog_rect = pygame.Rect(150, 150, 500, 300)
        pygame.draw.rect(screen, WHITE, dialog_rect)
        pygame.draw.rect(screen, BLACK, dialog_rect, 3)
        title = LARGE_FONT.render("Amélioration des monstres !", True, BLACK)
        screen.blit(title, (dialog_rect.x + 60, dialog_rect.y + 20))
        y = dialog_rect.y + 80
        for monster in self.player_monsters:
            if hasattr(monster, 'is_fainted') and not monster.is_fainted:
                up_text = FONT.render(f"{monster.name} : +10 PV, +2 Attaque", True, BLACK)
                screen.blit(up_text, (dialog_rect.x + 40, y))
                y += 30
        # Boutons Oui/Non
        self.btn_yes = Button(dialog_rect.x + 80, dialog_rect.y + 220, 120, 50, "Oui", GREEN)
        self.btn_no = Button(dialog_rect.x + 300, dialog_rect.y + 220, 120, 50, "Non", RED)
        self.btn_yes.draw(screen)
        self.btn_no.draw(screen)
        pygame.display.flip()

    def upgrade_monsters(self):
        for monster in self.player_monsters:
            if hasattr(monster, 'is_fainted') and not monster.is_fainted:
                monster.max_hp += 10
                monster.current_hp = monster.max_hp
                if hasattr(monster, 'attack_power'):
                    monster.attack_power += 2

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
                        self.create_switch_buttons()
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
                    self.create_buttons()
                    return "ENEMY_TURN"
            if self.back_button.handle_event(event):
                self.state = "MAIN"
                self.create_buttons()
        elif self.state == "ITEMS":
            for i, button in enumerate(self.item_buttons):
                if button.handle_event(event):
                    item_name = list(self.inventory.keys())[i]
                    item, qty = self.inventory[item_name]
                    if qty <= 0:
                        self.show_message("Plus de cet objet!")
                        return None
                    if item_name == 'revive':
                        self.selected_item = 'revive'
                        self.target_monster_buttons = []
                        for j, monster in enumerate(self.player_monsters):
                            if hasattr(monster, 'is_fainted') and monster.is_fainted:
                                x = 10 + (j % 2) * (BUTTON_WIDTH + 10)
                                y = WINDOW_HEIGHT - 180 + (j // 2) * (BUTTON_HEIGHT + 10)
                                text = f"{monster.name} (K.O.)"
                                self.target_monster_buttons.append(Button(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, text))
                        if not self.target_monster_buttons:
                            self.show_message("Aucun monstre à ressusciter!")
                            self.selected_item = None
                        return None
                    else:
                        success, message = item.use(self.current_monster)
                        if success:
                            self.inventory[item_name] = (item, qty - 1)
                            self.set_inventory(self.inventory)
                        self.show_message(message)
                        self.state = "MAIN"
                        self.create_buttons()
                        return "ENEMY_TURN"
            if self.selected_item == 'revive' and self.target_monster_buttons:
                for j, button in enumerate(self.target_monster_buttons):
                    if button.handle_event(event):
                        monster = [m for m in self.player_monsters if hasattr(m, 'is_fainted') and m.is_fainted][j]
                        item, qty = self.inventory['revive']
                        success, message = item.use(monster)
                        if success:
                            self.inventory['revive'] = (item, qty - 1)
                            self.set_inventory(self.inventory)
                        self.show_message(message)
                        self.selected_item = None
                        self.state = "MAIN"
                        self.create_buttons()
                        return "ENEMY_TURN"
            if self.back_button.handle_event(event):
                self.state = "MAIN"
                self.selected_item = None
                self.target_monster_buttons = []
                self.create_buttons()
                return None
        elif self.state == "SWITCH":
            for i, button in enumerate(self.switch_monster_buttons):
                if button.handle_event(event):
                    monster = [m for m in self.player_monsters if hasattr(m, 'is_alive') and m.is_alive() and m != self.current_monster][i]
                    self.set_current_monster(monster)
                    self.show_message(f"{monster.name} entre en combat !")
                    self.state = "MAIN"
                    self.create_buttons()
                    return None
            if self.back_button.handle_event(event):
                self.state = "MAIN"
                self.create_buttons()
                return None
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
    battles_won = 0
    show_upgrade = False
    upgrade_done = False
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

        # Vérification victoire
        if not enemy_monster.is_alive():
            if not show_upgrade:
                show_upgrade = True
                upgrade_done = False
        if show_upgrade:
            battle_scene.show_upgrade_dialog()
            if not upgrade_done:
                battle_scene.upgrade_monsters()
                upgrade_done = True
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if battle_scene.btn_yes.rect.collidepoint(event.pos):
                        show_upgrade = False
                        upgrade_done = False
                        # Apparition d'un nouvel ennemi
                        from game import get_player_average_level, create_enemy_monster
                        avg_level = get_player_average_level(player_monsters) if hasattr(player_monsters[0], 'level') else 1
                        enemy_monster = create_enemy_monster(avg_level)
                        battle_scene.enemy_monster = enemy_monster
                        battle_scene.show_message(f"Un {enemy_monster.name} de niveau {enemy_monster.level} apparaît !")
                        battle_scene.create_buttons()
                    elif battle_scene.btn_no.rect.collidepoint(event.pos):
                        running = False
                        show_upgrade = False
                        upgrade_done = False
        # Vérification défaite
        if hasattr(battle_scene.current_monster, 'is_alive') and not battle_scene.current_monster.is_alive():
            alive_monsters = [m for m in player_monsters if hasattr(m, 'is_alive') and m.is_alive()]
            if not alive_monsters:
                battle_scene.show_message(f"Tous vos monstres sont K.O.! Vous avez perdu après {battles_won} victoires.")
                pygame.time.wait(2000)
                running = False
            else:
                battle_scene.current_monster = alive_monsters[0]
                battle_scene.create_buttons()
                battle_scene.show_message(f"{battle_scene.current_monster.name} entre en combat !")

        battle_scene.update_message()
        battle_scene.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
