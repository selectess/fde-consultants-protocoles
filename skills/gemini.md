# FDE Consultant Skill for Gemini

## Installation

### Gemini Workspace (web)

1. Go to https://gemini.google.com/settings
2. Click "Custom Instructions"
3. Paste the content of `skill/ZERO-INSTALL.md`
4. Save

### Gemini API

```python
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=open("skill/ZERO-INSTALL.md").read(),
)
response = model.generate_content("Scope this SaaS churn project.")
```

## Usage

In Gemini:

```
Use the FDE Consultant methodology. Start with Stage 0 Reconnaissance — run `skill/scripts/fde_recon.py` (or the `fde_recon` tool) to scrutinize the codebase — before scoping. Then scope this project.
```

## License

Apache-2.0.

## FDE Assurance Score

94/100 → Certified.
