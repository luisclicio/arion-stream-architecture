import json
import os
import pathlib

import yaml


def arion_compose_generator(
    adapters: list,
    processors: dict[str, list],
    n_classifiers: int,
    n_actuators: int,
    file_name: str,
    dir_path: str = ".",
    root_path: str = ".",
    generator_env: dict = {},
):
    compose = {
        "volumes": {
            "mongodb_data": {},
        },
        "services": {
            "clock": {
                "image": "127.0.0.1:5000/arion-benchmark-clock",
                "build": f"{root_path}/services/clock",
                "deploy": {
                    "mode": "global",
                    "placement": {
                        "constraints": ["node.role == manager"],
                    },
                },
            },
            "broker": {
                "image": "127.0.0.1:5000/arion-benchmark-broker",
                "build": f"{root_path}/services/broker",
                "environment": {
                    "RABBITMQ_DEFAULT_USER": "${BROKER_RABBITMQ_DEFAULT_USER}",
                    "RABBITMQ_DEFAULT_PASS": "${BROKER_RABBITMQ_DEFAULT_PASS}",
                },
                "deploy": {
                    "mode": "global",
                    "placement": {
                        "constraints": ["node.role == manager"],
                    },
                },
            },
            "mongodb": {
                "image": "mongo:8",
                "environment": {
                    "MONGO_INITDB_ROOT_USERNAME": "${MONGO_USERNAME}",
                    "MONGO_INITDB_ROOT_PASSWORD": "${MONGO_PASSWORD}",
                },
                "ports": ["27017:27017"],
                "volumes": ["mongodb_data:/data/db"],
                "deploy": {
                    "mode": "global",
                    "placement": {
                        "constraints": ["node.role == manager"],
                    },
                },
            },
        },
    }
    BROKER_RABBITMQ_HOST = "broker:5672"

    # Adiciona adaptadores
    for i, adapter in enumerate(adapters):
        service_name = f"stream-adapter-{i}"
        compose["services"][service_name] = {
            "image": "127.0.0.1:5000/arion-benchmark-adapter",
            "build": f"{root_path}/services/stream-adapter",
            "expose": ["5000"],
            "command": f"wait-for-it {BROKER_RABBITMQ_HOST} -- python -m src.main",
            "environment": {
                "SERVICE_TYPE": "stream-adapter",
                "SERVICE_NAME": service_name,
                "SOURCE_URI": adapter["source_uri"],
                "MONGO_URI": "mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodb:27017/",
                "LOG_LEVEL": "${LOG_LEVEL}",
                **generator_env,
            },
            "deploy": {
                "restart_policy": {
                    "condition": "none",
                },
            },
        }

    # Adiciona processadores
    for processor_type, processor_list in processors.items():
        for i, processor in enumerate(processor_list):
            service_name = f"stream-processor-{processor_type}-{i}"
            sender = processor["sender"]
            sender_uri = f"{sender}:5000"

            compose["services"][service_name] = {
                "image": "127.0.0.1:5000/arion-benchmark-processor",
                "build": f"{root_path}/services/stream-processors/base",
                "command": f"wait-for-it {sender_uri} -- python -m src.main",
                "expose": ["5000"],
                "environment": {
                    "SERVICE_TYPE": "stream-processor",
                    "SERVICE_NAME": service_name,
                    "SENDER_URI": sender_uri,
                    "BROKER_RABBITMQ_CONNECTION_URI": "${BROKER_RABBITMQ_CONNECTION_URI}",
                    "BROKER_RABBITMQ_EXCHANGE_NAME": "${BROKER_RABBITMQ_EXCHANGE_NAME}",
                    "MONGO_URI": "mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodb:27017/",
                    "LOG_LEVEL": "${LOG_LEVEL}",
                    **generator_env,
                },
                # "depends_on": {
                #     "broker": {"condition": "service_healthy"},
                #     sender: {"condition": "service_started"},
                # },
                "depends_on": ["broker", sender],
                "deploy": {
                    "restart_policy": {
                        "condition": "none",
                    },
                },
            }

    # Adiciona classificadores
    for i in range(n_classifiers):
        service_name = f"classifier-js-all-{i}"
        compose["services"][service_name] = {
            "image": "127.0.0.1:5000/arion-benchmark-classifier",
            "build": f"{root_path}/services/classifiers/base-js",
            "command": f"wait-for-it {BROKER_RABBITMQ_HOST} -- node index.js",
            "environment": {
                "SERVICE_TYPE": "classifier",
                "SERVICE_NAME": service_name,
                "BROKER_RABBITMQ_CONNECTION_URI": "${BROKER_RABBITMQ_CONNECTION_URI}",
                "BROKER_RABBITMQ_EXCHANGE_NAME": "${BROKER_RABBITMQ_EXCHANGE_NAME}",
                "MONGO_URI": "mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodb:27017/",
                "LOG_LEVEL": "${LOG_LEVEL}",
                **generator_env,
            },
            "depends_on": ["broker"],
            "deploy": {
                "restart_policy": {
                    "condition": "none",
                },
            },
        }

    # Adiciona atuadores
    for i in range(n_actuators):
        service_name = f"actuator-{i}"
        compose["services"][service_name] = {
            "image": "127.0.0.1:5000/arion-benchmark-actuator",
            "build": f"{root_path}/services/actuators/base-js",
            "command": f"wait-for-it {BROKER_RABBITMQ_HOST} -- node index.js",
            "environment": {
                "SERVICE_TYPE": "actuator",
                "SERVICE_NAME": service_name,
                "BROKER_RABBITMQ_CONNECTION_URI": "${BROKER_RABBITMQ_CONNECTION_URI}",
                "BROKER_RABBITMQ_EXCHANGE_NAME": "${BROKER_RABBITMQ_EXCHANGE_NAME}",
                "MONGO_URI": "mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodb:27017/",
                "LOG_LEVEL": "${LOG_LEVEL}",
                **generator_env,
            },
            "depends_on": ["broker"],
            "deploy": {
                "restart_policy": {
                    "condition": "none",
                },
            },
        }

    os.makedirs(dir_path, exist_ok=True)

    with open(f"{dir_path}/{file_name}", "w") as file:
        yaml.dump(compose, file, sort_keys=False, default_flow_style=False, indent=2)


