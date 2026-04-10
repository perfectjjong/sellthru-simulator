#!/usr/bin/env python3
# AI 예측 탭 추가 패치 스크립트

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("Original size:", len(html))

# ── 1. 탭 버튼 추가 ──────────────────────────────────────────────────
old = "  <div class=\"tab\" onclick=\"switchTab('backtest')\">🔬 백테스트</div>\n</div>"
new = """  <div class="tab" onclick="switchTab('backtest')">🔬 백테스트</div>
  <div class="tab" onclick="switchTab('aiforecast')">🤖 AI 예측</div>
  <div class="tab" onclick="switchTab('tracker')">📊 비교 트래커</div>
</div>"""
assert old in html, "탭 버튼 찾기 실패"
html = html.replace(old, new, 1)
print("✅ 탭 버튼 추가")

# ── 2. TAB_IDS 업데이트 ──────────────────────────────────────────────
old = "const TAB_IDS = ['mix','supply','scenario','annual','trend','backtest'];"
new = "const TAB_IDS = ['mix','supply','scenario','annual','trend','backtest','aiforecast','tracker'];"
assert old in html, "TAB_IDS 찾기 실패"
html = html.replace(old, new, 1)
print("✅ TAB_IDS 업데이트")

# ── 3. ACTUAL_2023 추가 ───────────────────────────────────────────────
old_data = "const _DATA = {"
new_block = 'const ACTUAL_2023 = {"Split AC":{"Jan":1784,"Feb":7552,"Mar":10298,"Apr":6618,"May":9774,"Jun":8746,"Jul":9758,"Aug":5387,"Sep":6523,"Oct":6182,"Nov":3928,"Dec":2441},"Floor Standing AC":{"Jan":73,"Feb":300,"Mar":940,"Apr":258,"May":449,"Jun":1473,"Jul":1072,"Aug":235,"Sep":746,"Oct":305,"Nov":318,"Dec":182},"Window AC":{"Jan":206,"Feb":1257,"Mar":743,"Apr":2613,"May":155,"Jun":623,"Jul":0,"Aug":1338,"Sep":6118,"Oct":47,"Nov":512,"Dec":1116},"Concealed Set":{},"Cassette AC":{}};\n\nconst _DATA = {'
assert old_data in html, "const _DATA 찾기 실패"
html = html.replace(old_data, new_block, 1)
print("✅ ACTUAL_2023 추가")

# ── 4. switchTab에 AI 탭 핸들러 추가 ─────────────────────────────────
old_switch_end = "  if (name === 'trend') buildTrendTab();\n}"
new_switch_end = """  if (name === 'trend') buildTrendTab();
  if (name === 'aiforecast') buildAiForecastTab();
  if (name === 'tracker') buildTrackerTab();
}"""
assert old_switch_end in html, "switchTab 끝 찾기 실패"
html = html.replace(old_switch_end, new_switch_end, 1)
print("✅ switchTab 핸들러 추가")

