# Public key naming

The host helper expects the public key filename to match the Linux username.

For user:

```text
example_user
```

Install the public key as:

```text
/etc/ed25519-token-auth/keys/example_user.pub
```

The file must contain the raw 32-byte Ed25519 public key.
