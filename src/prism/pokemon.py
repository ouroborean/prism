
from typing import Tuple, Optional
import typing
import random
from PIL import Image
from prism.abi_db import initialize_abilities
from prism.status import StatusEffect, status_applied, is_greater_status
from prism.stat import Stat
from prism import ptypes
from prism.ability import Ability, AbilityType, TargetingType
from prism.passive import Passive
import importlib.resources
from prism.poke_db import initialize_pokemon



if typing.TYPE_CHECKING:
    from prism.battle import BattleSlot

def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)

def get_stat_mod(stages: int) -> float:
    over = 2
    under = 2
    if stages > 0:
        over += stages
    elif stages < 0:
        under += stages * -1
    
    return over/under

db = initialize_pokemon()
adb = initialize_abilities()

def pokespawn(database_name: str, level: int, moveset: list[str] = [], wild: bool = False) -> "Pokemon":
    pokemon = Pokemon(*db[database_name])
    pokemon.set_level(level)
    if moveset:
        for move in moveset:
            pokemon.learn_ability(adb[move])

    return pokemon

natures = {
    "Serious": (None),
    "Lonely": (Stat.ATK, Stat.DEF),
    "Brave": (Stat.ATK, Stat.SPD),
    "Adamant": (Stat.ATK, Stat.SPATK),
    "Naughty": (Stat.ATK, Stat.SPDEF),
    "Bold": (Stat.DEF, Stat.ATK),
    "Relaxed": (Stat.DEF, Stat.SPD),
    "Impish": (Stat.DEF, Stat.SPATK),
    "Lax": (Stat.DEF, Stat.SPDEF),
    "Timid": (Stat.SPD, Stat.ATK),
    "Hasty": (Stat.SPD, Stat.DEF),
    "Jolly": (Stat.SPD, Stat.SPATK),
    "Naive": (Stat.SPD, Stat.SPDEF),
    "Modest": (Stat.SPATK, Stat.ATK),
    "Mild": (Stat.SPATK, Stat.DEF),
    "Quiet": (Stat.SPATK, Stat.SPD),
    "Rash": (Stat.SPATK, Stat.SPDEF),
    "Calm": (Stat.SPDEF, Stat.ATK),
    "Gentle": (Stat.SPDEF, Stat.DEF),
    "Sassy": (Stat.SPDEF, Stat.SPD),
    "Careful": (Stat.SPDEF, Stat.SPATK)
}



