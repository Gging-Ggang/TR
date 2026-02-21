from .base_character import BaseCharacter
from game_logic.dice import roll

class CharacterB(BaseCharacter):
    def __init__(self, name="B"):
        super().__init__(name=name, health=100)
        self.skills = {
            "attack": {"damage": "2d10", "cooldown": 2, "current_cd": 0}
        }
        self.stats_values = {"Combo": 0} # 고유 수치: 콤보

    def get_passive_log(self) -> str:
        roll_result = roll("1d6")
        return f"{self.name}의 패시브 발동! 주사위 결과: {roll_result}"

    def act(self, action_name: str = None, turn_count: int = 1) -> dict:
        if action_name is None:
            action_name = "attack"

        if action_name == "defense":
            if self.defense_cooldown > 0:
                return {"type": "log", "message": f"{self.name}는 아직 방어할 수 없습니다."}
            self.defense_cooldown = 2
            self.shield += 8
            return {"type": "defense", "message": f"{self.name}가 방어 태세를 갖추어 방어막 8을 얻었습니다."}

        if action_name == "attack":
            skill = self.skills[action_name]
            if skill["current_cd"] > 0:
                return {"type": "log", "message": f"{self.name}의 공격은 아직 사용할 수 없습니다."}
            
            damage = roll(skill["damage"])
            skill["current_cd"] = skill["cooldown"]
            
            # 공격 시 콤보 수치 상승 (통계용)
            self.stats_values["Combo"] += 1
            
            return {"type": "attack", "damage": damage, "message": f"{self.name}의 공격! {damage}의 피해를 입히고 콤보가 증가했습니다."}
        
        return {"type": "log", "message": "알 수 없는 행동입니다."}