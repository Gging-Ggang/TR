// 애니메이션 상태 관리
let currentTurnRotation = -90;
let strikerFixedRotation = -90; 
let lastTurnCount = 0; 
let isFirstActionWipe = true;

/**
 * 변경된 자릿수만 엄격하게 선택하여 슬라이딩 업데이트
 */
function updateDigitWithCheck(num, easing = 'none', overshoot = 0, prevNum = null) {
    const currStr = String(num).padStart(2, '0');
    // prevNum이 null이면 초기 설정으로 간주하여 움직임을 허용함
    const prevStr = (prevNum !== null) ? String(prevNum).padStart(2, '0') : null;
    
    const currTens = currStr[0];
    const currUnits = currStr[1];
    const prevTens = prevStr ? prevStr[0] : null;
    const prevUnits = prevStr ? prevStr[1] : null;
    
    const tensWrapper = document.getElementById('digit-tens');
    const unitsWrapper = document.getElementById('digit-units');
    const transition = easing === 'none' ? 'none' : `transform ${easing}`;

    const updateDigit = (wrapper, curr, prev) => {
        if (!wrapper) return;
        
        // [지시사항] 값이 변하지 않았다면 어떠한 트랜지션이나 이동도 수행하지 않음 (반동 포함)
        if (prev !== null && curr === prev) return;

        let targetIdx;
        const n = parseInt(curr);
        const p = parseInt(prev);

        // 9에서 0으로 넘어가는 경우: 상단 '0' (인덱스 0)으로 이동
        if (p === 9 && n === 0) {
            targetIdx = 0;
        } else {
            targetIdx = 10 - n; 
        }

        wrapper.style.transition = transition;
        wrapper.style.transform = `translateY(-${targetIdx * 160 + overshoot}px)`;

        // 9->0 텔레포트 복구용
        if (targetIdx === 0 && easing !== 'none') {
            setTimeout(() => {
                wrapper.style.transition = 'none';
                wrapper.style.transform = `translateY(-${10 * 160}px)`;
            }, 600); 
        }
    };

    // 각 자릿수별로 독립적인 변화 체크 후 업데이트 수행
    updateDigit(tensWrapper, currTens, prevTens);
    updateDigit(unitsWrapper, currUnits, prevUnits);
}

/**
 * 게임 시작 시 연출
 */
function playStartAnimations(combat) {
    const firstIdx = combat.first_striker_idx;
    const firstGroup = document.getElementById('svg-first-striker-group');
    const turnGroup = document.getElementById('svg-current-turn-group');
    const decorGroup = document.getElementById('svg-decor-text-group');
    const turnText = document.getElementById('bg-turn-display');
    const curtain = document.getElementById('action-curtain');
    const curtainBorder = document.getElementById('action-curtain-border');
    
    isFirstActionWipe = true;
    lastTurnCount = 0;
    const target = firstIdx === 0 ? -90 : 90;
    currentTurnRotation = target;
    strikerFixedRotation = target;
    
    // 초기 00 설정 (prevNum을 null로 주어 강제 초기화)
    updateDigitWithCheck(0, '0.8s ease-out', 0, null);
    turnText.style.color = 'rgba(255, 255, 255, 0.15)';
    
    [firstGroup, turnGroup, curtain, curtainBorder, decorGroup].forEach(el => {
        if (!el) return;
        el.style.transition = 'none';
    });
    
    firstGroup.style.transform = `rotate(${target + 540}deg)`; 
    turnGroup.style.transform = `rotate(${target - 360}deg)`; 
    if (decorGroup) decorGroup.style.transform = `rotate(0deg)`;
    
    curtain.className = 'cover';
    curtainBorder.className = 'cover';

    setTimeout(() => {
        // 다이얼 회전
        firstGroup.style.transition = 'transform 0.7s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.7s ease';
        firstGroup.style.opacity = '0.3';
        firstGroup.style.transform = `rotate(${target}deg)`;

        turnGroup.style.transition = 'transform 1s cubic-bezier(0.22, 1, 0.36, 1), opacity 1s ease';
        turnGroup.style.opacity = '0.4';
        turnGroup.style.transform = `rotate(${target}deg)`;

        // [추가] 요소들이 타오르듯 나타나는 순차 연출
        const helperCircle = document.getElementById('svg-helper-circle');
        const decorGroup = document.getElementById('svg-decor-text-group');
        const battleLogTitle = document.getElementById('battle-log-title');
        const rotatingRing = document.getElementById('svg-rotating-ring');

        // 1. 중앙 보조 원 (즉시)
        if (helperCircle) {
            helperCircle.style.opacity = '1';
            helperCircle.style.transform = 'scale(1)';
        }

        // 2. 데코 텍스트 (300ms 뒤)
        setTimeout(() => {
            if (decorGroup) {
                decorGroup.style.opacity = '1';
                decorGroup.style.transform = 'scale(1)';
            }
        }, 300);

        // 3. BATTLE LOG 제목 (600ms 뒤)
        setTimeout(() => {
            if (battleLogTitle) {
                battleLogTitle.style.opacity = '1';
                battleLogTitle.style.transform = 'scale(1)';
            }
        }, 600);

        // 4. 무한 회전 링 (900ms 뒤)
        setTimeout(() => {
            if (rotatingRing) rotatingRing.style.opacity = '1';
        }, 900);

        setTimeout(() => {
            document.getElementById('curtain-p1').classList.add('wipe');
            document.getElementById('curtain-p2').classList.add('wipe');
        }, 1100);
    }, 50);
}

