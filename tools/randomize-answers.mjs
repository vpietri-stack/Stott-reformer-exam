// Randomize which option holds the answer, in place, inside index.html.
//   node tools/randomize-answers.mjs
// The game already reads options[q.ans] and shuffles the on-screen answer tiles, so this
// only changes the stored bank: after a run, roughly half the questions carry ans 1, which
// means reading the source no longer reveals "the first option is always the answer".
// Run it after adding a batch of questions (new ones are authored as ans: 0), then
// re-run tools/check-bank.mjs.
import fs from 'fs';

const FILE = 'index.html';
const raw = fs.readFileSync(FILE, 'utf8');
const eol = raw.includes('\r\n') ? '\r\n' : '\n';
const lines = raw.split(/\r?\n/);
const start = lines.findIndex(l => l.trim().startsWith('const questionDatabase = ['));
const end = lines.findIndex((l, i) => i > start && l.trim() === '];');
if (start < 0 || end < 0) { console.error('could not locate the questionDatabase array'); process.exit(1); }

const bank = JSON.parse('[' + lines.slice(start + 1, end).join('\n').replace(/,(\s*)$/, '$1') + ']');
let flipped = 0;
for (const q of bank) {
  if (!Array.isArray(q.options) || q.options.length !== 2) throw new Error(`bad question: ${q.q}`);
  if (Math.random() < 0.5) { q.options.reverse(); q.ans = q.ans === 0 ? 1 : 0; flipped++; }
}

const j = s => JSON.stringify(s);
const rows = [lines[start], ''];
for (const q of bank) rows.push('            { "q": ' + j(q.q) + ', "options": [' + q.options.map(j).join(', ') + '], "ans": ' + q.ans + ', "cat": ' + j(q.cat) + ' },');
rows.push(lines[end]);
fs.writeFileSync(FILE, [...lines.slice(0, start), ...rows, ...lines.slice(end + 1)].join(eol));

const at0 = bank.filter(q => q.ans === 0).length;
console.log(`${bank.length} questions, ${flipped} flipped — answer sits at index 0 in ${at0}, index 1 in ${bank.length - at0}`);