class Pokemon:
    
    name: str
    database_name: str
    is_egg: bool
    abilities: list[Ability]
    status_effects: dict[StatusEffect, int]
    current_hp: int
    passive_pool: Tuple[Passive]
    passive: Passive
    decision: int
    fainted: bool
    battle_slot: Optional["BattleSlot"]
    move_pool: list[Ability]
    team: list["Pokemon"]
    level: int
    front_image: Image.Image
    back_image: Image.Image
    current_pp: list[int]
    sleep_duration: int
    action_failed: bool
    failed_confusion: bool
    failed_attract: bool
    failed_sleep: bool
    failed_frozen: bool
    failed_paralyze: bool

    def __init__(self, name: str, types: Tuple[ptypes.PokemonType], atk: int, defense: int, spatk: int, spdef: int, spd: int, hp: int, passive_pool: Tuple[Passive], egg: bool = False):
        self.decision = 10
        self.name = name
        self.database_name = self.get_database_name(name)
        self.is_egg = egg
        self.sleep_duration = 0
        self.action_failed = False
        self.failed_attract = False
        self.failed_confusion = False
        self.failed_frozen = False
        self.failed_paralyze = False
        self.failed_sleep = False
        self.passive = Passive.INTIMIDATE
        try:
            self.front_image = get_image_from_path(self.database_name + "_front.png")
        except:
            self.front_image = None
        
        try:
            self.back_image = get_image_from_path(self.database_name + "_back.png")
        except:
            self.back_image = None
        

        self.level = 1
        self.nature = "Serious"
        self.types = types
        self.abilities = []
        self.team = []
        self.status_effects = {}
        self.passive_pool = passive_pool
        self.current_pp = []
        self.fainted = False
        self.base_stats = {
            Stat.ATK: atk,
            Stat.DEF: defense,
            Stat.SPATK: spatk,
            Stat.SPDEF: spdef,
            Stat.SPD: spd,
            Stat.HP: hp
        }
        self.boosts = {
            Stat.ATK: 0,
            Stat.DEF: 0,
            Stat.SPATK: 0,
            Stat.SPDEF: 0,
            Stat.SPD: 0,
            Stat.EVAS: 0,
            Stat.ACC: 0
        }
        self.ev = {
            Stat.ATK: 0,
            Stat.DEF: 0,
            Stat.SPATK: 0,
            Stat.SPDEF: 0,
            Stat.SPD: 0,
            Stat.HP: 0
        }
        self.iv = {
            Stat.ATK: 0,
            Stat.DEF: 0,
            Stat.SPATK: 0,
            Stat.SPDEF: 0,
            Stat.SPD: 0,
            Stat.HP: 0
        }
        self.current_hp = self.get_stat(Stat.HP)

    def get_database_name(self, name:str) -> str:
        for char in name:
            if not char.isalpha():
                name.replace(char, "")
        return name.lower()

    def using_ability(self) -> bool:
        if self.decision >= len(self.abilities) and self.decision != 10:
            return False
        return True

    def level_up(self):
        pass

    def set_level(self, level: int):
        self.level = level
        self.current_hp = self.get_stat(Stat.HP)

    def describe(self):
        print(f"{self.name}")
        if len(self.types) == 1:
            print(f"{self.types[0].name}")
        else:
            print(f"{self.types[0].name}/{self.types[1].name}")
        print(f"ATK: {self.get_stat(Stat.ATK)}")
        print(f"DEF: {self.get_stat(Stat.DEF)}")
        print(f"SPA: {self.get_stat(Stat.SPATK)}")
        print(f"SDF: {self.get_stat(Stat.SPDEF)}")
        print(f"SPD: {self.get_stat(Stat.SPD)}")
        print(f"HP: {self.get_stat(Stat.HP)}")

    def assign_team(self, team: list["Pokemon"]):
        self.team = team

    def learn_ability(self, ability: Ability):
        self.current_pp.append(ability.max_pp)
        self.abilities.append(ability)

    def set_passive(self, passive: Passive):
        self.passive = passive

    def get_enemy(self, active_pokemon: list["Pokemon"]) -> "Pokemon":
        for pokemon in active_pokemon:
            if self != pokemon:
                return pokemon
        return active_pokemon[0]

    def get_crit_stat(self, stat: Stat) -> int:
        mod_stat = 2 * self.base_stats[stat] + self.iv[stat] + self.ev[stat]//4
        mod_stat += 5
        if natures[self.nature] is not None:
            if natures[self.nature][0] == stat:
                mod_stat = int(mod_stat * 1.1)
            elif natures[self.nature][1] == stat:
                mod_stat = int(mod_stat * .9)

        if (stat == Stat.ATK or stat == Stat.SPATK) and self.boosts[stat] < 0:
            mod_stat = int(mod_stat * get_stat_mod(0))

        if (stat == Stat.DEF or stat == Stat.SPDEF) and self.boosts[stat] > 0:
            mod_stat = int(mod_stat * get_stat_mod(0))

        return mod_stat

    def get_stat(self, stat: Stat) -> int:
        if stat == Stat.HP:
            mod_stat = (.01 * (2 * self.base_stats[stat] + self.iv[stat] + (self.ev[stat] * .25)) * self.level)
            mod_stat += 10 + self.level
        else:
            mod_stat = (.01 * (2 * self.base_stats[stat] + self.iv[stat] + (self.ev[stat] * .25)) * self.level)
            mod_stat += 5
            if natures[self.nature] is not None:
                if natures[self.nature][0] == stat:
                    mod_stat = int(mod_stat * 1.1)
                elif natures[self.nature][1] == stat:
                    mod_stat = int(mod_stat * .9)

            mod_stat = int(mod_stat * get_stat_mod(self.boosts[stat]))

        if self.has_status(StatusEffect.PARALYZE) and stat == Stat.SPD:
            mod_stat = mod_stat // 2

        return mod_stat

    def has_status(self, status: StatusEffect) -> bool:
        for effect in self.status_effects:
            if effect == StatusEffect.PARALYZE:
                return True
        return False

    def execute_ability(self, enemy: "Pokemon", abi: Ability):
        print(f"{self.name} used {abi.name}!")
        if abi.target == TargetingType.ENEMY:
            immune_check = False
            for ptype in enemy.types:
                if ptype in ptypes.immune_to and abi.ptype in ptypes.immune_to[ptype]:
                    immune_check = True
            if not immune_check:
                if self.miss_check(enemy, abi):
                    if AbilityType.DAMAGE in abi.atype:
                        for effect in abi.atype[AbilityType.DAMAGE]:
                            self.damage(enemy, abi, effect)
                    if AbilityType.TARGET_STATUS in abi.atype:
                        for effect in abi.atype[AbilityType.TARGET_STATUS]:
                            self.apply_status(enemy, effect)
                    if AbilityType.SELF_STATUS in abi.atype:
                        for effect in abi.atype[AbilityType.SELF_STATUS]:
                            self.apply_status(self, effect)
                    if AbilityType.TARGET_BOOST in abi.atype:
                        for effect in abi.atype[AbilityType.TARGET_BOOST]:
                            self.apply_boost(enemy, effect)
                    if AbilityType.SELF_BOOST in abi.atype:
                        for effect in abi.atype[AbilityType.SELF_BOOST]:
                            self.apply_boost(self, effect)
            else:
                print(f"It doesn't affect the enemy {enemy.name}!")
        elif abi.target == TargetingType.SELF:
            if AbilityType.DAMAGE in abi.atype:
                for effect in abi.atype[AbilityType.DAMAGE]:
                    self.damage(self, abi, effect)
            if AbilityType.SELF_STATUS in abi.atype:
                for effect in abi.atype[AbilityType.SELF_STATUS]:
                    self.apply_status(self, effect)
            if AbilityType.SELF_BOOST in abi.atype:
                for effect in abi.atype[AbilityType.SELF_BOOST]:
                    self.apply_boost(self, effect)
            if AbilityType.HEALING in abi.atype:
                for effect in abi.atype[AbilityType.HEALING]:
                    self.apply_healing(self, effect)
        elif abi.target == TargetingType.ENEMY_BATTLEZONE:
            if AbilityType.ENEMY_BATTLEZONE in abi.atype:
                for effect in abi.atype[AbilityType.ENEMY_BATTLEZONE]:
                    self.apply_battlezone_effect(enemy, effect)
        elif abi.target == TargetingType.SELF_BATTLEZONE:
            if AbilityType.SELF_BATTLEZONE in abi.atype:
                for effect in abi.atype[AbilityType.SELF_BATTLEZONE]:
                    self.apply_battlezone_effect(enemy, effect)
        abi.expend_pp()
        if enemy.passive == Passive.PRESSURE:
            abi.expend_pp()

    def apply_healing(self, target: "Pokemon", abi_details: list):
        heal_mag = abi_details[0] / 100

        heal_amount = int(target.get_stat(Stat.HP) * heal_mag)

        target.current_hp += heal_amount

        if target.current_hp > target.get_stat(Stat.HP):
            target.current_hp = target.get_stat(Stat.HP)
        
        print(f"{target.name} had its HP restored!")
        print(f"{target.name} has {target.current_hp}/{target.get_stat(Stat.HP)} HP!")

    def set_battleslot(self, battle_slot: "BattleSlot"):
        self.battle_slot = battle_slot

    def apply_battlezone_effect(self, target: "Pokemon", abi_details: list):
        effect = abi_details[0]
        activation_string = abi_details[1]

        for eff in target.battle_slot.effects:
            if eff.effect_type == effect.effect_type:
                print("It failed!")
                return

        target.battle_slot.add_effect(effect)
        print(activation_string)

    def apply_boost(self, target: "Pokemon", abi_details: list):
        chance = abi_details[0]
        boost_type = abi_details[1]
        boost_mag = abi_details[2]

        roll = random.randint(1, 100)

        if roll <= chance:
            for boost in boost_type:
                if boost_mag < 0:
                    print(f"{target.name}'s {boost.name} has been lowered by {boost_mag * -1}!")
                else:
                    print(f"{target.name}'s {boost.name} has been raised by {boost_mag}!")
                target.receive_boost(boost, boost_mag)

    def pre_check_for_status_failure(self, scene) -> bool:
        for status in self.status_effects:
            if status == StatusEffect.PARALYZE:
                roll = random.randint(1,100)
                if roll <= 25:
                    self.failed_paralyze = True
                    scene.pre_message_queue.append(f"{self.name} is paralyzed! It can't move!")
                    return True
            if status == StatusEffect.CONFUSE:
                roll = random.randint(1, 100)
                print(f"{self.name} is confused!")
                if roll <= 33:
                    self.failed_confusion = True
                    scene.pre_message_queue.append(f"{self.name} hurt itself in its confusion!")
                    self.confusion_self_damage()
                    return True
            if status == StatusEffect.FREEZE:
                if roll <= 20:
                    self.failed_frozen = True
                    scene.pre_message_queue.append(f"{self.name} is frozen solid!")
                    return True
            if status == StatusEffect.ATTRACT:
                scene.pre_message_queue.append(f"{self.name} is in love!")
                roll = random.randint(1, 100)
                if roll <= 50:
                    self.failed_attract = True
                    scene.pre_message_queue.append(f"{self.name} is immobilized by love!")
                    return True
            if status == StatusEffect.SLEEP:
                if self.sleep_duration > 0:
                    self.sleep_duration -= 1
                if self.sleep_duration == 0:
                    self.failed_sleep = True
                    return True
                
        return False

    def execute_status_failure(self, scene) -> str:
        for status in self.status_effects:
            if status == StatusEffect.PARALYZE:
                roll = random.randint(1,100)
                if roll <= 25:
                    scene.pre_message_queue.append(f"{self.name} is paralyzed! It can't move!")
                    return True
            if status == StatusEffect.CONFUSE:
                roll = random.randint(1, 100)
                print(f"{self.name} is confused!")
                if roll <= 33:
                    scene.pre_message_queue.append(f"{self.name} hurt itself in its confusion!")
                    self.confusion_self_damage()
                    return True
            if status == StatusEffect.FREEZE:
                scene.pre_message_queue.append(f"{self.name} is frozen solid!")
                return True
            if status == StatusEffect.ATTRACT:
                scene.pre_message_queue.append(f"{self.name} is in love!")
                roll = random.randint(1, 100)
                if roll <= 50:
                    scene.pre_message_queue.append(f"{self.name} is immobilized by love!")
                    return True
        return False

    def status_failed(self) -> bool:
        return self.failed_attract or self.failed_confusion or self.failed_frozen or self.failed_paralyze or self.failed_sleep

    def confusion_self_damage(self):
        damage_base = 42
        damage_base = damage_base * 40
        attack_defense = self.get_stat(Stat.ATK) / self.get_stat(Stat.DEF)
        damage_base = int(damage_base * attack_defense)
        damage_base = damage_base // 50
        damage_base += 2

        damage_roll = (100 - random.randint(0, 15)) / 100
        damage_base = int(damage_base * damage_roll)

        self.current_hp -= damage_base
        if self.current_hp < 0:
            self.current_hp = 0
            self.fainted = True

    def is_status_immune(self, status: StatusEffect) -> bool:
        if status == StatusEffect.BURN and (ptypes.PokemonType.FIRE in self.types): 
            return True

    def burn_tick(self):
        print(f"{self.name} was hurt by its burn!")
        burn_damage = self.get_stat(Stat.HP) // 16
        self.current_hp -= burn_damage
        if self.current_hp < 0:
            self.current_hp = 0
            self.fainted = True
        print(f"{self.name} has {self.current_hp}/{self.get_stat(Stat.HP)}!")

    def apply_status(self, target: "Pokemon", abi_details: list):
        chance = abi_details[0]
        status_list = abi_details[1]

        for status in status_list:
            if not target.is_status_immune(status):
                roll = random.randint(1,100)
                if roll <= chance:
                    if is_greater_status(status) and target.contains_greater_status():
                        print(f"{target.name} is already afflicted!")
                    else:
                        target.receive_status(status)
                        print(status_applied(target,status))
                        return

    def contains_greater_status(self) -> bool:
        gen = (StatusEffect.BURN, StatusEffect.FREEZE, StatusEffect.PARALYZE, StatusEffect.POISON, StatusEffect.TOXIC, StatusEffect.SLEEP)
        for eff in gen:
            if eff in self.status_effects:
                return True
        return False

    def already_contains_lesser(self, effect: StatusEffect) -> bool:
        pass

    def receive_boost(self, stat: Stat, boost: int):
        self.boosts[stat] += boost

        if self.boosts[stat] > 6:
            self.boosts[stat] = 6
        elif self.boosts[stat] < -6:
            self.boosts[stat] = -6

    def receive_damage(self, damage: int):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0
        print(f"{self.name} has {self.current_hp}/{self.get_stat(Stat.HP)} HP!")
        if self.current_hp == 0:
            print(f"{self.name} fainted!")
            self.fainted = True

    def receive_status(self, status: StatusEffect):
        if status == StatusEffect.CONFUSE:
            dur = random.randint(2,5)
        elif status == StatusEffect.SLEEP:
            dur = random.randint(1,3)
        elif status == StatusEffect.REST_SLEEP:
            dur = random.randint(3)
        else:
            dur = None
        self.status_effects[status] = dur

    def miss_check(self, target:"Pokemon", used_ability: Ability) -> bool:
        
        if used_ability.accuracy is not None:
            lower_acc = 3
            upper_acc = 3
            if self.boosts[Stat.ACC] < 0:
                lower_acc -= self.boosts[Stat.ACC]
            else:
                upper_acc += self.boosts[Stat.ACC]

            upper_evas = 3
            lower_evas = 3
            if self.boosts[Stat.EVAS] < 0:
                lower_evas -= self.boosts[Stat.EVAS]
            else:
                upper_evas += self.boosts[Stat.EVAS]

            accuracy_range = int(used_ability.accuracy * (upper_evas/lower_evas) * (upper_acc/lower_acc))

            hit_roll = random.randint(1, 100)

            if hit_roll <= accuracy_range:
                return True
            else:
                print(f"{self.name}'s attack missed!")
                return False
        return True



    def recoil_damage(self, target: "Pokemon", used_ability: Ability, abi_details: list):
        
        #Unpack effect details from argument
        power = abi_details[0]
        off_stat = abi_details[1]
        def_stat = abi_details[2]
        recoil = abi_details[3]

        crit_stage = 0
        if "crit" in used_ability.tags:
            crit_stage += 1
        if StatusEffect.FOCUS_ENERGY in self.status_effects:
            crit_stage += 2
        
        crit_range = 24
        if crit_stage == 1:
            crit_range = 8
        elif crit_stage == 2:
            crit_range = 2
        elif crit_stage == 3:
            crit_range = 1
        
        crit_roll = random.randint(1, crit_range)
        crit = False
        if crit_roll == 1:
            crit = True

        #Base damage magic numbers
        damage_base = 42
        damage_base = damage_base * power
        if not crit:
            attack_defense = self.get_stat(off_stat) / target.get_stat(def_stat)
        else:
            attack_defense = self.get_crit_stat(off_stat) / target.get_crit_stat(def_stat)
        damage_base = int(damage_base * attack_defense)
        damage_base = damage_base // 50
        damage_base += 2

        
        if crit:
            damage_base = int(damage_base * 1.5)

        damage_roll = (100 - random.randint(0, 15)) / 100
        damage_base = int(damage_base * damage_roll)

        
        
        for type in target.types:
            if used_ability.ptype in ptypes.strong_against[type]:
                damage_base = int(damage_base * .5)
            if used_ability.ptype in ptypes.weak_against[type]:
                damage_base = int(damage_base * 2)
        
        #Burn modification
        if off_stat == Stat.ATK and self.has_status(StatusEffect.BURN):
            damage_base = damage_base // 2
        
        print(f"Against {target.name}, {self.name}'s {used_ability.name} deals {damage_base} damage!")
        if crit:
            print("A critical hit!")
        target.receive_damage(damage_base)
        print(f"{self.name} was damaged by recoil!")
        self.receive_damage(int(damage_base * (recoil / 100)))

    def damage(self, target: "Pokemon", used_ability: Ability, abi_details: list):
        
        power = abi_details[0]
        off_stat = abi_details[1]
        def_stat = abi_details[2]

        crit_stage = 0
        if "crit" in used_ability.tags:
            crit_stage += 1
        if StatusEffect.FOCUS_ENERGY in self.status_effects:
            crit_stage += 2
        
        crit_range = 24
        if crit_stage == 1:
            crit_range = 8
        elif crit_stage == 2:
            crit_range = 2
        elif crit_stage == 3:
            crit_range = 1
        
        crit_roll = random.randint(1, crit_range)
        crit = False
        if crit_roll == 1:
            crit = True

        damage_base = 42
        damage_base = damage_base * power
        if not crit:
            attack_defense = self.get_stat(off_stat) / target.get_stat(def_stat)
        else:
            attack_defense = self.get_crit_stat(off_stat) / target.get_crit_stat(def_stat)
        damage_base = int(damage_base * attack_defense)
        damage_base = damage_base // 50
        damage_base += 2

        if crit:
            damage_base = int(damage_base * 1.5)
    
        damage_roll = (100 - random.randint(0, 15)) / 100
        damage_base = int(damage_base * damage_roll)

        
        
        for type in target.types:
            if used_ability.ptype in ptypes.strong_against[type]:
                damage_base = int(damage_base * .5)
            if used_ability.ptype in ptypes.weak_against[type]:
                damage_base = int(damage_base * 2)
        
        #Burn modification
        if off_stat == Stat.ATK and self.has_status(StatusEffect.BURN):
            damage_base = damage_base // 2

        print(f"Against {target.name}, {self.name}'s {used_ability.name} deals {damage_base} damage!")
        if crit:
            print("A critical hit!")
        target.receive_damage(damage_base)

        
        
    



