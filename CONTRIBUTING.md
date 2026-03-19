# Contributing to AquaIntel

Thank you for your interest in contributing to AquaIntel. This project is an open research platform — all kinds of contributions are valuable, from bug reports and documentation improvements to new sensor integrations and ML model upgrades.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branch Naming](#branch-naming)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Research Contributions](#research-contributions)

---

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold these standards.

---

## Ways to Contribute

| Type | Description |
|------|-------------|
| **Bug fixes** | Correct errors in backend logic, firmware, or dashboard |
| **Documentation** | Improve guides in `docs/`, code comments, or this README |
| **New sensors** | Add support for heavy metals, nitrates, phosphates, etc. |
| **ML improvements** | Better models, hyperparameter tuning, alternative architectures |
| **New regulatory frameworks** | Add EU WFD, US EPA, or other regional governance modules |
| **Infrastructure** | Docker, MQTT transport layer, deployment automation |
| **Frontend** | Dashboard enhancements, accessibility, mobile improvements |
| **Research** | Publish results, cite this work, report real-world deployment findings |

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/aquaintel.git
   cd aquaintel/smart_pollution_system
   ```
3. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Generate the dataset and train models** to verify your setup:
   ```bash
   python setup_ml_pipeline.py
   ```
5. **Start the server** and open the dashboard to confirm everything works.

---

## Development Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Make your changes.
3. Test your changes thoroughly (see below).
4. Commit with a descriptive message.
5. Push and open a Pull Request against `main`.

### Testing

- **Backend:** Run `python server/app.py` and send test payloads via `curl` or the dashboard simulate endpoint.
- **ML models:** Run `python ml_training/test_model.py` after retraining to verify metrics have not regressed.
- **Firmware:** Test `.ino` files in Arduino IDE's Serial Monitor with a mock server before flashing hardware.
- **Dashboard:** Open `dashboard/index.html` in-browser and verify all six views render correctly in both light and dark themes.

---

## Branch Naming

| Prefix | Use case |
|--------|----------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation only |
| `refactor/` | Code restructuring without behavior change |
| `ml/` | Machine learning model or pipeline changes |
| `hw/` | Hardware / firmware changes |

---

## Commit Messages

Use short, imperative-present-tense summaries:

```
feat: add nitrate sensor support to sensor_node firmware
fix: correct EMA smoothing coefficient in app.py
docs: update hardware_setup.md wiring diagram for actuator node
ml: increase LSTM window to 15 steps and retune learning rate
```

---

## Pull Request Process

1. Ensure your branch is up to date with `main` before opening a PR.
2. Fill in the pull request template completely.
3. Link any related issues using `Closes #123` syntax.
4. Ensure the PR description explains **what** changed and **why**.
5. A maintainer will review within a reasonable timeframe.

---

## Reporting Bugs

Use the [Bug Report issue template](.github/ISSUE_TEMPLATE/bug_report.md). Include:

- Operating system and Python version
- Steps to reproduce
- Expected vs. actual behavior
- Relevant logs or screenshots

---

## Suggesting Features

Use the [Feature Request issue template](.github/ISSUE_TEMPLATE/feature_request.md). Describe:

- The problem you are trying to solve
- Your proposed solution
- Any alternatives you considered

---

## Research Contributions

If you deploy AquaIntel in a real-world environment or extend it for a research study, we would love to hear about it:

- Open a GitHub Discussion describing your deployment
- If you publish a paper citing this work, open a PR to add your citation to the README
- Share any labelled real-world datasets you collect (under an appropriate open data license) so the community can improve the ML models

---

Thank you for helping make clean water monitoring more accessible.
