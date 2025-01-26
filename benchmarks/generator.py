import os

import yaml


def arion_compose_generator(
    adapters: list,
    processors: dict[str, list],
    n_classifiers: int,
    n_actuators: int,
    file_name: str,
    dir_path: str = ".",
    root_path: str = ".",
    name: str = "arion-bechmark",
):
    compose = {
        "name": name,
        "volumes": {},
        "services": {
            "broker": {
                "build": f"{root_path}/services/broker",
                "environment": {
                    "RABBITMQ_DEFAULT_USER": "${BROKER_RABBITMQ_DEFAULT_USER}",
                    "RABBITMQ_DEFAULT_PASS": "${BROKER_RABBITMQ_DEFAULT_PASS}",
                },
            }
        },
    }

    # Adiciona adaptadores
    for i, adapter in enumerate(adapters):
        compose["services"][f"stream-adapter-{i}"] = {
            "build": f"{root_path}/services/stream-adapter",
            "expose": ["5000"],
            "environment": {
                "SOURCE_URI": adapter["source_uri"],
                "LOG_LEVEL": "${LOG_LEVEL}",
            },
            "volumes": ["./videos:/videos"],
        }

    # Adiciona processadores
    for processor_type, processor_list in processors.items():
        for i, processor in enumerate(processor_list):
            service_name = f"stream-processor-{processor_type}-{i}"
            sender = processor["sender"]
            sender_uri = f"{sender}:5000"

            compose["services"][service_name] = {
                "build": f"{root_path}/services/stream-processors/base",
                "expose": ["5000"],
                "environment": {
                    "SENDER_URI": sender_uri,
                    "BROKER_RABBITMQ_CONNECTION_URI": "${BROKER_RABBITMQ_CONNECTION_URI}",
                    "BROKER_RABBITMQ_EXCHANGE_NAME": "${BROKER_RABBITMQ_EXCHANGE_NAME}",
                    "LOG_LEVEL": "${LOG_LEVEL}",
                },
                "depends_on": {
                    "broker": {"condition": "service_healthy"},
                    sender: {"condition": "service_started"},
                },
            }

    # Adiciona classificadores
    for i in range(n_classifiers):
        compose["services"][f"classifier-js-all-{i}"] = {
            "build": f"{root_path}/services/classifiers/base-js",
            "environment": {
                "BROKER_RABBITMQ_CONNECTION_URI": "${BROKER_RABBITMQ_CONNECTION_URI}",
                "BROKER_RABBITMQ_EXCHANGE_NAME": "${BROKER_RABBITMQ_EXCHANGE_NAME}",
                "LOG_LEVEL": "${LOG_LEVEL}",
            },
        }

    # Adiciona atuadores
    for i in range(n_actuators):
        compose["services"][f"actuator-{i}"] = {
            "build": f"{root_path}/services/actuator",
            "environment": {
                "LOG_LEVEL": "${LOG_LEVEL}",
            },
        }

    os.makedirs(dir_path, exist_ok=True)

    with open(f"{dir_path}/{file_name}", "w") as file:
        yaml.dump(compose, file, sort_keys=False, default_flow_style=False, indent=2)


if __name__ == "__main__":
    adapters = [
        {"source_uri": "http://localhost:8080"},
        {"source_uri": "http://localhost:8081"},
    ]
    processors = {
        "face": [{"sender": "stream-adapter-0"}, {"sender": "stream-adapter-1"}],
        "object": [{"sender": "stream-adapter-0"}, {"sender": "stream-adapter-1"}],
    }
    n_classifiers = 2
    n_actuators = 2

    arion_compose_generator(
        adapters,
        processors,
        n_classifiers,
        n_actuators,
        "docker-compose.bench.yaml",
        root_path="..",
    )
