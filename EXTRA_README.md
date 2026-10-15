# Docker Images: Tenant Registry Access

I have resolved the issue on the "musl" versions.

## Special Token Required

A special token is required to access the Tenant Registry.

1. Generate a new token for Tenant Registry access.
2. Use the **PaaS Integration** template.

**Token management page:**
https://{TENANT_ID}.apps.dynatrace.com/ui/apps/dynatrace.classic.tokens/ui/access-tokens?gtf=-2h&gf=all

## Testing Registry Access

With this token you can test and access the Tenant Registry.

### Browser Access

You can access this URL with Chrome if your corporate proxy allows it:

- **URL:** https://{TENANT_ID}.live.dynatrace.com/v2/linux/oneagent-codemodules-musl/manifests/all
- **User ID:** `{TENANT_ID}`
- **Access Token:** `dt0c01.XXXXXXXXXX` (the token starts with `dt0c01`)

### Docker Login and Pull

```bash
docker login {TENANT_ID}.live.dynatrace.com
```

- **User ID:** `{TENANT_ID}`
- **Access Token:** `dt0c01.XXXXXXXXXX` (the token starts with `dt0c01`)

```bash
docker pull {TENANT_ID}.live.dynatrace.com/linux/oneagent-codemodules-musl:all
```

## Python Test Script

I also wrote a Python script to test access:
https://github.com/dynhughbrien/dynatrace_tenant_registry
````

A few notes on what I changed:

- **`docker login`**: Your original listed it without a registry host. I added `{TENANT_ID}.live.dynatrace.com` so the command targets the tenant registry rather than Docker Hub. Remove it if you'd prefer to keep your original wording.
- **Token placeholders**: I wrapped them in code formatting so the `XXXXXXXXXX` isn't rendered oddly, and moved the "starts with dt0c01" note into parentheses.
- **Structure**: I added headings to separate the token setup from the testing steps, but kept your wording otherwise intact.

If this is headed to a customer-facing doc, you may want to replace the tenant ID (`{TENANT_ID}`) with a placeholder like `<tenant-id>`.
