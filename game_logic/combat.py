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

    def run_turn(self, action_input: str) -> bool:
        actor = self.get_current_player()
        opponent = self.get_opponent()
        
        # 1. 영창 취소
        if action_input == "영창 취소" and actor.is_casting:
            print(f"> {actor.name}가 {actor.casting_skill_name} 영창을 취소했습니다.")
            actor.cancel_casting()
            return True

        # 2. 영창 유지
        if action_input == "casting_wait" and actor.is_casting:
            print(f"> {actor.name}는 {actor.casting_skill_name} 영창을 유지합니다...")
            if opponent.is_alive():
                self.switch_player()
            return True

        # 3. 영창 완료 자동 발동
        if actor.is_casting and actor.casting_completed:
            print(f"> {actor.name}의 {actor.casting_skill_name} 발동!")
            action_result = actor.act(actor.casting_skill_name)
            actor.is_casting = False
            actor.casting_skill_name = None
            actor.casting_completed = False
            
            if action_result['type'] == 'attack':
                damage = action_result['damage']
                print(f"  - {action_result['message']}")
                opponent.take_damage(damage, attacker=actor)
                print(f"  - 결과: {opponent.name}에게 {damage}의 피해를 입혔습니다.")
            elif 'message' in action_result:
                print(f"  - {action_result['message']}")
            return True

        internal_action = action_input
        if action_input == "방어": internal_action = "defense"

        if internal_action != "defense":
            skill = actor.skills.get(internal_action)
            if skill and skill['current_cd'] > 0:
                print(f"> {action_input}는 아직 사용할 수 없습니다.")
                return False
        elif actor.defense_cooldown > 0:
            print(f"> 방어는 아직 사용할 수 없습니다.")
            return False

        print(f"> {actor.name}의 행동: {action_input}")
        actor.current_turn_count = self.turn_count
        action_result = actor.act(internal_action)
        
        if action_result['type'] == 'log':
            print(f"  - {action_result['message']}")
            return False

        # 4. 영창 시작 (로그 출력 필수)
        if action_result['type'] == 'casting':
            print(f"  - {actor.name}가 {action_result['skill_name']} 영창을 시작합니다!")
            actor.start_casting(action_result['skill_name'], action_result['turns'])
            if opponent.is_alive():
                self.switch_player()
            return True

        if action_result['type'] == 'attack':
            damage = action_result['damage']
            print(f"  - {action_result['message']}")
            opponent.take_damage(damage, attacker=actor)
            print(f"  - 결과: {opponent.name}에게 {damage}의 피해를 입혔습니다.")
        else:
            if 'message' in action_result:
                print(f"  - {action_result['message']}")
        
        if opponent.is_alive():
            self.switch_player()
        
        return True

    def is_game_over(self) -> bool:
        return not (self.players[0].is_alive() and self.players[1].is_alive())

    def get_winner(self):
        if self.is_game_over():
            if self.players[0].is_alive(): return self.players[0]
            elif self.players[1].is_alive(): return self.players[1]
        return None
