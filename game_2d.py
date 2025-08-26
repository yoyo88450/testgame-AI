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


# --- Design Pokémon ---
WHITE = (255, 255, 255)
BLACK = (40, 40, 40)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
POKE_BG_TOP = (180, 220, 255)
POKE_BG_BOTTOM = (120, 180, 255)
POKE_PANEL = (255, 255, 255)
POKE_PANEL_BORDER = (80, 120, 180)
POKE_HP_BG = (255, 255, 255)
POKE_HP_BORDER = (80, 120, 180)
POKE_HP_BAR = (80, 200, 80)
POKE_BTN = (240, 240, 255)
POKE_BTN_BORDER = (80, 120, 180)
POKE_BTN_HOVER = (200, 220, 255)
POKE_SHADOW = (100, 100, 100, 80)

# Création de la fenêtre
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Monster Battle Game")

# Fonts
FONT = pygame.font.SysFont('Verdana', 22)
LARGE_FONT = pygame.font.SysFont('Comic Sans MS', 36)

class Button:
    def __init__(self, x, y, width, height, text, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False

    def draw(self, surface):
        # Bouton arrondi style Pokémon
        color = POKE_BTN_HOVER if self.is_hovered else POKE_BTN
        pygame.draw.rect(surface, color, self.rect, border_radius=18)
        pygame.draw.rect(surface, POKE_BTN_BORDER, self.rect, 3, border_radius=18)
        # Ajustement du texte pour ne pas dépasser le bouton
        max_width = self.rect.width - 16
        text = self.text
        text_surface = FONT.render(text, True, POKE_BTN_BORDER)
        # Si le texte est trop large, on le réduit
        while text_surface.get_width() > max_width and len(text) > 3:
            text = text[:-2] + "…"
            text_surface = FONT.render(text, True, POKE_BTN_BORDER)
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
    # --- Ajout pour animations ---
    def reset_animation(self):
        self.anim_state = None
        self.anim_timer = 0
        self.anim_attacker = None
        self.anim_target = None
        self.anim_attack_name = None
        self.anim_attack_damage = 0
        self.anim_hp_start = 0
        self.anim_hp_end = 0
        self.anim_hp_current = 0
        self.anim_callback = None

    def start_attack_animation(self, attacker, target, attack_name, damage, callback):
        self.anim_state = "attack"
        self.anim_timer = 20  # frames
        self.anim_attacker = attacker
        self.anim_target = target
        self.anim_attack_name = attack_name
        self.anim_attack_damage = damage
        self.anim_hp_start = target.current_hp
        self.anim_hp_end = max(0, target.current_hp - damage)
        self.anim_hp_current = self.anim_hp_start
        self.anim_callback = callback

    def update_animation(self):
        if self.anim_state == "attack":
            self.anim_timer -= 1
            if self.anim_timer == 0:
                # Commence l'animation de barre de vie
                self.anim_state = "hp"
                self.anim_timer = 20
        elif self.anim_state == "hp":
            # Animation de barre de vie qui baisse
            progress = 1 - self.anim_timer / 20
            self.anim_hp_current = int(self.anim_hp_start - (self.anim_hp_start - self.anim_hp_end) * progress)
            self.anim_timer -= 1
            if self.anim_timer == 0:
                self.anim_hp_current = self.anim_hp_end
                self.anim_state = None
                # Applique les dégâts réels
                self.anim_target.current_hp = self.anim_hp_end
                if self.anim_callback:
                    self.anim_callback()

    def is_animating(self):
        return self.anim_state is not None
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

    def draw_monster_info(self, monster, x, y, is_enemy=False, anim_hp=None, anim_attack=False):
        # Ombre sous le monstre
        shadow_rect = pygame.Rect(x+18, y+MONSTER_SIZE-10, MONSTER_SIZE-36, 24)
        pygame.draw.ellipse(screen, POKE_SHADOW, shadow_rect)
        # Cadre arrondi style Pokémon
        panel_rect = pygame.Rect(x-10, y-10, MONSTER_SIZE+20, MONSTER_SIZE+80)
        pygame.draw.rect(screen, POKE_PANEL, panel_rect, border_radius=24)
        pygame.draw.rect(screen, POKE_PANEL_BORDER, panel_rect, 4, border_radius=24)
        # Animation d'attaque (effet de flash ou déplacement)
        img_x = x
        img_y = y
        if anim_attack:
            img_x += 18 if not is_enemy else -18
            img_y -= 10
        # Afficher l'image PNG si elle existe
        img = self.load_monster_image(monster.name)
        if img:
            img = pygame.transform.scale(img, (MONSTER_SIZE, MONSTER_SIZE))
            screen.blit(img, (img_x, img_y))
            if anim_attack:
                s = pygame.Surface((MONSTER_SIZE, MONSTER_SIZE), pygame.SRCALPHA)
                s.fill((255,255,0,80))
                screen.blit(s, (img_x, img_y))
        else:
            monster_rect = pygame.Rect(img_x, img_y, MONSTER_SIZE, MONSTER_SIZE)
            pygame.draw.rect(screen, GRAY, monster_rect, border_radius=18)
        # Barre de vie style Pokémon
        hp_val = anim_hp if anim_hp is not None else monster.current_hp
        health_percent = hp_val / monster.max_hp
        health_width = int(MONSTER_SIZE * health_percent)
        hp_bg_rect = pygame.Rect(x+10, y + MONSTER_SIZE + 18, MONSTER_SIZE-20, 18)
        pygame.draw.rect(screen, POKE_HP_BG, hp_bg_rect, border_radius=10)
        pygame.draw.rect(screen, POKE_HP_BORDER, hp_bg_rect, 2, border_radius=10)
        hp_bar_rect = pygame.Rect(x+12, y + MONSTER_SIZE + 20, health_width-24 if health_width>24 else 0, 14)
        pygame.draw.rect(screen, POKE_HP_BAR, hp_bar_rect, border_radius=7)
        # Nom du monstre dans une bulle arrondie
        name_rect = pygame.Rect(x+MONSTER_SIZE//2-60, y-32, 120, 32)
        pygame.draw.rect(screen, POKE_PANEL, name_rect, border_radius=16)
        pygame.draw.rect(screen, POKE_PANEL_BORDER, name_rect, 2, border_radius=16)
        name_text = FONT.render(f"{monster.name} Nv.{monster.level}", True, POKE_PANEL_BORDER)
        name_text_rect = name_text.get_rect(center=name_rect.center)
        screen.blit(name_text, name_text_rect)
        # PV
        hp_text = FONT.render(f"PV: {hp_val}/{monster.max_hp}", True, POKE_HP_BORDER)
        screen.blit(hp_text, (x+MONSTER_SIZE//2-60, y + MONSTER_SIZE + 42))

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
        # Fond dégradé style Pokémon
        for y in range(WINDOW_HEIGHT):
            color = [
                int(POKE_BG_TOP[i] + (POKE_BG_BOTTOM[i] - POKE_BG_TOP[i]) * y / WINDOW_HEIGHT)
                for i in range(3)
            ]
            pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))
        # Animation
        if self.is_animating():
            # Attaque du joueur ou de l'ennemi
            if self.anim_attacker == self.current_monster:
                self.draw_monster_info(self.enemy_monster, WINDOW_WIDTH - MONSTER_SIZE - 50, 50, True,
                                      anim_hp=self.anim_hp_current if self.anim_target==self.enemy_monster else None)
                self.draw_monster_info(self.current_monster, 50, WINDOW_HEIGHT - MONSTER_SIZE - 150,
                                      anim_hp=None,
                                      anim_attack=(self.anim_state=="attack"))
            else:
                self.draw_monster_info(self.enemy_monster, WINDOW_WIDTH - MONSTER_SIZE - 50, 50, True,
                                      anim_hp=None,
                                      anim_attack=(self.anim_state=="attack"))
                self.draw_monster_info(self.current_monster, 50, WINDOW_HEIGHT - MONSTER_SIZE - 150,
                                      anim_hp=self.anim_hp_current if self.anim_target==self.current_monster else None)
        else:
            self.draw_monster_info(self.enemy_monster, WINDOW_WIDTH - MONSTER_SIZE - 50, 50, True)
            self.draw_monster_info(self.current_monster, 50, WINDOW_HEIGHT - MONSTER_SIZE - 150)
        self.draw_monster_selection()
        # Message dans une bulle arrondie
        if self.message:
            msg_rect = pygame.Rect(WINDOW_WIDTH//2-180, 18, 360, 38)
            pygame.draw.rect(screen, POKE_PANEL, msg_rect, border_radius=16)
            pygame.draw.rect(screen, POKE_PANEL_BORDER, msg_rect, 2, border_radius=16)
            text = FONT.render(self.message, True, POKE_PANEL_BORDER)
            text_rect = text.get_rect(center=msg_rect.center)
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
    battle_scene.reset_animation()
    running = True
    battles_won = 0
    show_upgrade = False
    upgrade_pending = False
    upgrade_applied = False
    enemy_attack_pending = False
    while running:
        # Gestion du pop-up d'amélioration dans une boucle dédiée
        if show_upgrade:
            battle_scene.show_upgrade_dialog()
            if not upgrade_applied:
                battle_scene.upgrade_monsters()
                upgrade_applied = True
            waiting_choice = True
            while waiting_choice:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting_choice = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if battle_scene.btn_yes.rect.collidepoint(event.pos):
                            show_upgrade = False
                            upgrade_applied = False
                            # Apparition d'un nouvel ennemi
                            from game import get_player_average_level, create_enemy_monster
                            avg_level = get_player_average_level(player_monsters) if hasattr(player_monsters[0], 'level') else 1
                            enemy_monster = create_enemy_monster(avg_level)
                            battle_scene.enemy_monster = enemy_monster
                            battle_scene.show_message(f"Un {enemy_monster.name} de niveau {enemy_monster.level} apparaît !")
                            battle_scene.create_buttons()
                            waiting_choice = False
                        elif battle_scene.btn_no.rect.collidepoint(event.pos):
                            running = False
                            show_upgrade = False
                            upgrade_applied = False
                            waiting_choice = False
                clock.tick(60)
            continue  # Recommence la boucle principale après le choix

        # Animation d'attaque en cours
        if battle_scene.is_animating():
            battle_scene.update_animation()
            battle_scene.draw()
            clock.tick(60)
            continue

        # Gestion normale des événements
        for event in pygame.event.get():
            result = battle_scene.handle_event(event)
            if result == "QUIT":
                running = False
            elif result == "ENEMY_TURN":
                # Lance animation d'attaque du joueur
                attack = random.choice(enemy_monster.attacks)
                def enemy_counter():
                    # Animation de contre-attaque de l'ennemi
                    battle_scene.start_attack_animation(
                        battle_scene.enemy_monster,
                        battle_scene.current_monster,
                        attack.name,
                        attack.damage,
                        None
                    )
                    battle_scene.show_message(f"{enemy_monster.name} utilise {attack.name}!")
                # Animation d'attaque du joueur
                last_attack = battle_scene.current_monster.attacks[0] if hasattr(battle_scene.current_monster, 'attacks') else None
                # On récupère le nom et les dégâts de la dernière attaque utilisée
                # Pour cela, on modifie handle_event pour stocker l'attaque utilisée
                # Ici, on suppose que le joueur vient d'attaquer
                # On lance l'animation d'attaque du joueur
                battle_scene.start_attack_animation(
                    battle_scene.current_monster,
                    battle_scene.enemy_monster,
                    last_attack.name if last_attack else "Attaque",
                    last_attack.damage if last_attack else 20,
                    enemy_counter
                )
                battle_scene.show_message(f"{battle_scene.current_monster.name} utilise {last_attack.name if last_attack else 'Attaque'}!")

        # Vérification victoire
        if not enemy_monster.is_alive():
            if not show_upgrade:
                show_upgrade = True
                upgrade_applied = False
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
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
