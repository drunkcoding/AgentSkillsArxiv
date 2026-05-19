# Pedagogy & Supervision Reference Palette

> **Purpose**: Evidence-based concepts an academic CS applicant can reference in a Statement on Education, organized by statement section. Not a checklist — draw selectively from what fits your experience and context. Aim for substance over volume; citing a few frameworks you genuinely apply is far more credible than name-dropping everything.

---

## 1. Evidence-Based CS Pedagogy

### Active Learning
**What it is**: Any classroom practice that engages students in higher-order thinking rather than passive listening — peer discussion, in-class problems, think–pair–share, clickers, collaborative coding. The landmark evidence is a 2014 PNAS meta-analysis of 225 studies (Freeman et al.) showing a **0.47 SD improvement in exam performance** and a **55% higher failure rate in traditional lecture sections**. Effects held across STEM disciplines and all class sizes, strongest in small classes (≤50).

**Essence for your statement**: "Active learning is not a preference but an empirical conclusion — the largest meta-analysis in undergraduate STEM education shows students perform significantly better and fail less under active learning than lecture."

**Source**: Freeman, S. et al. (2014). *Active learning increases student performance in science, engineering, and mathematics.* PNAS, 111(23), 8410–8415. https://doi.org/10.1073/pnas.1319030111

**Best used in**: **Philosophy** (your overall teaching stance) and **Methods** (specific in-class techniques).

---

### Pair Programming & Peer Instruction

**What it is**: Pair programming — two students at one machine, switching driver/navigator roles — comes from XP/agile methodology and has strong empirical support in CS education. Peer instruction (Mazur) uses conceptual multiple-choice questions posed to the whole class with peer discussion between question and answer reveal; particularly powerful for shifting student mental models in CS.

**Essence for your statement**: "I use pair programming as both a pedagogical and professional socialization tool — students simultaneously learn technical and collaborative skills. Peer instruction lets me check student understanding in real time rather than discovering misconceptions weeks later on an exam."

**Source**: pairs research: Nagel, K. & R. G. R. (2006). Pair programming in the introductory programming course. SIGCSE TS. Peer instruction: Mazur, E. (1997). *Peer Instruction: A User's Manual.* Prentice Hall.

**Best used in**: **Methods** (lab/recitation design) and **Supervision** (how you structure collaborative student teams).

---

### Live Coding / Worked Examples

**What it is**: Live coding ("think-aloud" programming by the instructor in real time) is a high-impact active learning technique — you model the problem-solving process, not just the product. Worked examples (presenting complete solutions with annotations) exploit the "expertise reversal effect": what helps novices may hinder experts. In CS, showing code construction step-by-step, narrating decisions, and leaving deliberate errors for class diagnosis are all effective variants.

**Essence for your statement**: "I use live coding to make my problem-solving process visible — students see not just what code looks like but what the decision-making looks like. I follow worked examples with faded versions where students complete increasingly larger portions independently, aligning with cognitive load theory."

**Source**: Sweller's worked examples effect (Sweller & Cooper, 1985); Denny et al. on Parsons problems for reducing extraneous load in CS1. See also: Reges, Z. (2015). *Live coding in CS1.* ACM SIGCSE.

**Best used in**: **Methods** (in-class technique descriptions).

---

### POGIL, Problem-Based Learning, Project-Based Learning

**What it is**: **POGIL** (Process-Oriented Guided Inquiry Learning) uses structured inquiry cycles where students explore models, make observations, and derive principles — particularly well-suited to algorithms and data structures. **Problem-based learning (PBL)** presents students with real-world problems without a predetermined solution path; the instructor facilitates rather than lectures. **Project-based learning (PjBL)** is similar but centers on a sustained, tangible product (e.g., a functioning application, a research artifact).

**Essence for your statement**: "I design projects that require students to integrate multiple concepts — a full-stack application demands database theory, architecture decisions, testing strategy, and ethical considerations simultaneously. I use POGIL for conceptually dense topics like recursion or concurrency, where guided inquiry does more than lecture."

**Best used in**: **Methods** and **Assessment** (how you design major assessments).

---

### Bloom's Taxonomy Applied to CS

**What it is**: Bloom's taxonomy (remember → understand → apply → analyze → evaluate → create) gives you a vocabulary for aligning learning outcomes with activities and assessments. In CS, most faculty over-assess at the lower "apply" level (write code) and under-assess at "evaluate" (debug, reason about tradeoffs) and "create" (design systems). Naming Bloom's levels signals you think intentionally about cognitive progression.

