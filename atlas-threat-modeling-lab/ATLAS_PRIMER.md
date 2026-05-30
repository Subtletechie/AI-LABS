# ATLAS Tactic Primer

Plain-English descriptions of the ATLAS tactics used in this lab. For the complete framework, see https://atlas.mitre.org.

| Tactic | What it means in plain English |
|---|---|
| **Reconnaissance** | The attacker learns about your AI system — what model it uses, what data it was trained on, what APIs it can call, and where its edges are. |
| **Resource Development** | The attacker prepares tools, accounts, or datasets they will need before launching an attack (e.g., crafting adversarial inputs, setting up throwaway accounts). |
| **Initial Access** | The attacker finds a way into the system — through the public chat interface, a stolen credential, or an exposed API endpoint. |
| **ML Model Access** | The attacker gains the ability to query or examine the model directly, which lets them probe its behavior systematically (black-box or white-box). |
| **Poisoning** | The attacker corrupts the data the model learns from — either during training or by injecting malicious content into the knowledge base the model retrieves from. |
| **Defense Evasion** | The attacker gets around safety filters, output guardrails, or content policies — typically through prompt injection, jailbreaks, or encoding tricks. |
| **Discovery** | The attacker maps what the model can do and what it can reveal — system prompt contents, connected tools, internal API names, or sensitive data in its context. |
| **Exfiltration** | The attacker steals data, the system prompt, or captured model behavior — extracting information that should never leave the system. |
| **Impact** | The actual damage: fraud, account data disclosure, reputational harm, or downstream harm to customers caused by the compromised chatbot. |
