import fs from "node:fs";
import { AlignmentType, Document, Packer, Paragraph, TextRun, HeadingLevel } from "docx";

const font = { ascii: "Times New Roman", hAnsi: "Times New Roman", cs: "Times New Roman", eastAsia: "SimSun" };
const run = (text, options = {}) => new TextRun({ text, font, size: 24, ...options });
const para = (children, options = {}) => new Paragraph({
  spacing: { after: 160, line: 400 },
  alignment: AlignmentType.JUSTIFIED,
  children: Array.isArray(children)
    ? children.map(c => (typeof c === "string" ? run(c) : c))
    : [typeof children === "string" ? run(children) : children],
  ...options,
});
const h = (text) => para(run(text, { bold: true }), { spacing: { before: 240, after: 120 }, alignment: AlignmentType.LEFT });

// ---------- Response to Editor ----------
const response = new Document({
  sections: [{
    children: [
      para(run("Response to Editorial Assessment", { bold: true, size: 30 }), { alignment: AlignmentType.LEFT, spacing: { after: 240 } }),
      para([run("Manuscript: ", { bold: true }), run("Cognitive state transitions and stage-graded stroke associations in older Chinese adults: a multi-state analysis of CHARLS 2018–2023")]),
      para([run("Submission ID: ", { bold: true }), run("7b2e054b-96c7-4fac-afb3-7c4e819d79bd")]),
      para([run("Corresponding author: ", { bold: true }), run("Yong Chen, Department of Neurology, Peking University Third Hospital, ronaldchen@bjmu.edu.cn")]),
      para([run("Date: ", { bold: true }), run("25 November 2026")]),
      para("Dear Ms Tope,"),
      para("Thank you for assessing our manuscript and for the opportunity to address the two points raised before peer review. We respond to each point below; the corresponding manuscript changes are summarised at the end of this letter. No changes to results, analyses, or conclusions were required."),

      h("Point 1. MMSE — license and proof of permission"),
      para([run("Response: ", { bold: true }), run("The authors did not administer, reproduce, or distribute the Mini-Mental State Examination (MMSE) in this study. All cognitive items derived from the MMSE were administered by the China Health and Retirement Longitudinal Study (CHARLS) as part of its standard survey protocol, under the oversight of the Peking University Institutional Review Board (IRB00001052-11015), with written informed consent obtained from all participants by the CHARLS study team. Our study is a secondary analysis of de-identified, publicly available CHARLS data files obtained under the CHARLS data-use agreement; the authors had no contact with participants and played no role in the selection, licensing, or administration of survey instruments.")]),
      para("MMSE-derived items as embedded in the CHARLS instrument have been used extensively in previously published CHARLS studies, including the cohort profile [11] and published analyses of cognitive impairment and dementia in CHARLS [5,6]. No MMSE content beyond the item-level responses present in the public CHARLS dataset is reproduced in our manuscript or its supplementary files."),
      para("As requested, we attach a formal statement covering the use of the MMSE and the survey instruments as an additional file (Additional file 2: Statement on the use of the MMSE and CHARLS survey instruments). We have also requested a confirmation letter from the CHARLS project team at the National School of Development, Peking University, and will forward it to the editorial office upon receipt. We are of course willing to obtain a licence from the copyright holder should the journal consider it necessary."),
      para([run("Manuscript change: ", { bold: true }), run("The Methods (Cognitive battery) now states explicitly that cognitive assessment used the standard CHARLS survey instrument, administered by trained CHARLS interviewers as part of the parent study, with provenance citations.")]),

      h("Point 2. Interview — provenance of the instrument"),
      para([run("Response: ", { bold: true }), run("No interview instrument was developed for this study. The participant interview used the standard CHARLS cognition instrument (orientation, episodic memory, executive function, language, and visuoconstruction items) that forms part of the published CHARLS survey, documented in the cohort profile [11] and in the CHARLS study instruments (https://charls.pku.edu.cn). Informant assessment used the short form of the Informant Questionnaire on Cognitive Decline in the Elderly (IQCODE), a published instrument [12]. The cognitive-state classification algorithm (education-stratified z-scores, domain cut-offs, IQCODE thresholds, and proxy rules) was pre-specified in our statistical analysis plan and follows conventions established in prior CHARLS publications [5,15].")]),
      para([run("Manuscript changes: ", { bold: true }), run("The Methods now states, in the Cognitive battery paragraph, that the instrument is the standard CHARLS survey instrument with no instrument developed for this study, and, in the Informant assessment paragraph, cites the published short-form IQCODE (new reference 12: Jorm AF, Psychol Med 1994;24:145–53).")]),

      h("Summary of changes"),
      para("1. Methods, Cognitive battery: added instrument provenance (standard CHARLS survey instrument; administered by CHARLS interviewers; no instrument developed for this study)."),
      para("2. Methods, Informant assessment: added citation to the published short-form IQCODE (Jorm 1994), inserted as new reference 12."),
      para("3. Additional file 2 uploaded: Statement on the use of the MMSE and CHARLS survey instruments."),
      para("We hope these clarifications address the editorial points, and we would be glad to provide anything further that would assist a swift move to peer review."),
      para("Sincerely,"),
      para("Yong Chen, MD (on behalf of all authors)\nDepartment of Neurology, Peking University Third Hospital\nNo. 49 North Garden Road, Haidian District, Beijing 100191, China\nronaldchen@bjmu.edu.cn"),
    ],
  }],
});