**Essence for your statement**: "I use Bloom's taxonomy as a design check: if all my assessments sit at 'apply,' I am not developing higher-order skills. I design at least one major assignment at the 'create' level — e.g., architecting a system under constraints — to give students practice in the kind of open-ended synthesis they will face professionally."

**Source**: Anderson, L. W. & Krathwohl, D. R. (Eds.) (2001). *A Taxonomy for Learning, Teaching, and Assessing.* Merrill. Bloom's original: Bloom, B. S. (1956). *Taxonomy of Educational Objectives.*

**Best used in**: **Assessment** and **Philosophy** (course design philosophy).

---

### Constructive Alignment (Biggs)

**What it is**: The core principle that learning outcomes, teaching activities, and assessment tasks must all align — each assessment should directly measure the learning outcome it claims to, and each activity should prepare students for that assessment. Misaligned courses reward the wrong behaviors (e.g., studying trivia while higher-order synthesis is claimed). Constructive alignment is one of the most widely cited frameworks in university teaching quality worldwide.

**Essence for your statement**: "I design courses backwards: I define learning outcomes first, then ask what activity would realistically prepare a student to demonstrate that outcome, and only then design the assessment that measures it. This 'constructive alignment' keeps my courses coherent rather than a collection of interesting but unassessed topics."

**Source**: Biggs, J. (1996). Enhancing teaching through constructive alignment. *Higher Education*, 32, 347–364. Also: Biggs, J. & Tang, C. (2011). *Teaching for Quality Learning at University.* Open University Press (5th ed.).

**Best used in**: **Philosophy** and **Assessment** (explicit design methodology).

---

### Cognitive Load Theory in Programming Education

**What it is**: Cognitive load theory (CLT) describes learning as constrained by working memory — we can only hold ~4 items in working memory at once, but long-term memory capacity is effectively unlimited. In programming, novices face high *intrinsic* load (the material is inherently complex with high "element interactivity") and can be overwhelmed by *extraneous* load (poor IDE design, confusing error messages, syntactically dense notation). *Germane* load is the productive cognitive effort of schema building. Effective CS instruction reduces extraneous load (worked examples, Parsons problems, structured IDEs) and manages intrinsic load through sequencing.

**Essence for your statement**: "I am conscious that learning to program taxes working memory in ways that other disciplines do not — students must simultaneously manage syntax, semantics, runtime behavior, and algorithmic strategy. I reduce extraneous cognitive load through worked examples, Parsons problems in early weeks, and structured scaffolds that let students focus on conceptual understanding before syntax is fully automatic."

**Source**: Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science*, 12, 257–285. Application to CS: Morrison, B. (2013). Using cognitive load theory to improve the efficiency of learning to program. *ICER '13*. Also: L. Looker (2021). A pedagogical framework combining social constructivism and CLT. *ICER '21*.

**Best used in**: **Methods** and **Philosophy** (explains specific pedagogical choices).

---

### Notional Machines & Threshold Concepts in CS

**What it is**: A **notional machine** is the abstract mental model a student builds of how a program executes — variables, state, control flow, memory. Novice programmers often hold fundamentally incorrect notional machines (e.g., viewing a variable as a "box" whose name matters, or believing that code executes all-at-once rather than line-by-line). A **threshold concept** is a concept that, once understood, transforms a student's entire view of the discipline — it is troublesome (causes confusion), transformative, irreversible, and integrative. In CS, candidates include: recursion, pointers/memory allocation, concurrency, object polymorphism, and the notional machine itself.

**Essence for your statement**: "I make the notional machine explicit — I teach students to visualize program execution step-by-step, and I treat correct mental models as a first learning outcome. I also identify threshold concepts in my courses, particularly recursion and abstraction, and invest disproportionate time in them because unlocking them transforms student trajectories."

**Source**: Sorva, J. (2013). Notional machines and introductory programming education. *ICER '13*. Threshold concepts in CS: Eckerdal, A. et al. (2006). Putting threshold concepts into context in CS education. *ITiCSE '06*. Boustedt, J. et al. (2007). Threshold concepts in CS: Do they exist and are they useful? *SIGCSE Bulletin*, 39(1).

**Best used in**: **Philosophy** and **Methods** (curriculum sequencing rationale).

---

### Parsons Problems & The Rainfall Problem