function closeActionCurtain(combat) {
    if (isFirstActionWipe) return;
    const curtain = document.getElementById('action-curtain');
    const curtainBorder = document.getElementById('action-curtain-border');
    [curtain, curtainBorder].forEach(el => {
        if(!el) return;
        el.style.transition = 'clip-path 1.0s cubic-bezier(0.25, 1, 0.5, 1)';
        el.className = 'cover';
    });
}

/**
 * 인디케이터 및 턴 카운터 정밀 동기화
 */
function updateTurnUI(combat, renderButtonsCallback) {
    const turnNum = combat.turn_count;
    const currentIdx = combat.current_player_idx;
    const firstIdx = combat.first_striker_idx;
    const curtain = document.getElementById('action-curtain');
    const curtainBorder = document.getElementById('action-curtain-border');
    const turnGroup = document.getElementById('svg-current-turn-group');
    const strikerGroup = document.getElementById('svg-first-striker-group');
    const decorGroup = document.getElementById('svg-decor-text-group');
    const ripple = document.getElementById('action-ripple');
    
    ripple.classList.remove('active'); 
    if (renderButtonsCallback) renderButtonsCallback();

    if (isFirstActionWipe) {
        // [수정] 최초 행동 턴에서 숫자를 01로 슬라이딩 갱신
        updateDigitWithCheck(turnNum, '0.8s cubic-bezier(0.22, 1, 0.36, 1)', 0, 0);
        
        setTimeout(() => {
            const wipeClass = 'reveal-' + (currentIdx === 0 ? 'p1' : 'p2');
            [curtain, curtainBorder].forEach(el => {
                if(!el) return;
                el.style.transition = 'clip-path 1.0s cubic-bezier(0.25, 1, 0.5, 1)';
                el.className = wipeClass;
            });
            isFirstActionWipe = false;
            lastTurnCount = turnNum; // 첫 턴(1) 저장
        }, 500);
    } else {
        const isReturningToStriker = (currentIdx === firstIdx);
        const mainTarget = currentTurnRotation + 180;

        if (isReturningToStriker) {
            const overshootTurn = mainTarget + 10;
            const overshootStriker = strikerFixedRotation + 10;
            
            turnGroup.style.transition = 'transform 0.25s cubic-bezier(0.5, 0, 1, 1)';
            turnGroup.style.transform = `rotate(${mainTarget}deg)`;

            setTimeout(() => {
                const rushTiming = '0.12s cubic-bezier(0, 0, 0.5, 1)';
                [turnGroup, strikerGroup, decorGroup].forEach(g => g.style.transition = 'transform ' + rushTiming);
                
                turnGroup.style.transform = `rotate(${overshootTurn}deg)`;
                strikerGroup.style.transform = `rotate(${overshootStriker}deg)`;
                decorGroup.style.transform = `rotate(5deg)`;
                
                // [엄격 자릿수 감지] 튕김 연출 수행
                updateDigitWithCheck(turnNum, rushTiming, -20, lastTurnCount);

                setTimeout(() => {
                    const snapTiming = '0.2s cubic-bezier(0.25, 1, 0.5, 1)';
                    [turnGroup, strikerGroup, decorGroup].forEach(g => g.style.transition = 'transform ' + snapTiming);
                    
                    turnGroup.style.transform = `rotate(${mainTarget}deg)`;
                    strikerGroup.style.transform = `rotate(${strikerFixedRotation}deg)`;
                    decorGroup.style.transform = `rotate(0deg)`;
                    
                    // [엄격 자릿수 감지] 정위치 안착
                    updateDigitWithCheck(turnNum, snapTiming, 0, lastTurnCount);
                    currentTurnRotation = mainTarget;
                    lastTurnCount = turnNum;
                }, 120);
            }, 250);
        } else {
            currentTurnRotation = mainTarget;
            turnGroup.style.transition = 'transform 0.4s cubic-bezier(0.22, 1, 0.36, 1)';
            turnGroup.style.transform = `rotate(${mainTarget}deg)`;
            updateDigitWithCheck(turnNum, '0.4s cubic-bezier(0.22, 1, 0.36, 1)', 0, lastTurnCount);
            // 턴이 올라가지 않는 선공->후공 단계에서도 현재 번호를 유지하도록 함
        }

        setTimeout(() => {
            const wipeClass = 'reveal-' + (currentIdx === 0 ? 'p1' : 'p2');
            [curtain, curtainBorder].forEach(el => {
                if(!el) return;
                el.style.transition = 'clip-path 1.0s cubic-bezier(0.25, 1, 0.5, 1)';
                el.className = wipeClass;
            });
        }, 100);
    }
}

function handleActionAnimation(e, combat, onComplete) {
    const ripple = document.getElementById('action-ripple');
    const wrapper = document.getElementById('action-wrapper');
    const rect = wrapper.getBoundingClientRect();
    ripple.style.left = (e.clientX - rect.left) + 'px';
    ripple.style.top = (e.clientY - rect.top) + 'px';
    ripple.classList.add('active');
    if (onComplete) onComplete();
}
