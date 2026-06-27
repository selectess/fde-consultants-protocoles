# Third-Party Notices

This document lists all third-party software, libraries, and resources used by the FDE Consultant Skill project, along with their respective licenses.

## Python dependencies

### `mcp` (Model Context Protocol SDK)
- **Version**: >=1.0.0
- **License**: MIT
- **Source**: https://pypi.org/project/mcp/
- **Used by**: `skill/mcp_server/`
- **Copyright**: 2024 Anthropic

### `pytest` (testing framework)
- **Version**: >=7.0
- **License**: MIT
- **Source**: https://pypi.org/project/pytest/
- **Used by**: `skill/tests/`, `modex/tests/`

### `pytest-asyncio`
- **Version**: >=0.21
- **License**: Apache-2.0
- **Source**: https://pypi.org/project/pytest-asyncio/
- **Used by**: `skill/tests/test_mcp_server.py`

## Agent ecosystem compatibility

### Anthropic Agent Skills specification
- **Source**: https://agentskills.io
- **Used as**: reference for `skill/SKILL.md` frontmatter and structure
- **License**: Apache-2.0 (Anthropic open-source skills)
- **Copyright**: 2024-2026 Anthropic

### Anthropic skills repository
- **Source**: https://github.com/anthropics/skills
- **Used as**: inspiration for `template-skill/` directory
- **License**: Apache-2.0 (most skills), source-available (document-skills)

## Trademark notices

- **Claude** and **Claude Code** are trademarks of Anthropic.
- **OpenAI** and **Codex** are trademarks of OpenAI.
- **Cursor** is a trademark of Anysphere.
- **Windsurf** is a trademark of Codeium.
- **OpenClaw** and **Hermes** are open-source agent runtimes.
- **Continue.dev** is an open-source AI coding assistant.
- **GitHub** and **GitHub Actions** are trademarks of GitHub, Inc.
- **Stripe** is a trademark of Stripe, Inc.
- **Gemini** is a trademark of Google.

The FDE Consultant Skill is **not affiliated with, endorsed by, or sponsored by** any of the above trademark holders.

## Open-source acknowledgments

- **Palantir's Forward Deployed Engineer (FDE)** methodology
- **Anthropic's Agent Skills specification**
- **OpenTelemetry semantic conventions for GenAI**
- **Model Context Protocol**

## License compatibility matrix

| License | Compatible with Apache-2.0 | Compatible with BSL |
|---|---|---|
| Apache-2.0 | ✅ | ✅ |
| MIT | ✅ | ✅ |
| BSD-2/3-Clause | ✅ | ✅ |
| BSL | ✅ | ✅ |
| GPL-2.0 | ❌ | ❌ |
| GPL-3.0 | ❌ | ❌ |

---

Last updated: 2026-06-22