# ── 5. TAB 7 & 8 HTML 삽입 (백테스트 탭 div 닫힘 뒤, <script> 앞) ───
tab78 = """
<!-- TAB 7: AI 예측 엔진 -->
<div id="tab-aiforecast" class="tab-content">
  <div class="card">
    <div class="card-title">🤖 AI Adaptive Forecast Engine — 2026 예측</div>
    <div class="info-box" style="font-size:12px">
      📊 <strong>학습 데이터</strong>: 2023+2024+2025 (3년 36개월) &nbsp;|&nbsp;
      🔬 <strong>방법</strong>: Holt-Winters + 앙상블 + 베이지안 업데이트 &nbsp;|&nbsp;
      🎯 <strong>Q1 실적 반영</strong>: Jan~Mar 2026 오차 기반 자동 가중치 조정
    </div>
    <div style="margin-bottom:12px">
      <label style="font-size:11px;font-weight:600;color:#555">카테고리</label>
      <select id="ai-cat-sel" onchange="buildAiForecastTab()" style="margin-left:8px">
        <option>Split AC</option><option>Floor Standing AC</option><option>Window AC</option>
      </select>
    </div>
    <div class="card" style="background:#f8fafd;padding:12px">
      <div class="sec-hdr">
        <h3>📈 2026 AI 예측 (신뢰구간 포함)</h3>
        <span class="badge badge-blue" id="ai-conf-badge">계산중...</span>
      </div>
      <svg id="ai-svg" width="100%" height="230" viewBox="0 0 900 230" style="overflow:visible;display:block"></svg>
      <div style="margin-top:6px;font-size:11px;color:#666;display:flex;gap:16px;flex-wrap:wrap">
        <span>▓ ±25% 구간</span>
        <span>▒ ±15% 구간</span>
        <span>━ AI 중앙값</span>
        <span>● 실제(2026)</span>
        <span>╌ 2025 실적</span>
      </div>
    </div>
    <div class="tbl-wrap" style="margin-top:12px">
      <table>
        <thead><tr>
          <th>월</th><th>AI 중앙</th><th>낙관+15%</th><th>보수-15%</th>
          <th>2026 실적</th><th>오차%</th><th>2025</th><th>2024</th><th>2023</th>
        </tr></thead>
        <tbody id="ai-detail-body"></tbody>
      </table>
    </div>
    <div class="card" style="margin-top:12px;background:#f8fafd">
      <div class="card-title">📊 3년 계절성 지수 (2023~2025 기반)</div>
      <div id="ai-season-chart"></div>
    </div>
    <div id="ai-comment-box" style="margin-top:12px"></div>
  </div>
</div>

<!-- TAB 8: 비교 트래커 -->
<div id="tab-tracker" class="tab-content">
  <div class="card">
    <div class="card-title">📊 2026 Forecast Tracker — 내 플랜 vs AI vs 실제</div>
    <div class="info-box" style="font-size:12px">
      💡 탭1에서 입력한 연간 목표와 AI 예측을 실제 실적과 비교합니다.<br>
      월별 실적 입력 시 AI가 자동 재학습하여 잔여 월 예측을 갱신합니다.
    </div>
    <div class="stat-grid" id="tracker-scores" style="margin-bottom:12px"></div>
    <div style="margin-bottom:12px">
      <label style="font-size:11px;font-weight:600;color:#555">카테고리</label>
      <select id="tracker-cat-sel" onchange="buildTrackerTab()" style="margin-left:8px">
        <option>Split AC</option><option>Floor Standing AC</option><option>Window AC</option>
      </select>
    </div>
    <div class="card" style="background:#f8fafd;padding:12px">
      <div class="sec-hdr"><h3>✏️ 월별 실적 입력 (베이지안 재학습)</h3></div>
      <div class="info-box" style="font-size:11px">Q1(Jan~Mar)은 자동 반영. Apr 이후 실적을 입력하면 AI가 재보정합니다.</div>
      <div id="tracker-input-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin-bottom:12px"></div>
      <button class="btn btn-primary" onclick="applyTrackerInputs()">🔄 실적 반영 + AI 재학습</button>
      <button class="btn" style="background:#e74c3c;color:white;margin-left:8px" onclick="clearTrackerInputs()">🗑️ 초기화</button>
    </div>
    <div class="card" style="background:#f8fafd;padding:12px;margin-top:8px">
      <div class="sec-hdr"><h3>📈 3-Way 비교 차트</h3></div>
      <svg id="tracker-svg" width="100%" height="230" viewBox="0 0 900 230" style="overflow:visible;display:block"></svg>
      <div style="margin-top:6px;font-size:11px;color:#666;display:flex;gap:16px;flex-wrap:wrap">
        <span>━━ 실제 실적 (녹색)</span>
        <span>╌╌ 내 플랜 (파란)</span>
        <span>┅┅ AI 예측 (빨간)</span>
      </div>
    </div>
    <div class="tbl-wrap" style="margin-top:12px">
      <table>
        <thead><tr>
          <th>월</th><th>실제</th><th>내 플랜</th><th>플랜 오차%</th>
          <th>AI 예측</th><th>AI 오차%</th><th>우세</th>
        </tr></thead>
        <tbody id="tracker-compare-body"></tbody>
      </table>
    </div>
    <div class="card" style="margin-top:12px;background:#f8fafd">
      <div class="card-title">📉 AI 학습 진행률</div>
      <div id="tracker-learning-viz"></div>
    </div>
    <div id="tracker-comment-box" style="margin-top:12px"></div>
  </div>
</div>

"""

old_script_marker = "\n<script>\nconst ACTUAL_2023 ="
assert old_script_marker in html, "script 삽입 지점 찾기 실패"
html = html.replace(old_script_marker, tab78 + old_script_marker, 1)
print("✅ TAB 7&8 HTML 삽입")

