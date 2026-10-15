# Dynatrace Tenant Registry
The GitHub link returned a 404 (private or not pushed), so this summary comes from the Dynatrace docs and the registry testing you've done in this project.

**What the tenant registry is**

The tenant registry is Dynatrace's built-in container registry, served from your tenant's Environment API domain. It is separate from the public registries. Dynatrace's immutable, signed images are also published on other registries, such as public ECR. The tenant registry is mainly the source for images that aren't published elsewhere. The classic full-stack OneAgent image must be replicated through the built-in registry, and the tag format uses a raw suffix.

**Key characteristics**

- **Authentication:** It requires credentials, and the docs list obtaining the built-in registry credentials as a prerequisite. Pulls from the tenant are authenticated, unlike ECR Public or Docker Hub.
- **Architecture:** A community answer notes the server acts as the Docker registry and provides only x86 images. For other CPU architectures, use the public registry images instead.
- **Not for mirroring:** The docs say not to use the built-in registry for copying images to private registries. For ActiveGate and the other images, mirror from public ECR (the docs show `skopeo copy --all`). The exception is the classic full-stack OneAgent image, which has no public source.
- **Versioning:** Tags are version-based, and there are no mutable `latest` tags on the tenant, Docker Hub or ECR Public. Pin exact versions.
- **ActiveGate role:** The ActiveGate can route and cache image downloads when the cluster can't reach Dynatrace directly. It isn't a registry itself.

**Practical notes for the POC**

- Use the correct domain: the Environment API domain, not the `.apps.` UI domain. The wrong one fails silently.
- Keep PaaS or registry tokens out of `ARG`/`ENV` and verbose curl output. Base64 Authorization headers are easy to leak.
- A tag or digest lookup only proves the image exists and is reachable. Only a full pull verifies the layers via SHA-256.
- For Kubernetes, once images are in your own registry, point DynaKube's `image`, `codeModulesImage` and `customPullSecret` fields at it.

I can turn this into a section for the POC addendum, or extend it into a short comparison of tenant registry, ECR Public and Docker Hub if that helps.
