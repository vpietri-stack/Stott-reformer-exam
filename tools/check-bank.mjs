// Checks the question bank that lives inside index.html.
//   node tools/check-bank.mjs            exit 0 = fit to commit
// Contract of the bank: exactly 2 options per question, options[0] is the correct
// answer (the UI shuffles display order, so "ans" is always 0), and "cat" is one of
// CATS below. The banned-word list encodes the teacher's rule that the exam contains
// no pregnancy/postpartum and no injury/pain/pathology content.
import fs from 'fs';

const CATS = {
  mat: '垫上', cadillac: '凯迪拉克床', ref_rep: '核心床动作', ref_setup: '核心床设置',
  anatomy: '解剖', principles: '基本原则', breath: '呼吸', posture: '姿势',
  cueing: '提示语', standards: '职业规范',
};

// subject matter the teacher asked to have removed; must never appear again
const BANNED = ['孕', '妊娠', '产后', '哺乳', '月子', '剖宫', '松弛素', '腹直肌分离',
  '伤', '痛', '术后', '手术', '康复', '疾病', '诊断', '转介', '红旗', '骨质疏松', '间盘',
  '关节炎', '炎', '置换', '脊柱侧弯', '结构性侧弯', '凸侧', 'Cobb', '高血压', '血压',
  '糖尿病', '神经病变', 'SOAP', '病史', '医嘱', '医生', '肿胀', '头晕', '卧床', '症状',
  '骨折', '脱位', 'pregnan', 'postpartum', 'injury', 'pain', 'surgery', 'clinical',
  'patholog', 'medical', 'diagnos', 'rehab', 'osteopor', 'scoliosis', 'herniat', 'arthritis'];
// these also occur inside legitimate technique words (侧弯 = side bend, 技术 = technique),
// so they are reported for a human read instead of failing the run
const REVIEW = ['术', '病', '医', '麻', '炎', '肿', '晕', '痛', '伤', '血压', '侧弯'];

const lines = fs.readFileSync('index.html', 'utf8').split(/\r?\n/);
const start = lines.findIndex(l => l.trim().startsWith('const questionDatabase = ['));
const end = lines.findIndex((l, i) => i > start && l.trim() === '];');
if (start < 0 || end < 0) { fail('could not locate the questionDatabase array in index.html'); }
const bank = JSON.parse('[' + lines.slice(start + 1, end).join('\n').replace(/,(\s*)$/, '$1') + ']');

const problems = [];
function fail(msg) { console.error('FAIL: ' + msg); process.exit(1); }
const norm = s => s.replace(/[\s“”"'’‘()（）:：、，,。.；;\-—?？!！]/g, '').toLowerCase();

bank.forEach((q, i) => {
  const at = `#${i} ${q.q ? q.q.slice(0, 24) : '(no stem)'}`;
  if (typeof q.q !== 'string' || !q.q.trim()) problems.push(`${at}: empty stem`);
  if (!Array.isArray(q.options) || q.options.length !== 2) { problems.push(`${at}: needs exactly 2 options`); return; }
  if (q.ans !== 0) problems.push(`${at}: ans must be 0 (options[0] is the correct answer)`);
  if (!Object.keys(CATS).includes(q.cat)) problems.push(`${at}: unknown cat "${q.cat}"`);
  if (norm(q.options[0]) === norm(q.options[1])) problems.push(`${at}: the two options are the same`);
  if (q.options.some(o => typeof o !== 'string' || !o.trim())) problems.push(`${at}: empty option`);
  if (/[：:]{2}|？？|，，/.test(q.q)) problems.push(`${at}: doubled punctuation in stem`);
  if (!/[：？?]$/.test(q.q)) problems.push(`${at}: stem must end with ：or ？`);
  const hay = q.q + ' ' + q.options.join(' ');
  const hits = BANNED.filter(w => hay.includes(w));
  if (hits.length) problems.push(`${at}: banned topic ${hits.join(', ')}`);
});

// near-duplicate stems: bitset Jaccard over character bigrams
const ids = new Map();
const grams = bank.map(q => {
  const s = norm(q.q), set = new Set();
  for (let i = 0; i < s.length - 1; i++) {
    const g = s.slice(i, i + 2);
    if (!ids.has(g)) ids.set(g, ids.size);
    set.add(ids.get(g));
  }
  return set;
});
const words = Math.ceil(ids.size / 32);
const bits = grams.map(set => {
  const b = new Uint32Array(words);
  for (const g of set) b[g >> 5] |= 1 << (g % 32);
  return b;
});
const popcount = x => { let n = 0; while (x) { n += x & 1; x >>>= 1; } return n; };
const dupes = [];
for (let i = 0; i < bank.length; i++) {
  for (let j = i + 1; j < bank.length; j++) {
    let shared = 0;
    for (let w = 0; w < words; w++) shared += popcount(bits[i][w] & bits[j][w]);
    const union = grams[i].size + grams[j].size - shared;
    if (shared / union > 0.62) dupes.push([i, j, shared / union]);
  }
}

const review = [];
bank.forEach((q, i) => {
  const hay = q.q + ' ' + q.options.join(' ');
  const hits = REVIEW.filter(w => hay.includes(w) && !BANNED.includes(w));
  if (hits.length) review.push(`#${i} [${hits.join(',')}] ${q.q}`);
});

const counts = bank.reduce((a, q) => { a[q.cat] = (a[q.cat] || 0) + 1; return a; }, {});
console.log(`questions: ${bank.length}   (scanned lines ${start + 1}..${end + 1} of index.html)`);
for (const c of Object.keys(CATS)) console.log(`  ${c.padEnd(10)} ${CATS[c].padEnd(7)} ${String(counts[c] || 0).padStart(4)}`);
console.log(`near-duplicate stems (>0.62 similarity): ${dupes.length}`);
dupes.slice(0, 20).forEach(([i, j, v]) => console.log(`  ${Math.round(v * 100)}%  #${i} ${bank[i].q}  <>  #${j} ${bank[j].q}`));
console.log(`items to eyeball for clinical wording: ${review.length}`);
review.slice(0, 20).forEach(r => console.log('  ? ' + r));

if (problems.length) {
  console.error(`\n${problems.length} PROBLEM(S):`);
  problems.slice(0, 40).forEach(p => console.error('  ! ' + p));
  process.exit(1);
}
console.log('\nbank OK');
