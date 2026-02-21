import random

class Combat:
    def __init__(self, player1, player2, verbose=True):
        self.players = [player1, player2]
        self.current_player_idx = random.randint(0, 1)
        self.turn_count = 1
        self.verbose = verbose
        
        # 개전 효과 발동 (선공 먼저)
        p1 = self.get_current_player()
        p2 = self.get_opponent()
        p1.on_battle_start()
        p2.on_battle_start()

    def get_current_player(self):
        return self.players[self.current_player_idx]

    def get_opponent(self):
        return self.players[1 - self.current_player_idx]

    def switch_player(self):
        self.current_player_idx = 1 - self.current_player_idx
        if self.current_player_idx == 0:
            self.turn_count += 1
            
    def get_status(self) -> str:
        p1, p2 = self.players[0], self.players[1]
        return f"{p1.name}: HP {p1.health}/{p1.max_health} | {p2.name}: HP {p2.health}/{p2.max_health}"

    def run_turn(self, action_input: str) -> dict:
        actor = self.get_current_player()
        opponent = self.get_opponent()
        
        # 1. 영창 취소
        if action_input == "영창 취소" and actor.is_casting:
            print(f"> {actor.name}가 {actor.casting_skill_name} 영창을 취소했습니다.")
            actor.cancel_casting()
            return {'success': True, 'damage': 0}

        # 2. 영창 유지
        if action_input == "casting_wait" and actor.is_casting:
            print(f"> {actor.name}는 {actor.casting_skill_name} 영창을 유지합니다...")
            if opponent.is_alive():
                self.switch_player()
            return {'success': True, 'damage': 0}

        # 3. 영창 완료 자동 발동
        if actor.is_casting and actor.casting_completed:
            print(f"> {actor.name}의 {actor.casting_skill_name} 발동!")
            action_result = actor.act(actor.casting_skill_name)
            actor.is_casting = False
            actor.casting_skill_name = None
            actor.casting_completed = False
            
            damage = 0
            if action_result['type'] == 'attack':
                damage = action_result.get('damage', 0)
                dmg_type = action_result.get('damage_type', '일반 피해')
                print(f"  - {action_result['message']}")
                opponent.take_damage(damage, damage_type=dmg_type, attacker=actor)
                print(f"  - 결과: {opponent.name}에게 {damage}의 {dmg_type}를 입혔습니다.")
            elif 'message' in action_result:
                print(f"  - {action_result['message']}")
            return {'success': True, 'damage': damage}

        internal_action = action_input

        # 침묵 상태 확인
        if actor.has_buff("침묵"):
            if internal_action not in ["일반공격", "방어", "defense"]:
                print(f"  - [침묵] {actor.name}는 침묵 상태여서 {action_input}를 사용할 수 없습니다!")
                return {'success': False, 'damage': 0}

        skill = actor.skills.get(internal_action)
        if skill and skill['current_cd'] > 0:
            print(f"> {action_input}는 아직 사용할 수 없습니다.")
            return {'success': False, 'damage': 0}

        print(f"> {actor.name}의 행동: {action_input}")
        actor.current_turn_count = self.turn_count
        action_result = actor.act(internal_action)
        
        if action_result['type'] == 'log':
            print(f"  - {action_result['message']}")
            return {'success': False, 'damage': 0}

        # 4. 영창 시작 (로그 출력 필수)
        if action_result['type'] == 'casting':
            print(f"  - {actor.name}가 {action_result['skill_name']} 영창을 시작합니다!")
            actor.start_casting(action_result['skill_name'], action_result['turns'])
            if opponent.is_alive():
                self.switch_player()
            return {'success': True, 'damage': 0}

        damage = 0
        if action_result['type'] == 'attack':
            print(f"  - {action_result['message']}") # 메시지 선출력

            damage = action_result.get('damage', 0)
            dmg_type = action_result.get('damage_type', '일반 피해')
            
            # [결심 효과] 피해량 -25% 부여
            if 'inflict_weaken' in action_result:
                duration = action_result['inflict_weaken']
                print(f"  - [결심] 상대에게 피해량 -25%를 {duration}턴간 부여합니다.")
                opponent.add_buff("피해량 감소", "[해로운 효과]", duration, {"dmg_mod": 0.75})

            # [이로운 효과 제거]
            if 'dispel' in action_result:
                print(f"  - [비열한 기습] {opponent.name}의 모든 이로운 효과를 제거합니다!")
                opponent.clear_buffs("[이로운 효과]")

            # [침묵 부여]
            if 'silence' in action_result:
                duration = action_result['silence']
                print(f"  - [몽환삼단] {opponent.name}에게 {duration}턴간 침묵을 부여합니다.")
                opponent.add_buff("침묵", "[해로운 효과]", duration)

            opponent.take_damage(damage, damage_type=dmg_type, attacker=actor)
            print(f"  - 결과: {opponent.name}에게 {damage}의 {dmg_type}를 입혔습니다.")
            
            # [살의 10스택: 상대 최대 생명력 10% 고정 피해]
            if action_result.get("special_fixed_dmg") == -1:
                f_dmg = int(opponent.max_health * 0.1) # 최대 체력 10%
                print(f"  - [살의 폭발] {opponent.name}의 최대 생명력 10%인 {f_dmg}의 고정 피해를 입힙니다!")
                opponent.take_damage(f_dmg, damage_type='고정 피해', attacker=actor)
                print(f"  - 결과: {opponent.name}에게 {f_dmg}의 고정 피해를 추가로 입혔습니다.")

            if 'fixed_damage' in action_result:
                f_dmg = action_result['fixed_damage']
                opponent.take_damage(f_dmg, damage_type='고정 피해', attacker=actor)
                print(f"  - 결과: {opponent.name}에게 {f_dmg}의 고정 피해를 추가로 입혔습니다.")
        else:
            if 'message' in action_result:
                print(f"  - {action_result['message']}")
                if 'inflict_weaken' in action_result:
                    duration = action_result['inflict_weaken']
                    opponent.add_buff("피해량 감소", "[해로운 효과]", duration, {"dmg_mod": 0.5})
        
        if opponent.is_alive():
            self.switch_player()
        
        return {'success': True, 'damage': damage}

    def is_game_over(self) -> bool:
        return not (self.players[0].is_alive() and self.players[1].is_alive())

    def get_winner(self):
        if self.is_game_over():
            if self.players[0].is_alive(): return self.players[0]
            elif self.players[1].is_alive(): return self.players[1]
        return None
