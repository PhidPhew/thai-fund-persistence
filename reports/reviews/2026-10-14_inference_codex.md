# Independent review — inference design (OpenAI Codex, read-only, 2026-10-14)

Codex did not see Claude's proposal before answering and computed no real-data persistence statistic.
Outcome: adopted as Amendment 7; secondary AMC-level persistence reduced to descriptive only; power statement added.

---

ข้อเสนอหลักคือ เปลี่ยนจาก fund-level permutation/bootstrap เป็น AMC-clustered wild cluster bootstrap-t โดยให้ทั้ง 6 ปีและทุก family ใน AMC เดียวกันได้รับ bootstrap weight เดียวกัน วิธีนี้ยังทดสอบ statistic เดิม แต่ไม่แกล้งถือว่า family-year ทุกแถวเป็น independent observation

1. Primary test และ confidence interval
กำหนดสำหรับ family i, evaluation year y:

X_iy = 1: อยู่ top quintile ใน 36-month ranking window
Y_iy = 1: อยู่ top quintile ใน 12-month evaluation window
Y_iy = 0: ไม่อยู่ top รวมถึงปิด/ยกเลิกในปีนั้นตาม SEC register
a(i): AMC ของ family
Primary estimate เดิมคงไว้:

P̂ = Σ(X_iy · Y_iy) / Σ X_iy

Null expectation ต้องแก้ให้ชัด
มีความไม่สอดคล้องเล็กน้อยใน preregistration: ถ้าจัด evaluation quintile เฉพาะ survivors แล้วนับ closures เป็น 0 โอกาสภายใต้ within-year permutation จะไม่เท่ากับ 20% เสมอ

ให้ล็อกล่วงหน้าว่า

p_0y = K_y / N_y

โดย N_y คือ ranking cohort ต้นปี รวม closures และ K_y คือจำนวนสมาชิก cohort ที่ได้ evaluation top-quintile จริง ๆ ดังนั้นนี่คือ exact expectation ของ within-year random matching ภายใต้ fixed margins ส่วน pooled null คือ

P̂_0 = Σ_y (n_1y · p_0y) / Σ_y n_1y,  โดย n_1y = Σ_i X_iy

ถ้าสร้าง evaluation quintile จาก cohort ทั้งหมดรวม closures จน K_y/N_y ≈ 20% อยู่แล้ว ทั้งสองนิยามแทบตรงกัน แต่ต้องระบุ algorithm และ rounding rule ก่อนเห็นผล

ผมแนะนำให้ทดสอบ

H_0: Δ ≤ 0,  Δ = Σ X_iy (Y_iy − p_0y) / Σ X_iy

นี่เป็น cluster-robust analogue ของ permutation test เดิม ส่วนการทดสอบ P̂ > 0.20 โดยตรงให้รายงานเป็น secondary "absolute 20% benchmark"; เมื่อมี closures มันมัก conservative กว่า randomization null

ขั้นตอน implementation ที่ควร pre-register
ใช้เฉพาะแถว X=1 แล้วตั้ง pseudo-outcome D_iy = Y_iy − p_0y
Estimate intercept ของ D; intercept คือ Δ̂
Cluster ที่ comp_name_en หรือ corporate AMC group ที่ freeze ไว้
ใช้ restricted wild cluster bootstrap-t, Webb six-point weights, 99,999 draws, fixed seed
Bootstrap weight หนึ่งค่าต่อ AMC และใช้ค่าเดียวกันกับทุก family และทุกปี 2020–2025 ของ AMC นั้น ห้าม draw แยก AMC-year
Studentization ใช้ CR2 small-sample correction; one-sided p<0.05
รายงานจำนวน contributing AMCs, cluster leverage, สัดส่วนของ top observations ที่มาจาก AMC ใหญ่สุด และ leave-one-AMC-out estimates
CI ของ P̂: invert two-sided 95% wild cluster bootstrap-t test บนช่วง 0 ≤ P ≤ 1 ด้วย cluster เดิม ไม่ใช้ ordinary fund bootstrap
ควรรายงาน CR2/Satterthwaite result และ Rademacher wild-bootstrap result เป็น robustness แต่กำหนด Webb WCR เป็น decision test เพียงตัวเดียวล่วงหน้า

ไม่ควรใช้ two-way clustering โดย AMC และ year เป็น primary เพราะมี year clusters เพียง 6 กลุ่ม ซึ่งน้อยเกินไปสำหรับ reliable year-cluster inference

2. Secondary tests ที่จำเป็น
Within-AMC family persistence
ประมาณ linear probability model:

Y_iay = η_ay + β_W · X_iay + ε_iay

