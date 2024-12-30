docker container stop aplgolfapi-staging
docker-compose -f docker-compose.aplgolfapi.yml --env-file .env.staging up -d
