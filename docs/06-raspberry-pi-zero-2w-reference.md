# Raspberry Pi Zero 2 W reference implementation

The Raspberry Pi Zero 2 W is the reference token device for this project.

## Why this device is suitable

- It can run Linux.
- It can operate as a USB gadget device.
- It can expose a USB CDC ACM serial interface.
- It can securely store the token private key on its local filesystem.

## Boot configuration notes

On Raspberry Pi OS-style systems, USB gadget mode normally requires `dwc2`.

Typical configuration areas:

```text
/boot/config.txt
/etc/modules-load.d/
```

A typical modules file contains:

```text
dwc2
libcomposite
```

The exact boot configuration varies by distribution and Raspberry Pi OS release.

## Expected USB identity

The example gadget uses:

```text
manufacturer: Ed25519Token
product: SDDM Ed25519 Token
serial: CHANGE_ME_TOKEN_SERIAL
```

Use a unique serial number per token before deployment. The reference gadget script reads the serial from `/etc/ed25519-token-auth/device.conf`.
