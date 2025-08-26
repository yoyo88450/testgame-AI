import random
from monster import Monster, Attack
from items import Item

def create_items():
    return {
        'potion': Item("Potion", "Restaure 50 PV", "heal", 50),
        'super_potion': Item("Super Potion", "Restaure 100 PV", "heal", 100),
        'revive': Item("Rappel", "Ressuscite un monstre avec 50% de ses PV", "revive", 50),
        'attack_boost': Item("Protéine", "Augmente l'attaque de 10 points", "attack_boost", 10)
    }

def create_monster_list():
    # Création des attaques
    fire_blast = Attack("Boule de Feu", 30)
    thunder = Attack("Tonnerre", 25)
    heal = Attack("Soin", 0, 20)
    ice_beam = Attack("Rayon Glacé", 20)
    
    # Création des monstres
    dragon = Monster("Dragon", 100, [fire_blast, thunder, heal, ice_beam])
    golem = Monster("Golem", 120, [Attack("Séisme", 35), Attack("Lance-Pierre", 15),
                                 Attack("Protection", 0, 15), Attack("Charge", 20)])
    phoenix = Monster("Phénix", 90, [Attack("Flammes Éternelles", 40), Attack("Renaissance", 0, 30),
                                   Attack("Tornade", 25), Attack("Griffes", 15)])
    
    return [dragon, golem, phoenix]

def display_monster_status(monster):
    print(f"\n{monster.name} - PV: {monster.current_hp}/{monster.max_hp}")

def display_attacks(monster):
    print("\nAttaques disponibles:")
    for i, attack in enumerate(monster.attacks, 1):
        print(f"{i}. {attack.name} (Dégâts: {attack.damage}, Soin: {attack.heal})")

def display_inventory(inventory):
    print("\nInventaire:")
    for item_name, (item, quantity) in inventory.items():
        print(f"{item_name}: {quantity}x {item.description}")

def use_item(inventory, item_name, monster):
    if item_name in inventory:
        item, quantity = inventory[item_name]
        if quantity > 0:
            success, message = item.use(monster)
            if success:
                inventory[item_name] = (item, quantity - 1)
                print(message)
                return True
            else:
                print(message)
                return False
    return False

def main():
    # Initialisation
    print("Bienvenue dans le jeu de combat de monstres!")
    monsters = create_monster_list()
    player_monsters = monsters.copy()
    current_monster = player_monsters[0]
    
    # Création de l'inventaire initial
    items = create_items()
    inventory = {
        'potion': (items['potion'], 3),
        'super_potion': (items['super_potion'], 1),
        'revive': (items['revive'], 1),
        'attack_boost': (items['attack_boost'], 2)
    }
    enemy_monster = Monster("Boss", 150, [
        Attack("Frappe Puissante", 30),
        Attack("Régénération", 0, 25),
        Attack("Explosion", 40),
        Attack("Coup Rapide", 20)
    ])

    # Boucle principale du jeu
    while True:
        # Affichage de l'état du combat
        print("\n" + "="*50)
        display_monster_status(current_monster)
        display_monster_status(enemy_monster)

        # Tour du joueur
        print("\nVotre tour!")
        print("Actions disponibles:")
        print("1-4: Utiliser une attaque")
        print("5: Changer de monstre")
        print("6: Utiliser un objet")
        
        display_attacks(current_monster)
        
        # Choix du joueur
        while True:
            try:
                choice = int(input("\nQue souhaitez-vous faire ? "))
                if 1 <= choice <= 6:
                    break
                print("Choix invalide!")
            except ValueError:
                print("Veuillez entrer un nombre!")

        # Traitement du choix du joueur
        if choice == 5:
            print("\nChoisissez votre monstre:")
            alive_monsters = [m for m in player_monsters if m.is_alive()]
            for i, monster in enumerate(alive_monsters, 1):
                print(f"{i}. {monster.name} (PV: {monster.current_hp}/{monster.max_hp})")
            
            while True:
                try:
                    monster_choice = int(input("Numéro du monstre: ")) - 1
                    if 0 <= monster_choice < len(alive_monsters):
                        current_monster = alive_monsters[monster_choice]
                        break
                    print("Choix invalide!")
                except ValueError:
                    print("Veuillez entrer un nombre!")
        else:
            if choice == 6:
                # Utilisation d'un objet
                display_inventory(inventory)
                print("\nObjets disponibles:")
                available_items = [name for name, (item, qty) in inventory.items() if qty > 0]
                
                if not available_items:
                    print("Vous n'avez plus d'objets!")
                    continue
                
                for i, item_name in enumerate(available_items, 1):
                    item, qty = inventory[item_name]
                    print(f"{i}. {item.name} ({qty}x) - {item.description}")
                
                try:
                    item_choice = int(input("\nChoisissez un objet (0 pour annuler): "))
                    if item_choice == 0:
                        continue
                    if 1 <= item_choice <= len(available_items):
                        item_name = available_items[item_choice - 1]
                        
                        # Si c'est un objet de résurrection, montrer tous les monstres K.O.
                        if item_name == 'revive':
                            fainted_monsters = [m for m in player_monsters if m.is_fainted]
                            if not fainted_monsters:
                                print("Aucun monstre n'a besoin d'être ressuscité!")
                                continue
                            print("\nChoisissez un monstre à ressusciter:")
                            for i, monster in enumerate(fainted_monsters, 1):
                                print(f"{i}. {monster.name}")
                            monster_choice = int(input("Numéro du monstre: ")) - 1
                            if 0 <= monster_choice < len(fainted_monsters):
                                target_monster = fainted_monsters[monster_choice]
                                use_item(inventory, item_name, target_monster)
                        else:
                            use_item(inventory, item_name, current_monster)
                except ValueError:
                    print("Choix invalide!")
                continue
            
            # Attaque du joueur
            attack = current_monster.attacks[choice - 1]
            print(f"\n{current_monster.name} utilise {attack.name}!")
            damage = current_monster.get_attack_damage(attack.damage)
            enemy_monster.take_damage(damage)
            current_monster.heal(attack.heal)

        # Vérification de la victoire
        if not enemy_monster.is_alive():
            print(f"\nFélicitations! Vous avez vaincu {enemy_monster.name}!")
            break

        # Tour de l'ennemi
        print(f"\nTour de {enemy_monster.name}!")
        enemy_attack = random.choice(enemy_monster.attacks)
        print(f"{enemy_monster.name} utilise {enemy_attack.name}!")
        current_monster.take_damage(enemy_attack.damage)
        enemy_monster.heal(enemy_attack.heal)

        # Vérification de la défaite
        if not current_monster.is_alive():
            alive_monsters = [m for m in player_monsters if m.is_alive()]
            if not alive_monsters:
                print("\nTous vos monstres sont K.O.! Vous avez perdu!")
                break
            else:
                print(f"\n{current_monster.name} est K.O.!")
                current_monster = alive_monsters[0]
                print(f"{current_monster.name} entre en combat!")

if __name__ == "__main__":
    main()
