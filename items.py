class Item:
    def __init__(self, name, description, effect_type, value):
        self.name = name
        self.description = description
        self.effect_type = effect_type  # 'heal', 'revive', 'attack_boost'
        self.value = value

    def use(self, monster):
        if self.effect_type == 'heal':
            if monster.is_alive():
                monster.heal(self.value)
                return True, f"{monster.name} a récupéré {self.value} PV!"
            return False, f"{monster.name} est K.O. et ne peut pas être soigné!"
        
        elif self.effect_type == 'revive':
            if monster.revive(self.value):
                return True, f"{monster.name} a été ressuscité avec {self.value} PV!"
            return False, f"{monster.name} n'est pas K.O.!"
        
        elif self.effect_type == 'attack_boost':
            if monster.is_alive():
                monster.apply_attack_boost(self.value)
                return True, f"L'attaque de {monster.name} augmente de {self.value}!"
            return False, f"{monster.name} est K.O. et ne peut pas recevoir de bonus!"
        
        return False, "Type d'objet inconnu!"
