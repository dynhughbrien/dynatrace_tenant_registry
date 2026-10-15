# Dynatrace Tenant Registry Access Check

- Describe the Tenant Registry 
- Access the Registry
- Query the Registry

## Dynatrace Tenant Registry

The **tenant registry is Dynatrace's built-in container registry**, served from your tenant's Environment. 

It is separate from the public registries. Dynatrace's immutable, signed images are also published on other registries, such as public ECR. 

The tenant registry is mainly the source for images that aren't published elsewhere. 

## Key characteristics

- **Authentication:** It requires credentials, and the docs list obtaining the built-in registry credentials as a prerequisite. Pulls from the tenant are authenticated, unlike ECR Public or Docker Hub.
- **Architecture:** A community answer notes the server acts as the Docker registry and **provides only x86 images**. For other CPU architectures, use the public registry images instead.
- **Not for mirroring:** The docs say not to use the built-in registry for copying images to private registries. For ActiveGate and the other images, mirror from public ECR (the docs show `skopeo copy --all`). The exception is the classic full-stack OneAgent image, which has no public source.
- **Versioning:** Tags are version-based, and there are no mutable `latest` tags on the tenant, Docker Hub or ECR Public. Pin exact versions.
- **ActiveGate role:** The ActiveGate can route and cache image downloads when the cluster can't reach Dynatrace directly. It isn't a registry itself.

## Python SCript 
A small script that checks and displays  the  images from the  tenant  registry `TENANT_ID` (`TENANT_ID.live.dynatrace.com`).

### What it does

1. Authenticates against the registry (`/v2/`) using the tenant ID as username and your token as password.
2. Probes the image manifests for each repository and reports the digest if the tag is available:

   | Repository | Tags probed |
   | --- | --- |
   | `linux/oneagent` | `latest` |
   | `linux/oneagent-codemodules` | `all`, `java`, `nodejs`, `go`, `apache`, `nginx`, `php`, `dotnet` |
   | `linux/oneagent-codemodules-musl` | `all`, `java`, `nodejs`, `go`, `apache`, `nginx`, `php`, `dotnet` |
   | `linux/activegate` | `latest` |

The token is never printed. No Docker installation is needed.

### Requirements

- Python 3.6+
- Standard library only, so there are no packages to install
- A Dynatrace token with the **PaaS (Installer download)** scope

### Setup

Create a `.env` file next to `main.py` containing your token, and restrict its permissions:

```
DT_TOKEN=<your PaaS token>
```

```sh
chmod 600 .env
```

If there is no `.env`, the script falls back to a `DT_TOKEN` environment variable.

## Usage

```sh
python3 main.py
```

Example output:

```
Registry: TENANT_ID.live.dynatrace.com
[ OK ] Auth succeeded

=== linux/oneagent ===
  [ OK ] latest     sha256:...

=== linux/oneagent-codemodules ===
  [ OK ] all        sha256:...
  [ -- ] dotnet     HTTP 404
...
Pull: docker pull TENANT_ID.live.dynatrace.com/linux/oneagent-codemodules-musl:all
```

`[ -- ]` means the tag wasn't available (the HTTP status is shown).

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Authentication succeeded and all probes ran |
| `1` | `.env` is missing or `DT_TOKEN` is empty |
| `2` | The registry host could not be reached |
| `3` | Authentication failed (401, so the token is invalid, expired or missing the PaaS scope) or the registry returned another HTTP error |

## Pulling an image

After a successful check, log in to the registry with the tenant ID as username and the token as password, then pull:

```sh
docker login TENANT_ID.live.dynatrace.com
docker pull TENANT_ID.live.dynatrace.com/linux/oneagent-codemodules-musl:all
```

## Security

Keep `.env` out of version control (add it to `.gitignore`) and never share the token.


## Special Token Required

A special token is required to access the Tenant Registry.

1. Generate a new token for Tenant Registry access.
2. Use the **PaaS Integration** template.

**Token management page:**
https://{TENANT_ID}.apps.dynatrace.com/ui/apps/dynatrace.classic.tokens/ui/access-tokens?gtf=-2h&gf=all

## Testing Registry Access

With this token you can test and access the Tenant Registry.

### Browser Access

You can also access the Tenant Registry with  the following URL with Chrome if your corporate proxy allows it:

- **URL:** https://{TENANT_ID}.live.dynatrace.com/v2/linux/oneagent-codemodules-musl/manifests/all
- **User ID:** `{TENANT_ID}`
- **Access Token:** `dt0c01.XXXXXXXXXX` (the token starts with `dt0c01`)

## Docker Login and Pull

```bash
docker login {TENANT_ID}.live.dynatrace.com
```

- **User ID:** `{TENANT_ID}`
- **Access Token:** `dt0c01.XXXXXXXXXX` (the token starts with `dt0c01`)

```bash
docker pull {TENANT_ID}.live.dynatrace.com/linux/oneagent-codemodules-musl:all
```


## Example Scrip Output 
```
Registry: {TENANT_ID}.live.dynatrace.com
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

Pull: docker pull {TENANT_ID}.live.dynatrace.com/linux/oneagent-codemodules-musl:all

