# CINCH CMS Evaluation – Visual Architecture & Quick Reference

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER (Interactive)                         │
│                  Streamlit Web Interface                        │
│  ┌───────────────┬────────────────┬────────────┬──────────────┐ │
│  │ Scores Tab   │ Ontology Tab   │ Stacks Tab │ Report Tab   │ │
│  └───────────────┴────────────────┴────────────┴──────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
         ┌──────▼──────┐            ┌────────▼────────┐
         │  Quick Mode │            │  AI Mode        │
         │ (Local data)│            │ (Claude API)    │
         └──────┬──────┘            └────────┬────────┘
                │                            │
         ┌──────▼────────────────────────────▼──────┐
         │     EVALUATION ENGINE                     │
         │  ┌─────────────────────────────────────┐ │
         │  │ 1. CMSOntology (7 capabilities)    │ │
         │  │ 2. PlatformEvaluator (LLM + JSON)  │ │
         │  │ 3. CapabilityScorer (0-1 scale)    │ │
         │  │ 4. ReportGenerator (MD/DOCX)       │ │
         │  └─────────────────────────────────────┘ │
         └──────┬───────────────────────────────┬──┘
                │                               │
         ┌──────▼──────┐               ┌────────▼────────┐
         │ Local Data  │               │ Claude API      │
         │             │               │ Structured JSON │
         │ PLATFORMS_  │               │                 │
         │ DATA dict   │               │ endpoint:       │
         │             │               │ messages.create │
         │ 6 CMS:      │               │                 │
         │ • HubSpot   │               │ model:          │
         │ • Contentful│               │ claude-3.5-     │
         │ • Liferay   │               │ sonnet-20241022 │
         │ • Sitecore  │               │                 │
         │ • Sanity    │               │ response_       │
         │ • Composable│               │ format:         │
         │             │               │ json_schema     │
         └─────────────┘               │ (strict: true)  │
                                       │                 │
                                       └─────────────────┘
```

---

## Data Flow: Quick Scoring Mode

```
User selects:
  - Use cases: [paid_landing_pages, enrollment_funnel]
  - Business weights: {conversion_lift: 0.3, time_to_market: 0.2, ...}
           │
           ▼
┌─────────────────────────────────────────────────┐
│ For each platform in PLATFORMS_DATA:            │
│                                                 │
│ 1. Get capability_scores (0-3 scale)            │
│    {content_modeling: 3, delivery: 3, ...}     │
│                                                 │
│ 2. Calculate use_case_fit:                      │
│    For each selected use case:                  │
│      - Get required_capabilities                │
│      - Compare actual vs required               │
│      - Average across use cases                 │
│                                                 │
│ 3. Calculate business_fit:                      │
│    Average all capability scores / 3.0          │
│                                                 │
│ 4. Composite score:                             │
│    (use_case_fit × 0.6) + (business_fit × 0.4) │
│                                                 │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│ OUTPUT: Ranked Platform List                    │
│                                                 │
│ 1. Composable CMS     0.88  ← Best fit          │
│ 2. Contentful         0.82                      │
│ 3. Sanity             0.80                      │
│ 4. Liferay            0.65                      │
│ 5. HubSpot            0.61  ← Not great at CMS  │
│ 6. Sitecore           0.48  ← Too expensive     │
│                                                 │
└─────────────────────────────────────────────────┘
           │
           ▼
        Display in Streamlit
        Show strengths/weaknesses
        Generate recommendation
```

---

## Data Flow: AI-Powered Mode

```
User selects:
  - Platform: "Contentful"
  - Run "AI-Powered Analysis"
           │
           ▼
