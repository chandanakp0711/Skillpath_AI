"""
===============================================================================
 growth_pathway.py  --  Personalised learning-roadmap generator
===============================================================================
Turns a skill-gap report into an actionable, time-boxed growth plan that adapts
to the student's readiness band and specific gaps:

    * Recommended skills (priority-ordered, with reasons)
    * Recommended portfolio projects
    * Recommended certifications (levelled Foundation -> Advanced)
    * Curated learning resources per skill (Coursera / Udemy / NPTEL / YouTube /
      freeCodeCamp ...)
    * Interview-preparation plan
    * Weekly learning roadmap
    * 30-day action plan
    * 90-day career-growth plan

The plans are generated dynamically — a Beginner gets a foundation-heavy plan, an
"Industry Ready" student gets a specialisation + interview + job-hunt plan.
===============================================================================
"""

from __future__ import annotations

from . import config
from .skill_gap import analyze_skill_gap


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #
def _resource_bucket(skill: str) -> str:
    """Map an arbitrary recommended skill onto a RESOURCE_LIBRARY key."""
    s = skill.lower()
    rules = [
        (("deep learning", "neural", "transformer", "llm"), "Deep Learning"),
        (("mlops", "experiment tracking", "model serving", "feature store"), "MLOps"),
        (("devops", "docker", "kubernetes", "ci/cd", "terraform", "ansible"), "DevOps"),
        (("data structure", "algorithm", "dsa"), "Data Structures & Algorithms"),
        (("react", "node", "web", "javascript", "html", "css", "front", "full"), "Web Development"),
        (("sql", "database"), "SQL"),
        (("cloud", "aws", "azure", "gcp", "networking"), "Cloud Computing"),
        (("cyber", "security", "ethical", "siem", "crypto"), "Cybersecurity"),
        (("data analysis", "analytics", "power bi", "tableau", "excel", "storytelling"), "Data Analysis"),
        (("machine learning", "ml", "feature engineering", "a/b", "statistic", "probability"), "Machine Learning"),
        (("python",), "Python"),
    ]
    for keywords, bucket in rules:
        if any(k in s for k in keywords):
            return bucket
    return ""


def resources_for_skill(skill: str) -> list[dict]:
    """Return a small curated resource list for a recommended skill."""
    bucket = _resource_bucket(skill)
    return config.RESOURCE_LIBRARY.get(bucket, config.DEFAULT_RESOURCES)


def _cert_level(name: str) -> str:
    """Heuristically classify a certification's difficulty level."""
    n = name.lower()
    if any(k in n for k in ("fundamental", "practitioner", "essentials", "entry",
                            "security+", "associate cloud", "cc)", "specialist",
                            "foundation")):
        return "Foundation"
    if any(k in n for k in ("professional", "specialty", "expert", "cka",
                            "advanced", "architect")):
        return "Advanced"
    return "Intermediate"


# --------------------------------------------------------------------------- #
#  Section builders
# --------------------------------------------------------------------------- #
def _recommended_skills(gap: dict, career: str) -> list[dict]:
    """Priority-ordered skills to learn, each with a reason."""
    spec = config.CAREERS[career]
    items: list[dict] = []
    seen: set[str] = set()

    def add(skill: str, reason: str, priority: str):
        if skill and skill not in seen:
            seen.add(skill)
            items.append({"skill": skill, "reason": reason, "priority": priority})

    for s in gap["missing_technical"]:
        add(s, f"Core technical skill for a {career}.", "High")
    for s in gap["missing_languages"]:
        add(s, f"Frequently required programming language for this role.", "High")
    for s in spec["learn_next"]:
        add(s, "Advances your depth and employability in this field.", "Medium")
    for s in gap["missing_soft"]:
        add(s, "Soft skill that strengthens interviews and teamwork.", "Medium")
    return items[:8]


def _interview_prep(gap: dict, career: str, profile: dict) -> dict:
    """Interview-preparation plan tailored to the role & the student's challenge."""
    spec = config.CAREERS[career]
    challenge = profile.get("learning_challenge", "")
    tips = [
        "Practise 2-3 coding/role problems daily on LeetCode / HackerRank.",
        f"Prepare 5 STAR stories that showcase {career.lower()} project work.",
        "Do at least 3 mock interviews (peer or platforms like Pramp).",
        "Build a one-page resume with quantified, impact-driven bullet points.",
    ]
    if "anxiety" in challenge.lower():
        tips.append("Reduce interview anxiety with timed mock drills and breathing routines.")
    if "resume" in challenge.lower():
        tips.append("Use the XYZ formula ('Accomplished X by doing Y, measured by Z') on every bullet.")
    if "networking" in challenge.lower():
        tips.append("Reach out to 3 professionals/alumni weekly on LinkedIn for referrals.")
    return {
        "topics": spec["interview_topics"],
        "tips": tips,
        "timeline": "Begin light prep from week 4; intensive prep in the final 3-4 weeks.",
    }


