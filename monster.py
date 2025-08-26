class Monster:
    def __init__(self, name, hp, attacks, level=1):
        self.name = name
        self.base_hp = hp
        self.level = level
        self.exp = 0
        self.exp_to_next_level = 100 * self.level
        self.attack_boost = 0
        self.is_fainted = False
        self.attacks = attacks
        self.update_stats()
    
    def update_stats(self):
        # Les stats augmentent avec le niveau
        self.max_hp = int(self.base_hp * (1 + 0.1 * (self.level - 1)))
        self.current_hp = self.max_hp
    
    def gain_exp(self, exp_amount):
        self.exp += exp_amount
        leveled_up = False
        while self.exp >= self.exp_to_next_level:
            self.level_up()
            leveled_up = True
        return leveled_up
    
    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = 100 * self.level
        old_max_hp = self.max_hp
        self.update_stats()
        hp_gain = self.max_hp - old_max_hp
        print(f"\n{self.name} passe au niveau {self.level}!")
        print(f"PV max +{hp_gain} (nouveau total: {self.max_hp})")
        print(f"Puissance d'attaque augmentée!")
    
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
