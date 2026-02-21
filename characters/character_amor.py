from .base_character import BaseCharacter
import random

class CharacterAmor(BaseCharacter):
    def __init__(self, name="아모르"):
        super().__init__(name=name, health=100)
        self.skills.update({
            "자활_집념": {"cooldown": 2, "current_cd": 0},
            "백야_흑야": {"cooldown": 4, "current_cd": 0},
            "혼돈선": {"cooldown": 7, "current_cd": 0}
        })
        self.persona_accumulated_dmg = 0
        self.is_dark = False
        self.dark_turns_left = 0
        self.persona_count = 0
        self.white_night_active = False
        self.chaos_good_light_turns = 0
        self.chaos_good_dark_accumulated = 0
        self.chaos_good_dark_active = False
        self.tenacity_shield_active = False
        self.pending_dark_dmg = 0
        self.stats_values = {"Darkness Count": 0, "Persona Stack": 0, "Max Dark Dmg": 0}

    def take_damage(self, damage: int, damage_type: str = "일반 피해", attacker=None):
        actual_damage = damage
        if self.chaos_good_light_turns > 0:
            actual_damage = damage // 2
            print(f"  - [빛의 가호] 데미지 반감 적용: {damage} -> {actual_damage}")

        self.persona_accumulated_dmg += actual_damage
        if self.is_dark and self.chaos_good_dark_active:
            self.chaos_good_dark_accumulated += actual_damage
            print(f"  - [축적] 어둠 속에 {actual_damage}의 피해를 가둡니다. (현재 누적: {self.chaos_good_dark_accumulated})")

        if self.white_night_active and self.shield > 0:
            value = (actual_damage // 2) + 2
            if not self.is_dark:
                print(f"  - [백야] 피격 시 생명력 {value} 회복")
                self.health = min(self.max_health, self.health + value)
            else:
                if attacker:
                    print(f"  - [흑야] {attacker.name}에게 {value}의 피해를 반사!")
                    attacker.take_damage(value, damage_type="일반 피해")

        if self.tenacity_shield_active and self.shield > 0:
            if self.shield <= actual_damage:
                print(f"  - [자활] 보호막 파괴 시 생명력 4 회복")
                self.health = min(self.max_health, self.health + 4)
                self.tenacity_shield_active = False

        actual_dealt = super().take_damage(actual_damage, damage_type, attacker)

        if not self.is_dark and self.persona_accumulated_dmg >= 44:
            self.enter_darkness()
            
        return actual_dealt

    def enter_darkness(self):
        print(f"  - [페르소나] 고통이 극에 달해 내면의 어둠이 깨어납니다! 모든 스킬 초기화")
        self.is_dark = True
        self.dark_turns_left = 4
        self.persona_accumulated_dmg = 0
        for s in self.skills.values(): s['current_cd'] = 0
        self.stats_values["Darkness Count"] += 1

    def end_darkness(self):
        print(f"  - [어둠 해제] 다시 빛의 상태로 돌아옵니다.")
        self.is_dark = False
        self.persona_count += 1
        self.stats_values["Persona Stack"] = self.persona_count
        if self.chaos_good_dark_active:
            release_dmg = self.chaos_good_dark_accumulated // 2
            print(f"  - [폭발] {self.chaos_good_dark_accumulated} 피해의 절반인 {release_dmg}를 방출합니다!")
            self.pending_dark_dmg = release_dmg
            if self.health <= 20:
                print(f"  - [역전] 생명력이 낮아 {release_dmg}만큼 생명력을 회복합니다!")
                self.health = min(self.max_health, self.health + release_dmg)
            self.chaos_good_dark_active = False
            self.chaos_good_dark_accumulated = 0

    def start_turn(self):
        super().start_turn()
        self.white_night_active = False
        if self.chaos_good_light_turns > 0:
            print(f"  - [혼돈선] 턴 시작 시 생명력 3 회복")
            self.health = min(self.max_health, self.health + 3)
            self.chaos_good_light_turns -= 1
        if self.is_dark:
            self.dark_turns_left -= 1
            if self.dark_turns_left < 0: self.end_darkness()

    def get_passive_log(self) -> str:
        state = "어둠" if self.is_dark else "빛"
        return f"{self.name} 현재 상태: [{state}]"

    def act(self, action_name: str = None) -> dict:
        if action_name == "일반공격":
            dmg = self.roll_dice("2d6")
            return {"type": "attack", "damage": dmg, "message": f"{self.name}의 묵직한 공격!"}
        
        if action_name in ["defense", "방어"]:
            skill = self.skills["방어"]
            skill["current_cd"] = skill["cooldown"]
            self.add_buff("방어", "일반", 1)
            return {"type": "defense", "message": f"{self.name}가 방어 태세로 1턴간 받는 일반 피해가 90% 감소합니다."}
            
        if action_name == "자활_집념":
            skill = self.skills[action_name]
            r_val = self.roll_dice("1d10")
            damage = r_val + 5
            if not self.is_dark:
                s_gain = damage // 2
                self.shield += s_gain
                self.tenacity_shield_active = True
                msg = f"{self.name}의 자활! {s_gain}의 보호막 획득"
            else:
                damage += 6
                msg = f"{self.name}의 집념! 추가 피해 +6 적용"
            skill["current_cd"] = skill["cooldown"]
            return {"type": "attack", "damage": damage, "message": msg}
        if action_name == "백야_흑야":
            skill = self.skills[action_name]
            self.shield += 8
            self.white_night_active = True
            skill["current_cd"] = skill["cooldown"]
            return {"type": "defense", "message": f"{self.name}가 백야/흑야를 전개했습니다."}
        if action_name == "혼돈선":
            skill = self.skills[action_name]
            skill["current_cd"] = skill["cooldown"]
            if not self.is_dark:
                self.chaos_good_light_turns = 3
                return {"type": "status", "message": f"{self.name}가 혼돈선(빛)을 영창합니다."}
            else:
                self.chaos_good_dark_active = True
                return {"type": "status", "message": f"{self.name}가 혼돈선(어둠)을 준비합니다."}
        return {"type": "log", "message": "알 수 없는 행동"}