**What it is**: **Parsons problems** give students all the code lines needed to solve a problem but jumbled — students arrange them in correct order. This reduces the cognitive load of code writing (no syntax production required) so students can focus on logic, structure, and control flow. Can include distractors (extra lines) to increase challenge. The **Rainfall problem** is a well-studied CS1 assessment task that reveals how novices approach algorithmic problem-solving and has become a benchmark for comparing pedagogical interventions.

**Essence for your statement**: "I use Parsons problems in early programming courses to bridge between reading code and writing code — students practice sequencing and logic without the overhead of syntax production. I also use the Rainfall problem as a formative diagnostic because it surfaces the planning and decomposition strategies students bring to algorithmic problems."

**Source**: Parsons problems: Denny, P. et al. (2008). Improving the acquisition of code order. *ICER '08*. Rainfall problem: Powers, K. et al. (2007). The Rainfall problem. *ITiCSE '07*.

**Best used in**: **Methods** and **Assessment**.

---

### CS Education Research Venues

**What they are**: If you are asked to demonstrate engagement with CS education research, know these venues:

- **SIGCSE** (ACM SIGCSE Symposium on Computer Science Education) — the largest, most general CS education conference; breadth over depth.
- **ICER** (International Computing Education Research Workshop) — more research-methodology-intensive, higher proportion of empirical studies; closer to "education research" than "practice reports."
- **ITiCSE** (Innovation and Technology in Computer Science Education) — focuses on curricular innovation and tooling; strong in CS1/CS2.
- **Koli Calling** — European-focused, strong in programming education research and threshold concepts.
- **Journal of Engineering Education** (JEE), **Computer Science Education** (Taylor & Francis), **ACM TOCE** (Transactions on Computing Education) — peer-reviewed publication venues.

**Essence for your statement**: "I maintain awareness of the CS education research literature (SIGCSE, ICER) and I have used findings from that community — for example, the evidence on Parsons problems and cognitive load theory — to redesign my introductory programming course."

**Best used in**: **Philosophy** (demonstrates scholarly approach to teaching) or **Methods** (explaining why you use specific techniques).

---

## 2. Supervision Frameworks

### Vitae Researcher Development Framework (RDF)

**What it is**: The Vitae RDF is a UK/EU-wide framework describing the knowledge, behaviors, and attributes of successful researchers. It organizes development across four domains: **A: Knowledge and Intellectual Ability; B: Personal Effectiveness; C: Research Governance and Organization; D: Engagement, Influence and Impact.** Each domain has sub-domains with descriptors at different career stages. It is widely used in the UK and increasingly in EU institutions to structure doctoral supervision conversations and development planning.

**Essence for your statement**: "I use the Vitae Researcher Development Framework as the backbone of my doctoral supervision — it gives both me and my students a shared vocabulary for discussing progress, identifying development needs, and planning training. I find the D: Engagement domain particularly useful for helping students see their research trajectory beyond academia."

**Source**: Vitae (2011). *Researcher Development Framework.* https://www.vitae.ac.uk/vitae-researcher-development-framework

**Best used in**: **Supervision** section.

---

### Lave & Wenger: Cognitive Apprenticeship / Legitimate Peripheral Participation

**What it is**: **Situated learning** theory argues that knowledge is constructed through social participation in a community of practice, not in isolation inside an individual's mind. **Legitimate peripheral participation (LPP)** describes how newcomers join a community — starting at the periphery doing peripheral tasks, gradually taking on more central, complex work as their competence grows. **Cognitive apprenticeship** (Brown, Collins & Duguid) extends this to intellectual skills — modeling a task, coaching, scaffolding, fading support as the learner progresses.

**Essence for your statement**: "I think of my role with graduate students as a cognitive apprenticeship: I model expert practice (how I read literature, how I approach open problems), then coach as they attempt early work, then scaffold their independent work and gradually withdraw support as they develop competent autonomy. For undergraduate students, I use LPP — I look for authentic peripheral participation opportunities, such as contributing to real research projects or open-source repositories."

**Source**: Lave, J. & Wenger, E. (1991). *Situated Learning: Legitimate Peripheral Participation.* Cambridge University Press. Brown, J. S., Collins, A. & Duguid, P. (1989). Cognitive apprenticeship. *Cognition and Instruction*, 6(2).

**Best used in**: **Supervision** section.

---

### Gurr's Supervisory Styles Matrix