def _weekly_roadmap(skills: list[dict], gap: dict, career: str) -> list[dict]:
    """An ~8-week learning roadmap derived from the priority skills."""
    spec = config.CAREERS[career]
    roadmap: list[dict] = []
    week = 1
    # Weeks 1-N: one skill focus each (high-priority first).
    for item in skills[:5]:
        roadmap.append({
            "week": week,
            "focus": f"Learn {item['skill']}",
            "tasks": [
                f"Complete a structured course on {item['skill']}.",
                f"Take notes & build a mini-exercise applying {item['skill']}.",
                "Summarise learnings in a short blog/Notion page.",
            ],
        })
        week += 1
    # Project build weeks.
    project = spec["projects"][0] if spec["projects"] else "a portfolio project"
    roadmap.append({
        "week": week,
        "focus": "Start a portfolio project",
        "tasks": [f"Scope and begin: {project}.",
                  "Push code to GitHub with a clear README.",
                  "Apply the skills learned in weeks 1-5."],
    })
    week += 1
    roadmap.append({
        "week": week,
        "focus": "Finish project + first certification",
        "tasks": [f"Complete and document: {project}.",
                  f"Begin studying for: {spec['certifications'][0]}.",
                  "Add the project to your resume & LinkedIn."],
    })
    week += 1
    roadmap.append({
        "week": week,
        "focus": "Interview preparation & applications",
        "tasks": ["Daily problem-solving practice.",
                  "2 mock interviews + resume review.",
                  "Apply to 5-10 relevant roles/internships."],
    })
    return roadmap


def _plan_30_day(skills: list[dict], gap: dict, career: str, band: str) -> list[dict]:
    """A focused 4-week / 30-day action plan."""
    spec = config.CAREERS[career]
    top_skills = [s["skill"] for s in skills[:4]] or ["core skills"]
    foundation = (band in ("Beginner", "Intermediate"))
    return [
        {"phase": "Days 1-7", "title": "Foundations & setup",
         "goals": [
             f"Set a daily 2-hour learning habit focused on {top_skills[0]}.",
             "Set up GitHub, LinkedIn and a learning tracker.",
             f"Finish an intro course on {top_skills[0]}.",
         ]},
        {"phase": "Days 8-15", "title": "Core skill building",
         "goals": [
             f"Deep-dive into {', '.join(top_skills[1:3]) or top_skills[0]}.",
             "Solve 20+ practice problems / exercises.",
             "Start sketching your first portfolio project.",
         ]},
        {"phase": "Days 16-23", "title": "Build & apply",
         "goals": [
             f"Build {spec['projects'][0]}.",
             "Publish the project to GitHub with documentation.",
             ("Revisit fundamentals where you struggled."
              if foundation else f"Begin {spec['certifications'][0]}."),
         ]},
        {"phase": "Days 24-30", "title": "Polish & visibility",
         "goals": [
             "Update resume & LinkedIn with the new project.",
             "Write a short post about what you built.",
             "Do 1 mock interview and gather feedback.",
         ]},
    ]


def _plan_90_day(skills: list[dict], gap: dict, career: str, band: str) -> list[dict]:
    """A 3-month / 90-day career-growth plan."""
    spec = config.CAREERS[career]
    top_skills = [s["skill"] for s in skills[:6]] or ["core skills"]
    return [
        {"month": "Month 1", "title": "Foundation",
         "milestones": [
             f"Master the fundamentals: {', '.join(top_skills[:2])}.",
             "Complete 1 structured course + 1 mini-project.",
             "Establish a consistent daily study routine.",
         ]},
        {"month": "Month 2", "title": "Application & projects",
         "milestones": [
             f"Build 2 portfolio projects (e.g. {spec['projects'][0]}).",
             f"Learn intermediate skills: {', '.join(top_skills[2:4]) or 'advanced topics'}.",
             f"Start the {spec['certifications'][0]} certification.",
         ]},
        {"month": "Month 3", "title": "Specialise & launch",
         "milestones": [
             f"Earn {spec['certifications'][0]} and start a second cert.",
             "Complete intensive interview preparation & 5+ mock interviews.",
             "Apply to 20+ roles/internships and seek referrals.",
         ]},
    ]


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
def generate_pathway(profile: dict, career: str, gap: dict | None = None) -> dict:
    """Generate the full personalised growth pathway for a target career."""
    if gap is None:
        gap = analyze_skill_gap(profile, career)
    band = gap["readiness_band"]

    skills = _recommended_skills(gap, career)
    learning_resources = [
        {"skill": item["skill"], "resources": resources_for_skill(item["skill"])}
        for item in skills
    ]
    certifications = [
        {"name": c, "level": _cert_level(c)}
        for c in config.CAREERS[career]["certifications"]
    ]

    return {
        "career": career,
        "readiness_band": band,
        "readiness_score": gap["readiness_score"],
        "recommended_skills": skills,
        "recommended_projects": config.CAREERS[career]["projects"],
        "recommended_certifications": certifications,
        "learning_resources": learning_resources,
        "interview_prep": _interview_prep(gap, career, profile),
        "weekly_roadmap": _weekly_roadmap(skills, gap, career),
        "plan_30_day": _plan_30_day(skills, gap, career, band),
        "plan_90_day": _plan_90_day(skills, gap, career, band),
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    from .readiness import make_profile

    demo = make_profile(
        technical_list=["Python", "SQL"], language_list=["Python"],
        soft_list=["Communication"], technical_rating=3, soft_rating=2,
        has_projects="No", career_interest="Data Scientist",
        course="B.Sc Data Science",
    )
    pathway = generate_pathway(demo, "Data Scientist")
    print("Career:", pathway["career"], "| Band:", pathway["readiness_band"])
    print("\nRecommended skills:")
    for s in pathway["recommended_skills"]:
        print(f"  [{s['priority']}] {s['skill']} — {s['reason']}")
    print("\n30-day plan:")
    for p in pathway["plan_30_day"]:
        print(f"  {p['phase']}: {p['title']}")
