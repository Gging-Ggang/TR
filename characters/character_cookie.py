from .base_character import BaseCharacter
import random

class CharacterCookie(BaseCharacter):
    def __init__(self, name="쿠키"):
        super().__init__(name=name, health=70)
        self.skills.update({
            "하이 파이쟈": {"cooldown": 1, "current_cd": 0},
            "불덩이 작렬": {"cooldown": 3, "current_cd": 0},
            "마력 각성": {"cooldown": 4, "current_cd": 0},
            "역화 폭발": {"cooldown": 0, "current_cd": 0}
        })
        self.fuse = 5
        self.flame = 0
        self.backfire = 0
        self.next_turn_empowered = False
        self.current_passive_shield = 0
        self.ma_shield = 0
        self.meteor_shield = 0 # 궁극기 전용 역화 보호막
        self.current_turn_count = 1
        self.stats_values = {
            "도화선": 5, "불꽃": 0, "역화": 0,
            "패시브 보호막": 0, "마력 각성 보호막": 0, "역화 보호막": 0
        }

    def on_battle_start(self):
        """개전: 도화선 5 획득"""
        self.fuse = 5
        print(f"  - [개전] {self.name}의 도화선이 5로 설정되었습니다.")
        self.stats_values["도화선"] = self.fuse

    def trigger_passive(self):
        """반복 패시브 로직: 불꽃/역화 획득 및 보호막 생성"""
        if self.next_turn_empowered:
            print(f"  - [마력 각성] 패시브 강화! 주사위를 두 번 굴립니다.")
            r1 = random.randint(1, 3)
            r2 = random.randint(1, 3)
            self.flame = max(r1, r2)
            shield_roll = min(r1, r2)
            
            self.fuse += self.flame
            gain = self.flame * 2
            self.backfire += gain
            print(f"    > 주사위 결과: [{r1}], [{r2}] -> 불꽃 {self.flame}, 역화 {gain} 획득")
            self.next_turn_empowered = False
        else:
            dice_roll = random.randint(1, 3)
            self.flame = dice_roll
            shield_roll = dice_roll
            
            self.fuse += self.flame
            self.backfire += self.flame
            print(f"    > 주사위 결과: [{dice_roll}] -> 불꽃 {self.flame}")

        new_sh = (3 - shield_roll) * 4
        if new_sh > 0:
            self.shield += new_sh
            self.current_passive_shield = new_sh
            print(f"  - [보호막] (3 - {shield_roll}) * 4 = {new_sh}의 보호막 획득")

    def start_turn(self):
        """반복: 자신의 턴 시작 시 발동"""
        super().start_turn()
        
        if self.current_passive_shield > 0:
            self.shield = max(0, self.shield - self.current_passive_shield)
            self.current_passive_shield = 0
        if self.ma_shield > 0:
            self.shield = max(0, self.shield - self.ma_shield)
            self.ma_shield = 0

        # 영창 중에는 패시브가 발동하지 않음
        if self.is_casting:
            print(f"  - [영창 중] 패시브가 발동하지 않습니다.")
            self.flame = 0
            self.current_passive_shield = 0
        else:
            self.trigger_passive()

        display_backfire = self.meteor_shield if self.is_casting else self.backfire
        self.stats_values.update({
            "도화선": self.fuse, "불꽃": self.flame, "역화": display_backfire,
            "패시브 보호막": self.current_passive_shield, "마력 각성 보호막": self.ma_shield,
            "역화 보호막": self.meteor_shield
        })

    def take_damage(self, damage: int, damage_type: str = "일반 피해", attacker=None):
        # 역화 보호막 처리
        if self.meteor_shield > 0:
            if self.meteor_shield > damage:
                self.meteor_shield -= damage
                damage = 0
            else:
                self.meteor_shield = 0
                damage = 0
                if self.is_casting:
                    print(f"  - [영창 실패] {self.name}의 역화 보호막이 파괴되어 영창이 중단되었습니다!")
                    self.cancel_casting()
        
        old_hp = self.health
        actual_dealt = 0
        if damage > 0:
            actual_dealt = super().take_damage(damage, damage_type, attacker)
        
        if self.health < old_hp:
            if not self.is_casting:
                loss = random.randint(1, 3)
                self.fuse = max(5, self.fuse - loss)
                print(f"  - [피격] {self.name}의 도화선이 {loss}만큼 감소했습니다. (현재: {self.fuse})")
        
        display_backfire = self.meteor_shield if self.is_casting else self.backfire
        self.stats_values.update({
            "도화선": self.fuse, "역화": display_backfire,
            "패시브 보호막": self.current_passive_shield, "마력 각성 보호막": self.ma_shield,
            "역화 보호막": self.meteor_shield
        })
        return actual_dealt

    def get_passive_log(self) -> str:
        return f"{self.name}의 [도화선] 화염:{self.flame}, 도화선:{self.fuse}"

    def act(self, action_name: str = None) -> dict:
        def cookie_roll(count, sides):
            total = 0
            for _ in range(count):
                val = random.randint(1, sides)
                if self.has_buff("무기 파괴"):
                    val = max(1, val - 2)
                total += val
            return total

        if action_name == "역화 폭발" and self.is_casting and self.casting_completed:
            # [지시사항] 행동 전 패시브 재발동
            print(f"  - [역화 폭발] 영창 완료! 행동 전 패시브가 재활성화됩니다.")
            self.trigger_passive()
            
            fixed_dmg = self.meteor_shield
            normal_dmg = 30
            msg = f"{self.name}의 궁극기 [역화 폭발]! 응축된 마력을 방출합니다! (일반 피해 30 + 고정 피해 {fixed_dmg})"
            
            # 공격 후 상태 초기화
            self.meteor_shield = 0
            self.backfire = 0
            self.fuse = 5
            self.stats_values.update({"도화선": 5, "역화": 0, "역화 보호막": 0})
            return {"type": "attack", "damage": normal_dmg, "damage_type": "일반 피해", "fixed_damage": fixed_dmg, "message": msg}

        if action_name == "일반공격":
            dmg = cookie_roll(self.flame, 6)
            return {"type": "attack", "damage": dmg, "message": f"{self.name}의 기본적인 마법 화살 공격!"}

        if action_name in ["defense", "방어"]:
            skill = self.skills["방어"]
            skill["current_cd"] = skill["cooldown"]
            self.add_buff("방어", "일반", 1)
            return {"type": "defense", "message": f"{self.name}가 방어 태세를 갖추어 1턴간 받는 일반 피해가 90% 감소합니다."}

        if action_name == "하이 파이쟈":
            skill = self.skills[action_name]
            dmg = cookie_roll(self.fuse, self.flame)
            self.fuse //= 2
            if self.fuse < 5: self.fuse = 5
            self.stats_values["도화선"] = self.fuse
            skill["current_cd"] = skill["cooldown"] + self.flame
            return {"type": "attack", "damage": dmg, "message": f"{self.name}의 강력한 화염 공격!"}

        if action_name == "불덩이 작렬":
            skill = self.skills[action_name]
            total_dmg = 0
            gained = 0
            print(f"  - [연사] {self.fuse}발의 불덩이 발사! (각 1d3-1)")
            for i in range(self.fuse):
                v = random.randint(1, 3) - 1
                if self.has_buff("무기 파괴"): v = max(0, v - 2) # 불덩이는 최소 0 유지
                total_dmg += v
                log_msg = f"    > {i+1}회차: [{v}] 데미지"
                if v == 0: gained += 1; log_msg += " (도화선 충전!)"
                print(f"DELAY_100:{log_msg}")
            
            if gained > 0:
                self.fuse += gained
                self.backfire += gained
            
            self.stats_values.update({"도화선": self.fuse, "역화": self.backfire})
            skill["current_cd"] = skill["cooldown"]
            return {"type": "attack", "damage": total_dmg, "message": f"{self.name}의 불덩이 작렬!"}

        if action_name == "마력 각성":
            skill = self.skills[action_name]
            self.remove_buff("방어")
            if "방어" in self.skills:
                self.skills["방어"]["current_cd"] += 1
            self.shield += 15
            self.ma_shield = 15
            self.next_turn_empowered = True
            self.stats_values["마력 각성 보호막"] = 15
            skill["current_cd"] = skill["cooldown"]
            return {"type": "status", "message": f"{self.name}가 마력을 각성하여 15의 보호막을 얻었습니다! (방어 버프 제거 및 쿨타임 1턴 증가) 다음 턴 주사위를 두 번 굴리며 역화 획득량이 두 배가 됩니다."}

        if action_name == "역화 폭발":
            if self.backfire >= 30:
                consumed = self.backfire
                self.meteor_shield = consumed
                self.backfire = 0
                self.stats_values.update({"역화": consumed, "역화 보호막": consumed})
                return {"type": "casting", "skill_name": "역화 폭발", "turns": 2}
            else:
                return {"type": "log", "message": f"역화 폭발을 사용하기 위한 조건이 부족합니다. (현재 역화: {self.backfire}/30)"}

        return {"type": "log", "message": "알 수 없는 행동"}
