import pathlib

from python_on_whales import docker

if __name__ == "__main__":
    env_file = pathlib.Path(__file__).parent / ".env"
    compose_mongodb_filepath = (
        pathlib.Path(__file__).parent / "docker-compose.mongodb.yaml"
    )

    print("Deploying MongoDB stack")
    docker.stack.deploy(
        "arion-benchmark", compose_mongodb_filepath, env_files=[env_file]
    )

    input("Press Enter to remove the stack...")

    docker.stack.remove("arion-benchmark")
    print("MongoDB stack removed")