# ── 6. AI JavaScript 코드 삽입 (initParamPanel 앞) ────────────────────
ai_js = r"""
// ═══════════════════════════════════════════════════════
// 🤖 AI FORECAST ENGINE v2.0
// Holt-Winters + Ensemble + Bayesian Update
// ═══════════════════════════════════════════════════════
const MONTHS_ALL = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

// 2026 Q1 확정 실적
const Q1_2026 = {
  'Split AC': {Jan:3761, Feb:7659, Mar:6943},
  'Floor Standing AC': {Jan:418, Feb:585, Mar:446},
  'Window AC': {Jan:0, Feb:41, Mar:23}
};

// 사용자 입력 월별 실적 (localStorage 영속)
let trackerUserActual = (function(){
  try { return JSON.parse(localStorage.getItem('tracker_actual_v2') || '{}'); } catch(e) { return {}; }
})();
function saveTrackerActual() {
  try { localStorage.setItem('tracker_actual_v2', JSON.stringify(trackerUserActual)); } catch(e) {}
}

// ─── Holt-Winters Triple Exponential Smoothing ──────────
function holtwinters(series, alpha, beta, gamma, periods, horizon) {
  const n = series.length;
  if (n < periods * 2) return Array(horizon).fill(0);
  let L = series.slice(0, periods).reduce((a,b)=>a+b,0) / periods;
  let T = 0;
  for (let i=0; i<periods; i++) T += (series[periods+i] - series[i]) / periods;
  T /= periods;
  const S = [];
  const avg0 = L || 1;
  for (let i=0; i<periods; i++) S.push(avg0 > 0 ? series[i] / avg0 : 1.0);
  for (let t=0; t<n; t++) {
    const si = t % periods;
    const St = S[si] || 1, yt = series[t];
    const Lnew = alpha * (yt / Math.max(St, 0.001)) + (1-alpha) * (L + T);
    T = beta * (Lnew - L) + (1-beta) * T;
    S[si] = gamma * (yt / Math.max(Lnew, 1)) + (1-gamma) * St;
    L = Lnew;
  }
  return Array.from({length: horizon}, (_, h) => {
    const si = (n + h) % periods;
    return Math.max(0, Math.round((L + (h+1)*T) * S[si]));
  });
}

// ─── 계절성 지수 (3년 평균) ────────────────────────────────
function seasonalIndex(cat) {
  const d23=ACTUAL_2023[cat]||{}, d24=ACTUAL_2024[cat]||{}, d25=ACTUAL_2025[cat]||{};
  const vals = MONTHS_ALL.map(m => ((d23[m]||0)+(d24[m]||0)+(d25[m]||0))/3);
  const avg = vals.reduce((s,v)=>s+v,0) / 12;
  return avg > 0 ? vals.map(v => v/avg) : vals.map(()=>1);
}

// ─── 앙상블 예측 (3가지 방법) ──────────────────────────────
function ensembleForecast(cat) {
  const d23=ACTUAL_2023[cat]||{}, d24=ACTUAL_2024[cat]||{}, d25=ACTUAL_2025[cat]||{};
  const series = [];
  [d23,d24,d25].forEach(yr => MONTHS_ALL.forEach(m => series.push(yr[m]||0)));
  // 방법A: Holt-Winters
  const hwA = holtwinters(series, 0.35, 0.12, 0.70, 12, 12);
  // 방법B: 3년 평균 계절성 x 트렌드
  const fy23=MONTHS_ALL.reduce((s,m)=>s+(d23[m]||0),0);
  const fy25=MONTHS_ALL.reduce((s,m)=>s+(d25[m]||0),0);
  const trend = fy23>0 ? Math.min(1.3, Math.max(0.7, Math.sqrt(fy25/fy23))) : 1.0;
  const est26 = fy25 * trend;
  const si = seasonalIndex(cat);
  const siSum = si.reduce((s,v)=>s+v,0);
  const hwB = si.map(s => Math.round(est26 * s / siSum));
  // 방법C: 2년 평균
  const avg2 = MONTHS_ALL.map(m => ((d24[m]||0)+(d25[m]||0))/2);
  const tot2 = avg2.reduce((s,v)=>s+v,0);
  const hwC = avg2.map(v => Math.round(tot2>0 ? v*(fy25*0.95)/tot2 : 0));
  // Q1 오차 기반 가중치
  let wA=0.5, wB=0.3, wC=0.2;
  const allQ1 = {...(Q1_2026[cat]||{}), ...(trackerUserActual[cat]||{})};
  const q1m = ['Jan','Feb','Mar'].filter(m => allQ1[m]!=null&&allQ1[m]>0);
  if (q1m.length > 0) {
    let eA=0,eB=0,eC=0,cnt=0;
    q1m.forEach(m => {
      const mi=MONTHS_ALL.indexOf(m), act=allQ1[m];
      if (act>0) { eA+=Math.abs(hwA[mi]-act)/act; eB+=Math.abs(hwB[mi]-act)/act; eC+=Math.abs(hwC[mi]-act)/act; cnt++; }
    });
    if (cnt>0) {
      const iA=1/(eA/cnt+0.01), iB=1/(eB/cnt+0.01), iC=1/(eC/cnt+0.01), tot=iA+iB+iC;
      wA=Math.max(0.1,Math.min(0.7,iA/tot));
      wB=Math.max(0.1,Math.min(0.6,iB/tot));
      wC=Math.max(0.05, 1-wA-wB);
    }
  }
  return MONTHS_ALL.map((_,i) => Math.max(0, Math.round(wA*hwA[i]+wB*hwB[i]+wC*hwC[i])));
}

// ─── 베이지안 업데이트 ─────────────────────────────────────
function bayesianUpdate(cat, prior) {
  const allActual = {...(Q1_2026[cat]||{}), ...(trackerUserActual[cat]||{})};
  let biasSum=0, cnt=0;
  MONTHS_ALL.forEach((m,i) => {
    const act=allActual[m];
    if (act!=null&&act>=0&&prior[i]>0) { biasSum+=act/prior[i]; cnt++; }
  });
  const bias = cnt>0 ? biasSum/cnt : 1.0;
  const adj = Math.min(1.30, Math.max(0.70, 0.5+0.5*bias));
  return prior.map((v,i) => {
    const m=MONTHS_ALL[i], act=allActual[m];
    if (act!=null) return act;
    return Math.max(0, Math.round(v*adj));
  });
}

// ─── 메인 AI 예측 ──────────────────────────────────────────
function getAiForecast(cat) {
  const prior = ensembleForecast(cat);
  const central = bayesianUpdate(cat, prior);
  const allActual = {...(Q1_2026[cat]||{}), ...(trackerUserActual[cat]||{})};
  let errSum=0, cnt=0;
  MONTHS_ALL.forEach((m,i) => {
    const act=allActual[m];
    if (act!=null&&act>=0&&prior[i]>0) { errSum+=Math.abs(prior[i]-act)/Math.max(act,1); cnt++; }
  });
  const mape = cnt>0?errSum/cnt:0.20;
  const conf = Math.max(0.50, Math.min(0.95, 1-mape));
  return {
    central,
    high: central.map(v=>Math.round(v*1.15)),
    low: central.map(v=>Math.round(v*0.85)),
    highW: central.map(v=>Math.round(v*1.25)),
    lowW: central.map(v=>Math.round(v*0.75)),
    mape, conf, allActual
  };
}

// ─── SVG 그리기 ────────────────────────────────────────────
function drawFcSvg(svgId, layers, W, H) {
  const svg = document.getElementById(svgId);
  if (!svg) return;
  const padL=44,padR=12,padT=18,padB=32;
  const cW=W-padL-padR, cH=H-padT-padB;
  const n=12, xSt=cW/(n-1);
  const allV = layers.flatMap(l=>(l.vals||[]).concat(l.valsH||[]).concat(l.valsL||[])).filter(v=>v!=null&&v>=0);
  const maxV = Math.max(1,...allV)*1.08;
  function px(i){return padL+i*xSt;}
  function py(v){return padT+cH-(v/maxV)*cH;}
  let s='';
  // 그리드
  [0.25,0.5,0.75,1.0].forEach(f=>{
    const y=padT+cH-f*cH;
    s+=`<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W-padR}" y2="${y.toFixed(1)}" stroke="#e0e6f0" stroke-width="1"/>`;
    const lbl=maxV*f>=1000?(maxV*f/1000).toFixed(1)+'k':Math.round(maxV*f).toString();
    s+=`<text x="${(padL-5).toFixed(1)}" y="${(y+4).toFixed(1)}" text-anchor="end" font-size="9" fill="#999">${lbl}</text>`;
  });
  MONTHS_ALL.forEach((m,i)=>{ s+=`<text x="${px(i).toFixed(1)}" y="${H-6}" text-anchor="middle" font-size="9" fill="#666">${m}</text>`; });
  layers.forEach(l=>{
    if (l.type==='band'&&l.valsH&&l.valsL) {
      const ph=l.valsH.map((v,i)=>`${px(i).toFixed(1)},${py(v).toFixed(1)}`).join(' ');
      const pl=[...l.valsL].reverse().map((v,i)=>`${px(n-1-i).toFixed(1)},${py(v).toFixed(1)}`).join(' ');
      s+=`<polygon points="${ph} ${pl}" fill="${l.fill||'rgba(79,195,247,0.2)'}"/>`;
    }
    if (l.type==='line'||l.type==='dot') {
      const validPts=(l.vals||[]).map((v,i)=>v!=null?`${px(i).toFixed(1)},${py(v).toFixed(1)}`:null).filter(Boolean);
      if (validPts.length>=2) s+=`<polyline points="${validPts.join(' ')}" fill="none" stroke="${l.stroke||'#333'}" stroke-width="${l.sw||1.5}" stroke-dasharray="${l.dash||''}"/>`;
      if (l.type==='dot') (l.vals||[]).forEach((v,i)=>{ if(v!=null) s+=`<circle cx="${px(i).toFixed(1)}" cy="${py(v).toFixed(1)}" r="${l.r||5}" fill="${l.fill||l.stroke||'#333'}" stroke="white" stroke-width="1.5"/>`; });
    }
  });
  svg.innerHTML=s;
}

// ─── Tab 7: AI 예측 탭 ─────────────────────────────────────
function buildAiForecastTab() {
  const sel=document.getElementById('ai-cat-sel');
  const cat=sel?sel.value:'Split AC';
  const fc=getAiForecast(cat);
  const d23=ACTUAL_2023[cat]||{}, d24=ACTUAL_2024[cat]||{}, d25=ACTUAL_2025[cat]||{};
  // 신뢰도 배지
  const badge=document.getElementById('ai-conf-badge');
  if (badge) {
    const pct=Math.round(fc.conf*100);
    badge.textContent=`신뢰도 ${pct}% (MAPE ${(fc.mape*100).toFixed(1)}%)`;
    badge.style.background=pct>=80?'#e8f5e9':pct>=65?'#fff9e6':'#ffebee';
    badge.style.color=pct>=80?'#2e7d32':pct>=65?'#f57f17':'#c62828';
  }
  // SVG
  drawFcSvg('ai-svg', [
    {type:'band', valsH:fc.highW, valsL:fc.lowW, fill:'rgba(79,195,247,0.15)'},
    {type:'band', valsH:fc.high, valsL:fc.low, fill:'rgba(79,195,247,0.38)'},
    {type:'line', vals:MONTHS_ALL.map(m=>d25[m]!=null?d25[m]:null), stroke:'#e74c3c', sw:1.5, dash:'5,4'},
    {type:'line', vals:fc.central, stroke:'#0f3460', sw:2.5},
    {type:'dot', vals:MONTHS_ALL.map(m=>fc.allActual[m]!=null?fc.allActual[m]:null), stroke:'#27ae60', fill:'#27ae60', r:5}
  ], 900, 230);
  // 상세 테이블
  const tbody=document.getElementById('ai-detail-body');
  if (tbody) {
    let rows='',totC=0,totH=0,totL=0,totA=0,tot25=0,tot24=0,tot23=0;
    MONTHS_ALL.forEach((m,i)=>{
      const c=fc.central[i],h=fc.high[i],l=fc.low[i];
      const act=fc.allActual[m],v25=d25[m],v24=d24[m],v23=d23[m];
      const hasA=act!=null;
      const err=hasA&&c>0?((act-c)/c*100).toFixed(1):'-';
      const ec=err!=='-'?(Math.abs(parseFloat(err))<=10?'#27ae60':Math.abs(parseFloat(err))<=20?'#f57f17':'#e74c3c'):'#999';
      totC+=c;totH+=h;totL+=l;if(hasA)totA+=act;if(v25!=null)tot25+=(v25||0);if(v24!=null)tot24+=(v24||0);if(v23!=null)tot23+=(v23||0);
      const bg=hasA?'background:#f0fff4':i>=3?'background:#f8fafd':'';
      rows+=`<tr style="${bg}"><td>${m}${hasA?' ✅':''}</td><td class="num">${c.toLocaleString()}</td><td class="num" style="color:#27ae60">${h.toLocaleString()}</td><td class="num" style="color:#e74c3c">${l.toLocaleString()}</td><td class="num" style="font-weight:${hasA?700:400}">${hasA?act.toLocaleString():'<span style="color:#ccc">-</span>'}</td><td class="num" style="color:${ec}">${err!=='-'?err+'%':'-'}</td><td class="num" style="color:#888">${v25!=null?(v25||0).toLocaleString():'-'}</td><td class="num" style="color:#3498db">${v24!=null?(v24||0).toLocaleString():'-'}</td><td class="num" style="color:#8e44ad">${v23!=null?(v23||0).toLocaleString():'-'}</td></tr>`;
    });
    rows+=`<tr style="font-weight:700;background:#e3f2fd"><td>합계</td><td class="num">${totC.toLocaleString()}</td><td class="num" style="color:#27ae60">${totH.toLocaleString()}</td><td class="num" style="color:#e74c3c">${totL.toLocaleString()}</td><td class="num">${totA>0?totA.toLocaleString():'-'}</td><td>-</td><td class="num">${tot25>0?tot25.toLocaleString():'-'}</td><td class="num">${tot24>0?tot24.toLocaleString():'-'}</td><td class="num">${tot23>0?tot23.toLocaleString():'-'}</td></tr>`;
    tbody.innerHTML=rows;
  }
  // 계절성 차트
  const seaEl=document.getElementById('ai-season-chart');
  if (seaEl) {
    const si=seasonalIndex(cat);
    const maxSi=Math.max(...si);
    seaEl.innerHTML=`<div style="display:flex;flex-wrap:wrap;align-items:flex-end;gap:4px">`+
      MONTHS_ALL.map((m,i)=>{
        const v=si[i],w=maxSi>0?Math.round(v/maxSi*80):0;
        const clr=v>=1.3?'#e74c3c':v>=1.0?'#f39c12':'#3498db';
        return `<div style="text-align:center;width:56px"><div style="font-size:10px;color:#888;margin-bottom:2px">${m}</div><div style="background:#e0e6f0;border-radius:2px;height:80px;position:relative;margin:0 auto"><div style="position:absolute;bottom:0;width:100%;height:${w}%;background:${clr};border-radius:2px"></div></div><div style="font-size:11px;font-weight:700;color:${clr};margin-top:2px">${v.toFixed(2)}</div></div>`;
      }).join('')+
    `</div><div style="font-size:11px;color:#666;margin-top:8px"><span style="color:#e74c3c">■ 피크(≥1.3)</span>&nbsp;<span style="color:#f39c12">■ 성수기(1.0~1.3)</span>&nbsp;<span style="color:#3498db">■ 비수기(&lt;1.0)</span></div>`;
  }
  // 코멘트
  const comEl=document.getElementById('ai-comment-box');
  if (comEl) {
    const si=seasonalIndex(cat);
    const peak=MONTHS_ALL.slice().sort((a,b)=>si[MONTHS_ALL.indexOf(b)]-si[MONTHS_ALL.indexOf(a)]).slice(0,3).join(', ');
    const fy25=MONTHS_ALL.reduce((s,m)=>s+(d25[m]||0),0);
    const fy26=fc.central.reduce((s,v)=>s+v,0);
    const yoy=fy25>0?((fy26-fy25)/fy25*100).toFixed(1):'n/a';
    const q1errs=['Jan','Feb','Mar'].filter(m=>fc.allActual[m]!=null&&fc.allActual[m]>0).map(m=>{
      const i=MONTHS_ALL.indexOf(m),a=fc.allActual[m];return fc.central[i]>0?(a-fc.central[i])/fc.central[i]*100:0;
    });
    const avgQ1=q1errs.length>0?q1errs.reduce((s,v)=>s+v,0)/q1errs.length:null;
    let h=`<div class="info-box"><strong>💡 AI 분석 코멘트</strong><br><br>`;
    h+=`📊 <strong>${cat}</strong> 피크 시즌: <strong>${peak}</strong><br>`;
    h+=`📈 2026 AI 연간 예측: <strong>${fy26.toLocaleString()}대</strong> (vs 2025 ${fy25.toLocaleString()}: ${yoy>0?'+':''}${yoy}%)<br>`;
    if (avgQ1!=null) h+=`🎯 Q1 실적이 AI 대비 <strong>${Math.abs(avgQ1).toFixed(1)}% ${avgQ1>0?'상회':'하회'}</strong> → 잔여 월 자동 ${avgQ1>0?'상향':'하향'} 보정<br>`;
    const hiM=MONTHS_ALL.filter((_,i)=>si[i]>=1.2);
    if(hiM.length>0) h+=`⚠️ 선제 재고 권장 시즌: <strong>${hiM.join(', ')}</strong>`;
    comEl.innerHTML=h+'</div>';
  }
}

// ─── Tab 8: 비교 트래커 ────────────────────────────────────
function buildTrackerTab() {
  const sel=document.getElementById('tracker-cat-sel');
  const cat=sel?sel.value:'Split AC';
  const fc=getAiForecast(cat);
  const allActual=fc.allActual;
  const userPlan=getUserPlan(cat);
  buildTrackerScores(cat,fc,allActual,userPlan);
  buildTrackerInputGrid(cat,allActual);
  drawTrackerSvg(cat,fc,allActual,userPlan);
  buildTrackerTable(cat,fc,allActual,userPlan);
  buildLearningViz(cat,fc,allActual);
  buildTrackerComments(cat,fc,allActual,userPlan);
}

function getUserPlan(cat) {
  const si=seasonalIndex(cat);
  const siSum=si.reduce((s,v)=>s+v,0);
  const catKey=cat.replace(/ /g,'-');
  const inp=document.getElementById('annual-target-'+catKey)||document.getElementById('target-'+catKey);
  const tot=inp?(parseInt(inp.value.replace(/,/g,''))||0):0;
  const plan={};
  if (tot>0) MONTHS_ALL.forEach((m,i)=>{ plan[m]=Math.round(tot*si[i]/siSum); });
  return plan;
}

function buildTrackerScores(cat,fc,allActual,userPlan) {
  const el=document.getElementById('tracker-scores');
  if (!el) return;
  const entered=MONTHS_ALL.filter(m=>allActual[m]!=null&&allActual[m]>0);
  if (entered.length===0) { el.innerHTML='<div class="stat-box" style="grid-column:span 4"><p style="color:#888;font-size:12px">실적 입력 시 정확도 비교가 표시됩니다.</p></div>'; return; }
  let aiE=0,planE=0,aiCnt=0,planCnt=0;
  entered.forEach(m=>{
    const i=MONTHS_ALL.indexOf(m),act=allActual[m];
    if(fc.central[i]>0){aiE+=Math.abs(fc.central[i]-act)/Math.max(act,1);aiCnt++;}
    if(userPlan[m]>0){planE+=Math.abs(userPlan[m]-act)/Math.max(act,1);planCnt++;}
  });
  const aiM=aiCnt>0?(aiE/aiCnt*100).toFixed(1):'n/a';
  const planM=planCnt>0?(planE/planCnt*100).toFixed(1):'n/a';
  const winner=aiM!=='n/a'&&planM!=='n/a'?(parseFloat(aiM)<parseFloat(planM)?'🤖 AI':'👤 내 플랜'):'비교 중';
  el.innerHTML=`<div class="stat-box"><div class="val" style="font-size:18px">${entered.length}</div><div class="lbl">실적 입력 월</div></div><div class="stat-box"><div class="val" style="font-size:16px;color:#0f3460">${aiM}%</div><div class="lbl">🤖 AI MAPE</div></div><div class="stat-box"><div class="val" style="font-size:16px;color:#27ae60">${planM}%</div><div class="lbl">👤 내 플랜 MAPE</div></div><div class="stat-box"><div class="val" style="font-size:14px">${winner}</div><div class="lbl">현재 우세</div></div>`;
}

function buildTrackerInputGrid(cat,allActual) {
  const el=document.getElementById('tracker-input-grid');
  if (!el) return;
  el.innerHTML=MONTHS_ALL.map(m=>{
    const isQ1=['Jan','Feb','Mar'].includes(m)&&Q1_2026[cat]&&Q1_2026[cat][m]!=null;
    const val=allActual[m]!=null?allActual[m]:'';
    const ro=isQ1?'readonly style="background:#f0fff4;font-weight:700;color:#27ae60"':'';
    return `<div class="input-item"><label>${m}${isQ1?' ✅':''}</label><input type="number" id="ti-${cat.replace(/ /g,'_')}-${m}" value="${val}" ${ro} min="0" placeholder="실적 입력"></div>`;
  }).join('');
}

function applyTrackerInputs() {
  const sel=document.getElementById('tracker-cat-sel');
  const cat=sel?sel.value:'Split AC';
  if (!trackerUserActual[cat]) trackerUserActual[cat]={};
  MONTHS_ALL.forEach(m=>{
    if (['Jan','Feb','Mar'].includes(m)&&Q1_2026[cat]&&Q1_2026[cat][m]!=null) return;
    const el=document.getElementById('ti-'+cat.replace(/ /g,'_')+'-'+m);
    if (el&&el.value.trim()!=='') {
      const v=parseInt(el.value.replace(/,/g,''));
      if (!isNaN(v)&&v>=0) trackerUserActual[cat][m]=v;
    }
  });
  saveTrackerActual();
  buildTrackerTab();
  buildAiForecastTab();
  alert('✅ 실적 반영 완료! AI가 잔여 월 예측을 재보정했습니다.');
}

function clearTrackerInputs() {
  const sel=document.getElementById('tracker-cat-sel');
  const cat=sel?sel.value:'Split AC';
  if (!confirm(cat+' 입력 실적을 초기화할까요? (Q1 제외)')) return;
  if (trackerUserActual[cat]) {
    MONTHS_ALL.forEach(m=>{
      if (['Jan','Feb','Mar'].includes(m)&&Q1_2026[cat]&&Q1_2026[cat][m]!=null) return;
      delete trackerUserActual[cat][m];
    });
  }
  saveTrackerActual();
  buildTrackerTab();
  buildAiForecastTab();
}

function drawTrackerSvg(cat,fc,allActual,userPlan) {
  drawFcSvg('tracker-svg',[
    {type:'line', vals:fc.central, stroke:'#e74c3c', sw:1.5, dash:'3,3'},
    {type:'line', vals:MONTHS_ALL.map(m=>userPlan[m]||null), stroke:'#0f3460', sw:2, dash:'6,4'},
    {type:'dot', vals:MONTHS_ALL.map(m=>allActual[m]!=null?allActual[m]:null), stroke:'#27ae60', fill:'#27ae60', r:5, sw:2.5}
  ], 900, 230);
}

function buildTrackerTable(cat,fc,allActual,userPlan) {
  const tbody=document.getElementById('tracker-compare-body');
  if (!tbody) return;
  tbody.innerHTML=MONTHS_ALL.map((m,i)=>{
    const act=allActual[m],ai=fc.central[i],plan=userPlan[m]||0;
    const hasA=act!=null;
    const aiE=hasA&&ai>0?((act-ai)/ai*100).toFixed(1):'-';
    const plE=hasA&&plan>0?((act-plan)/plan*100).toFixed(1):'-';
    let winner='-';
    if(hasA&&aiE!=='-'&&plE!=='-') winner=Math.abs(parseFloat(aiE))<Math.abs(parseFloat(plE))?'🤖 AI':'👤 플랜';
    const bg=hasA?'background:#f0fff4':i>=3?'background:#f8fafd':'';
    function ec(e){return e!=='-'?(Math.abs(parseFloat(e))<=10?'#27ae60':Math.abs(parseFloat(e))<=20?'#f57f17':'#e74c3c'):'#999';}
    return `<tr style="${bg}"><td>${m}${hasA?' ✅':''}</td><td class="num" style="font-weight:${hasA?700:400}">${hasA?act.toLocaleString():'<span style="color:#ccc">-</span>'}</td><td class="num">${plan>0?plan.toLocaleString():'-'}</td><td class="num" style="color:${ec(plE)}">${plE!=='-'?plE+'%':'-'}</td><td class="num">${ai.toLocaleString()}</td><td class="num" style="color:${ec(aiE)}">${aiE!=='-'?aiE+'%':'-'}</td><td style="text-align:center;font-size:12px">${winner}</td></tr>`;
  }).join('');
}

function buildLearningViz(cat,fc,allActual) {
  const el=document.getElementById('tracker-learning-viz');
  if (!el) return;
  const entered=MONTHS_ALL.filter(m=>allActual[m]!=null&&allActual[m]>0);
  if (entered.length===0) { el.innerHTML='<p style="color:#888;font-size:12px;padding:8px 0">실적 입력 시 표시됩니다.</p>'; return; }
  const errs=entered.map(m=>({m,e:fc.central[MONTHS_ALL.indexOf(m)]>0?Math.abs(fc.central[MONTHS_ALL.indexOf(m)]-allActual[m])/Math.max(allActual[m],1)*100:0}));
  const avg=errs.reduce((s,e)=>s+e.e,0)/errs.length;
  const avgClr=avg<=10?'#27ae60':avg<=20?'#f39c12':'#e74c3c';
  el.innerHTML=`<div style="margin-bottom:8px;font-size:12px;color:#555">${entered.length}개월 실적 반영 | 평균 오차: <strong style="color:${avgClr}">${avg.toFixed(1)}%</strong> ${avg<=12?' ✅ 우수':avg<=20?' 📊 양호':' ⚠️ 개선 중'}</div>`+
  errs.map(({m,e})=>{
    const w=Math.min(100,e),clr=e<=10?'#27ae60':e<=20?'#f39c12':'#e74c3c';
    return `<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px"><span style="font-size:11px;width:32px;color:#555">${m}</span><div style="flex:1;background:#e0e6f0;border-radius:2px;height:14px;overflow:hidden"><div style="width:${w.toFixed(1)}%;background:${clr};height:100%;border-radius:2px"></div></div><span style="font-size:11px;width:44px;text-align:right;color:${clr}">${e.toFixed(1)}%</span></div>`;
  }).join('');
}

function buildTrackerComments(cat,fc,allActual,userPlan) {
  const el=document.getElementById('tracker-comment-box');
  if (!el) return;
  const entered=MONTHS_ALL.filter(m=>allActual[m]!=null&&allActual[m]>0);
  if (entered.length===0) { el.innerHTML=''; return; }
  const remain=MONTHS_ALL.filter(m=>allActual[m]==null);
  const remAI=remain.reduce((s,m)=>s+fc.central[MONTHS_ALL.indexOf(m)],0);
  const compAct=entered.reduce((s,m)=>s+allActual[m],0);
  const fy25=MONTHS_ALL.reduce((s,m)=>s+(ACTUAL_2025[cat]&&ACTUAL_2025[cat][m]||0),0);
  const proj=compAct+remAI;
  const yoy=fy25>0?((proj-fy25)/fy25*100).toFixed(1):'n/a';
  el.innerHTML=`<div class="success-box"><strong>💡 트래커 인사이트</strong><br><br>✅ ${entered.length}개월 확정 / ${remain.length}개월 잔여<br>📈 누적 실적: <strong>${compAct.toLocaleString()}</strong> | 잔여 AI 예측: <strong>${remAI.toLocaleString()}</strong> | 예상 연간: <strong>${proj.toLocaleString()}</strong><br>${fy25>0?`YoY vs 2025(${fy25.toLocaleString()}): <strong>${yoy>0?'+':''}${yoy}%</strong>`:''}</div>`;
}

"""

old_init = "// ─── Init ─────────────────────────────────────────────────────────────────\ninitParamPanel();"
assert old_init in html, "Init 찾기 실패"
html = html.replace(old_init, ai_js + old_init, 1)
print("✅ AI JavaScript 코드 삽입")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ 완료! 최종 파일 크기: {len(html):,} bytes")
