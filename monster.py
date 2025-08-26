class Monster:
    def __init__(self, name, hp, attacks):
        self.name = name
        self.max_hp = hp
        self.current_hp = hp
        self.attacks = attacks
        self.attack_boost = 0
        self.is_fainted = False
    
    def is_alive(self):
        return self.current_hp > 0 and not self.is_fainted
    
    def take_damage(self, damage):
        self.current_hp = max(0, self.current_hp - damage)
        if self.current_hp == 0:
            self.is_fainted = True
    
    def heal(self, amount):
        if not self.is_fainted:
            self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def revive(self, heal_amount):
        if self.is_fainted:
            self.is_fainted = False
            self.current_hp = min(heal_amount, self.max_hp)
            return True
        return False
    
    def apply_attack_boost(self, boost):
        self.attack_boost += boost
    
    def get_attack_damage(self, base_damage):
        return base_damage + self.attack_boost

class Attack:
    def __init__(self, name, damage, heal=0):
        self.name = name
        self.damage = damage
        self.heal = heal
