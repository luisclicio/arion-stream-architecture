import glob
import pathlib
from datetime import datetime

from python_on_whales import docker

if __name__ == "__main__":
    # Read all files that match the pattern
    compose_benchmark_files = glob.glob(
        str(pathlib.Path(__file__).parent / "docker-compose.bench.*")
    )
    env_file = pathlib.Path(__file__).parent / ".env"

    print("=> Benchmark files found:", compose_benchmark_files, end="\n\n")

    # Deploy the stacks in sequence (one by one)
    for compose_benchmark_file in compose_benchmark_files:
        compose_filename = pathlib.Path(compose_benchmark_file).name

        option = input(
            f"=> Do you want to deploy the stack `{compose_filename}`? [y/N/c] "
        )

        if option.lower() == "c":
            # Cancel all deployments
            break

        if option.lower() != "y":
            # Skip this deployment
            continue

        print(f"=> [{datetime.now()}] Deploying stack: {compose_filename}")
        docker.stack.deploy(
            "arion-benchmark", compose_benchmark_file, env_files=[env_file]
        )

        print("=> Waiting for stack to complete...")
        # Wait for the stack to complete (you may need to implement a proper wait mechanism)
        input("=> Press Enter after the stack has completed...")

        docker.stack.remove("arion-benchmark")
        print(f"=> [{datetime.now()}] Stack removed: {compose_filename}")
        print()
