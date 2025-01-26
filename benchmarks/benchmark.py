from python_on_whales import DockerClient

if __name__ == "__main__":
    docker = DockerClient(compose_files=["docker-compose.bench.yaml"])
    print(docker.compose.config(return_json=True))
