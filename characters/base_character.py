from abc import ABC, abstractmethod
from game_logic.dice import roll as dice_roll

class BaseCharacter(ABC):
    def __init__(self, name: str, health: int = 100):
        self.name = name
        self.max_health = health
        self.health = health
        self.shield = 0
        self.skills = {
            "방어": {"cooldown": 3, "current_cd": 0}
        }
        self.stats_values = {} 

        # 버프 및 시스템 변수
        self.buffs = [] 
        self.turn_damage_received = 0 

        # 영창 관련
        self.is_casting = False
        self.casting_skill_name = None
        self.casting_turns_remaining = 0
        self.casting_total_turns = 0
        self.casting_completed = False

    def roll_dice(self, dice_str: str) -> int:
        """무기 파괴 등의 디버프를 고려한 주사위 굴림"""
        val = dice_roll(dice_str)
        if self.has_buff("무기 파괴"):
            print(f"  - [무기 파괴] {self.name}의 주사위 값이 2 감소합니다!")
            val = max(1, val - 2)
        return val

    def add_buff(self, name: str, buff_type: str, duration: int, effect: dict = None):
        self.buffs.append({'name': name, 'type': buff_type, 'duration': duration, 'effect': effect or {}})

    def remove_buff(self, name: str):
        self.buffs = [b for b in self.buffs if b['name'] != name]

    def clear_buffs(self, buff_type: str):
        self.buffs = [b for b in self.buffs if b['type'] != buff_type]

    def has_buff(self, name: str) -> bool:
        return any(b['name'] == name for b in self.buffs)

    def take_damage(self, damage: int, damage_type: str = "일반 피해", attacker=None) -> int:
        """피해를 입히고 실제 적용된 총 피해량(체력+보호막)을 반환합니다."""
        if hasattr(self, 'damage_cap') and self.damage_cap > 0:
            remaining_cap = max(0, self.damage_cap - self.turn_damage_received)
            if damage > remaining_cap:
                print(f"  - [패시브: 에테르 강탈] 피해 상한 적용: {damage} -> {remaining_cap}")
                damage = remaining_cap
            if damage <= 0:
                print(f"  - [패시브] {self.name}가 이번 턴 최대 피해량에 도달해 피해를 무시합니다!")
                return 0

        initial_total = self.health + self.shield
        
        if self.has_buff("회피"):
            print(f"  - {self.name}가 공격을 회피했습니다!")
            return 0

        final_damage = damage
        if damage_type == "관통 고정 피해":
            print(f"  - [관통] 보호막을 무시합니다!")
            self.health -= final_damage
        else:
            if damage_type == "일반 피해" and self.has_buff("방어"):
                final_damage = int(final_damage * 0.1)
                print(f"  - {self.name}의 방어로 피해가 90% 감소했습니다!")

            if self.shield > 0:
                if self.shield >= final_damage:
                    self.shield -= final_damage
                    final_damage = 0
                else:
                    final_damage -= self.shield
                    self.shield = 0
            self.health -= final_damage
            
        if self.health < 0: self.health = 0
        actual_dealt = initial_total - (self.health + self.shield)
        self.turn_damage_received += actual_dealt
        return actual_dealt

    def is_alive(self) -> bool:
        return self.health > 0
    
    def start_turn(self):
        self.turn_damage_received = 0 
        for skill in self.skills.values():
            if skill['current_cd'] > 0: skill['current_cd'] -= 1
        
        expired_buffs = []
        for buff in self.buffs:
            buff['duration'] -= 1
            if buff['duration'] <= 0: expired_buffs.append(buff['name'])
        
        for name in expired_buffs:
            print(f"  - {self.name}의 {name} 효과가 종료되었습니다.")
            self.remove_buff(name)

        if self.is_casting and not self.casting_completed:
            self.casting_turns_remaining -= 1
            if self.casting_turns_remaining <= 0: self.casting_completed = True

    def start_casting(self, skill_name, turns):
        self.is_casting, self.casting_skill_name, self.casting_turns_remaining, self.casting_total_turns, self.casting_completed = True, skill_name, turns, turns, False

    def cancel_casting(self):
        self.is_casting, self.casting_skill_name, self.casting_turns_remaining, self.casting_total_turns, self.casting_completed = False, None, 0, 0, False

    def on_battle_start(self): pass

    @abstractmethod
    def act(self, action_name: str = None) -> dict: pass
    
    @abstractmethod
    def get_passive_log(self) -> str: pass
