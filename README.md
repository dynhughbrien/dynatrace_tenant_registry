# Dynatrace Tenant Registry Access Check

This guide covers three things:

1. What the Dynatrace tenant registry is
2. How to get credentials and access it
3. How to query it with a Docker-free Python script

> **Placeholder convention:** `<TENANT_ID>` is your Dynatrace tenant ID (the first part of `<TENANT_ID>.live.dynatrace.com`). Replace it everywhere it appears.

---

## 1. About the Tenant Registry

The **tenant registry is Dynatrace's built-in container registry**, served from your tenant's Environment domain. It is separate from the public registries (such as AWS ECR Public and Docker Hub), where Dynatrace also publishes immutable, signed images. The tenant registry is mainly the source for images that are not published elsewhere.

| Characteristic | Detail |
| --- | --- |
| **Authentication** | Required. Obtaining the built-in registry credentials is a documented prerequisite. Unlike ECR Public or Docker Hub, pulls from the tenant are always authenticated. |
| **Architecture** | The registry serves **x86 images only** (per a community answer; confirm against current Dynatrace docs). For other CPU architectures, use the public registry images instead. |
| **Hostname** | `<TENANT_ID>.live.dynatrace.com` (the Environment API domain), **not** the `.apps.` UI domain. |

> **Watch the domains.** The token management page lives on the `.apps.` domain, but the registry itself is on the `.live.` domain. Using the wrong one causes silent failures.

---

## 2. Credentials

A dedicated token is required to access the tenant registry.

