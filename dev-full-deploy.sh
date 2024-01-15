sudo docker compose -f .docker/dev-compose.yml --env-file=.envs/.dev up -d --build;
sudo docker compose -f .docker/dev-worker-compose.yml --env-file=.envs/.dev up -d --build;