**What it is**: Gurr (2001) developed the "Rackety Bridge" model — the central idea is that **competent autonomy** is the universal objective of doctoral education, and the supervisor's job is to dynamically align their style with the student's development. Early in a PhD, more direction is appropriate; as the student matures, the supervisor shifts to a more delegative style. The model emphasizes that supervision is not static — the style must evolve with the student.

Gatfield (2005) extended this into a **four-quadrant supervisory management grid** with axes: **Structure** (how much the supervisor manages the process) and **Support** (how much pastoral/relational support is provided). Quadrants: laissez-faire (low structure, low support), pastoral (low structure, high support), contractual (high structure, low support), directive (high structure, high support). Again, effective supervisors move between quadrants as the student progresses.

**Essence for your statement**: "I am conscious of aligning my supervisory style to student development — early-stage PhDs receive more structure and direct guidance; as they develop competent autonomy, I shift to a more delegative mode. I use Gurr's model to reflect on whether I am over- or under-supporting a particular student at their current stage."

**Source**: Gurr, G. M. (2001). Negotiating the "Rackety Bridge" — a dynamic model for aligning supervisory style with research student development. *Higher Education Research & Development*, 20(1), 81–92. Gatfield, T. & Alpert, F. (2005). An investigation into PhD supervisory management styles. *Educational Management Administration & Leadership*, 33(4).

**Best used in**: **Supervision** section.

---

### Scaffolding Then Fading / Zone of Proximal Development

**What it is**: **Scaffolding** is temporary instructional support that enables a learner to complete a task they cannot yet do independently — it is calibrated to the student's current capability. As the student masters the skill, the scaffold is **faded** (progressively withdrawn). The concept originates from Vygotsky's **Zone of Proximal Development (ZPD)** — the gap between what a learner can do alone and what they can do with expert guidance. Effective supervision operates within the student's ZPD: challenging enough to stretch but not so hard as to overwhelm.

**Essence for your statement**: "I structure my supervision meetings around the student's ZPD — I aim to give feedback that moves them just beyond their current capability, not simply confirming what they already know. I find the 'scaffolding then fading' model particularly useful for MSc students doing their first substantial research project: initial meetings are more directive; later ones shift to critique and challenge."

**Source**: Wood, D., Bruner, J. S. & Ross, G. (1976). The role of tutoring in problem solving. *British Journal of Educational Psychology*, 66, 175–181. Vygotsky, L. S. (1978). *Mind in Society.* Harvard University Press.

**Best used in**: **Supervision** section.

---

### Practical Supervision Structures

**Weekly 1:1s**: Many experienced supervisors have a weekly or biweekly meeting rhythm — a standing agenda item is the student presenting what they did, what they found, and what they plan to do next. Some supervisors ask students to send a brief written update (1–2 paragraphs) 24 hours before the meeting so preparation is informed by actual progress.

**Written feedback culture**: For written work (draft chapters, paper submissions), giving tracked-changes feedback in a shared document rather than only verbal feedback gives students a permanent record and forces the supervisor to be precise. Some supervisors maintain a shared "supervision log" document with action items from each meeting.

**Lab notebook practice**: In experimental CS (systems, security, HCI), maintaining a research log/lab notebook is both a professional practice and a pedagogical tool for developing systematic habits. Some supervisors require it; others recommend it.

**Essence for your statement**: "I hold weekly meetings with my PhD students — I ask them to send a short written update 24 hours before so our time is used for discussion, not status reports. For written drafts, I use tracked-changes comments to give precise, actionable feedback that students can revisit. I also maintain a shared supervision log that records decisions and action items so both of us can track progress between meetings."

**Best used in**: **Supervision** section.

---

### PhD vs. MSc vs. BSc Supervision Differences

**PhD**: Typically 3–4 years; the supervisor has responsibility not just for the project but for the student's overall development as a researcher, including navigating publication, conference presentation, teaching, and career planning. PhD students should progressively develop autonomous research capability — the supervisor's role shifts from manager to advisor to peer colleague over the arc of the degree.

**MSc (thesis)**: Typically 1 year; the student is usually expected to demonstrate competence in research methods and produce an original contribution, but on a smaller scale than a PhD. Supervision tends to be more structured, with clearer intermediate milestones, because the timeline is compressed.

**BSc (final project / capstone)**: Often 1–2 quarters/semesters; many students are experiencing a substantial independent project for the first time. Expectations should be calibrated carefully — a BSc student should not be expected to produce PhD-level novelty. The supervisor may need to provide more scaffolding early and may need to cover basics of research methodology that a PhD student would already have.

