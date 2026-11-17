# SAP Amendments and Analysis Log (2026-11-17)

记录执行过程中对 SAP v1.0 的偏离与理由（均在结果出炉前因数据/数值原因决定）：

1. **语言域条目**：W6 无动物命名题（2018 有），语言域改用两波共有的 MMSE 条目（命名/复述/阅读/三步指令/书写）。已在 SAP 预指定偏差中声明。
2. **执行功能域**：2018 数列题为自适应 block 且仅存原始答案，跨波不可比；执行域仅用连减 7（0–5 正确数），放弃数列题。
3. **死亡时间处理**：精确死亡日期仅 59 例（2020 Exit）；其余按区间中点近似。`deathexact` 在全样本数值溢出，死亡按面板观测处理（SAP 原计划的敏感性方案转正）。
4. **协变量调整的主框架**：两波面板 + 多协变量全转移 msm 似然面脊化（Hessian 非正定），改用**基线状态分层多项 logit** 报告调整后 RRR（全协变量集）；msm 空模型报告转移强度/停留时间/5 年概率（收敛良好、CI 完整）。msm 协变量模型作为补充（单变量版均收敛，见 output/m_uni_*.rds）。
5. **吸烟**：2018 缺失 37.5%、W6 回填后仍 ~38%，从调整模型剔除，仅描述性报告。
6. **年龄**：出生年取 ba004_w3_1（户口登记，覆盖 19,494），ba002_1 仅 4,030 人；age>105 设为缺失。
7. **分析样本**：msm 与多项 logit 均为完整病例样本 n=8,178（2018 状态 + W6 结局/死亡 + 协变量齐全）。
8. **敏感性分析**：IQCODE 痴呆切点 3.48 / 3.9 已跑（run_sens.log），核心卒中关联方向与显著性一致。误分类校正 msm、ADL 支柱版定义未执行（时间预算），列为审稿期备选。

## 关键文件
- 数据构建：`code/build_dataset.py` → `output/analytic_panel.csv`, `output/covariates.csv`, `output/build_report.txt`
- 主分析：`code/analysis_msm2.R`（空模型）, `code/analysis_multinom.R`（RRR）, `code/sens_cutoffs.py` + `code/sens_multinom.R`（敏感性）
- 结果：`output/null_model_results.txt`, `output/multinom_rrr.csv`, `output/run_sens.log`, `output/table1_baseline.csv`
- 图：`output/fig1_transition_diagram.png`, `output/fig2_forest_stroke.png`

---

## 第二轮补记（2026-11-17，审稿后修订）

9. **基线样本量更正**：2018 访谈且 ≥60 岁 = **11,039**（非 11,043），不可分类 = **411**（非 415），排除 <60 岁 = 9,774。正文、流程图（fig1）已同步更正。原 11,043 为早期手工记录误差，build_report.txt 复核值为准。
10. **amendment 7 更正**：msm 空模型实际拟合于全分析面板 n=9,679（非 8,178）；8,178 仅为多项 logit 完整病例样本。
11. **amendment 8 更正**：误分类校正 msm **尝试过但不可识别**（两波面板，模型不收敛，见 run_misclass.log），并非"未执行"；已在正文 Limitations 第二条如实说明。
12. **SAP 未执行项如实登记**：SAP §4 敏感性 2（ADL 支柱版痴呆定义）与敏感性 3（informant 报告诊断敏感性）未执行——ADL 支柱已部分由 proxy 规则覆盖，informant 自报诊断与算法分类数据源重叠、增量有限；列为审稿期备选。
13. **SAP §5 协变量 residence 未构建**：城乡/居住变量在 SAP 中列出但数据构建阶段未生成（covariates.csv 无此列）；其与教育、户口高度相关，且非核心血管/心理社会变量，未纳入任何模型。
14. **语言域跨波等价性敏感性（SAP §4.1 预指定项）已执行**：`code/sens_language_domain.py`，2018 主分类 vs 含动物命名重分类，n=10,583 双重可分类，一致率 96.2%，Cohen's κ = 0.933（output/sens_language_domain.txt）。结果写入正文稳健性小节与 Supplementary Table S5。
15. **Table 2 分母改全分析面板**：观察转移矩阵由完整病例（n=8,178）改为全分析面板（n=9,679，analytic_panel.csv 每人首末行）；CIND→Normal 观察逆转率相应由 49.3% 更正为 45.4%，摘要、正文、fig4 同步更新。多项 logit 仍基于 8,178 完整病例。
16. **Table 1 删除吸烟行**：da059（ever smoked）仅 2018 刷新样本应答（分析样本缺失 38.5%，结构性缺失），从描述表删除并在 Methods 与表注说明；该变量从未进入任何模型，分析结论不受影响。
17. **多项 logit 完全分离行处理**：stroke_inc1→Death 三行 RRR=0 / 上界 0 或 1.6e139（幸存者结构所致的完全分离），Table 4 统一标注 "not estimable (complete separation)"。
18. **代理规则分类构成**：2018 年代理规则分类占 30.6%（3,257/10,628），W6 占 17.7%（1,552/8,790），双源两波完整 n=5,649——已写入正文。双源子样本全模型重估列入 P1 备选计划，本轮未执行。
19. **stage-dependence 正式检验（审稿后新增）**：按外部评审建议，用基线分层多项 logit 的结局水平系数 Wald 对比正式检验"痴呆进展 vs CIND 起病/逆转"的差异（`code/interaction_tests.R`，模型按 analysis_multinom.R 同一流程重拟合，复现 N=8,178）。6 个对比（stroke181/stroke_inc1/cesd101 各 2 个）全部不显著：未校正 p ≥ 0.33，BH 校正后 ≥ 0.48（output/interaction_tests.csv）。结论："stage-dependent" 仅为描述性模式，标题级 claim 已在摘要、正文、讨论降级为 "stage-graded / descriptive"；新增 Supplementary Table S6。多重比较控制在 6 个预设对比内，未做全协变量 × 全转移扫描。