โดย η_ay คือ AMC×year fixed effects ใช้เฉพาะ AMC-year cells ที่มีทั้ง X=0 และ X=1, และทำ WCR ที่ AMC

คำถามที่ตอบคือ: "ใน AMC เดียวกันและปีเดียวกัน family ที่เคย top ทำได้ดีกว่า sibling families หรือไม่?" จึงตัด house-level performance/style ออก ต่างจาก primary ซึ่งรวม house persistence เป็นส่วนหนึ่งของ signal

AMC-level persistence
สำหรับแต่ละ AMC-year กำหนด:

R_ay: สัดส่วน family ใน AMC ที่เป็น prior top
E_ay: สัดส่วนที่เป็น evaluation top โดย closures เป็น 0
Regress E_ay บน R_ay พร้อม year fixed effects, ให้ AMC เท่ากันใน estimand และ cluster ตาม AMC

คำถามที่ตอบคือ: "ทั้ง house มี winners ต่อเนื่องหรือไม่?" ไม่ใช่ "family เดิมยังเก่งอยู่หรือไม่" Power จะต่ำและควรถือเป็น explanatory secondary

Temporal stability diagnostic
รายงาน Δ̂_y แยก 6 ปี และ pooled leave-one-year-out ทั้งหกชุด ไม่ใช้ผลนี้เป็นการทดสอบเพิ่มเติม แต่ใช้ดูว่าผล pooled ถูกขับด้วยปีเดียวหรือไม่

Spearman และ top-vs-bottom spread ที่มีอยู่ใน preregistration ควรใช้ AMC-clustered inference เช่นกัน และประกาศเป็น secondary/exploratory; ถ้าจะให้ inferential claims หลายตัว ควรใช้ Holm adjustment ภายใน secondary family โดยไม่กระทบ primary alpha

3. Sample structure และ power
จากข้อมูลที่ตรวจแบบไม่คำนวณ performance outcome:

272 projects → 239 primary families → 22 AMCs
family_pairs.csv มี 42 core links และ 21 gray pairs
เมื่อกำหนด rankable ว่ามี r_tr ครบ 36 เดือนติดกัน จำนวน families ที่ผมนับได้คือ 126, 164, 177, 186, 198, 185 ในปี 2020–2025
มีเพียง 17–20 AMCs ต่อปี
AMC ใหญ่สุดมี 22–27 rankable families หรือประมาณ 13.4%–17.5% ของปีนั้น
สาม AMC ใหญ่สุดรวมประมาณ 31.2%–36.5%
HHI-implied effective AMC count มีเพียง 11.2–13.7
ตัวเลข rankable ต่ำกว่า provisional 168–226 ใน Amendment 5 เพราะการตรวจนี้ใช้ exact 36 consecutive r_tr และ primary family collapse แล้ว จึงควร reconcile กับ G3 implementation ก่อนล็อก amendment สุดท้าย โดยไม่ต้องดู alpha

จำนวน prior-top observations รวมจะอยู่ราว 204–210 เท่านั้น ไม่ใช่ผลรวม family-years ทั้งหมด หาก independent จริง standard error ใกล้ √(0.2·0.8/210) = 2.8 percentage points และ 80% power ต้องมีจริงประมาณ 27% แทน 20% แต่เมื่อมี clustering effective sample size อาจเหลือประมาณ 60–110 ทำให้ threshold สำหรับ 80% power ขยับไปแถว 30%–33% หรือสูงกว่า

Synthetic stress simulation
ผมใช้เฉพาะ AMC sizes ข้างต้น ไม่ใช้ real ranks หรือ real alphas:

exact 20% top quota ในแต่ละปี
latent within-AMC correlation ρ = 0.25
house shocks คงอยู่ตลอด 6 ปี
ranking และ evaluation house shocks independent กันภายใต้ H0
2,000 replications; Webb WCR 1,999 draws ต่อ replication
ผลโดยประมาณ:

H0: mean P = 20.3%; fund-level permutation approximation reject ผิด 11.8% ขณะที่ AMC-WCR reject 0.2%
H1 mean P = 26.2%: AMC-WCR power 11.4%
H1 mean P = 33.0%: power 58.3%
H1 mean P = 39.7%: power 90.1%
นี่เป็น intentionally severe stress design; WCR ค่อนข้าง conservative มาก จึงไม่ใช่ power forecast ที่แม่นยำ แต่แสดงชัดว่า "ไม่ reject" ยังเข้ากันได้กับ economically meaningful persistence และ naive fund permutation มี size distortion สูงได้