**Dutch context** (BSc end project, MSc thesis, PhD as employee): In the Netherlands, PhD candidates are typically employees rather than students — they have employment contracts, entitlements (vacation, parental leave), and a supervisor who is also an employer. The supervision dynamic has both pedagogical and professional dimensions. BSc end projects and MSc theses are more structured and often involve a formal report and defense.

**Essence for your statement**: "I calibrate my supervision style to the degree level — for PhD students I prioritize developing autonomous research capability and aim for a collaborative, critically伙伴 relationship; for MSc students I provide more structure and clearer intermediate milestones because of the compressed timeline; for BSc students I invest more in early scaffolding and setting realistic expectations for the scope of a first independent project."

**Best used in**: **Supervision** section.

---

## 3. Inclusion & Diversity in CS

> **Note**: "Substantive inclusion" means citing structural research, not just asserting a commitment. The difference between "I value diversity" (platitude) and "I design my intake pathways to counteract stereotype threat and belonging uncertainty" (substance) is the difference between a vague claim and a credible one.

### Margolis & Fisher: "Unlocking the Clubhouse"

**What it is**: The landmark 2003 study by Jane Margolis and Allan Fisher at Carnegie Mellon found that women were blocked not by a "pipeline problem" but by a social and cultural clubhouse — the environment, the "hacker" culture, the way CS was presented. Their intervention (redesigning introductory courses, creating a supportive cohort, making department climate visible) led to a dramatic increase in women's retention and achievement. The book is often credited with launching CS education as a field with a diversity research agenda.

**Essence for your statement**: "I draw on Margolis and Fisher's insight that the 'pipeline' framing misses the point — the issue is departmental climate and the message about who belongs. My approach to welcoming environments is not about lowering standards but about removing the cultural signals that say 'people like you don't belong here.'"

**Source**: Margolis, J. & Fisher, A. (2003). *Unlocking the Clubhouse: Women in Computing.* MIT Press.

**Best used in**: **Inclusion** section.

---

### Stereotype Threat (Steele) and Growth Mindset (Dweck) in CS

**What it is**: **Stereotype threat** (Steele & Aronson) describes the psychological risk that members of negatively stereotyped groups underperform because they are aware of the stereotype and fear confirming it — this operates even without explicit bias from others. In CS, women and other underrepresented groups experience stereotype threat in contexts where their group is negatively stereotyped (e.g., competitive coding environments, male-dominated classrooms). **Growth mindset** (Dweck) — the belief that intelligence and ability are developable through effort — counteracts the "entity theory" (that ability is fixed and innate), which is particularly damaging in CS where "innate genius" narratives are common.

