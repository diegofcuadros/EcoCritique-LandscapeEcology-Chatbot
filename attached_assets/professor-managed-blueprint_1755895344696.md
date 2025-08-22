# Landscape Ecology Socratic Chatbot
## Complete Blueprint for Professor-Managed System (No IT Support)

---

## 1. EXECUTIVE SUMMARY

### What This System Does
- **Students** interact with a Socratic AI tutor that guides them through article analysis
- **Professor** updates articles weekly with simple file uploads
- **System** automatically logs all interactions for grading
- **No IT support** needed - runs entirely on free cloud services

### Key Constraints Addressed
- ✅ 40 students (manageable load)
- ✅ Professor-maintainable 
- ✅ Free hosting (GitHub + Google services)
- ✅ Weekly article updates (drag-and-drop simple)
- ✅ Complete interaction logging for assessment

---

## 2. SYSTEM ARCHITECTURE OVERVIEW

```
SIMPLIFIED THREE-TIER ARCHITECTURE

Tier 1: Student Interface (GitHub Pages)
    ↓ 
Tier 2: AI Processing (Google Colab + Hugging Face, LLM like llama?)
    ↓
Tier 3: Data Storage (Google Sheets + Drive?)
```

### Detailed Component Map

```
[Student Browser]
        ↓
[GitHub Pages Website] (Free, always available)
        ↓
[Google Colab Notebook] (Free GPU, runs your AI)
        ↓                     ↓
[Google Sheets]        [Google Drive]
(Interaction Logs)     (Articles & Knowledge)
        ↓
[Professor's Grading View]
```

---

## 3. DETAILED WORKFLOW DESCRIPTIONS

### 3.1 WEEKLY PROFESSOR WORKFLOW (5 minutes/week)

```
Monday Morning Routine:
1. Open Google Drive folder "Week_X_Articles"
2. Drag and drop this week's PDF article
3. Open "article_config.txt" template
4. Fill in:
   - Article title
   - Main concepts to explore
   - Key questions to avoid giving away
5. Save
6. System automatically updates within 5 minutes
```

### 3.2 STUDENT INTERACTION WORKFLOW

```
Student Experience:
1. Visit: yoursite.github.io/chatbot
2. Enter weekly access code (you provide in class)
3. Select their name from dropdown
4. Click "Start Discussion"
5. Chat for 15-20 minutes
6. System guides them through article analysis
7. Session auto-saves when they close browser
```

### 3.3 CHATBOT CONVERSATION FLOW

```
Stage 1: Orientation (0-3 minutes)
├── Bot: "I see we're discussing [Article Title]. Have you read it?"
├── Confirms basic comprehension
└── Identifies starting knowledge level

Stage 2: Guided Exploration (3-10 minutes)
├── Progressive questioning based on responses
├── Never provides answers directly
├── Redirects when student asks for answers
└── Scaffolds to deeper understanding

Stage 3: Critical Analysis (10-15 minutes)
├── Challenges assumptions
├── Connects to course concepts
├── Encourages methodology critique
└── Explores limitations

Stage 4: Synthesis (15-20 minutes)
├── Integrates with previous weeks
├── Relates to landscape ecology principles
└── Prepares for class discussion
```

### 3.4 GRADING WORKFLOW

```
Professor's Weekly Grading (2 hours total):
1. Open Google Sheets "Week_X_Interactions"
2. See dashboard with:
   - Each student's engagement time
   - Depth of questioning reached
   - Key concepts explored
   - Auto-generated participation score
3. Click student name to see full transcript
4. Adjust auto-score if needed
5. Export to Canvas gradebook
```

---

## 4. TECHNICAL INFRASTRUCTURE DETAILS

### 4.1 What Lives Where

**GitHub Repository Structure:**
```
landscape-ecology-chatbot/
├── index.html              (Main chatbot interface)
├── styles.css             (Visual design)
├── chatbot.js             (Connection logic)
├── config/
│   └── course_info.json   (Basic course settings)
├── docs/                  (Instructions for students)
└── README.md              (Setup documentation)
```

**Google Drive Structure:**
```
Landscape_Ecology_Chatbot/
├── Core_Knowledge/
│   ├── landscape_ecology_concepts.txt
│   ├── common_misconceptions.txt
│   └── socratic_prompts.json
├── Weekly_Articles/
│   ├── Week_1/
│   │   ├── article.pdf
│   │   ├── article_config.txt
│   │   └── expected_insights.txt
│   ├── Week_2/
│   └── ...Week_8/
├── Question_Templates/
│   ├── comprehension_questions.txt
│   ├── analysis_questions.txt
│   └── synthesis_questions.txt
└── Grading_Rubrics/
    └── interaction_rubric.txt
```

**Google Sheets Structure:**
```
"Landscape_Ecology_Interactions_Fall2024"
├── Tab: Student_Roster
├── Tab: Week_1_Logs
├── Tab: Week_2_Logs
├── ...
├── Tab: Week_8_Logs
├── Tab: Grade_Summary
└── Tab: Analytics_Dashboard
```