if __name__ == "__main__":
    # Creates base services stack
    base_stack = {
        "adapters": [
            {"source_uri": "http://localhost:8080"},
        ],
        "processors": {
            "type-a": [{"sender": "stream-adapter-0"}],
        },
        "n_classifiers": 1,
        "n_actuators": 1,
    }

    arion_compose_generator(
        base_stack["adapters"],
        base_stack["processors"],
        base_stack["n_classifiers"],
        base_stack["n_actuators"],
        "docker-compose.base.yaml",
        dir_path="benchmarks",
        root_path="..",
        generator_env={
            "STACK_ID": "base_1ad_1p_1c_1at",
        },
    )

    # Creates benchmark stacks
    with open(pathlib.Path(__file__).parent / "stacks.json", "r") as file:
        stacks = json.load(file)

    for stack in stacks:
        n_adapters = len(stack["adapters"])
        n_processors = sum(
            [len(processors) for processors in stack["processors"].values()]
        )
        n_classifiers = stack["n_classifiers"]
        n_actuators = stack["n_actuators"]

        stack_id = f"{n_adapters}ad_{n_processors}p_{n_classifiers}c_{n_actuators}at"

        arion_compose_generator(
            stack["adapters"],
            stack["processors"],
            stack["n_classifiers"],
            stack["n_actuators"],
            f"docker-compose.bench.{stack_id}.yaml",
            dir_path="benchmarks",
            root_path="..",
            generator_env={
                "STACK_ID": stack_id,
            },
        )
