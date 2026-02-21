# main.py
import argparse
import math
import sys
import random
import os
from characters.character_a import CharacterA
from characters.character_b import CharacterB
from characters.character_cookie import CharacterCookie
from characters.character_solis import CharacterSolis
from characters.character_per import CharacterPer
from game_logic.combat import Combat

def get_stats(data):
    if not data: return 0.0, 0.0, 0.0, 0.0
    n = len(data)
    avg = sum(data) / n
    variance = sum((x - avg) ** 2 for x in data) / n
    return avg, math.sqrt(variance), max(data), min(data)

def get_char(name):
    if name == "Cookie": return CharacterCookie(name=name)
    if name == "Solis": return CharacterSolis(name=name)
    if name == "Amor": return CharacterAmor(name=name)
    if name == "Per": return CharacterPer(name=name)
    if name == "A": return CharacterA(name=name)
    if name == "B": return CharacterB(name=name)
    return CharacterA(name=name)

def main():
    parser = argparse.ArgumentParser(description="TR 프로젝트 시뮬레이터")
    parser.add_argument('--mode', type=str, default='interactive', choices=['interactive', 'stats'])
    parser.add_argument('--simulations', type=int, default=1000)
    parser.add_argument('--p1_name', type=str, default='A')
    parser.add_argument('--p2_name', type=str, default='B')
    args = parser.parse_args()

    if args.mode == 'interactive':
        p1 = get_char(args.p1_name)
        p2 = get_char(args.p2_name)
        combat = Combat(p1, p2, verbose=True)
        print(f"--- 대화형 모드 시작 ({p1.name} vs {p2.name}) ---")
        
        last_turn = -1
        while not combat.is_game_over():
            curr = combat.get_current_player()
            if combat.turn_count != last_turn:
                curr.start_turn()
                last_turn = combat.turn_count

            # 아모르 전용: 어둠 해제 시 대미지 방출 처리
            if hasattr(curr, 'pending_dark_dmg') and curr.pending_dark_dmg > 0:
                opp = combat.get_opponent()
                opp.take_damage(curr.pending_dark_dmg, attacker=curr)
                print(f"** {curr.name}의 혼돈선 해제! {curr.pending_dark_dmg} 피해 방출! **")
                curr.pending_dark_dmg = 0

            print(f"\n[턴 {combat.turn_count}] {curr.name}의 차례")
            acts = ["defense"] + list(curr.skills.keys())
            for i, a in enumerate(acts):
                cd = curr.defense_cooldown if a == "defense" else curr.skills[a]['current_cd']
                print(f"{i}: {a} {'(쿨: ' + str(cd) + '턴)' if cd > 0 else '(가능)'}")
            
            try:
                choice = input("행동 번호 입력: ")
                idx = int(choice)
                if combat.run_turn(acts[idx])['success']:
                    print(combat.get_status())
            except (ValueError, IndexError):
                print("올바른 번호를 입력하세요.")
        
        winner = combat.get_winner()
        print(f"\n최종 승자: {winner.name if winner else '무승부'}")

    elif args.mode == 'stats':
        num_sims = args.simulations
        p1_name, p2_name = args.p1_name, args.p2_name
        print(f"--- 시뮬레이션 시작 ({num_sims}회): {p1_name} vs {p2_name} ---")
        
        wins = {p1_name: 0, p2_name: 0, "Draw": 0}
        turns_list = []
        total_dmg_list = {p1_name: [], p2_name: []}
        skill_dmg_data = {p1_name: {}, p2_name: {}}
        custom_stats = {p1_name: {}, p2_name: {}}
        overall_turns = 0

        for i in range(1, num_sims + 1):
            print(f"\r진행률: {i}/{num_sims} ({(i/num_sims)*100:.1f}%)", end="", flush=True)
            
            p1 = get_char(p1_name)
            p2 = get_char(p2_name)
            sim = Combat(p1, p2, verbose=False)
            
            d_game = {p1_name: 0, p2_name: 0}
            t = 0
            while not sim.is_game_over() and t < 1000:
                curr = sim.get_current_player()
                cname = curr.name
                curr.start_turn()
                
                # 아모르 대미지 방출 처리
                if hasattr(curr, 'pending_dark_dmg') and curr.pending_dark_dmg > 0:
                    opp = sim.get_opponent()
                    opp.take_damage(curr.pending_dark_dmg, attacker=curr)
                    d_game[cname] += curr.pending_dark_dmg
                    curr.pending_dark_dmg = 0

                acts = ["defense"] + list(curr.skills.keys())
                random.shuffle(acts)
                
                for a in acts:
                    res = sim.run_turn(a)
                    if res['success']:
                        dmg = res['damage']
                        d_game[cname] += dmg
                        if a not in skill_dmg_data[cname]: skill_dmg_data[cname][a] = []
                        skill_dmg_data[cname][a].append(dmg)
                        break
                t += 1
            
            for p in [p1, p2]:
                for s_key, s_val in p.stats_values.items():
                    if s_key not in custom_stats[p.name]: custom_stats[p.name][s_key] = []
                    custom_stats[p.name][s_key].append(s_val)

            turns_list.append(t)
            overall_turns += t
            total_dmg_list[p1_name].append(d_game[p1_name])
            total_dmg_list[p2_name].append(d_game[p2_name])
            
            winner = sim.get_winner()
            if winner: wins[winner.name] += 1
            else: wins["Draw"] += 1

        print("\n\n" + "="*80)
        print("                   시뮬레이션 최종 상세 통계")
        print("="*80)
        
        avg_t, std_t, max_t, min_t = get_stats(turns_list)
        print(f"1. 전체 요약\n   - 경기 수: {num_sims}회\n   - 평균 턴: {avg_t:.2f} (표준편차: {std_t:.2f}, 최댓값: {max_t}, 최솟값: {min_t})\n   - 총 누적 턴: {overall_turns}턴")
        
        print(f"\n2. 캐릭터별 승률")
        for k, v in wins.items():
            print(f"   - {k:15}: {v:4}회 ({(v/num_sims)*100:5.1f}%)")

        print(f"\n3. 상세 통계 분석 (DPT: Damage Per Turn)")
        for c in [p1_name, p2_name]:
            avg_d_game, std_d_game, max_d_game, min_d_game = get_stats(total_dmg_list[c])
            total_char_dmg = sum(total_dmg_list[c])
            dpt = total_char_dmg / overall_turns if overall_turns > 0 else 0
            print(f"\n   [캐릭터: {c}]")
            print(f"     - 전체 DPT: {dpt:.2f}")
            print(f"     - 경기당 데미지: 평균 {avg_d_game:.2f} (표준편차 {std_d_game:.2f}, 최댓값 {max_d_game}, 최솟값 {min_d_game})")
            
            if c in custom_stats:
                for s_key, s_vals in custom_stats[c].items():
                    s_avg, s_std, s_max, s_min = get_stats(s_vals)
                    print(f"     - {s_key:15}: 평균 {s_avg:5.2f} (표준편차 {s_std:5.2f}, 최댓값 {s_max}, 최솟값 {s_min})")
            
            print(f"     - 스킬별 상세 통계 (사용 1회당 데미지):")
            for s_name, dmgs in skill_dmg_data[c].items():
                s_avg, s_std, s_max, s_min = get_stats(dmgs)
                s_sum = sum(dmgs)
                s_dpt = s_sum / overall_turns if overall_turns > 0 else 0
                print(f"       * {s_name:10}: 회당 평균 {s_avg:5.2f} (표준편차 {s_std:5.2f}, 최대 {s_max}) | DPT 기여 {s_dpt:.2f}")
        print("="*80)

if __name__ == '__main__':
    main()
