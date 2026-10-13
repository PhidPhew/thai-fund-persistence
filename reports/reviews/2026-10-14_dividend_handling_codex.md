# Independent review — dividend handling (OpenAI Codex, read-only, 2026-10-14)

Prompt: see conversation; Codex did not see Claude's proposal before answering.
Outcome: adopted as Amendment 5 with one change (fund-years without factsheet are flagged and kept, not dropped).

---

1. วิธีสร้าง monthly total-return series
ข้อเสนอหลักคือใช้ annual factsheet return เป็น hard annual constraint แล้วกระจายส่วนต่างลงรายเดือนแบบ timing-neutral แทนการพยายามเดาวันปันผลจาก NAV

ใช้ fund-family representative ตาม Amendment 1 และ chain เฉพาะ share class ที่เป็น verified หรือ probable ตาม Amendment 4

คำนวณ monthly price return จาก month-end last_val ของ class เดียวกัน และใช้ SCBSET แบบเดียวกัน

ดึง calendar-year return จาก performance.csv โดยต้องตรงทั้ง:

proj_id
fund_class_name
performance_type_desc == ผลตอบแทนกองทุนรวม
reference_period == ปีปฏิทิน
[ข้อเสนอ] เนื่องจาก annual values ถูกบันทึกซ้ำทุก monthly factsheet และมี transient mislabelling ให้ใช้ consensus/modal value หลังปัดเป็น 0.01pp ไม่ใช่ latest row โดยอัตโนมัติ ถ้าไม่มี unique mode ให้ใช้ค่าที่ stable อย่างน้อยสาม snapshots ติดต่อกันและทำ QC กับ NAV/YTD; ถ้ายังไม่ชัดให้ถือเป็น missing

สำหรับ fund i, ปี y, กระจาย annual correction เท่ากันใน log return ทั้ง 12 เดือน:

k_iy = [ log(1 + R_FS_iy) − Σ_{m=1..12} log(1 + r_NAV_im) ] / 12

r_TR_im = exp{ log(1 + r_NAV_im) + k_iy } − 1

วิธีนี้ทำให้ compounded monthly return เท่ากับ annual factsheet return พอดี โดยไม่ได้อ้างว่า dividend เกิดทุกเดือน; เป็น measurement convention ที่ไม่สร้าง market timing ขึ้นมาเอง

[ข้อเสนอ] QC rules:

ขาดเดือนใดเดือนหนึ่ง: fund-year ใช้ไม่ได้จนกว่าจะแก้ class lineage
annual correction ติดลบเกิน 0.05pp: ตรวจ date alignment, snapshot และ class
correction ติดลบเกิน 0.5% แบบ multiplicative และแก้ไม่ได้: ตัด fund-year นั้น ไม่สร้าง "negative dividend"
ห้ามเอา return ของ sibling class มาแทนตรง ๆ เว้นแต่มี verified lineage; same-project classes มี fee/payout differences จริง
ไม่ใช้ dividend_policy == N หรือ NAV detector เพียงอย่างเดียวเพื่อสมมติว่า return เป็น NAV-only
ใช้ year to date factsheet snapshots ปี 2023–2025 เป็น validation/sensitivity ไม่ใช่ primary series เพราะ cutoff ของบาง snapshots ไม่ตรง month-end อย่างสม่ำเสมอ

การจัดการ 2014–2016
[ข้อเสนอ] ไม่ impute dividends ในช่วงนี้สำหรับ primary analysis เนื่องจากไม่มี annual ground truth เพียงพอ การใช้ NAV-only, current dividend policy หรือ detector ล้วนสร้าง differential measurement error ที่อาจดูเหมือน persistence ได้

2. ควรเปลี่ยน pre-registered design หรือไม่
ควรเปลี่ยน ดังนี้:

sample return start: 2017-01
first ranking: 2020-01
primary evaluation years: 2020–2025
36-month ranking, January ranking, 12-month evaluation, SCBSET และ power rule คงเดิม
[ตรวจสอบแล้ว] Calendar-year factsheet coverage ใน universe มีเพียง 2 projects ต่อปีใน 2014, 2015 และ 2016 แต่เพิ่มเป็น 184, 207, 214, 229, 233, 231, 240, 243 และ 246 projects ในปี 2017–2025 ตามลำดับ

