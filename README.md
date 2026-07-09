# Agent Workflow Pattern Lab

A Streamlit classroom app for teaching workflow patterns through business scenarios and n8n-style flow design.

## What learners practise

- Match business scenarios to the best workflow pattern
- Arrange n8n-style workflow steps in the right order
- Understand when parallel steps can happen in any order
- Connect abstract workflow patterns to practical automation use cases
- Reinforce key concepts with a short end-of-session quiz

## Patterns covered

- Prompt chaining
- Routing
- Parallelization
- Evaluator-optimizer

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. In Streamlit Community Cloud, create a new app from that repository.
3. Set the main file path to `app.py`.
4. Deploy.

## Suggested classroom use

Use it for 20 to 30 minutes as an interactive segment before learners build the real workflow in n8n.

Suggested flow:

1. Pattern Gallery, 5 minutes
2. Scenario Challenge, 5 to 8 minutes
3. Build the n8n Flow, 10 to 15 minutes
4. Boss Battle Quiz, 5 minutes

## Teaching message

AI workflow patterns are easier to understand when learners can see them as triggers, AI nodes, switch logic, parallel branches, review loops, and business actions.