┌──────────────────────────────────────────────────┐
│ Build Claude Prompt:                             │
│                                                  │
│ "Assess Contentful against these capabilities:  │
│  - Content Modeling (scale 0-3)                 │
│  - Delivery & API                               │
│  - Personalization & Testing                    │
│  - Workflow & Governance                        │
│  - Integration Ecosystem                        │
│  - Performance & SEO                            │
│  - Operational                                  │
│                                                  │
│  CINCH Context:                                 │
│  - 20K+ paid views/day                          │
│  - Consolidate 5 CMS → 3 platforms              │
│  - Goal: Improve conversion rates               │
│  - Avoid Sitecore, avoid lightweight tools      │
│                                                  │
│  Return as JSON with:                           │
│  - capability_scores (object, each 0-3)         │
│  - strengths (array, 3 items)                   │
│  - weaknesses (array, 3 items)                  │
│  - best_for_use_case (string)                   │
│  - overall_fit_score (0-1)"                     │
│                                                  │
└──────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│ Call Claude API with Structured Output           │
│                                                  │
│ response = client.messages.create(               │
│   model="claude-3-5-sonnet-20241022",            │
│   max_tokens=1000,                              │
│   response_format={                             │
│     "type": "json_schema",                      │
│     "json_schema": {                            │
│       "name": "platform_assessment",            │
│       "schema": {...},  ← Enforced schema       │
│       "strict": True    ← No deviations allowed  │
│     }                                            │
│   },                                             │
│   messages=[{"role": "user", "content": prompt}]│
│ )                                                │
│                                                  │
└──────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│ Claude MUST return valid JSON matching schema    │
│ (or API fails)                                   │
│                                                  │
│ {                                                │
│   "platform": "Contentful",                     │
│   "capability_scores": {                        │
│     "content_modeling": 3,                      │
│     "delivery": 3,                              │
│     "personalization": 1,  ← Weakness!          │
│     "workflow": 2,                              │
│     "integrations": 2,                          │
│     "performance": 3,                           │
│     "operational": 3                            │
│   },                                             │
│   "strengths": [                                │
│     "Rich schema flexibility with JSON+...",    │
│     "Excellent API-first architecture...",      │
│     "Best-in-class page speed & CDN..."         │
│   ],                                             │
│   "weaknesses": [                               │
│     "No native A/B testing (need 3rd party)",   │
│     "Requires front-end team for display",      │
│     "Newer ecosystem with smaller support..."   │
│   ],                                             │
│   "best_for_use_case": "paid_landing_pages",   │
│   "overall_fit_score": 0.82                    │
│ }                                                │
│                                                  │
└──────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│ Parse JSON (guaranteed valid)                    │
│ Create PlatformAssessment object                 │
│ Display in Streamlit with commentary             │
│                                                  │
│ "Contentful: 0.82/1.0 overall fit"              │
│                                                  │
│ Strengths:                                       │
│ • Rich schema flexibility with JSON+...          │
│ • Excellent API-first architecture...            │
│ • Best-in-class page speed & CDN...              │
│                                                  │
│ Weaknesses:                                      │
│ • No native A/B testing (need 3rd party)         │
│ • Requires front-end team for display            │
│ • Newer ecosystem with smaller support...        │
│                                                  │
│ Best for: Paid landing pages                     │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Ontology Structure (JSON)

```json
{
  "capabilities": {
    "content_modeling": {
      "label": "Content Modeling",
      "facets": [
        "schema_flexibility",
        "relationship_support",
        "versioning",
        "multi_channel_support"
      ],
      "scale": "0-3",
      "importance": "critical"
    },
    "delivery": {
      "label": "Delivery & API",
      "facets": [
        "api_maturity",
        "headless_support",
        "cdn_integration",
        "performance_optimization"
      ],
      "scale": "0-3",
      "importance": "critical"
    },
    ...  // 5 more capabilities
  },

  "use_cases": {
    "paid_landing_pages": {
      "label": "High-velocity paid landing pages",
      "required_capabilities": {
        "personalization": 2,
        "delivery": 2,
        "integrations": 2
      }
    },
    ...  // 3 more use cases
  },

  "business_outcomes": {
    "conversion_lift": {
      "label": "Conversion rate lift (target: 10%+)",
      "weight": 0.25
    },
    ...  // 4 more outcomes
  }
}
```

---

## Platform Score Card Example