[ตรวจสอบแล้ว] ภายใต้การจับคู่ exact selected class และต้องมี monthly NAV ครบ 36 เดือน จำนวนที่อาจ rank ได้ในปี 2020–2025 คือประมาณ 132, 176, 192, 196, 219, 203 funds ก่อน family collapse และ unresolved QC จึงยังสูงกว่า threshold 80 ทุกปีในขั้นนี้

เหตุผลของ Amendment นี้เป็นเรื่อง measurement feasibility ไม่ใช่ผลการทดสอบ hypothesis: ช่วง 2014–2016 ไม่มีข้อมูลแก้ payout ที่เชื่อถือได้ และ missed payout ลดผลตอบแทนของ fund เดิมซ้ำ ๆ ซึ่งสร้าง false persistence ในทิศทางเดียวกับ H1 ได้

ควร lock เป็น Amendment 5 ลงวันที่ 2026-10-14 ก่อนคำนวณ transition matrix, persistence statistic หรือ p-value ผมไม่ได้คำนวณผลเหล่านั้นในการ review นี้

ชุดเดิม evaluation 2017–2019 อาจแสดงเป็น exploratory sensitivity ภายใต้ NAV-only/alternative imputations แต่ไม่ควรรวมใน primary pooled statistic ส่วน robustness ตั้งแต่ 2002 ไม่ควรเรียกว่า total-return robustness จนกว่าจะมีหลักฐาน accumulating class หรือ payout adjustment ที่เพียงพอ

3. Assumptions, failure modes, validation และ limitation
Assumptions
[สมมติฐาน] Calendar-year factsheet return ของ class ที่ตรงกันรวม distributions และเป็น annual total return ที่ถูกต้อง
[สมมติฐาน] การกระจาย annual correction เท่ากันใน log space ไม่ทำให้ fund ranking เปลี่ยนอย่างมีนัยสำคัญ
[สมมติฐาน] Verified/probable class lineage เป็น economic continuation ของ series เดิม
[ตรวจสอบแล้วจากรายงาน] SCBSET ไม่มีหลักฐาน payout ในช่วง 2001–2026 และมี monthly observations ครบ 12 เดือนทุกปี 2014–2025
Failure modes
Snapshot บางเดือนเลื่อน annual labels หรือแก้ค่าผิดชั่วคราว
Annual return จับคู่ผิด share class
Dividend timing สัมพันธ์กับ market return ทำให้ uniform allocation กระทบ beta และ alpha
Factsheet coverage ที่ขาดอาจไม่ random โดยเฉพาะ fund ที่ปิดหรือเปลี่ยนชื่อ class
Class lineage ที่ยังไม่เสร็จอาจทำให้ registered fund ดูเหมือนข้อมูลหาย
Annual values ปัดเศษและอาจใช้ valuation cutoff ต่างจาก SEC month-end NAV
Validation ที่ควรทำก่อน headline analysis
Annual closure: compounded synthetic monthly return ต้องตรง factsheet annual return ภายใน numerical tolerance
Snapshot QC: ใช้ modal/stable consensus และแสดงจำนวน conflicting keys
Non-payout check: annual factsheet กับ NAV-only ควรตรงประมาณ ±0.05pp
Timing sensitivity:
uniform log allocation
correction ทั้งหมดในเดือนที่ fund-minus-benchmark residual ต่ำสุด
correction ใน January
correction ใน December
YTD-derived monthly proxy สำหรับ 2023–2025
no-payout subsample ตาม Amendment 4
รายงาน rank correlation และ top-quintile overlap ระหว่างวิธี ไม่ใช่เพียงดูว่า p-value ยังผ่านหรือไม่
แสดง missingness แยกตาม year, status, class rename และ closure
[ตรวจสอบแล้ว] ใน 386 fund-years ที่ annual uplift มากกว่า 0.5% การย้าย correction ทั้งหมดไปแต่ละเดือนให้ช่วงของ annualized 12-month alpha มี median 2.83pp และ 95th percentile 16.38pp จึงต้องรายงาน timing limitation โดยเฉพาะ evaluation alpha

[ตรวจสอบแล้ว] สำหรับ 36-month rankings ปี 2020–2025 วิธี min-residual/January/December เทียบกับ uniform ให้ Spearman rank correlation ประมาณ 0.9871–0.9997 และ top-quintile overlap 88.5%–100% การจัดอันดับค่อนข้าง robust แต่ไม่สมบูรณ์

[ตรวจสอบแล้ว] สำหรับ 12-month evaluation ความไวสูงกว่า: rank correlation ต่ำสุดประมาณ 0.9670 และ 95th percentile ของ |Δalpha| สูงสุด 3.48pp ใน diagnostics ปี 2021

