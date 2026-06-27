# FDE Consultant Skill for ChatGPT

## Installation

ChatGPT supports Custom Instructions (free users have a character limit; ChatGPT Plus has full support).

### Steps

1. Go to https://chat.openai.com/#settings
2. Click "Personalization" → "Custom Instructions"
3. Enable "Custom Instructions for new chats"
4. In "How would you like ChatGPT to respond?", paste the content of `skill/ZERO-INSTALL.md` from this repo
5. Save

### Programmatic (ChatGPT API)

```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": open("skill/ZERO-INSTALL.md").read()},
        {"role": "user", "content": "Scope this SaaS churn project."}
    ]
)
```

## Usage

In ChatGPT:

```
Apply the FDE methodology I gave you in custom instructions. Start with Stage 0 Reconnaissance — run `skill/scripts/fde_recon.py` (or the `fde_recon` tool) to scrutinize the codebase — before scoping. Then scope this project.
```

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.