```
CONTENTFUL

Type:           Headless CMS
Category:       headless
Deployment:     SaaS
Cost Band:      $$
Traffic Fit:    20K+/day ✓

CAPABILITY SCORES (0-3 scale)
┌─────────────────────────────┬───┬────────────────────────┐
│ Capability                  │ ✓ │ Fit for CINCH          │
├─────────────────────────────┼───┼────────────────────────┤
│ Content Modeling            │ 3 │ STRONG – Rich schema   │
│ Delivery & API              │ 3 │ STRONG – Pure headless │
│ Personalization & Testing   │ 1 │ WEAK – Need partner    │
│ Workflow & Governance       │ 2 │ OK – Basic features    │
│ Integration Ecosystem       │ 2 │ OK – Growing partners  │
│ Performance & SEO           │ 3 │ STRONG – CDN built-in  │
│ Operational                 │ 3 │ STRONG – Great support │
└─────────────────────────────┴───┴────────────────────────┘

USE CASE FIT
• Paid Landing Pages:        2.67/3  (Good)
• Enrollment Funnel:         2.00/3  (OK, needs personalization partner)
• Multi-property:            2.67/3  (Good)
• Consolidation:             2.00/3  (OK, not strongest fit)

COMPOSITE SCORE:             0.82/1.0

RECOMMENDED STACK:           Contentful + Segment/mParticle (CDP)
ESTIMATED TIMELINE:          6 months implementation
COST BAND:                   $$
```

---

## Quick Reference: How to Adapt

### Add a New Capability

```python
CMS_ONTOLOGY["capabilities"]["my_capability"] = {
    "label": "My Capability Label",
    "facets": ["facet_1", "facet_2", "facet_3"],
    "scale": "0-3",
    "importance": "critical"  # or "high", "medium"
}
```

### Add a New Use Case

```python
CMS_ONTOLOGY["use_cases"]["my_use_case"] = {
    "label": "My Use Case Description",
    "required_capabilities": {
        "content_modeling": 2,      # Min required level (0-3)
        "delivery": 3,
        "personalization": 1
    }
}
```

### Add a New Platform

```python
PLATFORMS_DATA["MyCMS"] = {
    "type": "Headless CMS",
    "category": "headless",
    "deployment": "SaaS",
    "cost_band": "$$",
    "summary": "Brief description",
    "capabilities": {
        "content_modeling": 3,
        "delivery": 3,
        "personalization": 2,
        "workflow": 2,
        "integrations": 2,
        "performance": 3,
        "operational": 2
    }
}
```

### Adjust Business Outcome Weights

In Streamlit sidebar, use sliders. Or programmatically:

```python
outcome_weights = {
    "conversion_lift": 0.40,      # Up from 0.25
    "time_to_market": 0.20,       # Down from 0.25
    "operational_efficiency": 0.20,
    "flexibility": 0.10,
    "cost_efficiency": 0.10
}
# Normalize: sum = 1.0 ✓
```

---

## What's Pre-Implemented

✅ Ontology model (7 capabilities, 4 use cases, 5 outcomes)  
✅ Quick scoring (local data)  
✅ AI scoring (Claude structured output)  
✅ Interactive Streamlit UI (4 tabs)  
✅ 3 recommended architecture stacks  
✅ Report generation (Markdown, DOCX-ready)  
✅ Reusable Python library  

---

## What You Need to Add (Future Phases)

⬜ TCO calculator (license tiers, people, integration costs)  
⬜ Migration complexity scorer  
⬜ Team readiness assessment  
⬜ Fetch & parse vendor docs automatically  
⬜ Sensitivity analysis ("What if we weight X at 50%?")  
⬜ Gartner/Forrester quadrant data  
⬜ Integration with Figma for stakeholder decks  

---

## Success Metrics

- **User adoption:** "Did Barry use this to make the decision?"
- **Decision speed:** "Went from 4 weeks to 2 weeks of analysis"
- **Stakeholder alignment:** "Got buy-in from 80%+ of leadership team"
- **Recommendation quality:** "Recommendation proved sound in Phase 2 eval"
- **Extensibility:** "Reused framework for 2+ other vendor evaluations"

---

**Version:** 1.0  
**Last Updated:** 2025-12-11  
**Status:** PoC Complete, Ready for Interactive Workshop
