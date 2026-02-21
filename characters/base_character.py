from abc import ABC, abstractmethod

class BaseCharacter(ABC):
    def __init__(self, name: str, health: int = 100):
        self.name = name
        self.max_health = health
        self.health = health
        self.shield = 0
        self.skills = {}
        self.defense_cooldown = 0
        self.stats_values = {} # 통계용 고유 수치 (예: 분노, 콤보 등)

        # 영창 관련 속성 (추가)
        self.is_casting = False
        self.casting_skill_name = None
        self.casting_turns_remaining = 0
        self.casting_total_turns = 0
        self.casting_completed = False

    def take_damage(self, damage: int, attacker=None):
        if self.shield > 0:
            if self.shield >= damage:
                self.shield -= damage
            else:
                remaining_damage = damage - self.shield
                self.shield = 0
                self.health -= remaining_damage
        else:
            self.health -= damage
            
        if self.health < 0:
            self.health = 0

    def is_alive(self) -> bool:
        return self.health > 0
    
    def start_turn(self):
        """턴 시작 시 처리할 로직 (패시브, 쿨타임 감소 등)"""
        if self.defense_cooldown > 0:
            self.defense_cooldown -= 1
        for skill in self.skills.values():
            if skill['current_cd'] > 0:
                skill['current_cd'] -= 1
        
        # 영창 진행 처리 (추가)
        if self.is_casting and not self.casting_completed:
            self.casting_turns_remaining -= 1
            if self.casting_turns_remaining <= 0:
                self.casting_completed = True

    def start_casting(self, skill_name, turns):
        """영창 시작 (추가)"""
        self.is_casting = True
        self.casting_skill_name = skill_name
        self.casting_turns_remaining = turns
        self.casting_total_turns = turns
        self.casting_completed = False

    def cancel_casting(self):
        """영창 취소 (추가)"""
        if self.is_casting:
            self.is_casting = False
            self.casting_skill_name = None
            self.casting_turns_remaining = 0
            self.casting_total_turns = 0
            self.casting_completed = False

    def on_battle_start(self):
        """개전 효과 발동용"""
        pass

    @abstractmethod
    def act(self, action_name: str = None) -> dict:
        """캐릭터의 행동을 정의합니다. 공격, 방어 등."""
        pass
    
    @abstractmethod
    def get_passive_log(self) -> str:
        """캐릭터의 패시브 효과를 발동하고 로그를 반환합니다."""
        pass
