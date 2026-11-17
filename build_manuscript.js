import fs from "node:fs";
import path from "node:path";
import {
  AlignmentType, Document, Footer, Header, HeadingLevel, ImageRun, Packer,
  PageNumber, Paragraph, ShadingType, Table, TableCell, TableRow, TextRun,
  WidthType, PageBreak,
} from "docx";

const outputPath = process.argv[2];
if (!outputPath) throw new Error("Usage: node build_manuscript.js /abs/out.docx");
const content = JSON.parse(fs.readFileSync(
  "D:/CHARLS/DementiaTransition_W6/submission/content_main.json", "utf-8"));

const font = { ascii: "Times New Roman", hAnsi: "Times New Roman",
               cs: "Times New Roman", eastAsia: "SimSun" };
const run = (text, options = {}) => new TextRun({ text, font, size: 24, ...options });
const para = (children, options = {}) => new Paragraph({
  spacing: { after: 160, line: 480 }, ...options,
  children: Array.isArray(children) ? children : [children],
});
const runsFrom = (runs) => runs.map(r =>
  run(r.t, { bold: !!r.bold, italics: !!r.ital }));
const bodyPara = (runs, options = {}) =>
  para(runsFrom(runs), { alignment: AlignmentType.JUSTIFIED, ...options });
const h1 = (text) => para(run(text, { bold: true, size: 30 }), {
  heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 } });
const h2 = (text) => para(run(text, { bold: true, size: 26 }), {
  heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } });

const cell = (text, options = {}) => new TableCell({
  children: [para(run(String(text ?? "")), { spacing: { after: 0, line: 240 } })],
  margins: { top: 60, bottom: 60, left: 100, right: 100 }, ...options,
});
function makeTable(rows) {
  const ncol = rows[0].length;
  const total = 9000;
  const w0 = 2600;
  const wRest = Math.floor((total - w0) / (ncol - 1));
  const widths = Array.from({ length: ncol }, (_, i) => (i === 0 ? w0 : wRest));
  widths[ncol - 1] = total - widths.slice(0, -1).reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({
      children: r.map((c, ci) => cell(c, {
        width: { size: widths[ci], type: WidthType.DXA },
        ...(ri === 0 ? {} : {}),
      })),
    })),
  });
}
const caption = (text) => para(run(text, { bold: true }), { spacing: { before: 280 } });

const children = [];
// ---- title page ----
children.push(para(run(content.title, { bold: true, size: 32 }), {
  heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, spacing: { after: 280 } }));
children.push(para([run("Running title: ", { bold: true }), run(content.running)],
  { alignment: AlignmentType.CENTER }));
children.push(para([
  run("Qingli Sun"), run("1†", { superScript: true }),
  run(", Gan Zhang"), run("1†", { superScript: true }),
  run(", Yong Chen"), run("1*", { superScript: true }),
], { alignment: AlignmentType.CENTER }));
children.push(para([
  run("1", { superScript: true, size: 20 }),
  run(" Department of Neurology, Peking University Third Hospital, No. 49 North Garden Road, Haidian District, Beijing 100191, China", { size: 20 }),
], { alignment: AlignmentType.CENTER }));
children.push(para(run("† Qingli Sun and Gan Zhang contributed equally to this work (co-first authors).",
  { size: 20, italics: true }), { alignment: AlignmentType.CENTER }));
children.push(para([
  run("* Corresponding author: Yong Chen, ", { size: 20 }),
  run("ronaldchen@bjmu.edu.cn", { size: 20, italics: true }),
  run("; Tel: +86-18810975103; Fax: +86-10-82266699", { size: 20 }),
], { alignment: AlignmentType.CENTER }));
children.push(para(run("E-mails: qingli_sun@sohu.com (Q.S.); g.zhang@bjmu.edu.cn (G.Z.); ronaldchen@bjmu.edu.cn (Y.C.)",
  { size: 20 }), { alignment: AlignmentType.CENTER }));

