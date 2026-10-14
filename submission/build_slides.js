// Builds HIT140_A3_Group07_Slides.pptx from the project's Python outputs.
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(path.join(process.argv[2], "scripts/apply_theme.js"));

const FIG = path.join(__dirname, "..", "outputs", "figures");
const OUT = path.join(__dirname, "HIT140_A3_Group07_Slides.pptx");

const THEME = {
  name: "Pitch",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "16231D", lt1: "FFFFFF", dk2: "0B3D2E", lt2: "EEF3EF",
    accent1: "0B3D2E", accent2: "E0A800", accent3: "2E8B57", accent4: "9DB8A8",
    accent5: "C0392B", accent6: "5B6B63", hlink: "1F6F8B", folHlink: "5B6B63",
  },
};
const HEX = { pitch: "0B3D2E", gold: "E0A800", grass: "2E8B57", sage: "9DB8A8", ink: "16231D", muted: "5B6B63", grid: "DCE4DF", mist: "EEF3EF" };

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";           // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Predicting World Cup 2026 results with linear regression";
pres.author = "HIT140 Sydney Group 07";
const C = pres.SchemeColor;

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "DARK_TITLE",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.35, w: 8.8, h: 1.5,
      fontSize: 36, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.0, w: 8.8, h: 1.6,
      fontSize: 16, color: C.accent4, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75,
      fontSize: 26, bold: true, color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "HIT140 · Assessment 3 · Group 07", options: { x: 0.5, y: 5.2, w: 5, h: 0.3,
      fontSize: 10, color: C.accent6, margin: 0 } } },
  ],
  slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: C.accent6, align: "right" },
});

// ---------------------------------------------------------------- helpers
const T = (slide, text, o) => slide.addText(text, { isTextBox: true, margin: 0, fontSize: 14, color: C.text1, ...o });
const card = (slide, x, y, w, h, name, fill = C.background2) =>
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill },
    line: { color: fill }, objectName: name });
const stat = (slide, x, y, w, big, label, name, bigColor = C.text2) => {
  T(slide, big, { x, y, w, h: 0.75, fontSize: 40, bold: true, color: bigColor, fontFace: "Cambria", objectName: `${name} value` });
  T(slide, label, { x, y: y + 0.75, w, h: 0.5, fontSize: 12, color: C.accent6, objectName: `${name} label` });
};
const chartText = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
  titleFontFace: "+mn-lt", catAxisLabelColor: HEX.muted, valAxisLabelColor: HEX.muted, catAxisLabelFontSize: 11,
  valAxisLabelFontSize: 10, dataLabelFontSize: 10, dataLabelColor: HEX.ink, valGridLine: { color: HEX.grid, size: 0.5 },
  catGridLine: { style: "none" }, titleFontSize: 12, titleColor: HEX.ink };

// ================================================================ slides
// 1. Title
pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "DARK_TITLE", sectionTitle: "Introduction" });
s.addText("Predicting World Cup 2026 Results with Linear Regression", { placeholder: "title" });
s.addText([
  { text: "HIT140 Foundations of Data Science · Assessment 3 (Objective 2)", options: { breakLine: true } },
  { text: "Sydney Group 07 · [Member names and student IDs]" },
], { placeholder: "body" });
s.addNotes("Introduce the group and the two regression tasks from Objective 2.");

