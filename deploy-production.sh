docker container stop aplgolfapi-production
docker-compose -f docker-compose.aplgolfapi.yml --env-file .env.production up -d
