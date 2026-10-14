// Builds the Assessment 3 report TEMPLATE: layout, title block, figures and
// results tables are filled in; every paragraph of prose is a grey prompt the
// group replaces with its own writing (brief: report must be in own words).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, BorderStyle, ShadingType, HeadingLevel, LevelFormat,
} = require("docx");

const FIG = path.join(__dirname, "..", "outputs", "figures");
const FONT = "Calibri";
const PAGE_W = 11906 - 2 * 1021;   // A4 width minus 1.8 cm margins (DXA)
const GREY = "7F7F7F";

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: 20, ...o });
const p = (children, o = {}) => new Paragraph({ spacing: { after: 60, line: 240 }, children, ...o });
const prompt = (text) => p([run(`[Write in your own words: ${text}]`, { italics: true, color: GREY })]);
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 120, after: 60 },
  children: [new TextRun({ text: t, font: FONT, size: 24, bold: true, color: "1F3864" })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 80, after: 40 },
  children: [new TextRun({ text: t, font: FONT, size: 21, bold: true, color: "2E5395" })] });
const caption = (t) => p([run(t, { italics: true, size: 17 })], { alignment: AlignmentType.CENTER });

const img = (file, wPx) => {
  const buf = fs.readFileSync(path.join(FIG, file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);   // PNG header dims
  return new ImageRun({ type: "png", data: buf,
    transformation: { width: wPx, height: Math.round(wPx * h / w) } });
};

const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const line = { style: BorderStyle.SINGLE, size: 4, color: "A6A6A6" };

function figRow(cells) {   // side-by-side figures in a borderless table
  const colW = Math.floor(PAGE_W / cells.length);
  return new Table({
    width: { size: colW * cells.length, type: WidthType.DXA }, columnWidths: cells.map(() => colW),
    borders: noBorders,
    rows: [new TableRow({ children: cells.map(([f, w]) => new TableCell({
      width: { size: colW, type: WidthType.DXA }, borders: noBorders,
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [img(f, w)] })] })) })],
  });
}

function dataTable(header, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, i, isHead) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    margins: { top: 20, bottom: 20, left: 70, right: 70 },
    shading: isHead ? { fill: "DCE6F2", type: ShadingType.CLEAR, color: "auto" } : undefined,
    borders: { top: line, bottom: line, left: line, right: line },
    children: [new Paragraph({ alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
      children: [run(String(t), { size: 16, bold: isHead })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: header.map((t, i) => cell(t, i, true)) }),
           ...rows.map((r) => new TableRow({ children: r.map((t, i) => cell(t, i, false)) }))],
  });
}

// ---------------------------------------------------------------- content
const members = [1, 2, 3, 4].map((i) => [`[Member ${i} full name]`, "[Student ID]"]);

const varRows = [
  ["FIFA ranking", "fifa_rank_diff (team1 − team2)", "fifa_rank, opp_fifa_rank", "FIFA ranking, 11 Jun 2026"],
  ["Squad market value", "log_value_ratio = ln(V1/V2)", "log_market_value, opp_log_market_value", "Transfermarkt"],
  ["Average squad age", "avg_age_diff", "—", "RotoWire"],
  ["Host nation", "host_diff (+1/0/−1)", "is_host", "CAN, MEX, USA"],
  ["World Cup experience", "wc_experience_diff", "—", "Wikipedia"],
  ["Confederation strength", "elite_conf_diff (UEFA/CONMEBOL)", "—", "FIFA"],
  ["Rest days", "rest_days_diff", "—", "Match schedule"],
  ["Tournament form (earlier matches only)", "form_gd_pg_diff", "form_gf_pg, opp_form_ga_pg", "Match results"],
  ["Stage", "—", "is_knockout", "Match schedule"],
  ["Target", "goal_difference (104 rows)", "goals (208 rows)", ""],
];

const f2 = (x) => x.toFixed(2), f3 = (x) => x.toFixed(3);
const evalRows = [
  ["Explanatory variables used", "8", "3", "8", "2", "8"],
  ["R² / adj. R² (all rows)", "0.511 / 0.469", "0.495 / 0.480", "0.295 / 0.267", "0.268 / 0.261", "0.272 / 0.242 (log)"],
  ["F-test p-value", "<0.001", "<0.001", "<0.001", "<0.001", "<0.001"],
  ["Test R² (80/20 split)", f3(0.284), f3(0.495), f3(0.149), f3(0.180), f3(0.247)],
  ["Test RMSE / MAE", "1.78 / 1.44", "1.50 / 1.16", "1.02 / 0.81", "1.01 / 0.78", "0.96 / 0.73"],
  ["Test NRMSE", f3(0.223), f3(0.187), f3(0.205), f3(0.201), f3(0.193)],
  ["Baseline (mean) test RMSE", f2(2.107), f2(2.107), f2(1.179), f2(1.179), f2(1.179)],
  ["10-fold CV (×20) R²", f3(0.261), f3(0.336), f3(0.104), f3(0.142), f3(0.093)],
  ["10-fold CV RMSE (baseline)", "1.53 (1.98)", "1.45 (1.98)", "1.21 (1.37)", "1.19 (1.37)", "1.24 (1.37)"],
  ["Shapiro–Wilk p / Breusch–Pagan p", "0.60 / 0.15", "", "0.001 / <0.001", "", "0.021 / –"],
];

