from .base_character import BaseCharacter
import random

class CharacterSolis(BaseCharacter):
    def __init__(self, name="솔리스"):
        super().__init__(name=name, health=90)
        self.skills = {
            "속임수 공격": {"cooldown": 3, "current_cd": 0},
            "몽환삼단": {"cooldown": 4, "current_cd": 0},
            "극의": {"cooldown": 5, "current_cd": 0}
        }
        self.no_crit_turns = 0
        self.is_critical = False
        self.acrobatics_val = 0
        self.deceptive_strike_bonus = False
        self.ultimate_intent_active = False
        self.stats_values = {"Acrobatics": 0, "Crit Hits": 0}

    def start_turn(self):
        super().start_turn()
        r1, r2 = random.randint(1, 5), random.randint(1, 5)
        dice_roll = r1 + r2
        print(f"  - [곡예] 2d5 주사위 굴림: [{r1}, {r2}] = {dice_roll}")
        
        if self.ultimate_intent_active:
            print(f"    > 극의 보정 적용: {dice_roll} - 2 = {dice_roll - 2}")
            dice_roll = max(1, dice_roll - 2)
            self.ultimate_intent_active = False
        
        self.acrobatics_val = dice_roll
        self.stats_values["Acrobatics"] = dice_roll

        if self.acrobatics_val < 6:
            self.is_critical = True
            self.no_crit_turns = 0
            self.stats_values["Crit Hits"] += 1
            print(f"    > 곡예 성공! 치명타(1.5배) 상태가 됩니다.")
        else:
            self.is_critical = False
            self.no_crit_turns += 1

        if self.no_crit_turns >= 2:
            print(f"  - [곡예 실패] 2턴 연속 미발동으로 모든 스킬 쿨타임이 1턴 감소합니다.")
            for skill in self.skills.values():
                if skill['current_cd'] > 0: skill['current_cd'] -= 1
            self.no_crit_turns = 0

    def get_passive_log(self) -> str:
        crit_msg = "[치명타 준비]" if self.is_critical else "[일반 상태]"
        return f"{self.name}의 현재 상태: {crit_msg}"

    def take_damage(self, damage: int, attacker=None):
        if self.ultimate_intent_active and attacker:
            evade_roll = random.randint(1, 5)
            print(f"  - [회피 시도] 1d5 주사위: [{evade_roll}]")
            if evade_roll <= 3:
                print(f"    > 회피 성공! 대미지를 무시하고 반격을 준비합니다.")
                r_dmg = random.randint(1, 4) + 6
                counter_dmg = self.apply_crit(r_dmg)
                if self.deceptive_strike_bonus:
                    bonus = (self.acrobatics_val // 2) + 2
                    counter_dmg += bonus
                    print(f"    > [연계] 속임수 공격의 표식 발동: +{bonus} 피해")
                    self.deceptive_strike_bonus = False
                print(f"    > [반격] {attacker.name}에게 {counter_dmg}의 피해를 입혔습니다!")
                attacker.take_damage(counter_dmg)
                return

        super().take_damage(damage, attacker)

    def apply_crit(self, damage):
        if self.is_critical:
            final = int(damage * 1.5)
            print(f"    > 치명타 발동! {damage} -> {final} (1.5배)")
            return final
        return damage

    def act(self, action_name: str = None) -> dict:
        if action_name == "일반공격":
            r1, r2 = random.randint(1, 6), random.randint(1, 6)
            print(f"  - [주사위] 2d6 결과: [{r1}, {r2}] = {r1+r2}")
            dmg = self.apply_crit(r1 + r2)
            return {"type": "attack", "damage": dmg, "message": f"{self.name}의 가벼운 단검 투척!"}

        if action_name in ["defense", "방어"]:
            self.defense_cooldown = 2
            self.shield += 8
            return {"type": "defense", "message": f"{self.name}가 방어 태세로 보호막 8을 얻었습니다."}

        if action_name == "속임수 공격":
            skill = self.skills[action_name]
            r1, r2 = random.randint(1, 4), random.randint(1, 4)
            print(f"  - [주사위] 2d4+8 결과: ([{r1}, {r2}] + 8) = {r1+r2+8}")
            damage = self.apply_crit(r1 + r2 + 8)
            self.deceptive_strike_bonus = True
            self.shield += 4
            skill["current_cd"] = skill["cooldown"]
            return {"type": "attack", "damage": damage, "message": f"{self.name}의 기습적인 속임수 공격!"}

        if action_name == "몽환삼단":
            skill = self.skills[action_name]
            r1, r2 = random.randint(1, 3), random.randint(1, 3)
            base_hit = r1 + r2 + 1
            print(f"  - [주사위] 2d3+1 결과: ([{r1}, {r2}] + 1) = {base_hit}")
            hit = self.apply_crit(base_hit)
            total_damage = hit * 3
            print(f"  - [연격] {hit} 데미지로 3회 타격!")
            skill["current_cd"] = skill["cooldown"]
            if total_damage / 2 <= 9:
                print(f"    > 총 피해의 절반이 9 이하이므로 쿨타임이 1턴 감소합니다.")
                skill["current_cd"] -= 1
            return {"type": "attack", "damage": total_damage, "message": f"{self.name}의 현란한 몽환삼단!"}

        if action_name == "극의":
            skill = self.skills[action_name]
            self.ultimate_intent_active = True
            skill["current_cd"] = skill["cooldown"]
            return {"type": "status", "message": f"{self.name}가 정신을 집중하여 극의의 경지에 도달했습니다."}
        return {"type": "log", "message": "알 수 없는 행동"}
