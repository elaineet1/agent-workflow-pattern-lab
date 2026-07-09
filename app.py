import streamlit as st
import random

st.set_page_config(page_title="Agent Workflow Pattern Lab", page_icon="🧩", layout="wide")

st.markdown("""
<style>
    .main-title {font-size: 2.4rem; font-weight: 800; margin-bottom: 0.2rem;}
    .subtitle {font-size: 1.05rem; color: #555; margin-bottom: 1.2rem;}
    .pattern-card {padding: 1rem; border-radius: 16px; border: 1px solid #e8e8e8; background: #fafafa; margin-bottom: 1rem;}
    .step-box {padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 12px; background: white; margin: 0.35rem 0;}
    .good {padding: 0.9rem; border-radius: 12px; background: #eaf7ee; border: 1px solid #b9e3c4;}
    .warn {padding: 0.9rem; border-radius: 12px; background: #fff6e5; border: 1px solid #f5d28b;}
    .bad {padding: 0.9rem; border-radius: 12px; background: #fdecec; border: 1px solid #f2b6b6;}
    .tiny {font-size: 0.85rem; color: #666;}
</style>
""", unsafe_allow_html=True)

PATTERNS = {
    "Prompt chaining": {
        "plain": "Break one task into a fixed sequence. Each step improves or checks the previous output.",
        "when": "Use when the task is predictable and can be split cleanly into stages.",
        "n8n": ["Trigger", "LLM Step 1", "Quality Gate", "LLM Step 2", "Output"],
        "memory": "Good for: draft → check → improve → send.",
        "examples": [
            "A B2C retailer drafts a flash-sale SMS, checks the character count, then localizes it for another market.",
            "A B2B software firm drafts an account-based outreach email, reviews tone, then personalizes it for a CFO.",
            "A healthcare clinic summarizes a patient webinar, extracts action items, then formats a follow-up note for attendees.",
        ],
    },
    "Routing": {
        "plain": "Classify the input, then send it to the correct specialist path.",
        "when": "Use when there are clear categories, such as billing, technical, refund, general.",
        "n8n": ["Trigger", "AI Classifier", "Switch", "Specialist Path", "Action"],
        "memory": "Good for: one inbox, many possible paths.",
        "examples": [
            "A telecom provider sorts customer messages into billing, roaming, upgrade, and cancellation queues.",
            "A B2B SaaS company routes inbound leads to enterprise, mid-market, or partner sales teams.",
            "A university classifies student requests into admissions, finance, or academic advising workflows.",
        ],
    },
    "Parallelization": {
        "plain": "Run multiple AI checks or subtasks at the same time, then combine the results.",
        "when": "Use when independent checks can happen together, or when multiple opinions reduce risk.",
        "n8n": ["Trigger", "Split into parallel branches", "LLM Branches", "Aggregate", "Decision"],
        "memory": "Good for: speed, guardrails, multiple reviews.",
        "examples": [
            "A listed company checks a press release in parallel for tone, factual accuracy, and legal sensitivity.",
            "A B2B consulting firm reviews a proposal at the same time for commercial risk, delivery feasibility, and brand fit.",
            "An e-commerce marketplace runs separate sentiment, urgency, and fraud-risk checks on seller disputes.",
        ],
    },
    "Evaluator-optimizer": {
        "plain": "One AI creates an answer. Another AI evaluates it. The answer improves through feedback loops.",
        "when": "Use when there are clear quality criteria and iteration improves the result.",
        "n8n": ["Trigger", "Generator AI", "Evaluator AI", "IF Score Pass?", "Revise or Output"],
        "memory": "Good for: improve until it meets a standard.",
        "examples": [
            "A training provider drafts a course proposal, scores it against funding criteria, then revises until it passes.",
            "A global manufacturer generates a job description, checks clarity and bias, then improves it before posting.",
            "A fintech support team creates a knowledge-base article, evaluates completeness, then refines weak sections.",
        ],
    },
}