Limitation ที่ควรเขียนตรง ๆ
Monthly total returns ในปี 2017–2022 เป็น synthetic paths ที่ annual return ถูกต้อง แต่ไม่ทราบ ex-dividend month จริง ดังนั้น within-year beta และ CAPM alpha มี measurement uncertainty แม้ 36-month ranking จะค่อนข้าง stable ใน sensitivity tests ผลหลักจึงต้องรายงานควบคู่กับ alternative timing allocations และ no-payout subsample

4. สิ่งที่ตรวจจากข้อมูลและตัวเลข
[ตรวจสอบแล้ว] include == y มี 272 projects แต่มีเพียง 247 family labels; 24 families มีมากกว่าหนึ่ง project รวมเป็น 25 excess projects ปัจจุบัน universe_review.csv จึงยังไม่สะท้อน one-representative-per-family ขั้นสุดท้าย

[ตรวจสอบแล้ว] ทั้ง 272 included projects มีไฟล์ NAV และไม่มีไฟล์ที่เป็น header-only

[ตรวจสอบแล้ว] ใน 3,497 project-class-year annual keys ค่า latest ต่างจาก modal มากกว่า 0.05pp จำนวน 110 keys, มากกว่า 0.5pp จำนวน 95 keys, สูงสุด 31.51pp จึงไม่ควรใช้ latest snapshot อย่างเดียว

[ตรวจสอบแล้ว] สำหรับ 1,791 selected-class fund-years ที่มี NAV ครบ 12 เดือนและ annual factsheet:

73.9% ตรง NAV-only ภายใน ±0.05pp
21.7% ต้องการ multiplicative uplift มากกว่า 0.5%
มีเพียง 5 กรณีที่ implied uplift ต่ำกว่า −0.5% และควรถูก QC
[ตรวจสอบแล้ว] NAV detector เทียบ usable fund-level factsheet policy ได้ TP=39, FP=16, FN=85: precision 70.9%, recall 31.5% ตรงกับ g2_dividend_findings.md

[ตรวจสอบแล้ว] Raw policy data มี 57 classes ที่ปรากฏมากกว่าหนึ่ง policy state ในช่วง 2022–2026 จึงใช้ current policy ย้อนหลังไป 2014 ไม่ได้

[ตรวจสอบแล้ว] YTD snapshots สร้าง monthly proxy ครบสำหรับ selected classes 203, 210 และ 179 classes ในปี 2023–2025 ตามลำดับ

[ตรวจสอบแล้ว] จาก 6,792 monthly comparisons, YTD-derived return ตรง NAV-only ภายใน ±0.05pp จำนวน 92.1%; ปี 2024 ต่ำกว่าปีอื่นที่ 81.1% ซึ่งสนับสนุนให้ใช้ YTD เป็น sensitivity ไม่ใช่ primary month-end series

[ตรวจสอบแล้ว] Uniform allocation เทียบ YTD-derived timing ให้ 12-month alpha rank correlations 0.9928, 0.9989, 0.9986 ในปี 2023–2025 และ top-quintile overlap 97.6%, 100%, 100%; สำหรับ 36 เดือน 2023–2025 correlation เท่ากับ 0.9981, overlap 96.6%

[ตรวจสอบแล้ว] Exact-class evaluation coverage ยังมีช่องว่าง: ใน cohort 2024 มีข้อมูล evaluation ครบ 201/219 funds และ cohort 2025 มี 170/203; ส่วนใหญ่ที่ขาดยังมี status Registered จึงต้องแก้ class lineage ก่อน analysis จริง

[ตรวจสอบแล้ว] config/class_lineage.csv ซึ่ง Amendment 4 อ้างถึงยังไม่ปรากฏใน repo ที่ตรวจครั้งนี้

สรุป verified vs unverified
Verified: annual coverage, policy changes 57 classes, detector precision/recall, snapshot conflicts, annual NAV/factsheet reconciliation, provisional cohort sizes, benchmark monthly completeness และ timing-sensitivity diagnostics ข้างต้น

Unverified: ex-dividend dates จริงในปี 2017–2022, ความถูกต้องเชิงเศรษฐกิจของทุก factsheet value, final sample หลัง family/lineage QC, จำนวน N→Y ที่แน่นอน 52 classes และผล persistence/significance จริง ยังไม่ได้คำนวณครับ