import random
from monster import Monster, Attack

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

def main():
    # Initialisation
    print("Bienvenue dans le jeu de combat de monstres!")
    monsters = create_monster_list()
    player_monsters = monsters.copy()
    current_monster = player_monsters[0]
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
        
        display_attacks(current_monster)
        
        # Choix du joueur
        while True:
            try:
                choice = int(input("\nQue souhaitez-vous faire ? "))
                if 1 <= choice <= 5:
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
            # Attaque du joueur
            attack = current_monster.attacks[choice - 1]
            print(f"\n{current_monster.name} utilise {attack.name}!")
            enemy_monster.take_damage(attack.damage)
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
