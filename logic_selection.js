const CHAR_DATA = {
    "Solis": { full: "SOLIS CANTICUM STONECOLD", job: "PLANNER", ult: "RESOLUTION", baseHue: 200 },
    "Amor": { full: "AMORE MIDSOMA", job: "HEALER", ult: "HEART BEAT", baseHue: 340 },
    "Per": { full: "FERR", job: "BERSERKER", ult: "NETHER PATH", baseHue: 0 },
    "Cookie": { full: "COOKIE", job: "WITCH", ult: "MAGIC AWAKENING", baseHue: 40 }
};

window._mirrorMatchState = window._mirrorMatchState || false;

/**
 * 미러매치용 배경 사각형 텍스처 베이킹 (영역 확장 및 밝기 지터 대폭 강화)
 */
function generateMirrorBgTexture() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const fontSize = 160;
    const height = Math.ceil(fontSize * 1.6);
    const width = 2000; 
    
    canvas.width = width;
    canvas.height = height;
    
    const count = 15;
    for (let i = 0; i < count; i++) {
        ctx.save();
        const x = (i / count) * width + (Math.random() * 120 - 60);
        const y = height / 2;
        const rw = 180 + Math.random() * 250;
        const rh = fontSize * (1.0 + Math.random() * 0.3);
        const rot = (Math.random() * 16 - 8) * (Math.PI / 180);
        // [수정] 밝기 지터 범위를 더 크게 확장 (160 ~ 255)
        const br = 160 + Math.random() * 95;
        
        ctx.translate(x, y);
        ctx.rotate(rot);
        const skX = (Math.random() * 14 - 7) * (Math.PI / 180);
        ctx.transform(1, 0, skX, 1, 0, 0);
        ctx.fillStyle = `rgb(${br}, ${br}, ${br})`;
        ctx.fillRect(-rw/2, -rh/2, rw, rh);
        ctx.restore();
    }
    return { url: canvas.toDataURL('image/png'), width: width, height: height };
}

/**
 * 텍스트 텍스처 베이킹 (문자 색조 지터 강화)
 */
function generateTexture(data, isMirror = false) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    const fontSize = 160; 
    const phrase = isMirror ? "MIRROR MATCH • MIRROR MATCH • MIRROR MATCH • " : `${data.full} • ${data.job} • ${data.ult} • `;
    
    ctx.font = `900 ${fontSize}px 'Pretendard'`;
    let unitWidth = 0;
    const charWidths = [];
    for (let char of phrase) {
        const compress = 28;
        const cw = Math.max(1, ctx.measureText(char).width - compress); 
        charWidths.push(cw);
        unitWidth += cw;
    }
    unitWidth = Math.ceil(unitWidth);
    
    canvas.width = unitWidth;
    canvas.height = fontSize * 1.2;

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
        
        // [수정] 미러매치 보색 및 색조/채도/명도 지터 대폭 강화
        const compHue = (data.baseHue + 180) % 360;
        const h = isMirror ? compHue + (Math.random() * 60 - 30) : data.baseHue + (Math.random() * 20 - 10);
        const s = isMirror ? 75 + Math.random() * 25 : 80;
        const l = isMirror ? 45 + Math.random() * 25 : 60;
        const a = 0.7 + Math.random() * 0.3;

        ctx.font = `${weight} ${fontSize}px 'Pretendard'`;
        ctx.translate(currentX + charW / 2, canvas.height / 2);
        ctx.rotate(rotZ);
        ctx.transform(scaleX, skewY, skewX, scaleY, 0, 0);

        if (isMirror) {
            ctx.fillStyle = `hsla(${h}, ${s}%, ${l}%, ${a})`;
            ctx.fillText(char, -charW / 2, 0);
        } else if (char !== ' ' && Math.random() < 0.30) {
            ctx.fillStyle = `hsla(${h}, 80%, 60%, ${a})`;
            const rectH = canvas.height;
            const rectX = -charW / 2 - 15;
            const rectY = -rectH / 2;
            const rectW = charW + 30;
            ctx.fillRect(rectX, rectY, rectW, rectH);
            ctx.fillStyle = '#161616';
            ctx.fillText(char, -charW / 2, 0);
        } else {
            const grad = ctx.createLinearGradient(0, -fontSize/2, 0, fontSize/2);
            grad.addColorStop(0, `hsla(${h}, 80%, 75%, ${a})`);
            grad.addColorStop(1, `hsla(${h + 15}, 80%, 45%, ${a})`);
            ctx.fillStyle = grad;
            ctx.fillText(char, -charW / 2, 0);
        }
        ctx.restore();
        currentX += charW;
    }
    return { url: canvas.toDataURL('image/png'), width: unitWidth, height: canvas.height };
}

