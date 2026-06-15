# Overview

SDDM Ed25519 Token Auth adds a separate token login path to SDDM.

The project has four main parts:

1. a host-side PAM helper;
2. an external token implementation;
3. a small SDDM backend patch;
4. a greeter QML integration.

The token device is not required to be a Raspberry Pi. The Raspberry Pi Zero 2 W is only the reference implementation because it can operate as a Linux USB gadget.

## Design goals

- Keep normal password login intact.
- Add a separate token login path.
- Avoid sending passwords through the token protocol.
- Use Ed25519 signatures over short-lived challenges.
- Keep the device protocol simple enough to implement on Linux SBCs or microcontrollers.
- Make greeter integration possible for any SDDM QML theme.

## Separation of login paths

Password login uses the normal SDDM PAM service:

```text
/etc/pam.d/sddm
```

Token login uses a dedicated PAM service:

```text
/etc/pam.d/sddm-token
```

This separation reduces the chance of breaking normal password login while experimenting with token authentication.