// ---------- Statement (additional file) ----------
const statement = new Document({
  sections: [{
    children: [
      para(run("Statement on the use of the Mini-Mental State Examination and CHARLS survey instruments", { bold: true, size: 28 }), { alignment: AlignmentType.LEFT, spacing: { after: 240 } }),
      para([run("Manuscript: ", { bold: true }), run("Cognitive state transitions and stage-graded stroke associations in older Chinese adults: a multi-state analysis of CHARLS 2018–2023")]),
      para([run("Submission ID: ", { bold: true }), run("7b2e054b-96c7-4fac-afb3-7c4e819d79bd")]),

      h("1. Nature of this study"),
      para("This study is a secondary analysis of de-identified, publicly available data from the China Health and Retirement Longitudinal Study (CHARLS), wave 4 (2018), the 2020 exit module, and wave 6 (2021–2023). The authors analysed existing survey records only; no participants were recruited, interviewed, or contacted by the authors, and no survey content was administered by the authors."),

      h("2. MMSE administration and licensing"),
      para("Cognitive items derived from the Mini-Mental State Examination (MMSE) were administered to CHARLS respondents by trained CHARLS interviewers as part of the standard CHARLS survey protocol, under the ethical approval of the Peking University Institutional Review Board (IRB00001052-11015) and with written informed consent from all participants. The CHARLS study team was solely responsible for the design, translation, licensing, and administration of its survey instruments."),
      para("The authors of the present manuscript did not administer, reproduce, or distribute the MMSE, and no MMSE content beyond the item-level responses present in the public CHARLS dataset is reproduced in the manuscript or its supplementary files. The Chinese-language MMSE items as embedded in the CHARLS instrument have been widely used in previously published CHARLS studies of cognitive impairment and dementia. The authors will promptly obtain any licence that the journal considers necessary from the relevant copyright holder."),

      h("3. Interview instruments"),
      para("No interview instrument was developed for this study. The participant interview used the standard CHARLS cognition instrument (orientation, episodic memory, executive function, language, and visuoconstruction items), documented in the CHARLS cohort profile (Zhao et al., Int J Epidemiol 2014;43:61–8) and in the CHARLS study instruments available at https://charls.pku.edu.cn. Informant assessment used the short form of the Informant Questionnaire on Cognitive Decline in the Elderly (IQCODE; Jorm AF, Psychol Med 1994;24:145–53). The cognitive-state classification algorithm was pre-specified in the study's statistical analysis plan and follows conventions established in prior CHARLS publications."),

      h("4. Ethics"),
      para("The CHARLS parent study received ethical approval from the Peking University Institutional Review Board (IRB00001052-11015), and all participants gave written informed consent. The secondary analysis of publicly available, de-identified CHARLS data was conducted under the CHARLS data-use agreement."),
      para(" ", { spacing: { after: 240 } }),
      para("Yong Chen, MD\nCorresponding author\nDepartment of Neurology, Peking University Third Hospital\nNo. 49 North Garden Road, Haidian District, Beijing 100191, China\nronaldchen@bjmu.edu.cn\n25 November 2026"),
    ],
  }],
});

const outDir = "D:/CHARLS/DementiaTransition_W6/submission";
const w1 = await Packer.toBuffer(response);
fs.writeFileSync(outDir + "/Response_to_Editor.docx", w1);
const w2 = await Packer.toBuffer(statement);
fs.writeFileSync(outDir + "/Additional_file_Statement_MMSE_instruments.docx", w2);
console.log("written");