Descriptive check อีกชุดหนึ่งสนับสนุนเหตุผลในการ cluster: สำหรับ static one-representative-per-family และ monthly CAPM residuals ปี 2017–2025 คู่ใน AMC เดียวกันมี median correlation 0.354 เทียบกับ 0.186 ระหว่าง AMC; IQR เท่ากับ 0.168–0.579 และ 0.067–0.319 ตามลำดับ

4. Assumptions และ limitations
สมมติฐานหลักของแบบทดสอบนี้คือ:

AMCs เป็น independent clusters หลังควบคุม calendar year; ความสัมพันธ์ทุกชนิดภายใน AMC และข้ามปีได้รับอนุญาต
AMC mapping สะท้อน corporate group ที่แท้จริงและไม่เปลี่ยนแบบผิดกลุ่มจาก merger/rebrand/sub-advisor
จำนวน clusters ราว 20 เพียงพอสำหรับ CR2/WCR approximation แม้ cluster sizes ไม่เท่ากัน
Year-specific fixed-margin null เป็น exchangeable ระหว่าง families ภายใต้ H0
Rule สำหรับ Registered funds ที่ evaluation data ขาดต้องล็อกก่อนผล เช่น missing ไม่เท่ากับ closure
CAPM alpha กับ SCBSET วัด performance concept ที่ต้องการจริง
Failure modes สำคัญ:

AMCs อาจไม่ independent เพราะถือหุ้น/style เหมือนกัน ใช้ external sub-advisor เดียวกัน หรือมี industry-wide herding
Fixed quintile quota สร้าง weak negative dependence ข้าม AMC ซึ่ง cluster sandwich ไม่จำลองแบบ exact
ผลอาจมาจาก omitted factor exposure เช่น size/value/momentum ไม่ใช่ skill
Payout allocation, flagged NAV-only years, unresolved class lineage และ family misclassification อาจสร้าง persistence เชิง measurement
มีเพียง 6 evaluation years จึงแยก structural persistence จาก regime-specific luck ได้ยาก
Dominant AMC เพียงแห่งเดียวอาจขับผล แม้ clustered p-value จะผ่าน
Binary top-quintile statistic ทิ้งข้อมูลจำนวนมากและมี power ต่ำ
ข้อความ limitation ที่ควรเขียนอย่างชัดเจน:

หน่วยอิสระเชิง inference ที่เหมาะสมคือ AMC ไม่ใช่ family-year; ตัวอย่างมีเพียง 17–20 AMCs ต่อปีและ 6 evaluation years โดย effective AMC count ราว 11–14 ดังนั้นการไม่ปฏิเสธ H0 ไม่ได้ตัด persistence ที่มีนัยทางเศรษฐกิจ และการปฏิเสธ H0 แสดง predictive performance ระดับ fund/AMC ภายใต้ CAPM ไม่ใช่หลักฐาน causal ของ individual manager skill.

5. AMC-level persistence ควรนับหรือไม่
สำหรับคำถามที่แก้ตาม Amendment 4 เป็น fund-level performance persistence ควรนับ AMC-level persistence เป็น signal: นักลงทุนที่เลือก fund ได้รับประโยชน์จาก house research process, risk control หรือ organizational skill จริง แม้ไม่ได้มาจาก individual manager

แต่ไม่ควรเรียกว่า "manager skill persistence" และยังอาจเป็น persistent style exposure หรือ common measurement error

ดังนั้น primary design:

cluster ที่ AMC เพื่อไม่ให้หลาย funds ใน house เดียวกันเพิ่ม precision เทียม
แต่ไม่ใส่ AMC×year fixed effects จึงไม่ลบ house persistence ออกจาก effect
ส่วน within-AMC secondary แยกให้เห็นว่า persistence เหลืออยู่ในระดับ family หรือไม่ และ AMC-level secondary ระบุว่า signal มาจากทั้ง house เพียงใด

สิ่งที่ตรวจแล้วและยังไม่ได้ตรวจ
ตรวจจาก preregistration.md, reports/g2_series_summary.md, configs และ processed returns แล้ว:

family/AMC counts, core/gray counts
rankable-family counts ตาม exact 36-month coverage
AMC size imbalance และ effective cluster counts
monthly CAPM-residual correlation structure
synthetic null size/power ข้างต้น
ไม่ได้ตรวจหรือคำนวณ:

real-data persistence statistic
transition matrix
real top-vs-bottom spread
real-data p-value
evaluation-year alpha ranks
median daily-return TE 0.49% โดยอิสระ เพราะ daily-return input ไม่ได้อยู่ในชุดที่ขออ่าน; ตรวจเพียงว่าข้อความนี้ถูกบันทึกใน Amendment 6
ไม่มีไฟล์ถูกสร้างหรือแก้ไข และ worktree ยังคง clean.