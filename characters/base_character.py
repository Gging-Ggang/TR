from abc import ABC, abstractmethod

class BaseCharacter(ABC):
    def __init__(self, name: str, health: int = 100):
        self.name = name
        self.max_health = health
        self.health = health
        self.shield = 0
        self.skills = {
            "방어": {"cooldown": 3, "current_cd": 0}
        }
        self.stats_values = {} # 통계용 고유 수치 (예: 분노, 콤보 등)

        # 버프 관련 속성
        self.buffs = [] # [{'name': str, 'type': str, 'duration': int, 'effect': dict}]

        # 영창 관련 속성 (추가)
        self.is_casting = False
        self.casting_skill_name = None
        self.casting_turns_remaining = 0
        self.casting_total_turns = 0
        self.casting_completed = False

    def add_buff(self, name: str, buff_type: str, duration: int, effect: dict = None):
        """버프를 추가합니다. buff_type은 '[이로운 효과]' 또는 '[해로운 효과]'여야 합니다."""
        self.buffs.append({
            'name': name,
            'type': buff_type,
            'duration': duration,
            'effect': effect or {}
        })

    def remove_buff(self, name: str):
        self.buffs = [b for b in self.buffs if b['name'] != name]

    def clear_buffs(self, buff_type: str):
        """특정 타입의 버프를 모두 제거합니다 (예: 해제 시)"""
        self.buffs = [b for b in self.buffs if b['type'] != buff_type]

    def has_buff(self, name: str) -> bool:
        return any(b['name'] == name for b in self.buffs)

    def take_damage(self, damage: int, damage_type: str = "일반 피해", attacker=None):
        final_damage = damage
        
        # 회피 효과 확인 (이로운 효과)
        if self.has_buff("회피"):
            print(f"  - {self.name}가 공격을 회피했습니다!")
            return

        # 일반 피해일 경우 방어 메커니즘 적용 (고정 피해는 이를 무시함)
        if damage_type == "일반 피해":
            # "방어" 효과 확인 (1턴간 일반 피해 90% 감소)
            if self.has_buff("방어"):
                final_damage = int(final_damage * 0.1)
                print(f"  - {self.name}의 방어 효과로 피해가 90% 감소합니다! (최종 피해: {final_damage})")

        # 보호막 처리 (일반 피해와 고정 피해 모두 보호막으로 경감 가능)
        if self.shield > 0:
            if self.shield >= final_damage:
                self.shield -= final_damage
                final_damage = 0
            else:
                final_damage -= self.shield
                self.shield = 0
        
        # 최종 피해를 체력에서 차감
        self.health -= final_damage
            
        if self.health < 0:
            self.health = 0

    def is_alive(self) -> bool:
        return self.health > 0
    
    def start_turn(self):
        """턴 시작 시 처리할 로직 (패시브, 쿨타임 감소, 버프 지속시간 감소 등)"""
        for skill in self.skills.values():
            if skill['current_cd'] > 0:
                skill['current_cd'] -= 1
        
        # 버프 지속시간 감소 및 만료 처리
        expired_buffs = []
        for buff in self.buffs:
            buff['duration'] -= 1
            if buff['duration'] <= 0:
                expired_buffs.append(buff['name'])
        
        for name in expired_buffs:
            print(f"  - {self.name}의 {name} 효과가 종료되었습니다.")
            self.remove_buff(name)

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
