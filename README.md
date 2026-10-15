# Dynatrace Registry Access Check

## Dynatrace Tenant Registry

The **tenant registry is Dynatrace's built-in container registry**, served from your tenant's Environment. 

It is separate from the public registries. Dynatrace's immutable, signed images are also published on other registries, such as public ECR. 

The tenant registry is mainly the source for images that aren't published elsewhere. 

## Key characteristics

- **Authentication:** It requires credentials, and the docs list obtaining the built-in registry credentials as a prerequisite. Pulls from the tenant are authenticated, unlike ECR Public or Docker Hub.
- **Architecture:** A community answer notes the server acts as the Docker registry and provides only x86 images. For other CPU architectures, use the public registry images instead.
- **Not for mirroring:** The docs say not to use the built-in registry for copying images to private registries. For ActiveGate and the other images, mirror from public ECR (the docs show `skopeo copy --all`). The exception is the classic full-stack OneAgent image, which has no public source.
- **Versioning:** Tags are version-based, and there are no mutable `latest` tags on the tenant, Docker Hub or ECR Public. Pin exact versions.
- **ActiveGate role:** The ActiveGate can route and cache image downloads when the cluster can't reach Dynatrace directly. It isn't a registry itself.

## Practical notes for the POC
- Use the correct domain: the Environment API domain, not the `.apps.` UI domain. The wrong one fails silently.
- Keep PaaS or registry tokens out of `ARG`/`ENV` and verbose curl output. Base64 Authorization headers are easy to leak.
- A tag or digest lookup only proves the image exists and is reachable. Only a full pull verifies the layers via SHA-256.
- For Kubernetes, once images are in your own registry, point DynaKube's `image`, `codeModulesImage` and `customPullSecret` fields at it.


A small script that checks whether a Dynatrace PaaS token can pull images from the container registry of tenant `TENANT_ID` (`TENANT_ID.live.dynatrace.com`).

## What it does

1. Authenticates against the registry (`/v2/`) using the tenant ID as username and your token as password.
2. Probes the image manifests for each repository and reports the digest if the tag is available:

   | Repository | Tags probed |
   | --- | --- |
   | `linux/oneagent` | `latest` |
   | `linux/oneagent-codemodules` | `all`, `java`, `nodejs`, `go`, `apache`, `nginx`, `php`, `dotnet` |
   | `linux/oneagent-codemodules-musl` | `all`, `java`, `nodejs`, `go`, `apache`, `nginx`, `php`, `dotnet` |
   | `linux/activegate` | `latest` |

The token is never printed. No Docker installation is needed.

## Requirements

- Python 3.6+
- Standard library only, so there are no packages to install
- A Dynatrace token with the **PaaS (Installer download)** scope

## Setup

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