// 2. The two tasks
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Introduction" });
s.addText("Two questions, one tournament", { placeholder: "title" });
card(s, 0.5, 1.3, 4.35, 2.45, "Task 2.1 card");
T(s, "Linear Regression 2.1", { x: 0.8, y: 1.5, w: 3.8, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
T(s, "How big will the winning margin be?", { x: 0.8, y: 1.95, w: 3.8, h: 0.4, fontSize: 14, italic: true, color: C.accent6 });
stat(s, 0.8, 2.45, 1.7, "104", "matches (rows)", "2.1 rows");
stat(s, 2.6, 2.45, 2.0, "GD", "target: team1 − team2 goals", "2.1 target", C.accent2);
card(s, 5.15, 1.3, 4.35, 2.45, "Task 2.2 card");
T(s, "Linear Regression 2.2", { x: 5.45, y: 1.5, w: 3.8, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
T(s, "How many goals will a team score?", { x: 5.45, y: 1.95, w: 3.8, h: 0.4, fontSize: 14, italic: true, color: C.accent6 });
stat(s, 5.45, 2.45, 1.7, "208", "team-match rows", "2.2 rows");
stat(s, 7.25, 2.45, 2.0, "Goals", "target: goals scored", "2.2 target", C.accent2);
T(s, "Both models use exactly 8 explanatory variables, all known before kick-off. 48 teams · 308 goals · champions Spain.",
  { x: 0.5, y: 4.1, w: 9.0, h: 0.6, fontSize: 14, color: C.text1 });
s.addNotes("Explain the two targets and the 104/208 row requirement from the brief.");

// 3. Pipeline
pres.addSection({ title: "Data" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Data" });
s.addText("From raw results to leak-free features", { placeholder: "title" });
const steps = [
  ["1", "Collect", "Scores for 104 matches, FIFA ranking (11 Jun), Transfermarkt values, ages, WC history"],
  ["2", "Validate", "Group scores rebuild all 12 official tables; knockout scores confirmed by ≥2 sources"],
  ["3", "Engineer", "Form uses only matches played earlier; team1 − team2 differences for 2.1"],
  ["4", "Model", "OLS, backward elimination, 80/20 split + 20× repeated 10-fold CV"],
];
steps.forEach(([n, head, body], i) => {
  const x = 0.5 + i * 2.33;
  card(s, x, 1.35, 2.13, 3.2, `Step ${n} card`);
  s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 1.6, w: 0.6, h: 0.6, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `Step ${n} badge` });
  T(s, n, { x: x + 0.25, y: 1.6, w: 0.6, h: 0.6, fontSize: 20, bold: true, color: C.background1, align: "center", valign: "middle" });
  T(s, head, { x: x + 0.25, y: 2.35, w: 1.7, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
  T(s, body, { x: x + 0.25, y: 2.8, w: 1.7, h: 1.6, fontSize: 12, color: C.text1, valign: "top" });
});
s.addNotes("Stress the brief's rule: only information available before the match. Form features use cumulative sums minus the current match.");

// 4. Variables
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Data" });
s.addText("The 8 explanatory variables", { placeholder: "title" });
const head = (t) => ({ text: t, options: { bold: true, color: HEX.pitch, fill: { color: HEX.mist } } });
const rows = [
  [head("Concept"), head("LR 2.1 (team1 − team2)"), head("LR 2.2 (team view)")],
  ["Strength ranking", "fifa_rank_diff", "fifa_rank, opp_fifa_rank"],
  ["Squad value", "log_value_ratio", "log_market_value, opp_log_market_value"],
  ["Squad age", "avg_age_diff", "—"],
  ["Home continent", "host_diff", "is_host"],
  ["Experience / pedigree", "wc_experience_diff, elite_conf_diff", "—"],
  ["Fatigue / stage", "rest_days_diff", "is_knockout"],
  ["Tournament form so far", "form_gd_pg_diff", "form_gf_pg, opp_form_ga_pg"],
];
s.addTable(rows, { x: 0.5, y: 1.25, w: 9.0, colW: [2.4, 3.1, 3.5], fontSize: 12, fontFace: "Calibri",
  color: HEX.ink, border: { type: "solid", pt: 0.5, color: HEX.grid }, rowH: 0.42, valign: "middle", margin: 0.06 });
s.addNotes("Explain why each variable should matter before a match.");

// 5. LR2.1 EDA chart
pres.addSection({ title: "Regression 2.1" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Regression 2.1" });
s.addText("2.1: squad value and ranking move with goal difference", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Correlation with goal difference",
  labels: ["log_value_ratio", "fifa_rank_diff", "wc_experience_diff", "form_gd_pg_diff", "elite_conf_diff", "host_diff", "avg_age_diff", "rest_days_diff"],
  values: [0.662, -0.621, 0.533, 0.318, 0.316, 0.123, -0.081, 0.037] }],
  { x: 0.5, y: 1.2, w: 5.6, h: 3.8, barDir: "bar", chartColors: [HEX.pitch], showValue: true, dataLabelPosition: "outEnd",
    dataLabelFormatCode: "0.00", valAxisMinVal: -0.8, valAxisMaxVal: 0.8, showLegend: false, catAxisOrientation: "maxMin", catAxisLabelPos: "low",
    showTitle: true, title: "Pearson r with goal difference (104 matches)", ...chartText });
card(s, 6.4, 1.3, 3.1, 3.6, "VIF callout");
stat(s, 6.7, 1.5, 2.6, "7.4", "VIF of log_value_ratio: overlaps with FIFA rank (r = −0.79)", "VIF", C.accent2);
T(s, "Several variables carry the same 'team strength' signal, so not all can stay significant together.",
  { x: 6.7, y: 2.95, w: 2.6, h: 1.8, fontSize: 13, color: C.text1, valign: "top" });
s.addNotes("Correlations are strong for value, ranking and experience; collinearity explains later results.");

// 6. LR2.1 model
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Regression 2.1" });
s.addText("2.1: three variables survive elimination", { placeholder: "title" });
s.addImage({ path: path.join(FIG, "LR2.1_coefficients.png"), x: 0.4, y: 1.2, w: 5.4, h: 5.4 * 600 / 1040, objectName: "LR2.1 coefficient plot" });
const coefB = [["log_value_ratio", "+1.09", "per ln-unit (≈2.7× squad value)"], ["avg_age_diff", "+0.32", "per year older on average"], ["elite_conf_diff", "−0.71", "UEFA/CONMEBOL vs. others, given value"]];
coefB.forEach(([v, c, d], i) => {
  const y = 1.25 + i * 1.15;
  card(s, 6.1, y, 3.4, 1.0, `Model B coefficient ${v}`);
  T(s, c, { x: 6.3, y: y + 0.1, w: 1.2, h: 0.8, fontSize: 26, bold: true, fontFace: "Cambria", color: c.startsWith("−") ? C.accent5 : C.text2, valign: "middle" });
  T(s, [{ text: v, options: { bold: true, breakLine: true } }, { text: d }], { x: 7.5, y: y + 0.1, w: 1.9, h: 0.8, fontSize: 11, valign: "middle" });
});
T(s, "Model B: adjusted R² 0.480 (Model A, all 8 variables: 0.469). All p < 0.01.", { x: 0.5, y: 4.55, w: 9.0, h: 0.4, fontSize: 13, color: C.accent6 });
s.addNotes("Interpret coefficients holding others fixed; the negative confederation effect is not causal.");

// 7. LR2.1 evaluation
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Regression 2.1" });
s.addText("2.1: the simpler model predicts unseen matches better", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "CV RMSE (goals)", labels: ["Baseline (mean)", "Model A (8 vars)", "Model B (3 vars)"], values: [1.98, 1.53, 1.45] }],
  { x: 0.5, y: 1.2, w: 5.4, h: 3.8, barDir: "col", chartColors: [HEX.sage, HEX.grass, HEX.pitch], showValue: true, dataLabelPosition: "outEnd",
    dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 2.4, showLegend: false,
    showTitle: true, title: "Cross-validated RMSE, lower is better", ...chartText });
stat(s, 6.3, 1.4, 3.2, "0.50", "Model B test R² (Model A: 0.28)", "test R2");
stat(s, 6.3, 2.75, 3.2, "−27%", "error vs. predicting the average", "error cut", C.accent2);
T(s, "Residuals look normal (Shapiro–Wilk p = 0.60) with constant spread (Breusch–Pagan p = 0.15).",
  { x: 6.3, y: 4.05, w: 3.2, h: 0.9, fontSize: 12, color: C.text1, valign: "top" });
s.addNotes("Model A overfits: train R² 0.53 vs test 0.28. Model B generalises better.");

// 8. LR2.2 EDA
pres.addSection({ title: "Regression 2.2" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Regression 2.2" });
s.addText("2.2: goals are a small, skewed count", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "Team-match rows", labels: ["0", "1", "2", "3", "4", "5", "6", "7"], values: [55, 71, 39, 25, 10, 5, 2, 1] }],
  { x: 0.5, y: 1.2, w: 5.6, h: 3.8, barDir: "col", chartColors: [HEX.pitch], showValue: true, dataLabelPosition: "outEnd",
    showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 80, showTitle: true, title: "Goals scored by a team in a match (208 rows)", ...chartText });
stat(s, 6.4, 1.4, 3.1, "1.48", "mean goals per team per match", "mean goals");
stat(s, 6.4, 2.75, 3.1, "0.40", "strongest correlation (own squad value)", "max r", C.accent2);
T(s, "61% of rows are 0 or 1 goals, so one team's tally is much noisier than a match's margin.",
  { x: 6.4, y: 4.05, w: 3.1, h: 0.9, fontSize: 12, color: C.text1, valign: "top" });
s.addNotes("Right-skewed integer target: a challenge for linear regression assumptions.");

// 9. LR2.2 models
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Regression 2.2" });
s.addText("2.2: own value and opponent rank drive goals", { placeholder: "title" });
s.addChart(pres.charts.BAR, [{ name: "CV RMSE (goals)", labels: ["Baseline", "Model A", "Model B", "Model C (log)"], values: [1.37, 1.21, 1.19, 1.24] }],
  { x: 0.5, y: 1.2, w: 5.4, h: 3.8, barDir: "col", chartColors: [HEX.sage, HEX.grass, HEX.pitch, HEX.gold], showValue: true,
    dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 1.6, showLegend: false,
    showTitle: true, title: "Cross-validated RMSE, lower is better", ...chartText });
const coef22 = [["+0.45", "goals per ln-unit of own squad value"], ["+1.0", "goal vs. an opponent ranked 50 places lower"]];
coef22.forEach(([c, d], i) => {
  const y = 1.3 + i * 1.3;
  card(s, 6.2, y, 3.3, 1.1, `Model B effect ${i + 1}`);
  T(s, c, { x: 6.4, y: y + 0.15, w: 1.1, h: 0.8, fontSize: 26, bold: true, fontFace: "Cambria", color: C.text2, valign: "middle" });
  T(s, d, { x: 7.5, y: y + 0.15, w: 1.9, h: 0.8, fontSize: 12, valign: "middle" });
});
T(s, "Model B keeps 2 of 8 variables (adj. R² 0.261 vs. 0.267 for A) and is best in cross-validation.",
  { x: 6.2, y: 3.95, w: 3.3, h: 1.0, fontSize: 12, color: C.text1, valign: "top" });
s.addNotes("Model C = log(1+goals) target, back-transformed. Best on the single split (test R² 0.25) but not in CV.");

// 10. LR2.2 diagnostics
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Regression 2.2" });
s.addText("2.2: the residuals reveal the model's limits", { placeholder: "title" });
s.addImage({ path: path.join(FIG, "LR2.2_diagnostics.png"), x: 0.5, y: 1.15, w: 9.0, h: 9.0 * 500 / 1440, objectName: "LR2.2 diagnostics" });
T(s, [
  { text: "Striped residuals and failed checks (Shapiro–Wilk p = 0.001, Breusch–Pagan p < 0.001) come from an integer target.", options: { bullet: true, breakLine: true } },
  { text: "The log(1 + goals) Model C improves normality (p = 0.021) but not cross-validated error.", options: { bullet: true, breakLine: true } },
  { text: "Next step beyond this unit: Poisson regression for count data.", options: { bullet: true } },
], { x: 0.5, y: 4.4, w: 9.0, h: 0.75, fontSize: 13, paraSpaceAfter: 2, valign: "top" });
s.addNotes("Discuss assumptions and the improvement attempt honestly.");

// 11. Conclusion
pres.addSection({ title: "Conclusion" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Conclusion" });
s.addText("What we learned", { placeholder: "title" });
const takeaways = [
  ["Squad value wins", "The most consistent pre-match predictor in both models."],
  ["Margins beat tallies", "2.1 explains ~48% of variance; 2.2 only ~26%."],
  ["Simpler generalises", "Backward elimination cut error on unseen data in both tasks."],
];
takeaways.forEach(([h, b], i) => {
  const x = 0.5 + i * 3.07;
  card(s, x, 1.3, 2.86, 1.55, `Takeaway ${i + 1}`, C.accent1);
  T(s, h, { x: x + 0.25, y: 1.5, w: 2.4, h: 0.45, fontSize: 17, bold: true, color: C.accent2 });
  T(s, b, { x: x + 0.25, y: 2.0, w: 2.4, h: 1.0, fontSize: 13, color: C.background1, valign: "top" });
});
T(s, "Limitations", { x: 0.5, y: 3.2, w: 9.0, h: 0.35, fontSize: 15, bold: true, color: C.text2 });
T(s, [
  { text: "Small samples (104 / 208 rows); single test split varies, so CV is reported too", options: { bullet: true, breakLine: true } },
  { text: "Form = 0 before each team's first match; squad values snapshot from 18 June", options: { bullet: true, breakLine: true } },
  { text: "Paired rows in 2.2 are not independent; FIFA rank is ordinal", options: { bullet: true } },
], { x: 0.5, y: 3.6, w: 9.0, h: 1.2, fontSize: 13, paraSpaceAfter: 3, valign: "top" });
s.addNotes("Close with the three takeaways and limitations; invite questions.");

pres.writeFile({ fileName: OUT }).then(async () => {
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
});