// ---- inline tables & figures (placed at first citation, per submission system) ----
const inserted = new Set();
const tableEls = (cap, rows, note) => {
  const els = [caption(cap), makeTable(rows)];
  if (note) els.push(para(run(note, { italics: true, size: 20 })));
  return els;
};
const figEls = (fig) => [
  caption(fig.legend.split(". ")[0] + "."),
  para(run(fig.legend.substring(fig.legend.indexOf(". ") + 2))),
  para(new ImageRun({
    type: "png", data: fs.readFileSync(fig.path),
    transformation: { width: fig.w, height: fig.h },
  }), { alignment: AlignmentType.CENTER }),
];
const T = {
  t1: () => tableEls("Table 1. Baseline (2018) characteristics by cognitive state", content.table1,
    "Note. Participants with classifiable 2018 cognitive state (n = 10,628). ADL impairment percentages use non-missing denominators; ADL missingness was 25.1%, 20.6% and 1.7% in the Normal, CIND and Dementia groups (the low missingness in Dementia is structural: the proxy-rule classification requires informant-reported ADL data). Ever-smoked is not shown because the item was administered only to the 2018 refreshment sample (38.5% missing)."),
  t2: () => tableEls("Table 2. Observed 2018 → wave 6 transitions by baseline state", content.table2,
    "Note. Full analysis panel (n = 9,679); values are n (row %). W6, wave 6 (2021–2023)."),
  t3: () => tableEls("Table 3. Model-based 5-year transition probabilities (%)", content.table3,
    "Note. Point estimates from the time-homogeneous continuous-time Markov model; delta-method confidence intervals were numerically unstable and are not reported (see Methods)."),
  t4: () => tableEls("Table 4. Adjusted relative risk ratios for all covariates, by transition", content.table4,
    "Note. Baseline-state-stratified multinomial logistic models (complete-case sample, n = 8,178); the reference outcome within each stratum is remaining in the baseline state. “Not estimable (complete separation)” denotes transitions with zero exposed events or complete separation of the outcome, for which the RRR is not identifiable. Incident stroke was ascertainable only among wave-6 survivors, so its association with mortality transitions cannot be estimated."),
};
const F = {};
for (const fig of content.figures) {
  const m = fig.legend.match(/^Figure (\d+)/);
  if (m) F["f" + m[1]] = () => figEls(fig);
}
function inlineAfter(text) {
  const out = [];
  const ins = (key, re, fn) => { if (!inserted.has(key) && re.test(text)) { inserted.add(key); out.push(...fn()); } };
  ins("f1", /Fig\.\s?1\b/, F.f1);
  ins("t1", /Table 1\b/, T.t1);
  ins("t2", /Table 2\b/, T.t2);
  ins("f2", /Fig\.\s?2\b/, F.f2);
  ins("t3", /Table 3\b/, T.t3);
  ins("f3", /Fig\.\s?3\b/, F.f3);
  ins("f4", /Fig\.\s?4[a-z]?\b/, F.f4);
  ins("t4", /Table 4\b/, T.t4);
  return out;
}

// ---- body blocks ----
let skipPrefix = true;
for (const b of content.blocks) {
  if (b.type === "h1") continue;                      // title rendered above
  if (skipPrefix && b.type === "p") continue;   // title-page metadata lives above
  if (b.type === "h2") { skipPrefix = false; children.push(h1(b.runs.map(r => r.t).join(""))); }
  else if (b.type === "h3") children.push(h2(b.runs.map(r => r.t).join("")));
  else {
    const text = b.runs.map(r => r.t).join("");
    children.push(bodyPara(b.runs));
    children.push(...inlineAfter(text));
  }
}
for (const k of ["f1","t1","t2","f2","t3","f3","f4","t4"])
  if (!inserted.has(k)) throw new Error("never cited in body: " + k);

const doc = new Document({
  features: { updateFields: false },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [
      para(run(content.running, { italics: true, color: "546E7A" }),
           { alignment: AlignmentType.CENTER })] }) },
    footers: { default: new Footer({ children: [
      para(new TextRun({ children: [PageNumber.CURRENT] }),
           { alignment: AlignmentType.CENTER })] }) },
    children,
  }],
});
fs.writeFileSync(outputPath, await Packer.toBuffer(doc));
