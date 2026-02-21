const CHAR_DATA = {
    "Solis": { full: "SOLIS CANTICUM STONECOLD", job: "PLANNER", ult: "RESOLUTION", baseHue: 200 },
    "Amor": { full: "AMORE MIDSOMA", job: "HEALER", ult: "HEART BEAT", baseHue: 340 },
    "Per": { full: "FERR", job: "BERSERKER", ult: "NETHER PATH", baseHue: 0 },
    "Cookie": { full: "COOKIE", job: "WITCH", ult: "MAGIC AWAKENING", baseHue: 40 }
};

// 미러 매치 진입/이탈 상태 추적용 전역 변수
window._mirrorMatchState = window._mirrorMatchState || false;

/**
 * 텍스트 텍스처 베이킹
 */
function generateTexture(data, isMirror = false) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    const fontSize = isMirror ? 70 : 160; 
    const phrase = isMirror ? "MIRROR MATCH • MIRROR MATCH • MIRROR MATCH • " : `${data.full} • ${data.job} • ${data.ult} • `;
    
    ctx.font = `900 ${fontSize}px 'Pretendard'`;
    let unitWidth = 0;
    const charWidths = [];
    for (let char of phrase) {
        const compress = isMirror ? 8 : 28;
        const cw = Math.max(1, ctx.measureText(char).width - compress); 
        charWidths.push(cw);
        unitWidth += cw;
    }
    unitWidth = Math.ceil(unitWidth);
    
    canvas.width = unitWidth;
    canvas.height = isMirror ? 120 : 250;

    if (isMirror) {
        const mainHue = data.baseHue;
        const bgGrad = ctx.createLinearGradient(0, 0, 0, canvas.height);
        
        bgGrad.addColorStop(0, `hsla(${mainHue}, 90%, 65%, 0)`);       
        bgGrad.addColorStop(0.25, `hsla(${mainHue}, 90%, 65%, 0.85)`); 
        bgGrad.addColorStop(0.5, `hsla(${mainHue}, 90%, 85%, 1)`);     
        bgGrad.addColorStop(0.75, `hsla(${mainHue}, 90%, 65%, 0.85)`); 
        bgGrad.addColorStop(1, `hsla(${mainHue}, 90%, 65%, 0)`);       
        
        ctx.fillStyle = bgGrad;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    const weights = ['600', '900'];
    let currentX = 0;
    ctx.textBaseline = 'middle';
    
    for (let i = 0; i < phrase.length; i++) {
        const char = phrase[i];
        const charW = charWidths[i];
        
        ctx.save();
        
        const weight = weights[Math.floor(Math.random() * 2)];
        
        const rotZ = (Math.random() * 24 - 12) * (Math.PI / 180); 
        const rotY = (Math.random() * 40 - 20) * (Math.PI / 180); 
        const rotX = (Math.random() * 30 - 15) * (Math.PI / 180); 
        
        const baseScale = 0.85 + Math.random() * 0.3;
        const scaleX = Math.cos(rotY) * baseScale;
        const scaleY = Math.cos(rotX) * baseScale;
        
        const skewX = (Math.random() * 16 - 8) * (Math.PI / 180);
        const skewY = (Math.random() * 16 - 8) * (Math.PI / 180);
        
        const baseHue = isMirror ? (data.baseHue + 180) % 360 : data.baseHue;
        const h = baseHue + (Math.random() * 20 - 10);
        const a = 0.5 + Math.random() * 0.5;

        const hasStroke = Math.random() < 0.30;
        if (hasStroke) {
            const strokeWidth = 1.5 + Math.random() * 3.5;
            ctx.lineWidth = strokeWidth;
            
            const strokeOptions = ['black', 'white', 'main'];
            const chosenStroke = strokeOptions[Math.floor(Math.random() * 3)];
            let strokeColor = '';
            
            if (chosenStroke === 'black') {
                strokeColor = 'rgba(0, 0, 0, 0.8)';
            } else if (chosenStroke === 'white') {
                strokeColor = 'rgba(255, 255, 255, 0.8)';
            } else {
                const mainHue = (baseHue + Math.random() * 20 - 10) % 360; 
                const mainLight = 40 + Math.random() * 40; 
                strokeColor = `hsla(${mainHue}, 80%, ${mainLight}%, 0.9)`;
            }
            ctx.strokeStyle = strokeColor;
            ctx.lineJoin = 'miter'; 
        }

        ctx.font = `${weight} ${fontSize}px 'Pretendard'`;
        
        ctx.translate(currentX + charW / 2, canvas.height / 2);
        ctx.rotate(rotZ);
        ctx.transform(scaleX, skewY, skewX, scaleY, 0, 0);

        if (char !== ' ' && Math.random() < 0.30) {
            ctx.fillStyle = `hsla(${h}, 80%, 60%, ${a})`;
            const rectX = -charW / 2 - 15;
            const rectY = -fontSize * 0.75;
            const rectW = charW + 30;
            const rectH = fontSize * 1.5;
            
            ctx.fillRect(rectX, rectY, rectW, rectH);
            if (hasStroke) ctx.strokeRect(rectX, rectY, rectW, rectH); 
            
            ctx.fillStyle = '#161616';
            ctx.fillText(char, -charW / 2, 0);
            if (hasStroke) ctx.strokeText(char, -charW / 2, 0); 
        } else {
            const grad = ctx.createLinearGradient(0, -fontSize/2, 0, fontSize/2);
            grad.addColorStop(0, `hsla(${h}, 80%, 75%, ${a})`);
            grad.addColorStop(1, `hsla(${h + 15}, 80%, 45%, ${a})`);
            ctx.fillStyle = grad;
            ctx.fillText(char, -charW / 2, 0);
            if (hasStroke) ctx.strokeText(char, -charW / 2, 0);
        }
        
        ctx.restore();
        currentX += charW;
    }
    
    return { url: canvas.toDataURL('image/png'), width: unitWidth, height: canvas.height };
}

