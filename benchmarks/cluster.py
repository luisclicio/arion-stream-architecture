# https://docs.docker.com/engine/swarm/stack-deploy/
import os
import pathlib
import socket

from dotenv import load_dotenv
from python_on_whales import DockerClient, docker

load_dotenv(dotenv_path=pathlib.Path(__file__).parent / ".env")

# Initialize the Docker swarm on the manager
try:
    docker.swarm.init()
except Exception:
    # print(error)
    pass

# Get the join token for worker nodes and manager address
worker_join_token = docker.swarm.join_token("worker")
manager_address = socket.gethostname()
cluster_nodes_ssh = filter(
    lambda node: node != "", os.environ.get("CLUSTER_NODES_SSH", "").split(",")
)

for node_ssh in cluster_nodes_ssh:
    # Connect to the worker node via SSH
    node_docker = DockerClient(host=f"ssh://{node_ssh}")
    # Leave the swarm if already joined
    try:
        node_docker.swarm.leave(force=True)
    except Exception:
        pass
    # Join the worker node to the swarm
    node_docker.swarm.join(f"{manager_address}:2377", token=worker_join_token)

# Setup the registry
compose_registry_file = pathlib.Path(__file__).parent / "docker-compose.registry.yaml"
docker.stack.deploy("registry", compose_registry_file)
# docker.stack.remove("registry")

# Build and push the images from compose to the registry
compose_benchmark_file = pathlib.Path(__file__).parent / "docker-compose.base.yaml"

docker_compose_benchmark = DockerClient(compose_files=[compose_benchmark_file])
docker_compose_benchmark.compose.build()
docker_compose_benchmark.compose.push()