![access-token](https://github.com/dynhughbrien/dynatrace_tenant_registry/blob/main/extra_access_token.png)

1. Open the token management page:
   `https://<TENANT_ID>.apps.dynatrace.com/ui/apps/dynatrace.classic.tokens/ui/access-tokens`
2. Generate a new token using the **PaaS Integration** template (this provides the **PaaS / Installer download** scope).
3. Copy the token. It starts with `dt0c01.`.

Registry credentials:

| Field | Value |
| --- | --- |
| **Username** | `<TENANT_ID>` |
| **Password** | The `dt0c01.…` token |

---

## 3. Testing Access

### Option A: Browser

If your corporate proxy allows it, open the following URL in Chrome and enter the credentials when prompted:

```
https://<TENANT_ID>.live.dynatrace.com/v2/linux/oneagent-codemodules-musl/manifests/all
```

### Option B: curl

```sh
curl -s -o /dev/null -w "%{http_code}\n" \
  -u "<TENANT_ID>:$DT_TOKEN" \
  https://<TENANT_ID>.live.dynatrace.com/v2/
```

A `200` means authentication succeeded; a `401` means the token is invalid, expired or missing the PaaS scope.

> **Avoid `curl -v`.** Verbose output includes the base64-encoded `Authorization` header, which is trivially decodable.

### Option C: Docker

Pass the token on stdin so it doesn't end up in your shell history:

```sh
echo "$DT_TOKEN" | docker login <TENANT_ID>.live.dynatrace.com \
  --username <TENANT_ID> --password-stdin

docker pull <TENANT_ID>.live.dynatrace.com/linux/oneagent-codemodules-musl:all
```

---

## 4. Python Check Script

A small script that authenticates to the registry and reports which images and tags are available. **No Docker installation is needed.**

### What it does

1. Authenticates against the registry (`/v2/`) using the tenant ID as username and your token as password.
2. Probes the image manifest for each repository and tag, and reports the digest if the tag is available.

| Repository | Tags probed |
| --- | --- |
| `linux/oneagent` | `latest` |
| `linux/oneagent-codemodules` | `all`, `java`, `nodejs`, `go`, `apache`, `nginx`, `php`, `dotnet` |
| `linux/oneagent-codemodules-musl` | `all`, `java`, `nodejs`, `go`, `apache`, `nginx`, `php`, `dotnet` |
| `linux/activegate` | `latest` |

The token is never printed.

### Requirements

- Python 3.6+
- Standard library only (nothing to install)
- A Dynatrace token with the **PaaS (Installer download)** scope

### Setup

Create a `.env` file next to `main.py` containing your token, and restrict its permissions:

```sh
echo 'DT_TOKEN=<your PaaS token>' > .env
chmod 600 .env
```

If there is no `.env` file, the script falls back to the `DT_TOKEN` environment variable.

### Usage

```sh
python3 main.py
```

### Status markers

| Marker | Meaning |
| --- | --- |
| `[ OK ]` | Tag is available (digest shown) |
| `[ -- ]` | Tag is not available (HTTP status shown, e.g. `404`) |

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Authentication succeeded and all probes ran |
| `1` | `.env` is missing or `DT_TOKEN` is empty |
| `2` | The registry host could not be reached |
| `3` | Authentication failed (`401`: token invalid, expired or missing the PaaS scope), or the registry returned another HTTP error |

---

## 5. Example Output

Digests below are from one sample run and will change as Dynatrace publishes new images.

```
Registry: <TENANT_ID>.live.dynatrace.com
[ OK ] Auth succeeded

=== linux/oneagent ===
  [ OK ] latest     sha256:84f658b2bc26126943e807f1da682d89b5e9f995f6dd868ac5c7489df2fad442

=== linux/oneagent-codemodules ===
  [ OK ] all        sha256:d043bbd41944b786bb1d216cef191db2690c954cd9183996da6432f99bcce082
  [ OK ] java       sha256:c6c35b84802d468d6ce9e2301fc7aa0b566ca2fde252aab182786d09fd6462ff
  [ OK ] nodejs     sha256:618e0e64a8fdd20dd0c983f6975b6faaff851f32cee3b3f2b2cf9fe3c08a733c
  [ OK ] go         sha256:3c36166a936e370a084bbb9e1865f9e47da012454f4a441fec6ee045808d658a
  [ OK ] apache     sha256:b6360b325a73559f9b08be767cc7eba1e9a9b2c7d92e5f72d2894db3f0f09588
  [ OK ] nginx      sha256:a83da77584cfd873d6d4e82049b6c57561ee5f9d8d893605524c1109629ae8ac
  [ OK ] php        sha256:6397a8546fa95ef725ea3824eb509548469878cb53ac8a2070de22798fb63238
  [ OK ] dotnet     sha256:4ffa1458ae6cc4354fba62617159fcee841b3f46219664facf30791d7f4b6936

=== linux/oneagent-codemodules-musl ===
  [ OK ] all        sha256:148caea52c6674e5bd0a70327ee259c956243537f50c352a146b34d9eeb5e85d
  [ OK ] java       sha256:90271beb7e0bce3fe119249ba72e38c30faef01773cff0774902e016391ab0cf
  [ OK ] nodejs     sha256:464f3c4b96771c1bd63286c68713d636b0c1e65136e5b9923679566d925e01aa
  [ OK ] go         sha256:d1401a88f37062b75c3b447bad52616ee303cda862e2094d164d9f457d7ef80e
  [ OK ] apache     sha256:0c3d6153f95caa5996415735902e53d9bc7a97d628261a7c17e588ee348f6d3b
  [ OK ] nginx      sha256:594e70f9d9983f56b65a0380ea501efe32b7e334623e23213bd7507d33e1e122
  [ OK ] php        sha256:0506ffe120a05136aeaf2fa296994937301b55d231084ad5d4280d248c0edc01
  [ OK ] dotnet     sha256:d1f729cfba6475609d111f04629728ca6aa6316e22986fbc32983383b9bf9956

=== linux/activegate ===
  [ OK ] latest     sha256:51ea0b47b3449ad2ae47f5663fcd6b829c11fde3b2de17cabdaafd1fcea162aa

Pull: docker pull <TENANT_ID>.live.dynatrace.com/linux/oneagent-codemodules-musl:all
```

---

## 6. Limitations and Good Practice

- **A manifest check is not a pull.** The script confirms authentication and that a tag exists (and its digest). Only a full `docker pull` downloads the layers and verifies them via SHA-256.
- **Pin versions for deployments.** Tags such as `latest` and `all` are convenient for checks, but production builds should reference an exact version or digest.
- **Keep secrets out of version control.** Add `.env` to `.gitignore` and never share the token.
- **Keep secrets out of image layers.** In Dockerfiles, use BuildKit secrets rather than `ARG`/`ENV`, which remain visible in `docker history`.
- **Review logs before sharing.** Debug and verbose output (curl, Azure CLI, etc.) can expose tokens and `Authorization` headers.