const curtainState = {
    p1: { reqId: null, layers: [], speedMult: 1, lastChange: 0 },
    p2: { reqId: null, layers: [], speedMult: 1, lastChange: 0 }
};

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
        if (otherVal) updateCurtainTexture(otherSide, otherVal, true);
    }

    const state = curtainState[side];
    const data = CHAR_DATA[charKey] || CHAR_DATA["Solis"];
    
    const texNormal = generateTexture(data, false);
    const texMirrorText = isMirrorMatch ? generateTexture(data, true) : null;
    const texMirrorBg = isMirrorMatch ? generateMirrorBgTexture() : null;
    
    const newLayer = document.createElement('div');
    newLayer.className = 'texture-container';
    newLayer.style.opacity = '0'; 
    
    const rows = [];
    const numRows = 28; 

    for (let i = 0; i < numRows; i++) {
        const isMirrorRow = isMirrorMatch && (i % 3 === 0);
        const dir = (i % 2 === 0) ? -1 : 1;
        const speed = (0.01 + Math.random() * 0.015) * dir; 
        
        if (isMirrorRow) {
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            wrapper.style.width = '100%';
            wrapper.style.height = `${texMirrorBg.height}px`;
            wrapper.style.marginTop = (i === 0) ? '0px' : '-100px';
            wrapper.style.zIndex = '5';

            const bgRow = document.createElement('div');
            bgRow.style.position = 'absolute';
            bgRow.style.inset = '0';
            bgRow.style.backgroundImage = `url(${texMirrorBg.url})`;
            bgRow.style.backgroundRepeat = 'repeat-x';
            bgRow.style.zIndex = '1';

            const txtRow = document.createElement('div');
            txtRow.style.position = 'absolute';
            txtRow.style.inset = '0';
            txtRow.style.backgroundImage = `url(${texMirrorText.url})`;
            txtRow.style.backgroundRepeat = 'repeat-x';
            txtRow.style.backgroundPosition = 'center center'; 
            txtRow.style.zIndex = '2';

            wrapper.appendChild(bgRow);
            wrapper.appendChild(txtRow);
            newLayer.appendChild(wrapper);

            const offset = Math.random() * 2000;
            rows.push({ el: bgRow, elTxt: txtRow, speed, offset, widthBg: texMirrorBg.width, widthTxt: texMirrorText.width, isMirror: true });
        } else {
            const row = document.createElement('div');
            row.style.width = '100%';
            row.style.height = `${texNormal.height}px`;
            row.style.marginTop = (i === 0) ? '0px' : '-61px'; 
            row.style.backgroundImage = `url(${texNormal.url})`;
            row.style.backgroundRepeat = 'repeat-x';
            row.style.position = 'relative';
            row.style.zIndex = '1';
            
            newLayer.appendChild(row);
            const offset = Math.random() * texNormal.width;
            rows.push({ el: row, speed, offset, width: texNormal.width, isMirror: false });
        }
    }

    curtain.appendChild(newLayer);
    
    const startTime = performance.now();
    const peakTime = 800;
    const maxSpeed = 450;
    let virtualElapsed = 0;
    if (state.speedMult > 1) {
        virtualElapsed = peakTime * Math.sqrt(Math.min((state.speedMult - 1) / (maxSpeed - 1), 1));
        virtualElapsed = Math.min(virtualElapsed, peakTime * 0.8); 
    }
    state.lastChange = startTime - virtualElapsed;

    state.layers.forEach(l => { if (!l.isOut) { l.isOut = true; l.fadeStartTime = startTime; } });
    state.layers.push({ dom: newLayer, rows: rows, isOut: false, opacity: 0, fadeStartTime: startTime });

    if (state.reqId) return;

    let lastTime = performance.now();
    function tick(now) {
        const deltaTime = Math.min(now - lastTime, 50); 
        lastTime = now;
        const elapsedSinceChange = now - state.lastChange;
        const totalDuration = 1600;

        if (elapsedSinceChange < peakTime) {
            state.speedMult = 1 + (maxSpeed - 1) * Math.pow(elapsedSinceChange / peakTime, 2);
        } else if (elapsedSinceChange < totalDuration) {
            const p = (elapsedSinceChange - peakTime) / (totalDuration - peakTime);
            state.speedMult = 1 + (maxSpeed - 1) * Math.pow(1 - p, 3);
        } else {
            state.speedMult = 1;
        }

        for (let i = state.layers.length - 1; i >= 0; i--) {
            const layer = state.layers[i];
            const fadeElapsed = now - layer.fadeStartTime;
            const fadeDuration = 800;

            if (layer.isOut) {
                const ratio = Math.min(fadeElapsed / fadeDuration, 1);
                layer.opacity = Math.pow(1 - ratio, 2); 
                if (layer.opacity <= 0.01) { if (layer.dom.parentNode) layer.dom.remove(); state.layers.splice(i, 1); continue; }
            } else {
                const ratio = Math.min(fadeElapsed / (fadeDuration * 0.8), 1);
                layer.opacity = Math.sin((ratio * Math.PI) / 2);
            }
            layer.dom.style.opacity = layer.opacity;

            layer.rows.forEach(r => {
                r.offset += r.speed * state.speedMult * deltaTime;
                if (r.isMirror) {
                    const offBg = (r.offset % r.widthBg + r.widthBg) % r.widthBg;
                    const offTxt = (r.offset % r.widthTxt + r.widthTxt) % r.widthTxt;
                    r.el.style.backgroundPositionX = `${offBg}px`;
                    r.elTxt.style.backgroundPositionX = `${offTxt}px`;
                } else {
                    r.offset = (r.offset % r.width + r.width) % r.width; 
                    r.el.style.backgroundPositionX = `${r.offset}px`;
                }
            });
        }
        state.reqId = requestAnimationFrame(tick);
    }
    state.reqId = requestAnimationFrame(tick);
}

window.updateCurtainTexture = updateCurtainTexture;