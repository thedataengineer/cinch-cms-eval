# Quick Start Checklist – CINCH CMS Evaluation Framework

## ✅ Pre-Workshop Prep (Day 1-2)

- [ ] **Understand the problem**
  - Read: SOLUTION_APPROACH.md (15 min)
  - Watch: Run `streamlit run cms_eval_poc.py` (5 min)
  - Explore: All 4 tabs in the app (10 min)

- [ ] **Set up your local environment**
  ```bash
  git clone https://github.com/accionlabs/cinch-cms-eval.git
  cd cinch-cms-eval
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  export ANTHROPIC_API_KEY="sk-ant-..."
  streamlit run cms_eval_poc.py
  ```

- [ ] **Test both modes**
  - Quick scoring mode (local data, no API calls)
  - AI mode (calls Claude, requires API key)

- [ ] **Prepare talking points** (for workshop)
  - Why: "We're overcomplicating vendor selection with gut feel"
  - What: "This is an ontology + scoring framework"
  - How: "Interactive, what-if analysis in real-time"
  - Who: "Designed for you + product + tech team"

---

## ✅ Workshop Day (Day 3, 90 minutes)

### Pre-Workshop (10 min)
- [ ] Test app connection (no lag, quick scoring works)
- [ ] Have browser open to: `http://localhost:8501`
- [ ] Print out 3-page guide (ARCHITECTURE_VISUAL.md) for attendees

### Introduction (5 min)
- [ ] Show problem statement (5 CMS → 3)
- [ ] Show ontology diagram (7 capabilities)
- [ ] Show 3 recommendation stacks

### Demo 1: Quick Scoring (10 min)
- [ ] Walk through Platform Scores tab
- [ ] Show default: 6 platforms ranked
- [ ] Point out strengths/weaknesses (HubSpot weak at content modeling)
- [ ] Ask: "Does this match your gut feeling?"

### Demo 2: Interactive Adjustments (15 min)
- [ ] Ask: "What if conversion lift is more important?"
- [ ] Adjust weight: conversion_lift → 40% (from 25%)
- [ ] Watch scores update live
- [ ] Ask: "Does this ranking feel right now?"
- [ ] Try: 3-4 different weight scenarios
- [ ] Discuss: Tradeoffs revealed by scoring

### Demo 3: AI Analysis (15 min)
- [ ] Select: "AI-Powered Analysis" mode
- [ ] Pick top platform from quick mode
- [ ] Run Claude evaluation (takes ~2 sec)
- [ ] Show structured output: capabilities, strengths, weaknesses
- [ ] Discuss: "How does Claude's assessment compare to your knowledge?"

### Demo 4: Recommended Stacks (20 min)
- [ ] Show: Option A (HubSpot + Headless + A/B tool)
  - Pros/cons discussion
  - Fit score: 0.72
- [ ] Show: Option B (Pure Headless + CDP)
  - Pros/cons discussion
  - Fit score: 0.85 ← Best for flexibility
- [ ] Show: Option C (Composable CMS + HubSpot)
  - Pros/cons discussion
  - Fit score: 0.88 ← Best balanced
- [ ] Poll: Which resonates? (A, B, C, or need more analysis?)

### Decision & Commitment (15 min)
- [ ] "Based on what you've seen, what's your gut telling you?"
- [ ] "Let's use that to guide Phase 2: deep dive on Option X"
- [ ] Commit to next steps:
  - [ ] Assign owner for deep dive
  - [ ] Set review date (1 week)
  - [ ] Identify 1-2 additional evals to run

---

## ✅ Phase 2: Validation (Week 2)

- [ ] **Gather real data**
  - Vendor docs (Contentful, Sanity, Composable CMS)
  - Pricing sheets (license tiers, support)
  - Integration lists (HubSpot, analytics, martech)

- [ ] **Refine ontology** (based on workshop feedback)
  - "Did we miss any capabilities?"
  - "Are weights realistic for our use cases?"
  - Update PLATFORMS_DATA with real scores

- [ ] **Run AI evaluations** on top 3 candidates
  ```python
  from lib_core import PlatformEvaluator, CMSOntology
  
  onto = CMSOntology.from_file("data/cms_ontology.json")
  evaluator = PlatformEvaluator(api_key="sk-ant-...")
  
  for platform in ["Contentful", "Sanity", "Composable CMS"]:
      assessment = evaluator.evaluate(platform, onto)
      print(f"{platform}: {assessment.overall_fit_score:.2f}")
  ```

- [ ] **Document findings**
  - Compare Claude assessment vs manual eval
  - Identify any blind spots
  - Refine prompts if needed

- [ ] **Prepare recommendation** (1-pager for Barry)
  - Which stack wins
  - Why (top 3 reasons)
  - Next steps (Phase 3: TCO, migration)

---

## ✅ Phase 3: Extended Analysis (Week 3-4)

Choose 2-3 extensions:

