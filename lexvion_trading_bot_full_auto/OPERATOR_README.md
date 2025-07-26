# Lexvion Trading Bot

## Elevator pitch
A modular options trading system that connects data ingestion, signal stacking, order preparation and human-in-the-loop execution. By combining automation with operator oversight, it enables disciplined, audit-ready trading.

## Usage
1. Install dependencies and set up broker API keys in a `.env` file.
2. Run data ingestion scripts to populate caches.
3. Review generated signals and adjust the risk profile.
4. Approve trades via the CLI or dashboard before execution.
5. Inspect Lexvion for audit logs of executed trades.

## Architecture
- Data ingestion pulls options data, market indicators and custom metrics.
- Signal stacking aggregates heuristics or model outputs to determine candidate trades.
- Order preparation computes size, strike and expiry while applying risk constraints.
- Human approval requires operators to confirm or reject trades.
- Execution sends orders to the broker API and logs evidence via Lexvion.

![Diagram](./assets/diagram.png)

## Results & ROI
- **Demonstrated ability to execute end-to-end trades with risk management** — evidence: Trading logs
- **Human-in-the-loop control maintained at all times** — evidence: Operator approval records
- **Comprehensive audit logs stored in Lexvion** — evidence: Audit bundle content

## Part of the Operator Meta Portfolio
- [AI Code Review Bot](../ai_code_review_bot/OPERATOR_README.md)
- [Job Offer Factory](../job_offer_factory_autorun/OPERATOR_README.md)
- [Onboarding Assistant](../Onboarding_Assistant/OPERATOR_README.md)
- [Lexvion Compliance Engine](../lexvion/OPERATOR_README.md)
- [Operators Leadscore API](../operators-leadscore-api/OPERATOR_README.md)
- [Operator Metrics Dashboard](../operator_metrics_dashboard/OPERATOR_README.md)
- [Meta Portfolio](../meta_portfolio/README.md)

## Operator principles
Automation first, modularity, operator focus and compounding learning.
