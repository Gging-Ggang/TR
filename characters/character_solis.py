from .base_character import BaseCharacter
from game_logic.dice import roll
import random

class CharacterSolis(BaseCharacter):
    def __init__(self, name="솔리스"):
        super().__init__(name=name, health=90)
        self.skills.update({
            "속임수 공격": {"cooldown": 3, "current_cd": 0},
            "비열한 기습": {"cooldown": 5, "current_cd": 0},
            "몽환삼단": {"cooldown": 6, "current_cd": 0},
            "결심": {"cooldown": 8, "current_cd": 0}
        })
        self.salui_stack = 0
        self.kyulsim_stack = 0
        self.deceptive_bonus = False
        self.stats_values = {"살의": 0, "결심": 0}

    def start_turn(self):
        super().start_turn()
        
        # [패시브: 계획] 턴 시작 시 1d3 주사위
        plan_roll = random.randint(1, 3)
        print(f"  - [패시브: 계획] 1d3 주사위: [{plan_roll}]")
        
        if plan_roll == 1:
            print(f"    > 계획 성공 (1): 이번 턴 모든 공격을 회피합니다!")
            self.add_buff("회피", "[이로운 효과]", 1)
        elif plan_roll == 2:
            print(f"    > 계획 성공 (2): 모든 스킬의 쿨타임이 1턴 감소합니다.")
            for s_name, s_data in self.skills.items():
                if s_data["current_cd"] > 0:
                    s_data["current_cd"] -= 1
        elif plan_roll == 3:
            print(f"    > 계획 성공 (3): '살의' 1스택을 획득합니다.")
            self.gain_salui(1)

        # 모든 스킬이 쿨타임일 때 방어막 4 획득
        if all(s["current_cd"] > 0 for s in self.skills.values()):
            print(f"  - [패시브] 모든 스킬이 쿨타임 중입니다. 보호막 4를 획득합니다.")
            self.shield += 4

        self.update_stats()

    def gain_salui(self, count):
        self.salui_stack += count
        print(f"  - '살의' 스택 증가 (+{count}): 현재 {self.salui_stack}/10")
        if self.salui_stack >= 10:
            print(f"    > 살의 10스택 도달! 다음 공격 시 최대 생명력의 10% 고정 피해를 입힙니다.")
        self.update_stats()

    def update_stats(self):
        self.stats_values["살의"] = self.salui_stack
        self.stats_values["결심"] = self.kyulsim_stack

    def get_passive_log(self) -> str:
        return f"{self.name}의 살의: {self.salui_stack}/10, 결심: {self.kyulsim_stack}"

    def act(self, action_name: str = None) -> dict:
        # [결심] 스택 소모 및 보정 처리
        is_critical = False
        if self.kyulsim_stack > 0 and action_name not in ["방어", "defense"]:
            self.kyulsim_stack -= 1
            is_critical = True
            self.gain_salui(1)
            print(f"  - [결심] 스택 소모 (남은 결심: {self.kyulsim_stack})")

        # 살의 10스택 고정 피해 체크
        bonus_fixed_dmg = 0
        if self.salui_stack >= 10 and action_name not in ["방어", "defense", "결심"]:
            self.salui_stack -= 10
            bonus_fixed_dmg = -1 # 최대 생명력 10% 특수 코드
            print(f"  - [살의 폭발] 10스택을 소모하여 고정 피해를 입힙니다!")

        result = {"type": "log", "message": "알 수 없는 행동"}

        if action_name == "일반공격":
            self.gain_salui(1)
            dmg = self.roll_dice("1d10")
            if self.deceptive_bonus:
                extra = self.roll_dice("2d6")
                dmg += extra
                print(f"  - [속임수 연계] 추가 피해 +{extra} 적용")
                self.deceptive_bonus = False
            
            if is_critical: dmg = int(dmg * 1.5)
            result = {"type": "attack", "damage": dmg, "message": f"{self.name}의 기습적인 칼날 공격!"}

        elif action_name in ["방어", "defense"]:
            skill = self.skills["방어"]
            skill["current_cd"] = skill["cooldown"]
            self.add_buff("방어", "일반", 1)
            result = {"type": "defense", "message": f"{self.name}가 방어 태세로 1턴간 피해를 90% 줄입니다."}

        elif action_name == "속임수 공격":
            skill = self.skills["속임수 공격"]
            skill["current_cd"] = skill["cooldown"]
            dmg = self.roll_dice("2d6") + 4
            if is_critical: dmg = int(dmg * 1.5)
            self.gain_salui(2)
            self.deceptive_bonus = True
            result = {"type": "attack", "damage": dmg, "message": f"{self.name}의 속임수 공격! 다음 공격에 추가 피해가 붙습니다."}

        elif action_name == "비열한 기습":
            skill = self.skills["비열한 기습"]
            skill["current_cd"] = skill["cooldown"]
            dmg = self.roll_dice("2d6")
            if is_critical: dmg = int(dmg * 1.5)
            result = {"type": "attack", "damage": dmg, "dispel": True, "message": f"{self.name}의 비열한 기습! 상대의 강화 효과를 걷어냅니다."}

        elif action_name == "몽환삼단":
            skill = self.skills["몽환삼단"]
            skill["current_cd"] = skill["cooldown"]
            h1, h2, h3 = self.roll_dice("2d3")+3, self.roll_dice("2d3")+3, self.roll_dice("2d3")+3
            total = h1 + h2 + h3
            if is_critical: total = int(total * 1.5)
            result = {"type": "attack", "damage": total, "silence": 2, "message": f"{self.name}의 몽환삼단! 3연속 공격과 함께 침묵을 부여합니다."}

        elif action_name == "결심":
            if getattr(self, "current_turn_count", 1) < 6:
                return {"type": "log", "message": "결심은 6턴부터 사용할 수 있습니다."}
            
            skill = self.skills["결심"]
            skill["current_cd"] = skill["cooldown"]
            self.kyulsim_stack = 2
            self.gain_salui(1)
            result = {"type": "status", "message": f"{self.name}가 결심했습니다. 2회의 치명적인 일격을 준비합니다."}

        # 특수 효과 추가
        if bonus_fixed_dmg != 0: result["special_fixed_dmg"] = bonus_fixed_dmg
        if is_critical: result["inflict_weaken"] = 1 # 결심 효과: 1턴간 피해 -25%

        self.update_stats()
        return result
