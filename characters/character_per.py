from .base_character import BaseCharacter
import random

class CharacterPer(BaseCharacter):
    def __init__(self, name="페르"):
        super().__init__(name=name, health=110)
        self.skills.update({
            "선혈의 강타": {"cooldown": 3, "current_cd": 0},
            "무장 파괴": {"cooldown": 4, "current_cd": 0},
            "불굴의 투지": {"cooldown": 5, "current_cd": 0},
            "황천길": {"cooldown": 10, "current_cd": 0}
        })
        self.damage_cap = 25 
        self.lifesteal_mod = 0.5 
        self.stats_values = {"흡혈율": "50%"}

    def get_passive_log(self) -> str:
        return f"{self.name}의 에테르 강탈: 피해 상한 25, 흡혈율 {int(self.lifesteal_mod*100)}%"

    def act(self, action_name: str = None) -> dict:
        self.lifesteal_mod = 0.5 
        
        if action_name == "일반공격":
            dmg = self.roll_dice("1d6") + 8
            return {"type": "attack", "damage": dmg, "lifesteal": self.lifesteal_mod, "message": f"{self.name}의 에테르를 머금은 일격!"}

        if action_name in ["defense", "방어"]:
            skill = self.skills["방어"]
            skill["current_cd"] = skill["cooldown"]
            self.add_buff("방어", "일반", 1)
            return {"type": "defense", "message": f"{self.name}가 방어 태세로 에테르를 응축합니다."}

        if action_name == "선혈의 강타":
            skill = self.skills[action_name]
            skill["current_cd"] = skill["cooldown"]
            dmg = self.roll_dice("1d6") + 12
            self.lifesteal_mod = 0.75 
            return {"type": "attack", "damage": dmg, "lifesteal": self.lifesteal_mod, "message": f"{self.name}의 선혈이 튀는 강타!"}

        if action_name == "무장 파괴":
            skill = self.skills[action_name]
            skill["current_cd"] = skill["cooldown"]
            dmg = self.roll_dice("1d6") + 6
            return {"type": "attack", "damage": dmg, "lifesteal": self.lifesteal_mod, "weapon_break": 3, "message": f"{self.name}가 상대의 무장을 파괴합니다!"}

        if action_name == "불굴의 투지":
            if self.health > 70: return {"type": "log", "message": "체력이 70 이하일 때만 사용할 수 있습니다."}
            skill = self.skills[action_name]
            skill["current_cd"] = skill["cooldown"]
            self.health = min(self.max_health, self.health + 15)
            if self.skills["황천길"]["current_cd"] > 0: self.skills["황천길"]["current_cd"] -= 1
            return {"type": "status", "message": f"{self.name}가 불굴의 투지로 체력을 회복하고 황천길의 대기시간을 줄입니다!"}

        if action_name == "황천길":
            if self.health > 70: return {"type": "log", "message": "체력이 70 이하일 때만 사용할 수 있습니다."}
            skill = self.skills[action_name]
            skill["current_cd"] = skill["cooldown"]
            self.health -= 15
            if self.health < 1: self.health = 1
            dmg = self.roll_dice("3d6") + 20
            return {
                "type": "attack", "damage": dmg, "damage_type": "관통 고정 피해", 
                "lifesteal": 0, "dispel_all": True,
                "message": f"{self.name}가 황천길을 엽니다! 모든 효과를 지우고 죽음의 일격을 날립니다!"
            }
        return {"type": "log", "message": "알 수 없는 행동"}