SCENARIOS = {
    "Customer support triage": {
        "story": "A shared inbox receives refund requests, product questions, delivery issues, and technical complaints.",
        "best": "Routing",
        "why": "The first job is to classify the request, then send each category to the right path.",
        "sequence": ["Form or Email Trigger", "AI classifies request", "Switch by category", "Run specialist reply path", "Send reply and log case"],
    },
    "AI safety check for public replies": {
        "story": "Before publishing an AI-generated reply, the team wants separate checks for tone, factual risk, and policy risk.",
        "best": "Parallelization",
        "why": "The checks are independent and can run at the same time before being combined.",
        "sequence": ["Trigger with draft reply", "Send to tone checker", "Send to factual checker", "Send to policy checker", "Aggregate scores and decide"],
    },
    "Course proposal improvement loop": {
        "story": "An AI drafts a course proposal. Another AI checks if it meets SSG-style criteria, then asks for revision until it passes.",
        "best": "Evaluator-optimizer",
        "why": "There are clear quality criteria, and feedback can improve the output over one or more rounds.",
        "sequence": ["Trigger with course details", "Generator drafts proposal", "Evaluator scores against criteria", "IF score < pass, send feedback", "Generator revises or final output"],
    },
    "Marketing copy translation": {
        "story": "A retail team needs an English product caption, then a Chinese version. The final copy must be under 80 words.",
        "best": "Prompt chaining",
        "why": "The task has a fixed order: write, check length, translate, then output.",
        "sequence": ["Manual Trigger", "AI writes English caption", "IF word count ≤ 80", "AI translates caption", "Save final copy"],
    },
}

FLOW_CASES = {
    "Invoice reminder workflow": {
        "story": "A finance team wants AI to draft a payment reminder, check the tone, and send the final message to overdue customers.",
        "best": "Prompt chaining",
        "sequence": ["Schedule Trigger", "AI drafts reminder", "Tone check", "AI revises final message", "Send email"],
        "why": "Each step follows a fixed sequence from drafting to checking to sending.",
    },
    "Website lead routing": {
        "story": "A company receives inbound leads and needs to send each one to the right sales path based on company size and interest.",
        "best": "Routing",
        "sequence": ["Form Trigger", "AI classifies lead", "Switch by lead type", "Run specialist follow-up path", "Log in CRM"],
        "why": "The core decision is choosing the correct path for each incoming lead.",
    },
    "Press release review": {
        "story": "A communications team wants an AI draft checked in parallel for tone, factual accuracy, and legal sensitivity before release.",
        "best": "Parallelization",
        "sequence": ["Draft Trigger", "Tone review branch", "Fact check branch", "Legal risk branch", "Aggregate and approve"],
        "why": "The checks are independent, so parallel review is faster and clearer.",
    },
    "Policy document revision loop": {
        "story": "An internal policy draft should be improved until it meets readability and compliance standards.",
        "best": "Evaluator-optimizer",
        "sequence": ["Document Trigger", "Generator drafts policy", "Evaluator scores readability and compliance", "IF below threshold, return feedback", "Generator revises or publish"],
        "why": "The value comes from scoring and revision loops until the quality bar is met.",
    },
}

BOSS_QUESTIONS = [
    {"q": "Which pattern is best when tone, factual accuracy, and policy risk can be checked independently?", "a": "Parallelization", "opts": list(PATTERNS)},
    {"q": "Which pattern is best when the output improves through generate, evaluate, revise?", "a": "Evaluator-optimizer", "opts": list(PATTERNS)},
    {"q": "Which pattern is best for support messages that must go to billing, technical, or general paths?", "a": "Routing", "opts": list(PATTERNS)},
    {"q": "Which pattern is best when every task follows the same fixed sequence?", "a": "Prompt chaining", "opts": list(PATTERNS)},
]


def shuffled_options(seed_text: str, options: list[str]) -> list[str]:
    shuffled = options[:]
    random.Random(seed_text).shuffle(shuffled)
    return shuffled


def is_correct_flow(learner_order: list[str], flow: dict) -> bool:
    if flow["best"] != "Parallelization":
        return learner_order == flow["sequence"]

    expected = flow["sequence"]
    return (
        len(learner_order) == len(expected)
        and learner_order[0] == expected[0]
        and set(learner_order[1:4]) == set(expected[1:4])
        and learner_order[4] == expected[4]
    )

