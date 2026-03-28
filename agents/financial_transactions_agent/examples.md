# Example Use Cases

## Example 1

**Input**

Approve and process a supplier payment of USD 48,000 to Apex Components for invoice INV-2048 due this Friday. Procurement has approved the invoice, but finance approval is still pending and the counterparty bank details were changed last week.

**Expected behavior**

- classify the request as pending or blocked, not ready
- require finance approval and counterparty verification
- produce audit notes and a remediation workflow

## Example 2

**Input**

Execute a customer refund of USD 2,400 for a duplicate charge. Ticket reference, supervisor approval, verified customer identity, and original payment details are attached.

**Expected behavior**

- identify which controls are satisfied
- state whether the refund is ready to execute
- provide an auditable checklist and execution sequence
