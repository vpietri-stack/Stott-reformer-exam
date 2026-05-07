import re
import json

new_questions_text = """
第一部分：五大基本原则 (Section 1: Five Basic Principles)
1. 在进行三维侧向呼吸 (3D Breath) 时，吸气阶段的主要生物力学意图是： A) 扩张肋骨的侧方和后方，以最大限度利用肺下叶进行气体交换
 B) 扩张腹部压力，以完全放松腹横肌 (TA) 答案：A
2. 呼气 (Exhalation) 在脊柱动作中通常用于： A) 辅助脊柱屈曲 (Flexion)，因为肋骨向内向下闭合能促进腹肌收缩
 B) 辅助脊柱伸展 (Extension)，因为胸廓打开需要气流支撑 答案：A
3. 关于“中立位” (Neutral Pelvis) 的描述，以下哪项在生物力学上是正确的？ A) 它是脊柱最稳定、减震效果最佳的位置，且腰椎维持自然前突曲线
 B) 髂前上棘 (ASIS) 必须明显高于耻骨联合 (Pubic Symphysis) 答案：A
4. 什么时候必须从“中立位”切换到“印迹位” (Imprint)？ A) 当双脚抬离支撑面进入开链位 (Open Kinetic Chain)，且无法维持腰椎稳定时
 B) 当进行闭链运动 (Closed Kinetic Chain) 且需要增加臀部发力时 答案：A
5. “印迹位” (Imprint) 的正确建立方式是： A) 利用腹斜肌 (Obliques) 将骨盆轻微后倾，使腰椎向垫面靠拢，而不挤压骶骨
 B) 通过强烈收缩臀大肌 (Gluteus Maximus) 来压平下背部 答案：A
6. 针对臀部丰满 (Large gluteals) 的客户，在仰卧位寻找中立位时： A) 应优先确保腰椎不产生张力，即使 ASIS 与耻骨联合不在同一水平面
 B) 必须强制将骨盆三角形调节至平行于垫子 答案：A
7. “胸廓摆放” (Rib Cage Placement) 原则主要用于预防： A) 在手臂举过头顶时出现肋骨外翻 (Ribs Popping) 和胸椎过度伸展
 B) 肩胛骨的前伸 (Protraction) 运动 答案：A
8. 腹外斜肌 (External Obliques) 在胸廓摆放中的作用是： A) 将肋骨与骨盆连结，在吸气或手臂移动时维持胸廓稳定
 B) 辅助肋骨向上向外扩张以增加吸气量 答案：A
9. 肩胛骨稳定性 (Scapular Stabilization) 强调的是： A) 动态稳定性 (Stability, not rigidity)，即肩胛骨随动作滑动但平贴肋骨
 B) 将肩胛骨牢牢锁定在后缩 (Retraction) 位置 答案：A
10. 肩胛骨“翼状” (Winging) 通常暗示哪组肌肉缺乏控制？ A) 前锯肌 (Serratus Anterior) 和肩胛稳定肌群
 B) 上斜方肌 (Upper Trapezius) 答案：A
11. 在进行脊柱屈曲动作（如 Ab Prep）前，先行“头点” (Head Nod) 的目的是： A) 建立颅颈屈曲 (Cranio-vertebral Flexion) 以激活颈深屈肌
 B) 尽可能让下巴贴紧胸部以拉伸后颈 答案：A
12. 针对由于驼背 (Kyphosis) 导致仰卧时颈椎过伸的客户，应： A) 在头下放置垫子或小枕头，使颈椎恢复中立位对齐
 B) 告知客户强制下收下巴 答案：A
13. 呼气时采用“缩唇呼气” (Pursed-lip Breathing) 的生理作用是： A) 产生微小反压，辅助激活腹横肌 (TA) 与盆底肌
 B) 增加颈部肌肉的紧张度 答案：A
14. 盆底肌 (Pelvic Floor) 与腹横肌 (TA) 之间的关系是： A) 具有“共激活” (Co-contraction) 关系，即轻微收缩盆底肌能辅助 TA 激活
 B) 互为拮抗关系 答案：A
15. 侧卧位 (Side-lying) 练习中，维持脊柱中立的标志是： A) 下侧腰部应与垫面保持微小空隙 (Waist Lifted)，确保两侧腰部等长
 B) 允许下方肋骨完全塌陷在垫面上 答案：A
16. 肩胛骨的“下压” (Depression) 运动通常配合什么意象？ A) 想象将肩胛骨滑向后裤兜的方向
 B) 想象肩膀向上碰到耳朵 答案：A
17. 在吸气 (Inhalation) 过程中，脊柱的生物力学倾向是： A) 稍微伸展 (Spinal Extension)，因为胸廓扩张辅助了这一过程
 B) 产生屈曲 (Spinal Flexion) 答案：A
18. 腹横肌 (Transversus Abdominis) 的主要生理功能是： A) 像护腰带一样压缩腹部，为腰椎提供深层稳定性
 B) 产生强大的脊柱旋转力 答案：A
19. 关于“中立位”的维持，以下哪种收缩最为常见？ A) 等长收缩 (Isometric Contraction)，用于在四肢运动时稳定核心
 B) 向心收缩 (Concentric Contraction) 答案：A
20. 斯多特体系为何强调恢复“自然曲线”而非“平背”？ A) 因为自然曲线能提供更好的减震效果并平衡肌肉张力
 B) 因为平背会增加动作的平衡难度 答案：A

--------------------------------------------------------------------------------
第二部分：功能性解塑学 (Section 2: Functional Anatomy)
21. 多裂肌 (Multifidus) 在普拉提练习中的核心职责是： A) 脊柱的节段性稳定 (Segmental Stability) 和姿势微调
 B) 产生大幅度的躯干屈曲动作 答案：A
22. 髂腰肌 (Iliopsoas) 的主要动作是： A) 髋关节屈曲 (Hip Flexion)
 B) 髋关节伸展 (Hip Extension) 答案：A
23. 在执行离心收缩 (Eccentric Contraction) 时，肌肉： A) 产生张力的同时在被拉长，用于控制动作速度
 B) 缩短并产生最大爆发力 答案：A
24. 肩关节的外展 (Abduction) 运动发生在哪一个运动平面？ A) 冠状面 (Frontal Plane)
 B) 矢状面 (Sagittal Plane) 答案：A
25. 腘绳肌 (Hamstrings) 组在膝关节微屈时的主要作用是： A) 防止膝关节过伸 (Hyperextension) 并稳定膝关节
 B) 导致膝关节过伸 答案：A
26. 腹内斜肌 (Internal Oblique) 在单侧收缩时产生： A) 同侧旋转 (Ipsilateral Rotation)
 B) 对侧旋转 (Contralateral Rotation) 答案：A
27. 前锯肌 (Serratus Anterior) 的解剖学功能是： A) 肩胛骨的前伸 (Protraction) 并使其平贴肋骨
 B) 肩胛骨的后缩 (Retraction) 答案：A
28. 腰椎 (Lumbar Spine) 正常生理状态下由几节椎骨组成？ A) 5 节
 B) 12 节 答案：A
29. 哪组肌肉负责执行脊柱的伸展 (Extension)？ A) 竖脊肌 (Erector Spinae) 和多裂肌
 B) 腹直肌 (Rectus Abdominis) 答案：A
30. “肩袖” (Rotator Cuff) 的主要职责是： A) 在肱骨运动中维持肩关节头的稳定与中心化
 B) 负责手臂的大幅度摆动 答案：A
31. 矢状面 (Sagittal Plane) 将身体分为： A) 左右两部分，涉及屈曲与伸展动作
 B) 前后两部分 答案：A
32. 股直肌 (Rectus Femoris) 是股四头肌中唯一： A) 跨越髋关节和膝关节的肌肉 (Double-joint muscle)
 B) 仅作用于膝关节的肌肉 答案：A
33. 进行 Footwork 向上推开滑板时，股四头肌执行的是： A) 向心收缩 (Concentric Contraction)
 B) 离心收缩 (Eccentric Contraction) 答案：A
34. 所谓的“中轴骨骼” (Axial Skeleton) 包括： A) 头颅、脊柱、胸廓和骶骨
 B) 手臂、腿部和骨盆带 答案：A
35. 在矢状面内发生的脊柱运动称为： A) 屈曲与伸展 (Flexion & Extension)
 B) 侧屈 (Lateral Flexion) 答案：A
36. 腹内斜肌和腹外斜肌被统称为： A) 腹部斜肌，负责脊柱的旋转和侧屈
 B) 脊柱伸肌 答案：A
37. 向心收缩 (Concentric) 的定义是： A) 肌肉产生张力并缩短
 B) 肌肉完全放松并拉长 答案：A
38. 臀大肌 (Gluteus Maximus) 的主要解剖动作是： A) 髋关节伸展 (Extension) 与外旋
 B) 髋关节屈曲 答案：A
39. ASIS 是指哪一个骨性标志？ A) 髂前上棘 (Anterior Superior Iliac Spine)
 B) 坐骨结节 答案：A
40. 腓肠肌 (Gastrocnemius) 除了足跖屈外，还能辅助： A) 膝关节屈曲 (Knee Flexion)
 B) 膝关节伸展 答案：A

--------------------------------------------------------------------------------
第三部分：塑身机机械原理 (Section 3: Reformer Mechanics)
41. 斯多特塑身机的弹簧阻力随拉伸长度增加而： A) 递增 (Incremental/Variable resistance)
 B) 保持恒定 (Constant resistance) 答案：A
42. 典型的蓝色 (Blue) 弹簧代表的阻力比例是： A) 50%
 B) 25% 答案：A
43. 黑色 (Black) 弹簧的阻力级别是： A) 125% (特重弹簧)
 B) 75% 答案：A
44. 齿轮杆 (Gearbar) 的主要调节功能是： A) 调节弹簧的初始张力和滑板的起始位置
 B) 调节拉力绳的长度 答案：A
45. 如果在滑板回到挡块位时弹簧出现了“松动” (Play/Looseness)，说明： A) 齿轮杆与挡块的位置组合不匹配，缺乏初始张力
 B) 弹簧已完全损坏 答案：A
46. 对于身材高大的客户，为了防止膝关节过度弯曲，通常需要： A) 将齿轮杆向后移位 (Gear out)
 B) 将挡块移近踏板 答案：A
47. 塑身机设置的“90度原则”是指客户仰卧且脚跟在踏板上时： A) 髋关节应呈约 90 度屈曲
 B) 膝关节必须完全锁死 答案：A
48. 调节脚踏板 (Footbar) 的高度主要会影响： A) 髋、膝、踝关节的屈曲角度及客户的杠杆长度
 B) 弹簧的阻力系数 答案：A
49. 白色 (White) 弹簧通常用于： A) 25% 的轻阻力，常用于挑战核心稳定性的动作
 B) 替代红色弹簧进行大重量训练 答案：A
50. 为什么减轻弹簧（如 Knee Stretches 动作）反而会增加难度？ A) 因为滑板变得极不稳定，迫使核心稳定肌更多参与控制
 B) 因为滑板摩擦力增加了 答案：A
51. 塑身机滑轮 (Pulleys) 的高度调节主要目的是： A) 改变拉力线 (Line of Pull) 以适应不同动作和客户身高
 B) 增加滑板的重量 答案：A
52. 高精度齿轮杆 (High-Precision Gearbar) 通常具有几个位置？ A) 6 个
 B) 3 个 答案：A
53. 在进行 Footwork 时，标准的弹簧阻力通常为： A) 3-4 根红弹簧（或同比例 100% 弹簧）
 B) 1 根白弹簧 答案：A
54. 调节头托 (Headrest) 的首要生物力学考量是： A) 辅助颈椎达到中立位，特别是针对头前伸或颈部紧张的客户
 B) 改变滑板的移动阻力 答案：A
55. 红色 (Red) 弹簧在斯多特系统中代表： A) 100% (标准/重阻力)
 B) 50% 答案：A
56. 维护塑身机安全的最关键操作是： A) 定期检查弹簧、拉力绳的磨损以及弹簧挂钩是否完全落位
 B) 每天清洁滑板表面 答案：A
57. 挡块 (Stopper) 的位置决定了： A) 滑板返回时的最远行程和起始位置
 B) 弹簧的总数量 答案：A
58. 进行上肢划船系列 (Back Rowing) 时，若要增加手臂活动范围，应： A) 将挡块移向踏板方向（例如从 4 号位移至 2 号位）
 B) 使用更重的弹簧 答案：A
59. 弹簧在哪个阶段提供的阻力最大？ A) 弹簧拉伸最长的终点位
 B) 动作启动的瞬间 答案：A
60. 关于弹簧阻力比例，1 根蓝弹簧等于： A) 2 根白弹簧
 B) 1 根黑弹簧 答案：A

--------------------------------------------------------------------------------
第四部分：动作库知识 (Section 4: Repertoire Knowledge)
61. “百次拍击” (The Hundred) 动作中，手臂垂直脉动的频率是： A) 呼吸各 5 次脉动，总计 100 次
 B) 每个呼吸周期 1 次脉动 答案：A
62. 进行“腹部准备” (Ab Prep) 时，向上的动作应伴随： A) 呼气 (Exhalation)，以辅助核心激活和脊柱屈曲
 B) 吸气 (Inhalation) 答案：A
63. “短脊柱伸展” (Short Spine Stretch) 的绝对禁忌是： A) 在头部下方放置厚垫子或抬高头托（以防颈椎过度受压）
 B) 使用蓝色弹簧 答案：A
64. “胃部按摩” (Stomach Massage) 系列中，第一个变体“圆背”的目标是： A) 在脊柱整体屈曲下训练核心力量、脊柱柔韧性和下肢耐力
 B) 纯粹为了按摩腹肌 答案：A
65. “单腿划圈” (One Leg Circle) 的核心本质 (Essence) 是： A) 在单侧腿部运动挑战下维持骨盆绝对水平稳定
 B) 尽可能把圈划得最大 答案：A
66. “大象” (Elephant) 动作主要依靠什么力量将滑板拉回？ A) 深层腹肌 (Abdominals) 的收缩
 B) 腿部的惯性 答案：A
67. “美人鱼” (Mermaid) 动作主要在哪个平面内进行？ A) 冠状面 (Frontal Plane)
 B) 横断面 答案：A
68. “大腿拉伸” (Thigh Stretch) 动作中，身体后落时应维持： A) 从膝盖到头部的整体中立直线
 B) 脊柱弯曲成 C 型 答案：A
69. “滚动如球” (Rolling Like a Ball) 的翻滚终点应在： A) 肩胛骨/中胸椎位，绝对不能滚到颈部
 B) 头部后侧 答案：A
70. “单腿踢” (One Leg Kick) 在俯卧位挑战的是： A) 骨盆稳定性，防止膝关节运动导致骨盆前倾
 B) 手臂力量 答案：A
71. “Saw” (锯子) 动作结合了脊柱的哪两种运动？ A) 旋转与屈曲 (Rotation and Flexion)
 B) 侧屈与旋转 答案：A
72. 进行“半卷后” (Half Roll Back) 时，重点关注的肌肉是： A) 腹肌（维持 C 曲线）和髂腰肌（离心收缩）
 B) 竖脊肌 答案：A
73. “Shoulder Bridge Prep” (肩桥准备) 动作中，骨盆抬起时应： A) 维持肋骨闭合，通过臀肌和腘绳肌将骨盆整体抬起
 B) 使腰椎最大程度拱起 答案：A
74. “Teaser” 动作在平衡位要求： A) 维持轻微的腰椎屈曲和胸椎延伸平衡
 B) 背部完全平直 答案：A
75. “Leg Pull Front” (前支撑) 动作的本质是： A) 在非对称挑战下（抬腿）维持整体躯干稳定性
 B) 练习脚趾柔韧性 答案：A
76. 斯多特动作编排中的“Essence” (本质) 指的是： A) 动作的核心目标和生物力学意图
 B) 动作的起源背景 答案：A
77. “Cat Stretch” (猫式拉伸) 的主要目的是： A) 提高脊柱灵活性、逐节动员能力和核心控制
 B) 增加手臂围度 答案：A
78. 执行“Breast Stroke Preps” (蛙泳准备) 时，呼吸通常是： A) 吸气伴随脊柱伸展 (Extension)
 B) 呼气准备 答案：A
79. 在进行“Mid-back Series”时，向下拉动拉力绳的起始动力应来自： A) 背阔肌 (Latissimus Dorsi) 和肩胛骨稳定肌
 B) 仅由肱二头肌 答案：A
80. 动作库中的“Transition” (转换) 目的是： A) 维持课程流度 (Flow) 且保持原则执行
 B) 替代核心练习 答案：A

--------------------------------------------------------------------------------
第五部分：体态分析与安全 (Section 5: Posture & Safety)
81. 针对“平背体态” (Flat Back) 客户，主要的编程重点应是： A) 恢复腰椎自然前突，拉伸紧绷的腘绳肌并增加脊柱动员
 B) 进一步强化腘绳肌 答案：A
82. “驼背-腰椎前突” (Kyphosis-Lordosis) 客户通常需要拉伸： A) 髋屈肌 (Hip Flexors) 和背部伸肌
 B) 腹肌和臀肌 答案：A
83. 怀孕 16 周后的孕妇应绝对禁止： A) 长时间平躺仰卧位 (Supine Position)，以防压迫下腔静脉
 B) 四足跪姿 答案：A
84. 骨质疏松症 (Osteoporosis) 客户应避免的动作是： A) 任何深度的脊柱屈曲 (Spinal Flexion)，如滚动动作
 B) 脊柱伸展动作 答案：A
85. 患有急性腰椎间盘突出 (Disc Herniation) 的客户，练习应强调： A) 维持脊柱中立位 (Neutral Spine) 的稳定性
 B) 大幅度的脊柱卷起 答案：A
86. “摇摆背” (Sway Back) 体态的显著特征是： A) 骨盆相对于脚踝前移 (Pelvis shifted forward)
 B) 腰椎极度前突 答案：A
87. 针对膝关节过伸 (Hyperextension) 客户，Footwork 时的提示应是： A) 维持膝关节“微屈” (Soft Knees)，不锁死关节
 B) 完全锁死膝盖以获得稳定 答案：A
88. 意象引导 (Imagery) 在教学中的专业功能是： A) 使用生动比喻激发客户的本体感受和肌肉正确发力
 B) 仅仅是为了美化语言 答案：A
89. 斯多特实操评估中的“观察能力” (Observation) 重点在于： A) 瞬间捕捉代偿行为（如下巴突起、肋骨外翻）
 B) 观察客户的运动服品牌 答案：A
90. 针对关节过度灵活 (Hypermobility) 客户，教学重点应在： A) 建立关节周围肌肉支撑力，将动作限制在受控范围内
 B) 进一步增加动作幅度 答案：A
91. 体态分析 (Postural Analysis) 应在何时进行？ A) 课程开始前的静态评估及运动中的动态观察
 B) 仅在第一节课进行一次 答案：A
92. 怀孕期间分泌的哪种激素会导致韧带松弛？ A) 松弛素 (Relaxin)
 B) 肾上腺素 答案：A
93. 斯多特认证考试要求的最低平均分数是多少？ A) 80% (且单项不低于 75%)
 B) 60% 答案：A
94. 针对高血压客户，应避免的体位是： A) 长时间的倒置体位 (Head below Heart) 或屏息
 B) 坐姿练习 答案：A
95. 教练执行触觉辅助 (Tactile Cueing) 的首要原则是： A) 征得同意后，轻柔引导骨骼对齐或肌肉收缩感知
 B) 强力推动客户关节到位 答案：A
96. 评估教练“节奏与流度” (Flow & Pace) 的标准是： A) 动作切换是否流畅无间断，且保持原则执行
 B) 课程速度是否越快越好 答案：A
97. 针对脊柱侧弯 (Scoliosis) 客户，编程策略应包含： A) 针对不对称的背部肌肉进行差异化平衡练习
 B) 严禁一切运动 答案：A
98. 斯多特考试中肌肉识别题通常涉及多少道？ A) 约 20 道
 B) 5 道 答案：A
99. “Programming” (编程能力) 在考试中代表： A) 根据客户体态和目标选择合适的动作顺序及修改
 B) 会使用所有的器械 答案：A
100. 斯多特认证教练身份的唯一标志是： A) 收到由 Merrithew 颁发的正式纸质证书
 B) 拥有自己的塑身机 答案：A
"""