const curtainState = {
    p1: { reqId: null, layers: [] },
    p2: { reqId: null, layers: [] }
};

/**
 * 텍스처 업데이트 및 가속 물리 엔진
 */
function updateCurtainTexture(side, charKey, skipOther = false) {
    const curtain = document.getElementById(`curtain-${side}`);
    if (!curtain) return;

    const p1Val = document.getElementById('p1-choice')?.value;
    const p2Val = document.getElementById('p2-choice')?.value;
    const isMirrorMatch = (p1Val === p2Val) && (p1Val !== undefined);

    let shouldUpdateOther = false;
    if (isMirrorMatch) {
        shouldUpdateOther = true;
        window._mirrorMatchState = true;
    } else if (window._mirrorMatchState) {
        shouldUpdateOther = true;
        if (!skipOther) window._mirrorMatchState = false; 
    }

    if (!skipOther && shouldUpdateOther) {
        const otherSide = side === 'p1' ? 'p2' : 'p1';
        const otherVal = otherSide === 'p1' ? p1Val : p2Val;
        if (otherVal) {
            updateCurtainTexture(otherSide, otherVal, true);
        }
    }

    const state = curtainState[side];
    const data = CHAR_DATA[charKey] || CHAR_DATA["Solis"];
    
    const texNormal = generateTexture(data, false);
    const texMirror = isMirrorMatch ? generateTexture(data, true) : null;
    
    const newLayer = document.createElement('div');
    newLayer.className = 'texture-container';
    newLayer.style.opacity = '0'; 
    newLayer.style.position = 'relative'; 
    
    const rows = [];
    const numRows = 26; 

    // [1] 베이스 행 생성
    for (let i = 0; i < numRows; i++) {
        const isMirrorRow = isMirrorMatch && (i === 6 || i === 13);
        const currentTex = isMirrorRow ? texMirror : texNormal;

        const row = document.createElement('div');
        row.style.width = '100%';
        row.style.height = `${currentTex.height}px`;
        // [수정] 줄간격을 살짝 늘려 답답함 해소 (-160px -> -135px, -70px -> -55px)
        row.style.marginTop = i === 0 ? '0px' : (isMirrorRow ? '-55px' : '-135px'); 
        row.style.backgroundImage = `url(${currentTex.url})`;
        row.style.backgroundRepeat = 'repeat-x';
        row.style.willChange = 'background-position';
        row.style.position = 'relative';
        row.style.zIndex = '1';
        
        const dir = (i % 2 === 0) ? -1 : 1;
        const speed = (0.01 + Math.random() * 0.015) * dir; 
        const offset = Math.random() * currentTex.width;
        
        rows.push({ el: row, speed, offset, width: currentTex.width, type: 'base' });
        newLayer.appendChild(row);
    }

    // [2] 미러매치 전용 오버레이 3방향 행 추가
    if (isMirrorMatch) {
        // [수정] 각도를 +-60도 사이에서 무작위로 하되, 최소 하나씩은 양/음 부호가 나오도록 강제
        const angle1 = 15 + Math.random() * 45;       // +15도 ~ +60도
        const angle2 = -(15 + Math.random() * 45);    // -15도 ~ -60도
        const angle3 = (Math.random() * 120) - 60;    // -60도 ~ +60도 무작위
        
        const overlayAngles = [angle1, angle2, angle3];
        // 렌더링 순서 섞기
        overlayAngles.sort(() => Math.random() - 0.5);
        
        for (let j = 0; j < overlayAngles.length; j++) {
            const overlayRow = document.createElement('div');
            overlayRow.style.position = 'absolute';
            
            const baseTop = 20 + (j * 30);
            const topJitter = (Math.random() * 20 - 10);
            overlayRow.style.top = `${baseTop + topJitter}%`;
            
            overlayRow.style.width = '300%';
            overlayRow.style.left = '-100%'; 
            overlayRow.style.height = `${texMirror.height}px`;
            
            overlayRow.style.backgroundImage = `url(${texMirror.url})`;
            overlayRow.style.backgroundRepeat = 'repeat-x';
            overlayRow.style.willChange = 'background-position';
            overlayRow.style.zIndex = '10'; 
            
            // CSS 컨테이너 기본 회전(약 45도 추정)을 고려하여 시각적 절대 각도로 역산 적용
            const targetAngle = overlayAngles[j];
            const baseRot = targetAngle - 45; 
            const staticY = (Math.random() * 30 - 15);
            
            overlayRow.style.transformOrigin = 'center';
            overlayRow.style.transform = `translateY(calc(-50% + ${staticY}px)) rotate(${baseRot}deg)`;

            const speed = (0.02 + Math.random() * 0.02) * (j % 2 === 0 ? 1 : -1); 
            const offset = Math.random() * texMirror.width;

            rows.push({ el: overlayRow, speed, offset, width: texMirror.width, type: 'overlay' });
            newLayer.appendChild(overlayRow);
        }
    }

    curtain.appendChild(newLayer);

    state.layers.forEach(l => l.isOut = true);
    state.layers.push({ dom: newLayer, rows: rows, isOut: false, opacity: 0 });

    const transitionStartTime = performance.now();
    let lastTime = transitionStartTime;

    if (state.reqId) {
        cancelAnimationFrame(state.reqId);
    }

    function tick(now) {
        const deltaTime = Math.min(now - lastTime, 50); 
        lastTime = now;
        const elapsed = now - transitionStartTime;

        let speedMult = 1;
        // 전체 전환 시간을 조금 여유있게 잡아 가속/감속을 충분히 보여줌
        let isTransitioning = elapsed < 1200;

        if (isTransitioning) {
            // [수정] 0~500ms 구간 동안 점진적으로 가속. (새로운 텍스트가 나타나는 구간과 겹치게 하여 가속감을 확실히 전달)
            if (elapsed < 500) {
                speedMult = 1 + 319 * Math.pow(elapsed / 500, 3); 
            } else if (elapsed < 700) {
                speedMult = 320;
            } else {
                const p = (elapsed - 700) / 500;
                speedMult = 1 + 319 * Math.pow(1 - p, 3); 
            }
        }

        for (let i = state.layers.length - 1; i >= 0; i--) {
            const layer = state.layers[i];

            if (isTransitioning) {
                // [수정] 페이드인/아웃 시점을 0~400ms로 앞당김 (속도가 올라가는 과정 중에 새 캐릭터가 서서히 모습을 드러냄)
                if (elapsed < 400) {
                    const fadeRatio = elapsed / 400;
                    if (layer.isOut) {
                        layer.opacity = 1 - fadeRatio;
                    } else {
                        layer.opacity = fadeRatio;
                    }
                } else {
                    layer.opacity = layer.isOut ? 0 : 1;
                }
                layer.dom.style.opacity = layer.opacity;
            } else {
                if (layer.isOut) {
                    if (layer.dom.parentNode) layer.dom.remove();
                    state.layers.splice(i, 1);
                    continue;
                }
                layer.dom.style.opacity = '1';
            }

            layer.rows.forEach(r => {
                r.offset += r.speed * speedMult * deltaTime;
                r.offset = (r.offset % r.width + r.width) % r.width; 
                r.el.style.backgroundPositionX = `${r.offset}px`;
            });
        }

        state.reqId = requestAnimationFrame(tick);
    }

    state.reqId = requestAnimationFrame(tick);
}

window.updateCurtainTexture = updateCurtainTexture;