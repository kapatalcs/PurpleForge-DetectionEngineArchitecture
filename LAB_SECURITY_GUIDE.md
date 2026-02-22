PurpleForge – Lab Security & Hardening Guide
📌 Document Purpose

This document describes the security weaknesses intentionally present in PurpleForge labs and provides defensive mitigation and hardening strategies for each scenario.

**The goal is to**:
-Identify root causes
-Assess security impact
-Propose remediation strategies
-Define residual risk


# Lab-1: Web Login

## Vulnerabilities

### SQL Injection

**Root Cause:**
- User-controlled input directly embedded into SQL query.
- No parameterized queries used.
- No input validation layer.
- No ORM abstraction.

### Credential Stuffing & Password Spraying

**Root Cause:**
- No rate limiting on login endpoint.
- No account lockout mechanism.
- No failed attempt tracking.
- No CAPTCHA or MFA.

### Hardcoded Weak Secret Key

**Root Cause:**
- Secret key hardcoded in source code.
- Predictable value.
- No environment-based secret management.


## Risk Analysis

- Unauthorized authentication bypass
- Account takeover
- Privilege escalation
- Sensitive data exposure
- Session hijacking


## Mitigation

- Use parameterized queries
- Implement rate limiting (per IP + per account)
- Add account lockout policy
- Implement Multi-Factor Authentication
- Add progressive login delay
- Store secret key in environment variables

**Code-Level Improvements:**
```python

query = """
SELECT * FROM users
WHERE username = ?
AND password = ?
"""
cur.execute(query, (username, password))
```

## Residual Risk

- Valid credentials obtained from external breaches
- Distributed bot attacks bypassing basic rate limits



# Lab-2: Server Side Request Forgery

## Vulnerabilities

### SSRF (Server Side Request Forgery)

**Root Cause:**
- User-supplied URLs are fetched by the server without validation, internal IP filtering, or network egress restrictions.


## Risk Analysis
- Internal services may be accessed from the server context
- Sensitive internal data exposure
- Access to localhost-only services


## Mitigation

- Validate and sanitize user-supplied URLs
- Allow only trusted domains (domain allowlist)
- Block internal and private IP ranges
- Restrict allowed protocols to HTTP/HTTPS



**Code-Level Improvements:**
```python
from urllib.parse import urlparse
import socket
import ipaddress

parsed = urlparse(url)

if parsed.scheme not in ["http", "https"]:
    return "Invalid protocol", 400

hostname = parsed.hostname
resolved_ip = socket.gethostbyname(hostname)
ip_obj = ipaddress.ip_address(resolved_ip)

if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
    return "Access denied", 403  # This validation prevents access to internal and private network resources.
``` 

## Residual Risk
- IP obfuscation may allow internal access.



# Lab-3: Insecure File Upload With Extension

## Vulnerabilities

### Double Extension

**Root Cause:**
- Validation based only on file extension
- User-controlled filename used without sanitization


## Risk Analysis

- Malicious file upload
- Existing files overwritten
- Unsanitized filenames may allow path traversal


## Mitigation

- Validate file type based on content, not only extension.
- Reject filenames containing multiple extensions.

**Code-Level Improvements:**
```python

def is_valid_png(file):
    file.seek(0)
    header = file.read(8)
    file.seek(0)

    png_signature = b"\x89PNG\r\n\x1a\n"
    return header == png_signature
```

## Residual Risk

- Magic byte validation checks only the file header; attackers may craft polyglot files with a valid PNG signature but malicious embedded content. If file execution is enabled, such files may lead to remote code execution.


# Lab-4: Insecure File Upload With MIME

## Vulnerabilities

### MIME Spoofing

**Root Cause:**
- Server trusts client-supplied MIME header


## Risk Analysis

- Malicious file upload (fake MIME)


## Mitigation

- Validate file type based on content

**Code-Level Improvements:**
```python

def is_valid_png(file):
    file.seek(0)
    header = file.read(8)
    file.seek(0)

    png_signature = b"\x89PNG\r\n\x1a\n"
    return header == png_signature
```

## Residual Risk

- Magic byte validation checks only the file header; attackers may craft polyglot files with a valid PNG signature but malicious embedded content. If file execution is enabled, such files may lead to remote code execution.



# Lab-5: SSTI Access Control

## Vulnerabilities

### IDOR (Insecure Direct Object Reference)

**Root Cause:**
- Templates have no ownership control.
- User has unauthorized access to another user's template ID.

### SSTI (Server-Side Template Injection)

**Root Cause:**
- Template input from the user is processed directly.
- No verification/sanitization

### MFALC (Missing Function-Level Access Control)

**Root Cause:**
- Unauthorized users can access the /admin/panel endpoint.
- No role control.



## Risk Analysis

- Content belonging to others can be viewed.
- Sensitive data exposure
- Arbitrary code execution (RCE)
- Admin secrets exposure
- Privilege escalation


## Mitigation

- Add resource access control (owner check)
- Sanitize user input.
- Do not Run Input directly
- Add role-based access control (RBAC)


**Code-Level Improvements:**
```python

template = templates_db.get(template_id)
if template["owner"] != session["user"]:
    return "Access denied", 403
```

## Residual Risk
- Weak session management or insufficient logging could still expose sensitive data.



# Lab-6: JSON Web Token

## Vulnerabilities

### JWT Manipulation / Forgery

**Root Cause:**
- Server decodes JWT manually without verifying the signature using jwt.decode()
- Payloads are base64-decoded, but signature check is skipped


## Risk Analysis

- Unauthorized access to admin endpoints
- Privilege escalation
- Sensitive data exposure


## Mitigation

- Always verify JWT signature using the secret key
- Do not manually decode base64 payloads
- Use short-lived tokens and refresh mechanism
- Enforce role-based access control on sensitive endpoints

**Code-Level Improvements:**
```python

from flask import abort

try:
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
except jwt.InvalidTokenError:
    abort(401, "Invalid token")

if decoded.get("role") != "admin":
    abort(403, "You are not admin")
```

## Residual Risk

- If SECRET_KEY is weak or leaked, attacker can still forge tokens
- Long-lived tokens can be stolen and reused (session hijack)
