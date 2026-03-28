# Example Use Cases

## Example 1

**Input**

I have a customer churn dataset with 18 months of account history, product usage, support tickets, and billing features. The business wants to predict churn in the next 60 days and understand the main drivers, but the positive class is only 8%.

**Expected behavior**

- Recommend a small set of suitable classification approaches
- Call out class imbalance, leakage, temporal validation, and interpretability tradeoffs
- Return a workflow covering data prep, validation, modeling, diagnostics, and communication

## Example 2

**Input**

We ran an onboarding email intervention on some users but assignment was not randomized. We want to estimate whether the intervention actually improved 30-day retention.

**Expected behavior**

- Shift from pure prediction toward causal / quasi-experimental guidance
- Discuss confounding, selection bias, overlap, and identification assumptions
- Recommend an implementation path with diagnostics and sensitivity checks
