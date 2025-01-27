import pathlib

from python_on_whales import docker

if __name__ == "__main__":
    compose_benchmark_file = pathlib.Path(__file__).parent / "docker-compose.base.yaml"

    # Deploy the stack
    docker.stack.deploy("arion-benchmark", compose_benchmark_file)