const coefRows = [
  ["2.1-B", "log_value_ratio", "1.089", "[0.841, 1.336]", "<0.001", "0.90"],
  ["2.1-B", "avg_age_diff", "0.321", "[0.101, 0.540]", "0.005", "0.24"],
  ["2.1-B", "elite_conf_diff", "−0.706", "[−1.231, −0.180]", "0.009", "−0.26"],
  ["2.2-B", "log_market_value", "0.448", "[0.312, 0.585]", "<0.001", "0.39"],
  ["2.2-B", "opp_fifa_rank", "0.020", "[0.013, 0.027]", "<0.001", "0.33"],
];

const children = [
  // ---- Title block
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [
    new TextRun({ text: "[Your report title, e.g. Predicting FIFA World Cup 2026 Match Outcomes with Linear Regression]",
      font: FONT, size: 28, bold: true, color: "1F3864" })] }),
  p([run("HIT140 Foundations of Data Science · Assessment 3 · Sydney Group 07 · Code: [GitHub/OneDrive URL]",
    { size: 18 })], { alignment: AlignmentType.CENTER }),
  dataTable(["Name", "Student ID", "Name", "Student ID"],
    [[...members[0], ...members[1]], [...members[2], ...members[3]]],
    [3166, 1766, 3166, 1766]),

  h1("1. Introduction and Data"),
  prompt("aim of Objective 2 and the two regression tasks; data sources (see data/raw/SOURCES.md); how 104/208 rows were compiled; the 'known before kick-off' rule and how it was enforced; score convention (extra time counted, shoot-out = draw); validation against the 12 group tables."),
  caption("Table 1. Explanatory variables (all known before kick-off)"),
  dataTable(["Concept", "LR 2.1 variable (match level)", "LR 2.2 variable (team level)", "Source"],
    varRows, [2300, 2650, 2850, 2064]),

  h1("2. Linear Regression 2.1 — Goal Difference"),
  h2("2.1 Exploration and model building"),
  prompt("target distribution (mean 0.48, SD 2.02); strongest correlations (value ratio r = 0.66, rank r = −0.62); collinearity between value and rank (r = −0.79, VIF 7.4); Model A with all 8 variables; backward elimination to Model B."),
  figRow([["LR2.1_correlation.png", 300], ["LR2.1_coefficients.png", 330]]),
  caption("Figure 1. LR 2.1 — correlation matrix (left) and standardised coefficients of Model A with 95% CIs (right)"),
  h2("2.2 Evaluation and interpretation"),
  prompt("compare Model A vs B using Table 2 (overfitting of A; B better on unseen data; both beat the mean baseline); interpret the Model B coefficients in Table 3 in plain football terms; discuss the negative elite_conf_diff carefully (no causal claim); residual checks (assumptions reasonably met)."),

  caption("Table 2. Model comparison (A = all 8 variables; B = backward elimination, p < 0.05; C = A with log(1 + goals) target, predictions back-transformed)"),
  dataTable(["Metric", "2.1 Model A", "2.1 Model B", "2.2 Model A", "2.2 Model B", "2.2 Model C (log)"],
    evalRows, [2614, 1400, 1400, 1400, 1400, 1650]),
  caption("Table 3. Final (Model B) coefficients"),
  dataTable(["Model", "Variable", "Coef.", "95% CI", "p-value", "Std. coef."],
    coefRows, [1100, 2400, 1300, 2364, 1350, 1350]),
  h1("3. Linear Regression 2.2 — Goals Scored by a Team"),
  h2("3.1 Exploration and model building"),
  prompt("target is a right-skewed count (mean 1.48, 0–7 goals); why both own and opponent variables are needed; weaker correlations than 2.1; VIF all < 3.2; Model A and backward elimination to Model B."),
  figRow([["LR2.2_target_distribution.png", 255], ["LR2.2_coefficients.png", 330]]),
  caption("Figure 2. LR 2.2 — distribution of goals per team per match (left) and standardised coefficients of Model A (right)"),
  h2("3.2 Evaluation and interpretation"),
  prompt("compare Model A vs B (Table 2); interpret Model B (Table 3), e.g. what a 50-place weaker opponent means; diagnostics show non-normal, heteroscedastic residuals because goals are counts (Figure 3); Model C (log(1 + goals) target) as an improvement attempt: better residual normality and test-split error, but no gain in cross-validation; Poisson regression as future work."),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [img("LR2.2_diagnostics.png", 560)] }),
  caption("Figure 3. LR 2.2 Model A — residuals vs fitted, normal Q-Q plot, and actual vs predicted on the test set"),


  h1("4. Discussion and Conclusion"),
  prompt("why 2.1 explains more variance than 2.2; squad value as the most consistent predictor; limitations (small n, Transfermarkt snapshot date, form = 0 in first match, arbitrary team1/team2 order, paired rows in 2.2, ordinal ranking, secondary sources for knockout scores); improvements and conclusion."),

  h1("References"),
  prompt("list the sources from data/raw/SOURCES.md in the referencing style your unit requires."),
];

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1021, bottom: 1021, left: 1021, right: 1021 } } },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(__dirname, "HIT140_A3_Group07_Report_TEMPLATE.docx");
  fs.writeFileSync(out, buf);
  console.log("wrote", out);
});