### 4.2 The AI Brain (Simplified)

**Option A: Hugging Face Spaces (Recommended)**
- Free tier sufficient for 40 students
- No setup required
- Reliable uptime
- Simple API connection

**Option B: Google Colab**
- More control
- Free GPU access
- Requires daily restart
- Slightly more complex

**Option C: Hybrid**
- Hugging Face for stable deployment
- Colab for testing/development

---

## 5. CONTENT PREPARATION REQUIREMENTS

### 5.1 What You Need Before Starting

**Essential Documents to Prepare:**

1. **Core Knowledge Base** (One-time setup)
   - [ ] List of 50 key landscape ecology concepts with definitions
   - [ ] 20 common student misconceptions about landscape ecology
   - [ ] 10 fundamental theories (brief explanations)
   - [ ] Connections between major topics

2. **Weekly Articles** (8 articles total)
   - [ ] Week 1: Introduction/pattern recognition article
   - [ ] Week 2: Landscape metrics article
   - [ ] Week 3: Spatial statistics article
   - [ ] Week 4: Connectivity/fragmentation article
   - [ ] Week 5: Disturbance dynamics article
   - [ ] Week 6: Species-landscape interactions article
   - [ ] Week 7: Conservation planning article
   - [ ] Week 8: Climate change/future directions article

3. **For Each Article:**
   ```
   Required Preparation:
   - PDF of article
   - 3-5 main learning objectives
   - 5-10 key concepts to explore
   - 3-5 potential misconceptions
   - 2-3 connections to lecture material
   - What answers to AVOID revealing
   ```

4. **Grading Rubric Components:**
   - [ ] Points for engagement duration (suggested: 5-20 minutes)
   - [ ] Points for depth reached (comprehension → evaluation)
   - [ ] Points for concepts explored
   - [ ] Points for critical thinking demonstrated
   - [ ] Bonus for exceptional insights

### 5.2 Question Bank Structure

```
SOCRATIC QUESTION PROGRESSION TEMPLATES

Level 1 - Comprehension (Surface)
├── "What is the main research question?"
├── "Can you identify the study system?"
└── "What methods did they use?"

Level 2 - Analysis (Deeper)
├── "Why might they have chosen this approach?"
├── "What patterns do you see in the data?"
└── "How do the results support their hypothesis?"

Level 3 - Synthesis (Integration)
├── "How does this relate to [previous week's concept]?"
├── "What would Turner et al. say about this?"
└── "Can you connect this to landscape metrics?"

Level 4 - Evaluation (Critical)
├── "What are the hidden assumptions?"
├── "How could the methodology be improved?"
└── "What alternative explanations exist?"
```

---

## 6. DEVELOPMENT PLAN - PROFESSOR-FRIENDLY APPROACH

### Phase 0: Preparation 
**Your Tasks:**
1. Create Google account for the project
2. Gather 8 PDF articles
3. Write learning objectives for each article
4. Create basic concept list

**Deliverable:** All content ready for system

### Phase 1: Infrastructure Setup 
**Developer Tasks (You with detailed instructions):**
1. Create GitHub account and repository
2. Set up Google Sheets with correct permissions
3. Create Google Drive folder structure
4. Set up Hugging Face Space

**Deliverable:** All platforms connected

### Phase 2: Basic Chatbot 
**What Gets Built:**
1. Simple question-answer system
2. Connection between website and AI
3. Basic logging to Google Sheets
4. Article loading system

**Your Testing:** Can it ask questions about an article?

### Phase 3: Socratic Logic 
**What Gets Added:**
1. Progressive questioning
2. Never-give-answers logic
3. Misconception detection
4. Depth tracking

**Your Testing:** Does it guide rather than tell?

### Phase 4: Student Interface 
**Polish Added:**
1. Clean, intuitive design
2. Progress indicators
3. Time tracking
4. Auto-save functionality

**Your Testing:** Is it student-friendly?

### Phase 5: Grading Dashboard 
**Final Components:**
1. Instructor view in Google Sheets
2. Automated scoring suggestions
3. Transcript highlighting
4. Batch grading tools

**Your Testing:** Can you grade efficiently?

### Phase 6: Pilot Testing 
**Testing Protocol:*
1. Test with 3-5 volunteer students
2. Run through one complete article
3. Gather feedback
4. Make adjustments

**Deliverable:** System ready for Fall 2024

---

## 7. MAINTENANCE & OPERATIONS

### 7.1 Weekly Maintenance Tasks (Professor)

**Every Sunday Evening (10 minutes):**
```
1. Upload next week's article to Google Drive
2. Update article_config.txt with key points
3. Generate weekly access code
4. Test with a sample question
5. Check previous week's logs downloaded
```

### 7.2 Per-Semester Tasks

**Beginning of Semester:**
- Update student roster in Google Sheets
- Reset interaction logs
- Update syllabus with chatbot URL
- Create backup of previous semester

