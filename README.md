# APL Golf League Backend

The backend server for the APL Golf League website, containing the relevant databases and APIs.

## Deployment

This project uses GitHub Actions to deploy to the application hosted on a Digital Ocean droplet. The application is comprised of several docker containers that are orchestrated with several `docker-compose` files.

### Staging Environment

A staging environment is used to deploy new images for testing, along with an accompanying staging frontend.

To deploy the API to the staging environment, create and push a tag that matches the format "t*.*.*" such as:

```sh
git tag tX.Y.Z.n
git push --tags
```

The GitHub Action triggered by this push will build and push the image to the GitHub Container Registry (ghcr.io), then ssh into the server (Digital Ocean Droplet) to pull that image from the registry, update an environment variable that defines the staging tag to match, and run the deploy script to stop the existing container and stand up the new one.
