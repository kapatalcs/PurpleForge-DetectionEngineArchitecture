# PurpleForge - Threat Model

## 1. Overview
PurpleForge implements a modular system architecture for security lab orchestration and detection. It is designed to simulate attacks against intentionally vulnerable lab environments and generate alerts through a rule-based engine.

This threat model's purpose is to identify potential security threats, document architectural assumptions, define mitigations, and explicitly state residual risks.

---

## 2. System Components

- User
- Main Controller Script
- Attack Scripts (Sequential Execution)
- Lab Environment (Intentionally Vulnerable, Log Producer)
    -The lab environment is responsible for generating system and security logs, which are consumed by PurpleForge for analysis and alerting.
- Rule Engine
- Alerting Module

---

## 3. Design Assumptions

- Attack scripts are intentionally executed sequentially.
- Concurrent attack script execution is not supported by design.
- Labs are intentionally vulnerable and considered untrusted.
- Authentication payloads (passwords, raw requests) are not logged.
- Detection is prioritized over prevention.

---

## 4. Trust Boundaries

- Boundary between Lab Logs and Rule Engine
- Boundary between External Interaction and Lab Environment

---

## 5. Identified Threats

### T1: Temporal Event Replay
**STRIDE:** Denial of Service  
**Scenario:** Sequential attack execution causes old logs to remain within correlation windows, triggering duplicate alerts.

**Mitigation:**
- Reduced correlation window
- Rule trigger deduplication

**Residual Risk:** False positives under heavy sequential testing.

---

### T2: Out-of-Band SQL Injection via Lab Interface
**STRIDE:** Elevation of Privilege, Tampering  
**Scenario:** Users may directly exploit SQL Injection vulnerabilities through the lab web interface without using attack scripts.

**Mitigation:**
- Rule detect successful authentication with non-existent users

**Residual Risk:** SQL Injection impersonating existing users (e.g. admin) may bypass detection.

---

### T3: Confusing the credential stuffing attack and the password spray
**STRIDE:** Denial of Service
**Scenario:** A single IP password spray attack is run and the rule engine is confused as to whether the attack is credential stuffing or password spraying. 

**Mitigation:**
- Rule detect success rate of an attack and determine the conclusion

**Residual Risk:** Success-rate–based classification may still allow low-and-slow attacks to cause account lockouts or evade detection, resulting in partial denial of service.

---

### T4: Cross-Context Rule Triggering (False Positive Risk)
**STRIDE:** Denial of Service / Tampering

**Scenario:** An attacker sends SSRF-like patterns inside an SQL injection payload. The detection engine triggers the SSRF rule even though the lab does not perform outbound HTTP requests.

**Mitigation:**
- The detection engine uses action-based event classification. Each lab produces distinct action identifiers (e.g., LOGIN_SUCCESS, SUCCESS for SSRF). Rules are evaluated only against relevant action types, preventing rule confusion and cross-lab false positives.

**Residual Risk:** If action classification logic is flawed or manipulated, incorrect labeling may still cause rule bypass or false positives.

---

## 6. Limitations

- Some impersonation attacks cannot be definitively attributed.
- Labs are intentionally insecure and not hardened.
---

## 7. Security Philosophy

PurpleForge follows a detection-first security model. The system prioritizes visibility, observability, and educational value over full attack prevention and assumes that lab environments are adversarial and detection logic must not trust event content blindly.

---

## 8. Conclusion

This threat model reflects a conscious and documented approach to security engineering, emphasizing risk awareness, mitigation, and transparency.
