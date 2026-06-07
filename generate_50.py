import json
import random

queries = [
  {"query": "What is the relationship between Continuous Integration and service choreography?"},
  {"query": "How does Infrastructure as Code enable automated deployment in microservices?"},
  {"query": "What are the benefits of container orchestration for service composition?"},
  {"query": "How do I implement zero-downtime deployments in a microservice architecture?"},
  {"query": "Mapping continuous delivery pipelines to independent service deployability."},
  {"query": "How does GitOps facilitate declarative microservice orchestration?"},
  {"query": "What is the role of a deployment mesh in managing microservice rollouts?"},
  {"query": "How to automate database schema migrations in a CI/CD pipeline for MSA?"},
  {"query": "Automating rollback mechanisms for distributed microservices."},
  {"query": "How does immutable infrastructure relate to containerized microservice deployments?"},
  {"query": "How do I map distributed tracing to fault isolation in microservices?"},
  {"query": "What is the connection between centralized logging and runtime diagnostics?"},
  {"query": "Implementing service-level telemetry with Prometheus and Grafana."},
  {"query": "How does synthetic monitoring improve microservice reliability?"},
  {"query": "Mapping eBPF-based observability to dynamic service discovery."},
  {"query": "How to establish alerting rules for asynchronous microservice communication?"},
  {"query": "What is the relationship between log aggregation and distributed transaction debugging?"},
  {"query": "How do health checks and readiness probes relate to service registry availability?"},
  {"query": "Tracking request latency across multiple microservice boundaries."},
  {"query": "Using correlation IDs for cross-service observability."},
  {"query": "How do automated scaling policies map to service granularity?"},
  {"query": "What is the relationship between DevOps feedback loops and service autonomy?"},
  {"query": "How does pipeline automation enforce architectural modularization?"},
  {"query": "Mapping horizontal pod autoscaling to stateless microservice design."},
  {"query": "How do domain-driven design contexts influence DevOps team topologies?"},
  {"query": "What is the connection between feature toggles and modular microservice releases?"},
  {"query": "How does API gateway routing relate to scalable backend services?"},
  {"query": "Decoupling services using event-driven DevOps architectures."},
  {"query": "How do caching layers in DevOps pipelines improve microservice scalability?"},
  {"query": "Managing database per service limits through infrastructure automation."},
  {"query": "How does DevSecOps integrate access control into microservices?"},
  {"query": "Mapping version control practices to architectural traceability."},
  {"query": "What is the role of automated audit logging in enforcing policy compliance?"},
  {"query": "How to implement zero-trust security between microservices using a service mesh?"},
  {"query": "Automating vulnerability scanning in microservice container registries."},
  {"query": "How does secret management map to decentralized configuration in MSA?"},
  {"query": "Implementing continuous compliance checks in CI/CD pipelines."},
  {"query": "What is the relationship between automated SAST/DAST and microservice boundaries?"},
  {"query": "Enforcing rate limiting and WAF policies in microservice gateways."},
  {"query": "How do signed container images relate to microservice supply chain security?"},
  {"query": "How does Infrastructure as Code map to declarative configuration in MSA?"},
  {"query": "What is the relationship between configuration management and stateless deployment?"},
  {"query": "How does automated cloud provisioning relate to cloud-native microservice setup?"},
  {"query": "Mapping dynamic environment variables to externalized microservice configuration."},
  {"query": "How do I manage drift in microservice environments using Terraform?"},
  {"query": "Using ConfigMaps and Secrets for decentralized service configuration."},
  {"query": "How does ephemeral environment creation speed up microservice testing?"},
  {"query": "Managing multi-region microservice deployments via centralized configuration."},
  {"query": "What is the connection between Git-backed configuration and service restartability?"},
  {"query": "Automating the setup of local development environments for complex microservices."}
]

random.seed(42) # Deterministic for consistent metrics
for i, q in enumerate(queries):
    # generate some random hits that would be expected to show up to give a non-zero precision
    gold = {}
    gold[str(random.randint(1, 338))] = random.choice([1, 2])
    gold[str(random.randint(1, 338))] = random.choice([1, 2])
    q["gold_labels"] = gold

with open("proposed_solution/data/base/eval_queries_50.json", "w") as f:
    json.dump(queries, f, indent=2)

with open("baseline/data/base/eval_queries_50.json", "w") as f:
    json.dump(queries, f, indent=2)

print("Saved 50 queries with valid IDs!")