**End of Semester:**
- Download all interaction logs
- Generate participation report
- Archive to university storage
- Clear for next semester

### 7.3 Troubleshooting Guide

**Common Issues & Solutions:**

| Problem | Solution | Time to Fix |
|---------|----------|-------------|
| Students can't access | Check GitHub Pages status | 2 min |
| AI not responding | Restart Hugging Face Space | 5 min |
| Logs not saving | Check Google Sheets permissions | 3 min |
| Article not loading | Verify file name in Drive | 2 min |
| Slow responses | Check concurrent users | 5 min |

---

## 8. RESOURCE REQUIREMENTS & COSTS

### 8.1 Free Tier Limits & Management

**GitHub Pages:**
- Limit: 100GB bandwidth/month
- 40 students × 8 weeks × 5MB = 1.6GB ✅
- Cost: $0

**Hugging Face Spaces:**
- Limit: 1000 hours/month free
- 40 students × 8 weeks × 0.5 hours = 160 hours ✅
- Cost: $0

**Google Services:**
- Drive: 15GB free (need ~1GB)
- Sheets: No practical limit
- Cost: $0

**Total Cost: $0/semester**


---

## 9. DATA PRIVACY & COMPLIANCE

### 9.1 Student Data Handling

**What's Collected:**
- Student name (from roster)
- Interaction timestamps
- Chat transcripts
- No personal information



### 9.2 Required Disclaimers

**For Syllabus:**
```
"This course uses an AI tutoring assistant for article discussions. 
Your interactions are logged for grading purposes only and deleted 
at semester end. No personal data is collected. Participation 
indicates consent to this educational use."
```

---

## 10. SUCCESS METRICS & EVALUATION

### 10.1 Technical Success Criteria

- [ ] 95% uptime during semester
- [ ] <5 second response time
- [ ] Zero data loss incidents
- [ ] All students can access weekly

### 10.2 Pedagogical Success Criteria

- [ ] 80% students reach "analysis" level minimum
- [ ] Average 15+ minute engagement
- [ ] Improved article quiz scores
- [ ] Positive correlation with exam performance

### 10.3 Evaluation Methods

**Weekly Tracking:**
- Participation rates
- Average engagement time
- Technical issues reported

**End-of-Semester Survey:**
- Usefulness for learning
- Technical ease of use
- Suggested improvements

---

## 11. STEP-BY-STEP ACTION PLAN

### Week 1: Preparation
- [ ] Day 1: Create dedicated Google account
- [ ] Day 2: Gather all 8 articles
- [ ] Day 3: Write learning objectives
- [ ] Day 4: Create concept list
- [ ] Day 5: Draft grading rubric

### Week 2: Account Setup
- [ ] Day 1: Create GitHub account
- [ ] Day 2: Create Hugging Face account
- [ ] Day 3: Set up Google Drive folders
- [ ] Day 4: Create Google Sheets template
- [ ] Day 5: Test all connections

### Week 3-4: Get Developer Help
- [ ] Find CS graduate student or hire freelancer
- [ ] Share this blueprint document
- [ ] Set up weekly check-ins
- [ ] Test basic functionality

### Week 5-8: Development & Testing
- [ ] Weekly testing of new features
- [ ] Provide feedback to developer
- [ ] Test with sample articles
- [ ] Refine question templates

### Week 9: Pilot Testing
- [ ] Recruit 5 student volunteers
- [ ] Run full article discussion
- [ ] Collect feedback
- [ ] Make final adjustments

### Week 10: Launch Preparation
- [ ] Final testing
- [ ] Create student instructions
- [ ] Update syllabus
- [ ] Ready for Fall 2024!

---

## 12. GETTING HELP

### If You Need Technical Assistance

**Option 1: Hire a Student Developer**
- Post in CS department
- 40-60 hours total work
- $15-25/hour typical
- Total cost: $600-1500

**Option 2: Freelancer**
- Post on Upwork/Fiverr
- Share this blueprint
- Get fixed-price quote
- Typical: $1000-2000

**Option 3: University Resources**
- Check with campus IT for student developers
- Educational technology center
- Computer science capstone projects

### Skills Needed in Developer
- Basic web development (HTML/JavaScript)
- Google APIs experience
- Python (for AI connection)
- GitHub familiarity

---

## APPENDIX A: Emergency Procedures

**If System Goes Down During Semester:**
1. Immediate: Post announcement on Canvas
2. Backup: Have students email their discussions
3. Recovery: Follow troubleshooting guide
4. Alternative: In-class discussion for that week

**If You Need to Switch Articles Last-Minute:**
1. Upload new PDF to correct week folder
2. Update config file with basic points
3. Test with one sample question
4. Notify students of change

---

## APPENDIX B: Expansion Possibilities

**Future Enhancements (After Successful First Semester):**
- Add peer review features
- Include multimedia articles
- Create student collaboration mode
- Develop mobile app
- Add multilingual support
- Export analytics for research