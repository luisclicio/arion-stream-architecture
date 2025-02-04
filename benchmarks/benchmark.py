import glob
import pathlib

from python_on_whales import docker

if __name__ == "__main__":
    # Read all files that match the pattern
    compose_benchmark_files = glob.glob(
        str(pathlib.Path(__file__).parent / "docker-compose.bench.*")
    )

    print("Benchmark files found:", compose_benchmark_files)

    # Deploy the stacks in sequence (one by one)
    for compose_benchmark_file in compose_benchmark_files:
        compose_benchmark_filepath = (
            pathlib.Path(__file__).parent / compose_benchmark_file
        )

        print("Deploying stack:", compose_benchmark_file)
        docker.stack.deploy("arion-benchmark", compose_benchmark_filepath)

        print("Waiting for stack to complete...")
        # Wait for the stack to complete (you may need to implement a proper wait mechanism)
        input("Press Enter after the stack has completed...")

        docker.stack.remove("arion-benchmark")
        print("Stack removed:", compose_benchmark_file)
