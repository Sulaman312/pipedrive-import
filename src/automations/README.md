# Automations package

This package is reserved for application-owned automations.

- AUT-02 remains entirely inside native Pipedrive automations; no duplicate application code belongs here.
- AUT-03 is not implemented yet.
- When AUT-03 starts, keep HTTP Basic Auth and payload parsing in a webhook blueprint, stage-decision logic in an automation service, and Slack delivery in a small client module.

No webhook endpoint is currently registered.
