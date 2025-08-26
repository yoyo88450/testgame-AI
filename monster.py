class Monster:
    def __init__(self, name, hp, attacks):
        self.name = name
        self.max_hp = hp
        self.current_hp = hp
        self.attacks = attacks
    
    def is_alive(self):
        return self.current_hp > 0
    
    def take_damage(self, damage):
        self.current_hp = max(0, self.current_hp - damage)
    
    def heal(self, amount):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

class Attack:
    def __init__(self, name, damage, heal=0):
        self.name = name
        self.damage = damage
        self.heal = heal
