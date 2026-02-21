from .base_character import BaseCharacter
from game_logic.dice import roll

class CharacterA(BaseCharacter):
    def __init__(self, name="A"):
        super().__init__(name=name, health=100)
        self.skills.update({
            "attack": {"damage": "2d10", "cooldown": 2, "current_cd": 0}
        })
        self.stats_values = {"Rage": 0} # 고유 수치: 분노

    def get_passive_log(self) -> str:
        roll_result = roll("1d6")
        return f"{self.name}의 패시브 발동! 주사위 결과: {roll_result}"

    def act(self, action_name: str = None) -> dict:
        if action_name == "일반공격":
            damage = self.roll_dice("2d6")
            return {"type": "attack", "damage": damage, "message": f"{self.name}의 일반적인 공격!"}

        if action_name is None:
            action_name = "attack"

        if action_name == "방어" or action_name == "defense":
            skill = self.skills["방어"]
            skill["current_cd"] = skill["cooldown"]
            self.add_buff("방어", "일반", 1)
            return {"type": "defense", "message": f"{self.name}가 방어 태세를 갖추어 1턴간 받는 일반 피해가 90% 감소합니다."}

        if action_name == "attack":
            skill = self.skills[action_name]
            if skill["current_cd"] > 0:
                return {"type": "log", "message": f"{self.name}의 공격은 아직 사용할 수 없습니다."}
            
            damage = self.roll_dice(skill["damage"])
            skill["current_cd"] = skill["cooldown"]
            
            # 공격 시 분노 수치 상승 (통계용)
            self.stats_values["Rage"] += 2
            
            return {"type": "attack", "damage": damage, "message": f"{self.name}의 공격! {damage}의 피해를 입히고 분노가 2 상승했습니다."}
        
        return {"type": "log", "message": "알 수 없는 행동입니다."}
