import re, json

# Read existing file
with open(r'd:\coding\html games\Stott-reformer-exam\index.html', 'r', encoding='utf-8') as f:
    old = f.read()

# Extract questionDatabase JSON array
m = re.search(r'const questionDatabase\s*=\s*(\[.*?\]);', old, re.DOTALL)
if not m:
    print("Could not find questionDatabase!"); exit(1)

db_str = m.group(1)
# JSON parse (JS uses unquoted keys, convert first)
db_str_json = re.sub(r'(\s)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', db_str)
questions = json.loads(db_str_json)
print(f"Extracted {len(questions)} questions.")

new_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>斯多特普拉提 (STOTT PILATES) 模拟考试</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }

        .fade-in { animation: fadeIn 0.35s ease-in-out; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* Answer tile states */
        .answer-tile {
            transition: all 0.18s ease;
            cursor: pointer;
            border-width: 2px;
            word-break: break-word;
        }
        .answer-tile:hover   { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.10); }
        .answer-tile.selected { border-color: #3b82f6 !important; background: #eff6ff !important; color: #1d4ed8 !important; box-shadow: 0 0 0 3px rgba(59,130,246,.25); transform: scale(1.01); }

        /* Slot states */
        .slot-zone {
            transition: all 0.18s ease;
            cursor: pointer;
            min-height: 48px;
            border-width: 2px;
            border-style: dashed;
            display: flex;
            align-items: center;
            padding: 8px 12px;
            border-radius: 10px;
            font-size: 0.875rem;
            word-break: break-word;
        }
        .slot-zone.hover-active { border-color: #3b82f6; background: #eff6ff; }
        .slot-zone.filled       { border-style: solid; border-color: #94a3b8; background: #f8fafc; color: #334155; }
        .slot-zone.correct      { border-style: solid; border-color: #22c55e; background: #f0fdf4; color: #166534; font-weight: 600; }
        .slot-zone.incorrect    { border-style: solid; border-color: #ef4444; background: #fef2f2; color: #991b1b; font-weight: 600; }
        .slot-zone.empty        { border-color: #cbd5e1; color: #94a3b8; }

        .bin-slot-zone {
            transition: all 0.18s ease;
            cursor: pointer;
            min-height: 48px;
            border-width: 2px;
            border-style: dashed;
            display: flex;
            align-items: center;
            padding: 8px 12px;
            border-radius: 10px;
            font-size: 0.875rem;
            word-break: break-word;
        }
        .bin-slot-zone.filled    { border-style: solid; border-color: #94a3b8; background: #f8fafc; color: #334155; }
        .bin-slot-zone.correct   { border-style: solid; border-color: #22c55e; background: #f0fdf4; color: #166534; font-weight: 600; }
        .bin-slot-zone.incorrect { border-style: solid; border-color: #ef4444; background: #fef2f2; color: #991b1b; font-weight: 600; }
        .bin-slot-zone.empty     { border-color: #fca5a5; color: #94a3b8; }

        .question-card {
            border-radius: 14px;
            border-width: 2px;
            border-color: #e2e8f0;
            background: #f8fafc;
            transition: border-color 0.2s;
        }
        .question-card.correct-border { border-color: #22c55e; }
        .question-card.incorrect-border { border-color: #ef4444; }

        .pulse-correct { animation: pulseGreen 0.5s ease; }
        @keyframes pulseGreen {
            0%   { box-shadow: 0 0 0 0 rgba(34,197,94,.5); }
            70%  { box-shadow: 0 0 0 10px rgba(34,197,94,0); }
            100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
        }
    </style>
</head>
<body class="bg-slate-100 min-h-screen font-sans text-slate-800">

    <!-- ===== HEADER (always visible) ===== -->
    <div class="bg-teal-700 text-white px-6 py-5 text-center shadow-lg">
        <h1 class="text-2xl md:text-3xl font-bold tracking-tight">STOTT PILATES®</h1>
        <p class="text-teal-200 mt-1 text-sm">Intensive Reformer (IR) — 理论模拟考试</p>
    </div>

    <!-- ===== START SCREEN ===== -->
    <div id="start-screen" class="max-w-2xl mx-auto mt-10 bg-white rounded-2xl shadow-xl p-10 text-center fade-in">
        <div class="text-5xl mb-4">🏋️</div>
        <h2 class="text-2xl font-bold mb-3">准备好测试你的知识了吗？</h2>
        <p class="text-slate-500 mb-8 leading-relaxed">
            题库共包含 <strong class="text-teal-700">100</strong> 道精选试题。<br>
            每轮展示 <strong>4 道题目</strong>，将正确答案匹配到对应题目，<br>
            并将 <strong>1 个错误答案</strong> 拖入垃圾桶。共 <strong class="text-teal-700">25 轮</strong>。<br>
            <span class="text-xs text-slate-400 mt-2 block">只有第一次尝试正确才能得分，错误答案（垃圾桶）不计分。</span>
        </p>
        <button onclick="startGame()"
            class="bg-teal-600 hover:bg-teal-700 active:bg-teal-800 text-white font-bold py-3 px-10 rounded-full shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5">
            开始考试
        </button>
    </div>

    <!-- ===== GAME SCREEN ===== -->
    <div id="game-screen" class="hidden max-w-5xl mx-auto mt-0 pb-10">

        <!-- Tracker bar -->
        <div class="bg-white px-6 py-3 flex justify-between items-center text-sm font-semibold text-slate-500 shadow-sm">
            <span id="round-tracker" class="text-slate-700">第 1 / 25 轮</span>
            <span id="score-tracker" class="text-teal-600 font-bold text-base">得分: 0 / 100</span>
        </div>
        <!-- Progress bar -->
        <div class="w-full bg-slate-200 h-1.5">
            <div id="progress-bar" class="bg-teal-500 h-1.5 transition-all duration-500" style="width:0%"></div>
        </div>

        <div class="mt-4 px-3 md:px-4 fade-in" id="round-content">

            <!-- Instructions hint -->
            <p class="text-xs text-slate-400 text-center mb-4">
                💡 点击下方<strong>答案</strong>选中，再点击<strong>题目槽位</strong>或<strong>垃圾桶</strong>放置。点击已放置的槽位可取回答案。
            </p>

            <!-- 2-column layout: questions left, bin right on desktop -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

                <!-- Questions column (takes 2/3) -->
                <div class="lg:col-span-2 space-y-3" id="questions-container">
                    <!-- question cards injected here -->
                </div>

                <!-- Right column: Bin + Answer Pool -->
                <div class="lg:col-span-1 flex flex-col gap-4">
                    <!-- Bin -->
                    <div class="bg-white rounded-2xl shadow p-4 border-2 border-red-100">
                        <div class="flex items-center gap-2 mb-2">
                            <span class="text-2xl">🗑️</span>
                            <div>
                                <p class="font-bold text-slate-700 text-sm">错误答案垃圾桶</p>
                                <p class="text-xs text-slate-400">将错误答案放置于此</p>
                            </div>
                        </div>
                        <div id="bin-slot" class="bin-slot-zone empty" onclick="placeIntoSlot('bin')">
                            <span class="text-slate-400 text-sm italic">点击此处放置…</span>
                        </div>
                    </div>

                    <!-- Answer Pool -->
                    <div class="bg-white rounded-2xl shadow p-4">
                        <p class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">可用答案</p>
                        <div id="answers-pool" class="flex flex-col gap-2">
                            <!-- answer tiles injected -->
                        </div>
                    </div>
                </div>

            </div>

            <!-- Action buttons -->
            <div class="mt-6 flex justify-end gap-3">
                <button id="check-btn" onclick="checkAnswers()"
                    class="bg-slate-800 hover:bg-slate-900 active:scale-95 text-white font-bold py-2.5 px-8 rounded-xl shadow transition-all">
                    ✅ 检查答案
                </button>
                <button id="next-btn" onclick="nextRound()"
                    class="hidden bg-teal-600 hover:bg-teal-700 active:scale-95 text-white font-bold py-2.5 px-8 rounded-xl shadow transition-all">
                    下一轮 →
                </button>
            </div>

        </div>
    </div>

    <!-- ===== RESULT SCREEN ===== -->
    <div id="result-screen" class="hidden max-w-2xl mx-auto mt-10 bg-white rounded-2xl shadow-xl p-10 text-center fade-in">
        <div id="result-icon" class="text-6xl mb-4">🏆</div>
        <h2 class="text-2xl font-bold mb-2">考试完成！</h2>
        <p class="text-lg text-slate-600 mb-6">
            你的最终得分是：<strong id="final-score" class="text-teal-700 text-4xl"></strong>
            <span class="text-slate-400"> / 100</span>
        </p>
        <div id="result-message" class="text-slate-700 mb-8 p-4 bg-teal-50 rounded-xl text-sm leading-relaxed"></div>
        <button onclick="startGame()"
            class="bg-teal-600 hover:bg-teal-700 text-white font-bold py-3 px-10 rounded-full shadow transition-colors">
            重新开始
        </button>
    </div>

<script>
// ============================================================
// QUESTION DATABASE (100 questions)
// ============================================================
const questionDatabase = QUESTION_DB_PLACEHOLDER;

// ============================================================
// GAME STATE
// ============================================================
const QUESTIONS_PER_ROUND = 4;
const TOTAL_ROUNDS = 25; // 100 / 4

let shuffledQuestions = [];
let currentRound = 0;
let score = 0;

// Per-round state
let roundQuestions = [];   // 4 question objects
let correctAnswers = [];   // 4 correct answer strings (parallel to roundQuestions)
let wrongAnswer = '';      // 1 wrong answer string (the decoy)
let allAnswers = [];       // 5 shuffled answers for this round
let poolAnswers = [];      // answers still available to pick from pool
let placements = {};       // { 'slot-0': str, 'slot-1': str, ..., 'bin': str }
let selectedAnswer = null; // answer tile currently selected
let firstCheckDone = false;// whether the first check press happened this round
let lockedCorrect = new Set(); // slot IDs confirmed correct (locked permanently)
let isChecking = false;    // prevent double-clicks

// ============================================================
// UTILITIES
// ============================================================
function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
}

// ============================================================
// GAME FLOW
// ============================================================
function startGame() {
    score = 0;
    currentRound = 0;
    shuffledQuestions = shuffle([...questionDatabase]);
    document.getElementById('start-screen').classList.add('hidden');
    document.getElementById('result-screen').classList.add('hidden');
    document.getElementById('game-screen').classList.remove('hidden');
    loadRound();
}

function loadRound() {
    // Reset round state
    firstCheckDone = false;
    lockedCorrect = new Set();
    placements = {};
    selectedAnswer = null;
    isChecking = false;

    const start = currentRound * QUESTIONS_PER_ROUND;
    roundQuestions = shuffledQuestions.slice(start, start + QUESTIONS_PER_ROUND);
    correctAnswers = roundQuestions.map(q => q.options[q.ans]);

    // Pick 1 wrong answer from a random question in this round
    const decoyQ = roundQuestions[Math.floor(Math.random() * QUESTIONS_PER_ROUND)];
    const decoyOptions = decoyQ.options.filter((_, i) => i !== decoyQ.ans);
    wrongAnswer = decoyOptions[Math.floor(Math.random() * decoyOptions.length)];

    // Build & shuffle the 5-answer pool
    allAnswers = shuffle([...correctAnswers, wrongAnswer]);
    poolAnswers = [...allAnswers];

    updateTrackers();
    renderRound();
}

function updateTrackers() {
    document.getElementById('round-tracker').innerText = `第 ${currentRound + 1} / ${TOTAL_ROUNDS} 轮`;
    document.getElementById('score-tracker').innerText = `得分: ${score} / 100`;
    document.getElementById('progress-bar').style.width = `${(currentRound / TOTAL_ROUNDS) * 100}%`;
}

// ============================================================
// RENDER
// ============================================================
function renderRound() {
    renderQuestions();
    renderBinSlot();
    renderPool();
    document.getElementById('check-btn').classList.remove('hidden');
    document.getElementById('next-btn').classList.add('hidden');
}

function renderQuestions() {
    const container = document.getElementById('questions-container');
    container.innerHTML = '';
    roundQuestions.forEach((q, i) => {
        const slotId = `slot-${i}`;
        const card = document.createElement('div');
        card.className = 'question-card bg-white shadow p-4';
        card.id = `card-${i}`;

        // Question number badge + text
        const header = document.createElement('div');
        header.className = 'flex items-start gap-3 mb-3';

        const badge = document.createElement('div');
        badge.className = 'flex-shrink-0 w-7 h-7 rounded-full bg-teal-600 text-white text-xs font-bold flex items-center justify-center mt-0.5';
        badge.innerText = i + 1;

        const qText = document.createElement('p');
        qText.className = 'text-sm font-medium text-slate-700 leading-snug flex-1';
        qText.innerText = q.q;

        header.appendChild(badge);
        header.appendChild(qText);

        // Answer slot
        const slot = document.createElement('div');
        slot.id = slotId;
        slot.className = 'slot-zone empty';
        slot.innerHTML = '<span class="text-slate-400 italic">点击此处放置答案…</span>';
        slot.onclick = () => placeIntoSlot(slotId);

        card.appendChild(header);
        card.appendChild(slot);
        container.appendChild(card);
    });
}

function renderBinSlot() {
    const bin = document.getElementById('bin-slot');
    bin.className = 'bin-slot-zone empty';
    bin.innerHTML = '<span class="text-slate-400 text-sm italic">点击此处放置…</span>';
}

function renderPool() {
    const pool = document.getElementById('answers-pool');
    pool.innerHTML = '';
    if (poolAnswers.length === 0) {
        pool.innerHTML = '<p class="text-xs text-slate-400 italic text-center py-2">所有答案已放置</p>';
        return;
    }
    poolAnswers.forEach(ans => {
        const tile = document.createElement('button');
        const isSelected = (selectedAnswer === ans);
        tile.className = 'answer-tile text-left px-4 py-3 rounded-xl ' +
            (isSelected
                ? 'border-blue-500 bg-blue-50 text-blue-800 selected'
                : 'border-slate-300 bg-slate-50 text-slate-700 hover:border-teal-400 hover:bg-teal-50');
        tile.innerText = ans;
        tile.onclick = () => toggleSelect(ans);
        pool.appendChild(tile);
    });
}

// ============================================================
// INTERACTION
// ============================================================
function toggleSelect(ans) {
    if (isChecking) return;
    selectedAnswer = (selectedAnswer === ans) ? null : ans;
    renderPool();
}

function placeIntoSlot(slotId) {
    if (isChecking) return;
    // If this slot is locked correct, do nothing
    if (lockedCorrect.has(slotId)) return;

    if (selectedAnswer) {
        // Return any currently placed answer in this slot back to pool
        if (placements[slotId]) {
            poolAnswers.push(placements[slotId]);
        }
        // Place selected into slot
        placements[slotId] = selectedAnswer;
        poolAnswers = poolAnswers.filter(a => a !== selectedAnswer);
        selectedAnswer = null;
        updateSlotDisplay(slotId, 'filled');
        renderPool();
    } else if (placements[slotId]) {
        // No tile selected — retrieve it from slot back to pool
        poolAnswers.push(placements[slotId]);
        delete placements[slotId];
        updateSlotDisplay(slotId, 'empty');
        renderPool();
    }
}

function updateSlotDisplay(slotId, state, text) {
    const isBin = slotId === 'bin';
    const el = document.getElementById(isBin ? 'bin-slot' : slotId);
    if (!el) return;

    const placed = text || placements[slotId];
    const baseClass = isBin ? 'bin-slot-zone' : 'slot-zone';

    if (state === 'empty') {
        el.className = baseClass + ' empty';
        el.innerHTML = `<span class="text-slate-400 italic">${isBin ? '点击此处放置…' : '点击此处放置答案…'}</span>`;
    } else if (state === 'filled') {
        el.className = baseClass + ' filled';
        el.innerText = placed;
    } else if (state === 'correct') {
        el.className = baseClass + ' correct';
        el.innerText = placed;
    } else if (state === 'incorrect') {
        el.className = baseClass + ' incorrect';
        el.innerText = placed;
    }
}

// ============================================================
// CHECK LOGIC
// ============================================================
function checkAnswers() {
    if (isChecking) return;

    // Ensure all 5 slots are filled
    const allSlots = ['slot-0', 'slot-1', 'slot-2', 'slot-3', 'bin'];
    for (const s of allSlots) {
        if (!placements[s]) {
            showToast('请先将所有 5 个答案放置到槽位后再检查！');
            return;
        }
    }

    isChecking = true;
    let allGreen = true;

    // Check each question slot
    for (let i = 0; i < 4; i++) {
        const slotId = `slot-${i}`;
        const placed = placements[slotId];
        const expected = correctAnswers[i];
        const isCorrect = (placed === expected);

        if (isCorrect) {
            updateSlotDisplay(slotId, 'correct');
            document.getElementById(`card-${i}`).classList.remove('incorrect-border');
            document.getElementById(`card-${i}`).classList.add('correct-border');
            // Award point if this is the first check and not already locked
            if (!firstCheckDone && !lockedCorrect.has(slotId)) {
                score++;
            }
            lockedCorrect.add(slotId);
        } else {
            updateSlotDisplay(slotId, 'incorrect');
            document.getElementById(`card-${i}`).classList.add('incorrect-border');
            document.getElementById(`card-${i}`).classList.remove('correct-border');
            allGreen = false;
        }
    }

    // Check bin
    const binPlaced = placements['bin'];
    const binCorrect = (binPlaced === wrongAnswer);
    if (binCorrect) {
        updateSlotDisplay('bin', 'correct');
        lockedCorrect.add('bin');
    } else {
        updateSlotDisplay('bin', 'incorrect');
        allGreen = false;
    }

    firstCheckDone = true;
    updateTrackers();

    if (allGreen) {
        document.getElementById('check-btn').classList.add('hidden');
        document.getElementById('next-btn').classList.remove('hidden');
        isChecking = false;
    } else {
        // After 1.2s, return incorrect answers to pool so player can fix
        setTimeout(() => {
            returnIncorrectToPool();
            isChecking = false;
        }, 1200);
    }
}

function returnIncorrectToPool() {
    const allSlots = ['slot-0', 'slot-1', 'slot-2', 'slot-3', 'bin'];
    for (const slotId of allSlots) {
        if (lockedCorrect.has(slotId)) continue; // keep correct ones locked
        if (placements[slotId]) {
            poolAnswers.push(placements[slotId]);
            delete placements[slotId];
            updateSlotDisplay(slotId, 'empty');
            // Reset card border for question slots
            if (slotId !== 'bin') {
                const i = parseInt(slotId.split('-')[1]);
                document.getElementById(`card-${i}`).classList.remove('incorrect-border');
            }
        }
    }
    renderPool();
}

// ============================================================
// NEXT ROUND / RESULTS
// ============================================================
function nextRound() {
    currentRound++;
    if (currentRound >= TOTAL_ROUNDS) {
        showResults();
    } else {
        // Re-render with animation
        const content = document.getElementById('round-content');
        content.classList.remove('fade-in');
        void content.offsetWidth;
        content.classList.add('fade-in');
        loadRound();
    }
}

function showResults() {
    document.getElementById('game-screen').classList.add('hidden');
    document.getElementById('result-screen').classList.remove('hidden');
    document.getElementById('final-score').innerText = score;
    document.getElementById('progress-bar').style.width = '100%';

    const pct = score / 100;
    let msg, icon;
    if (pct >= 0.9) {
        msg = '太棒了！你的理论知识非常扎实，完全具备了通过真实考试的水平！🎉';
        icon = '🏆';
    } else if (pct >= 0.7) {
        msg = '表现不错！你已经掌握了大部分核心概念，再针对错题复习一遍就完美了。';
        icon = '⭐';
    } else {
        msg = '继续加油！建议重新复习普拉提五大基本原则和功能性解剖学部分。';
        icon = '📚';
    }
    document.getElementById('result-message').innerText = msg;
    document.getElementById('result-icon').innerText = icon;
}

// ============================================================
// TOAST NOTIFICATION
// ============================================================
function showToast(msg) {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#1e293b;color:#fff;padding:10px 22px;border-radius:999px;font-size:0.875rem;font-weight:600;z-index:9999;opacity:0;transition:opacity 0.3s';
        document.body.appendChild(toast);
    }
    toast.innerText = msg;
    toast.style.opacity = '1';
    clearTimeout(toast._t);
    toast._t = setTimeout(() => { toast.style.opacity = '0'; }, 2500);
}
</script>
</body>
</html>'''

# Embed question database
db_js = json.dumps(questions, ensure_ascii=False, indent=12)
new_html = new_html.replace('QUESTION_DB_PLACEHOLDER', db_js)

with open(r'd:\coding\html games\Stott-reformer-exam\index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Done! Written new index.html.")