if "score" not in st.session_state:
    st.session_state.score = 0
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
st.markdown('<div class="main-title">🧩 Agent Workflow Pattern Lab</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A classroom app for teaching Prompt Chaining, Routing, Parallelization, and Evaluator Optimizer using n8n-style thinking.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Class scoreboard")
    st.metric("Points", st.session_state.score)
    st.metric("Attempts", st.session_state.attempts)
    if st.button("Reset class score"):
        st.session_state.score = 0
        st.session_state.attempts = 0
        st.rerun()

page = st.tabs(["1. Pattern Gallery", "2. Scenario Challenge", "3. Build the n8n Flow", "4. Boss Battle Quiz"])

with page[0]:
    st.subheader("Pattern Gallery")
    cols = st.columns(2)
    for i, (name, p) in enumerate(PATTERNS.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="pattern-card">
            <h4>{name}</h4>
            <p>{p['plain']}</p>
            <p><b>When to use:</b> {p['when']}</p>
            <p><b>Memory hook:</b> {p['memory']}</p>
            <p><b>Business use cases:</b></p>
            <ul>
                <li>{p['examples'][0]}</li>
                <li>{p['examples'][1]}</li>
                <li>{p['examples'][2]}</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            st.caption(" → ".join(p["n8n"]))

with page[1]:
    st.subheader("Scenario Challenge: Pick the Best Pattern")
    scenario_name = st.selectbox("Choose a classroom scenario", list(SCENARIOS.keys()))
    scenario = SCENARIOS[scenario_name]
    st.markdown(f"""
    <div class="pattern-card">
    <h4>{scenario_name}</h4>
    <p>{scenario['story']}</p>
    </div>
    """, unsafe_allow_html=True)
    guess = st.radio(
        "Which workflow pattern fits best?",
        shuffled_options(f"scenario-{scenario_name}", list(PATTERNS.keys())),
        horizontal=False,
    )
    if st.button("Reveal feedback", key="scenario_reveal"):
        st.session_state.attempts += 1
        if guess == scenario["best"]:
            st.session_state.score += 10
            st.markdown(f"<div class='good'>Correct. Best pattern: <b>{scenario['best']}</b><br>{scenario['why']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bad'>Not quite. You chose <b>{guess}</b>, but the stronger fit is <b>{scenario['best']}</b>.<br>{scenario['why']}</div>", unsafe_allow_html=True)
        st.write("n8n-style sequence:")
        for step in scenario["sequence"]:
            st.markdown(f"<div class='step-box'>⬇️ {step}</div>", unsafe_allow_html=True)

with page[2]:
    st.subheader("Build the n8n Flow")
    st.write("Learners arrange the workflow sequence. This is the main hands-on classroom activity.")
    flow_scenario_name = st.selectbox("Choose business use case", list(FLOW_CASES.keys()), key="flow_scenario")
    flow = FLOW_CASES[flow_scenario_name]
    st.info(flow["story"])

    shuffled = flow["sequence"][:]
    random.Random(flow_scenario_name).shuffle(shuffled)
    st.write("Arrange the steps from first to last:")
    learner_order = []
    for i in range(len(shuffled)):
        remaining = [s for s in shuffled if s not in learner_order]
        choice = st.selectbox(f"Step {i+1}", remaining, key=f"{flow_scenario_name}_{i}")
        learner_order.append(choice)

    if st.button("Check my workflow", key="check_flow"):
        st.session_state.attempts += 1
        correct = is_correct_flow(learner_order, flow)
        if correct:
            st.session_state.score += 20
            st.markdown("<div class='good'><b>Excellent.</b> Your n8n flow is in the correct order.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='bad'><b>Review needed.</b> Some steps are out of order. Compare your version with the recommended flow below.</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.write("Your flow")
            for step in learner_order:
                st.markdown(f"<div class='step-box'>{step}</div>", unsafe_allow_html=True)
        with c2:
            st.write("Recommended flow")
            for step in flow["sequence"]:
                st.markdown(f"<div class='step-box'>{step}</div>", unsafe_allow_html=True)
        if flow["best"] == "Parallelization":
            st.caption("For parallel flows, the middle review branches can appear in any order as long as they all happen before aggregation.")
        st.markdown(f"<div class='warn'><b>Teaching point:</b> {flow['why']}</div>", unsafe_allow_html=True)

    st.divider()
    st.write("Convert to n8n node language")
    selected_pattern = flow["best"]
    st.caption(f"Pattern: {selected_pattern}")
    for node in PATTERNS[selected_pattern]["n8n"]:
        st.markdown(f"<div class='step-box'>🟦 {node}</div>", unsafe_allow_html=True)

with page[3]:
    st.subheader("Boss Battle Quiz")
    st.write("Use this at the end of the section as a fast recap game.")
    total = 0
    for i, item in enumerate(BOSS_QUESTIONS):
        ans = st.radio(
            item["q"],
            shuffled_options(f"boss-{i}-{item['q']}", item["opts"]),
            key=f"boss_{i}",
        )
        if ans == item["a"]:
            total += 1
    if st.button("Submit Boss Battle"):
        gained = total * 5
        st.session_state.score += gained
        st.session_state.attempts += 1
        if total == len(BOSS_QUESTIONS):
            st.balloons()
            st.success(f"Perfect score: {total}/{len(BOSS_QUESTIONS)}. You earned {gained} points.")
        else:
            st.warning(f"Score: {total}/{len(BOSS_QUESTIONS)}. You earned {gained} points. Review the Pattern Gallery and try again.")