- [ ] **TCO Calculator**
  - License costs (platform + support)
  - People costs (% team needed)
  - Integration costs (APIs, custom code)
  - Migration costs (implementation, training)
  - 5-year NPV comparison

- [ ] **Migration Complexity Scorer**
  - Data mapping effort (legacy → new)
  - Team training time
  - Workflow redesign complexity
  - Risk scoring (vendor viability, etc.)

- [ ] **Team Readiness Assessment**
  - Skills gap analysis (headless knowledge)
  - Training plan (internal vs external)
  - Hiring needs (frontend engineers, etc.)

- [ ] **Fetch Real Vendor Docs**
  - Parse capability info from Contentful/Sanity/etc. docs
  - Update PLATFORMS_DATA with live scores
  - Cache assessments to avoid repeated API calls

---

## ✅ Phase 4: Decision & Delivery (Week 5)

- [ ] **Board presentation**
  - 1 slide: Problem statement
  - 1 slide: 3 recommendation stacks
  - 1 slide: Why Stack X wins
  - 1 slide: Timeline + budget
  - 1 slide: Next steps (RFP, vendor meetings, POC)

- [ ] **RFP preparation**
  - Scorecard template (based on ontology)
  - Must-haves vs nice-to-haves
  - Evaluation criteria (weighted)
  - Timeline

- [ ] **Vendor meetings**
  - Schedule demos for top 2 platforms
  - Use scorecard during demo
  - Take notes on real capabilities vs claimed

- [ ] **POC plan**
  - Simple enrollment flow
  - Test: content modeling, personalization, delivery
  - Success metrics (speed, ease, flexibility)
  - Duration: 4 weeks

---

## 📋 Troubleshooting

### "App won't start"
```bash
# Check Python version (3.8+)
python --version

# Check pip installed packages
pip list | grep -E "streamlit|anthropic|pandas"

# Reinstall fresh
pip install -r requirements.txt --force-reinstall
```

### "Claude API fails"
```bash
# Check API key is set
echo $ANTHROPIC_API_KEY

# Test API call
python -c "import anthropic; c = anthropic.Anthropic(); print('OK')"

# Check quota (API dashboard)
# https://console.anthropic.com/account/usage
```

### "Scores don't match my intuition"
- [ ] Check ontology weights (Tab 2)
- [ ] Verify platform capability scores (in code)
- [ ] Adjust business outcome weights in sidebar
- [ ] Re-run evaluation

### "Want to add a new platform"
- [ ] Add to PLATFORMS_DATA (5 min)
  ```python
  PLATFORMS_DATA["NewCMS"] = {
      "type": "...",
      "capabilities": {...}
  }
  ```
- [ ] Rerun app
- [ ] See where it ranks

---

## 🎯 Success Indicators

By end of Week 5, you should have:

- ✅ **Unified recommendation** – "We're going with Stack X"
- ✅ **Stakeholder buy-in** – "80%+ agree with choice"
- ✅ **Documented reasoning** – "Here's why we scored Y higher than Z"
- ✅ **Budget approval** – "Finance OK'd the investment"
- ✅ **Timeline commitment** – "12-month migration plan"
- ✅ **RFP ready** – "We'll send to vendors this week"

---

## 📞 Getting Help

**From this framework:**
- Read: SOLUTION_APPROACH.md (all your "why" questions)
- Read: ARCHITECTURE_VISUAL.md (how it works, step-by-step)
- Run: `streamlit run cms_eval_poc.py` (try it yourself)

**From Python code:**
- Docs in lib_core.py (docstrings on all classes)
- Examples in README.md (usage patterns)
- Tests: tests/*.py (unit test examples)

**From Anthropic:**
- Claude models docs: https://docs.anthropic.com/
- Structured outputs: https://docs.anthropic.com/guides/structured-outputs
- API status: https://status.anthropic.com/

---

## 📅 Timeline At-a-Glance

```
Day 1-2:   Setup & Exploration (1 hour)
Day 3:     Interactive Workshop (90 min)
Week 2:    Validation & Refinement (4 hours)
Week 3-4:  Extended Analysis (8-16 hours, pick 2-3 topics)
Week 5:    Final Recommendation & Decision (4 hours)

TOTAL:     ~40 hours over 5 weeks
           (vs 120+ hours of manual RFP/evaluation)
```

---

## 🚀 Ready to Go?

1. **Setup** – Run setup commands ✅
2. **Explore** – Open the app in browser ✅
3. **Workshop** – Gather team, run demos ✅
4. **Decide** – Pick Stack A, B, or C ✅
5. **Deep Dive** – TCO, migration, team readiness ✅
6. **Recommend** – Board presentation + RFP ✅
7. **Execute** – Vendor selection + POC ✅

**You're 30 minutes away from having the framework running.**

Let's go.

---

**Version:** 1.0  
**Last Updated:** 2025-12-11  
**Questions?** Check SOLUTION_APPROACH.md or open an issue in GitHub.
