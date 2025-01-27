# https://docs.docker.com/engine/swarm/stack-deploy/
import pathlib

from python_on_whales import DockerClient, docker

# Initialize the Docker swarm on the manager
try:
    docker.swarm.init()
except Exception:
    # print(error)
    pass

# Get the join token for worker nodes
worker_join_token = docker.swarm.join_token("worker")

# Connect to the worker nodes via SSH
worker1_docker = DockerClient(host="ssh://user@system-vm1.local")
worker2_docker = DockerClient(host="ssh://user@system-vm2.local")

# # Join the worker nodes to the swarm
worker1_docker.swarm.join("system.local:2377", token=worker_join_token)
worker2_docker.swarm.join("system.local:2377", token=worker_join_token)

# Setup the registry
compose_registry_file = pathlib.Path(__file__).parent / "docker-compose.registry.yaml"
docker.stack.deploy("registry", compose_registry_file)
# docker.stack.remove("registry")

# Build and push the images from compose to the registry
compose_benchmark_file = pathlib.Path(__file__).parent / "docker-compose.base.yaml"

docker_compose_benchmark = DockerClient(compose_files=[compose_benchmark_file])
docker_compose_benchmark.compose.build()
docker_compose_benchmark.compose.push()
