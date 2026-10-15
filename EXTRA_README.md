# Docker Images: Tenant Registry Access


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



