# Codex Team Skills

Shared Codex skills for team installation.

## Included skills

- `webob-funnel-upsell-compare`
- `webob-funnel-second-upsell-compare`
- `webob-funnel-penetration-pay-compare`

## Install

After this repository is pushed to GitHub, install one skill with:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YOUR_ORG/YOUR_REPO \
  --path skills/webob-funnel-upsell-compare
```

Install all three with:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YOUR_ORG/YOUR_REPO \
  --path skills/webob-funnel-upsell-compare \
  --path skills/webob-funnel-second-upsell-compare \
  --path skills/webob-funnel-penetration-pay-compare
```

Restart Codex after installing new skills.