# Regex to parse the questions
# Pattern: Number. Question A) OptionA B) OptionB 答案：Answer
pattern = r'(\d+)\.\s+(.*?)\s+A\)\s+(.*?)\s+B\)\s+(.*?)\s+答案：([A-B])'
matches = re.finditer(pattern, new_questions_text, re.DOTALL)

parsed_questions = []
for match in matches:
    q_text = match.group(2).strip().replace('\n', ' ')
    opt_a = match.group(3).strip().replace('\n', ' ')
    opt_b = match.group(4).strip().replace('\n', ' ')
    ans_letter = match.group(5)
    
    ans_idx = 0 if ans_letter == 'A' else 1
    
    parsed_questions.append({
        "q": q_text,
        "options": [opt_a, opt_b],
        "ans": ans_idx
    })

# Check if we got 100
print(f"Parsed {len(parsed_questions)} questions.")

# Format as JSON string for JS
json_str = json.dumps(parsed_questions, ensure_ascii=False, indent=12)

# Load index.html
file_path = r'd:\coding\html games\Stott-reformer-exam\index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the questionDatabase
# Look for const questionDatabase = [ ... ];
# Using a simpler approach to replace the entire array content
start_marker = 'const questionDatabase = ['
end_marker = '];'

start_idx = content.find(start_marker)
if start_idx != -1:
    end_idx = content.find(end_marker, start_idx)
    if end_idx != -1:
        # We want to replace from after '[' to before ']'
        new_content = content[:start_idx + len(start_marker)] + "\n" + json_str[1:-1] + "\n        " + content[end_idx:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated index.html")
    else:
        print("Could not find end marker")
else:
    print("Could not find start marker")
