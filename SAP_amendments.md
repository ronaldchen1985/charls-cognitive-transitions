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
