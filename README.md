# APL Golf League Backend

The backend server for the APL Golf League website, containing the relevant databases and APIs.

## Development

This project uses `uv` for package management including virtual environments and dependencies.

```sh
uv venv -p 3.12
source .venv/bin/activate # on unix-based systems, or
.venv/Scripts/activate # on Windows
uv sync --dev
```

## Deployment

This project uses GitHub Actions to deploy to the application hosted on a Digital Ocean droplet. The application is comprised of several docker containers that are orchestrated with several `docker-compose` files.

### Staging Environment

A staging environment is used to deploy new images for testing, along with an accompanying staging frontend.

To deploy the API to the staging environment, create and push a tag that matches the format `t*.*.*` such as:

```sh
git tag tX.Y.Z.n
git push --tags
```

The GitHub Action triggered by this push will build and push the image to the GitHub Container Registry (ghcr.io), then ssh into the server (Digital Ocean Droplet) to pull that image from the registry, update an environment variable that defines the staging tag to match, and run the deploy script to stop the existing container and stand up the new one.

### Production Environment

Similarly, the production environment uses GitHub Actions for deploying new APIs. Simply push a new tag with `v*.*.*` format instead:

```sh
git tag vX.Y.Z.n
git push --tags
```