Research by Cheryan, Master et al. shows that women report lower sense of belonging in CS when environments signal stereotypical cues (e.g., gaming posters, tech-cluttered spaces, male-dominated imagery), and that this is mediated by identity expression threat (worry that expressing interest in CS contradicts one's social identity). Conversely, belonging interventions — brief social belonging interventions in first-year CS — have been shown to reduce the achievement gap.

**Essence for your statement**: "I am aware that stereotype threat can suppress performance even in the absence of explicit bias — I design assessments where identity-relevant cues are minimized (e.g., anonymous grading for the first programming assignment). I also explicitly teach a growth mindset framing, particularly in early CS courses where the 'you either have it or you don't' narrative is pervasive and damaging."

**Source**: Steele, C. M. & Aronson, J. (1995). Stereotype threat and the intellectual test performance of African Americans. *J. Personality and Social Psychology*, 69(5). Dweck, C. S. (2006). *Mindset: The New Psychology of Success.* Random House. Cheryan, S. et al. (2009). Ambient belonging. *J. Personality and Social Psychology*, 97(6). Master, A. et al. (2016). Computing whether she belongs. *J. Educational Psychology*, 108(3).

**Best used in**: **Inclusion** section.

---

### Universal Design for Learning (UDL)

**What it is**: UDL is a framework developed by CAST (Center for Specialized Technology) for proactively designing learning environments that accommodate individual variability — not by retrofitting accommodations afterward, but by designing from the outset. Three principles: **Multiple Means of Engagement** (relevance, interest, sustained effort), **Multiple Means of Representation** (information presented in multiple formats — text, visual, auditory), and **Multiple Means of Action & Expression** (students can demonstrate understanding in multiple ways). In CS specifically, UDL for CS (UDL4CS) extends these principles to computing content — e.g., offering multiple modalities for code explanation, multiple pathways to complete a coding task, flexible assessment formats.

**Essence for your statement**: "I design using Universal Design for Learning principles — I assume a diverse range of learners from the outset rather than reacting to individual accommodations. For example, I provide multiple means of engagement (choice in project topics, collaborative structures), representation (code examples in text, visual diagrams, and audio explanation), and action/expression (students can submit as a written report, demo video, or live code review)."

**Source**: CAST (2018). *UDL Guidelines 2.2.* https://udlguidelines.cast.org. UDL4CS: https://udl4cs.education.ufl.edu/

**Best used in**: **Inclusion** section, **Methods**.

---

### Belonging Interventions in Introductory CS

**What it is**: Brief, low-cost interventions that target students' sense of belonging in CS — typically a short writing exercise where students read information about the malleability of belonging and social identity. Walton & Cohen's belonging intervention research shows that a brief (1-hour) writing exercise about belonging can significantly improve academic outcomes for underrepresented students years later. In CS specifically, research shows that belonging uncertainty (worrying about whether one fits) is a significant predictor of dropout for women, mediated by perceived exclusion by peers and academic self-efficacy.

**Essence for your statement**: "I incorporate a brief belonging intervention at the start of introductory courses — research shows that even a single session can have lasting effects on student persistence, particularly for those from underrepresented groups. I also attend to the signals my own behavior sends: who I call on, how I respond to wrong answers, and whether I signal that intellectual struggle is normal and productive rather than a sign of unsuitability."

**Source**: Walton, G. M. & Cohen, G. L. (2007). A question of belonging. *J. Personality and Social Psychology*, 92(6). Dasgupta, N. (2011). Ingroup experts and peers. *Psychological Science*, 22(7). Craig, M. & S. Cheryan (2024). Climate and belonging interventions in CS.

**Best used in**: **Inclusion** section.

---

## 4. Modern CS-Specific Topics

### Teaching with LLMs / GenAI

**What it is**: The emergence of large language models (LLMs) like ChatGPT, Copilot, and Gemini has forced CS educators to take a position. Three broad stances:
- **Ban / restrict**: Concern about cheating, reduced learning, over-reliance. Common in early 2023 responses.
- **Embrace / integrate**: Treat LLMs as a productivity tool and teach students to use them effectively — prompting, testing, debugging, decomposition into LLM-solvable chunks. CS50's approach (Liu et al., 2024) is the most prominent exemplar — they built custom AI tools as "personal tutors," treating LLM literacy as a course goal.
- **Scaffold / critically integrate**: Neither wholesale embrace nor rejection — use LLMs for specific tasks (e.g., code explanation, style feedback, generated test cases) while designing assessments that require skills LLMs cannot replicate (e.g., system design, decomposition without given specs).

The emerging evidence suggests that moderate, strategic integration (scaffold approach) yields the best learning outcomes and is most aligned with professional reality — students will use these tools in industry regardless of course policy.

**Essence for your statement**: "I take the scaffold approach: I treat LLMs as a professional tool and explicitly teach students to use them — prompting skills, test-driven verification, debugging assistance — while designing assessments that require higher-order synthesis (system design, algorithmic reasoning) that current LLMs cannot reliably perform. I have found that students who use LLMs strategically (not passively) perform better in my course, and I explicitly discuss the difference between using a tool and understanding the underlying principles."

**Source**: Liu, R. et al. (2024). Teaching CS50 with AI. *SIGCSE '24.* Prather, J. et al. (2024). Generative AI in computing education. ITiCSE Working Group Report. Denny, P. et al. (2024). Computing education in the era of generative AI. *CACM.*

**Best used in**: **Methods** (course design choices) and **Philosophy** (your stance on technology and learning).

---

### Reproducibility, Open Science, Version Control as Pedagogy

**What it is**: The reproducibility crisis in science has led to a push for teaching open science practices as part of CS and data science education. Version control (Git) is both a professional skill and a pedagogical tool — it makes student work visible, enables structured collaboration, and provides a natural audit trail for assessment. Teaching version control early (CS1/2) also embeds good professional practice before students graduate.

**Essence for your statement**: "I teach version control as a pedagogical tool from the first programming course — students maintain all their work in Git from week 1. This serves both professional socialization (they enter industry with industry-standard tools) and pedagogical goals (I can see their process, not just their product, and give feedback on their development trajectory). For research-oriented students, I incorporate reproducibility practices: pre-registration, open data, and computational notebook discipline."

**Source**: Beck, K. (2000). *Extreme Programming Explained.* Addison-Wesley (Git adoption in education). For open science pedagogy: Wilson, G. et al. (2017). Good enough practices in scientific computing. *PLOS Computational Biology.*

**Best used in**: **Methods** and **Assessment** (assessment through version-controlled artifacts).

---

### Ethics & Responsible AI as Integrated Thread

**What it is**: There is growing consensus that ethics cannot be a bolt-on module at the end of a CS course — it must be woven in as an integrative thread. This means not just "CS for social good" as a special track but embedding ethical analysis throughout core CS courses: discussing bias in datasets in a machine learning course, privacy implications in a databases course, security ethics in a networks course. The "embedded ethics" approach (C. H. G. serving) is more effective than standalone courses because it ties ethical reasoning to technical content students are already engaged with.

**Essence for your statement**: "I embed ethics throughout the curriculum rather than treating it as an add-on — when my students build a database system, I ask them to write a short ethical analysis of what data they would and would not collect and why; in our machine learning unit, we analyze whose values are encoded in a model's training decisions. This approach follows the 'embedded ethics' model, treating ethical reasoning as a technical skill, not a separate domain."

**Source**: For embedded ethics in CS: Taddeo, M. & L. Floridi (2005). Defining ethics for an e-person. *Philos. Trans. Royal Society A.* For responsible AI in CS education: K. Burton et al. (2021). Integrating ethics across CS curricula. *ACM TOCE.*

**Best used in**: **Philosophy** and **Methods** (curriculum design).

---

### Real-World / Industry-Coupled Projects

**What it is**: Coupling student projects with external partners (industry collaborators, open-source communities, research labs) provides authentic contexts, increases student motivation, and gives students experience with the social and political dimensions of real software development (requirements negotiation, stakeholder management, deadline constraints). Models include: semester-long client projects with external partners (common in software engineering courses); research apprenticeship (students contribute to an ongoing research project); open-source contributions (students make meaningful PRs to real repositories).

**Essence for your statement**: "I design at least one major project each year with an external partner — this gives students practice in requirements gathering, stakeholder communication, and delivering to a real deadline. I have found that the motivational effect of a real audience is significant, and the ambiguity of real-world requirements is itself a valuable learning experience that prepares students for industry."

**Best used in**: **Methods** and **Assessment**.

---

## 5. Assessment in CS

### Specifications Grading / Mastery Learning

**What it is**: **Specifications (specs) grading** replaces point-based grading with pass/fail rubrics — students must meet explicit specifications ("specs") for each assignment, and can revise and resubmit until they meet the standard. This is a form of **mastery learning** (mastery before progression). The approach reduces grade-grubbing behavior, makes expectations transparent, and gives students agency over their grade. Many CS courses (including at University of Chicago and elsewhere) have documented positive outcomes from adopting this model.

**Essence for your statement**: "I use specifications grading — every assignment has explicit pass/fail criteria published in advance, and students may revise and resubmit until they meet the standard. This shifts the class culture from 'how many points can I earn' to 'what does it mean to really understand this material,' and it dramatically reduces the grade disputes I see. Students tell me the rubric makes their expectations clear and they feel more in control of their learning."

**Source**: Nilson, L. B. (2015). *Specifications Grading: Restoring Rigor, Motivating Students, and Saving Faculty Time.* Stylus Publishing. University of Chicago CS 121/301 spec grading documents (available publicly). SIGCSE 2023 workshop on mastery learning with specs grading.

**Best used in**: **Assessment** section.

---

### Authentic Assessment vs. Exams

**What it is**: **Authentic assessment** evaluates students on tasks that resemble real professional practice — e.g., code review, technical reports, presentations, code from specifications, debugging sessions. This contrasts with decontextualized exams (algorithm puzzles, trivia questions) that measure out-of-context recall. The case for authentic assessment in CS is strong: we want to know whether a student can debug a system, design a solution, communicate a technical idea — not whether they can solve a sorting algorithm on a whiteboard under time pressure.

**Essence for your statement**: "I weight authentic assessments (code review exercises, technical reports, presentations, multi-week projects) heavily because they better predict professional capability than timed exams. Where I do use exams, I design them to test applied reasoning — e.g., debugging an unfamiliar program, predicting output, reasoning about trade-offs — not decontextualized recall."

**Source**: Wiggins, G. (1998). *Authentic Assessment.* Jossey-Bass. In CS: McCauley, R. & M. W. (2008). Authentic assessment in CS. *SIGCSE '08.*

**Best used in**: **Assessment** section.

---

### Auto-Grading Pitfalls

**What it is**: Auto-graders (e.g., MOSS, Gradescope, local test suites) are widely used for programming assignment assessment but carry significant pedagogical risks: students can learn to pass tests without understanding the underlying logic; subtle bugs (e.g., off-by-one errors, style violations) may go undetected; gaming behavior (writing to the test rather than solving the problem) can emerge. Effective use of auto-graders requires supplementing with human review — code style, documentation quality, algorithmic approach are not captured by test suites alone.

**Essence for your statement**: "I use auto-graders for functionality checking but pair them with human code review for style, documentation, and design — auto-graders can verify that code works, but they cannot evaluate whether code is maintainable, readable, or well-architected. I am transparent with students about what the auto-grader can and cannot evaluate, and I give them feedback through code review so they understand the professional standards they are building toward."

**Source**: Singh, A. et al. (2013). Auto-grading in CS: A practical approach. *IEEE Transactions on Education.* Cartwright, E. & A. Sheehy (2020). Auto-grading and its impact on learning. *SIGCSE '20.*

**Best used in**: **Assessment** section.

---

### Code Review as Assessment

**What it is**: Code review — systematically reading and critiquing peer or one's own code — is simultaneously a professional practice and an assessment method. Peer code review develops critical evaluation skills that deepen understanding; it also normalizes receiving and giving critique, a key professional skill. Structuring code review as an assessed activity (with a rubric for critique quality, not just code quality) is an underused but powerful CS assessment method.

**Essence for your statement**: "I have students conduct peer code reviews as assessed activities — they receive a rubric for the quality of their critique (constructive, specific, referencing evidence from the code), not just the quality of the code they review. This develops professional communication skills and deepens their understanding: explaining why code is problematic requires deeper comprehension than writing it."

**Source**: Zoeller, A. (2019). Code review as a pedagogical tool. *SIGCSE '19.* In CS education: de Raadt, M. et al. (2019). Peer code review in CS education. *ACE '19.*

**Best used in**: **Assessment** section.

---

## Key Venues for Deeper Reading

| Venue | Focus | Best For |
|---|---|---|
| **SIGCSE** (ACM) | Broad CS education practice | General CS pedagogy, curriculum design |
| **ICER** | Empirical computing education research | Research methodology, theory-grounded studies |
| **ITiCSE** | Innovation in CS education | Tools, languages, pedagogy innovations |
| **Koli Calling** | Programming education research | Threshold concepts, novice learning, Parsons problems |
| **ACM TOCE** (Journal) | Peer-reviewed computing education research | Full-length empirical studies |
| **Computer Science Education** (Taylor & Francis) | Peer-reviewed CS ed research | European CS ed community |
| **Mastery Grading Conference** (masterygrading.com) | Specifications/mastery grading | Assessment reform |

---

## How to Use This Document

**Philosophy section**: Select 2–3 foundational frameworks (active learning, Bloom's taxonomy, constructive alignment) to anchor your overall stance. Don't claim everything — "My teaching philosophy is grounded in active learning, constructive alignment, and cognitive load theory" is credible. "I do everything" is not.

**Methods section**: Describe specific techniques you use and cite the evidence base — e.g., "I use Parsons problems in CS1 because research shows they reduce extraneous cognitive load and bridge the gap between code reading and writing (Denny et al., ICER '08)."

**Supervision section**: Name at most 1–2 frameworks (e.g., Vitae RDF + cognitive apprenticeship) and describe concretely how they manifest in your practice (weekly 1:1s, written feedback, scaffolding then fading).

**Assessment section**: Explain your philosophy (authentic > exam-heavy, specs grading) and your rationale — "I use specifications grading because research shows it reduces gaming behavior and improves mastery (Nilson, 2015), and because it better aligns with how students actually learn to program."

**Inclusion section**: Name-check Margolis & Fisher and/or UDL to signal awareness of the research landscape, then get specific — "I address belonging by using anonymous early assessments to minimize stereotype threat (Steele), and I design my physical and digital classroom environments to avoid ambient belonging cues (Cheryan et al.)."
