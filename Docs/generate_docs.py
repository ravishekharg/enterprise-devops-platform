"""One-off generation script for the Darviq Enterprise HLD/LLD .docx files.

Run from anywhere with: python generate_docs.py
(docx_builder.py must sit alongside this file.)

Kept in Docs/ so the documents can be regenerated later if the repo evolves;
not required at runtime by anything else in this repository.
"""
from docx_builder import DesignDoc

VERSION = "1.0"
DATE = "July 31, 2026"
REPO_ROOT = "D:/Projects/DevOps/Darviq-Enterprise"

# =====================================================================
# HLD
# =====================================================================

def build_hld():
    doc = DesignDoc(
        project_name="Darviq Enterprise",
        subtitle="Enterprise DevOps Platform on AWS EKS",
        doc_kind="High-Level Design (HLD)",
        version=VERSION,
        date=DATE,
    )
    doc.add_document_control()
    doc.add_toc_field()

    # 1. Introduction
    doc.add_heading1("1. Introduction")

    doc.add_heading2("1.1 Purpose")
    doc.add_paragraph(
        "This document describes the High-Level Design (HLD) of Darviq Enterprise, "
        "a portfolio repository that demonstrates a production-style enterprise "
        "DevOps / platform-engineering stack on AWS EKS. It records the architecture, "
        "component responsibilities, workflows, and design decisions actually present "
        "in the repository's Terraform, Helm, CI/CD, and automation scripts as of the "
        "date of this document, and calls out honestly where a piece of the platform "
        "is a simplification, a scaffold for future work, or not yet wired end-to-end."
    )

    doc.add_heading2("1.2 Scope")
    doc.add_paragraph("In scope for this document:")
    doc.add_bullets([
        "Terraform provisioning of the AWS network and EKS cluster (terraform/).",
        "Helm-based deployment of MySQL, Keycloak, and the Prometheus/Grafana "
        "monitoring stack (helm/deploy.sh).",
        "The GitHub Actions CI/CD pipeline that validates Terraform and runs the "
        "Helm deployment (.github/workflows/platform.yml).",
        "The automated MySQL backup script (backup/backup.py).",
        "The cluster health monitoring script (monitoring/cluster_monitor.py).",
        "The multi-environment tfvars scaffolding under terraform/environments/.",
    ])
    doc.add_paragraph("Out of scope for this document:")
    doc.add_bullets([
        "Any application code that would run inside the cluster and use the "
        "MySQL/Keycloak services (no such application is part of this repository).",
        "Detailed low-level implementation and file/line-level specifics — those "
        "are covered in the companion Low-Level Design document.",
        "Enhancements only described in the README's \"Future Enhancements\" list "
        "(ArgoCD, Sealed Secrets, ExternalDNS, AWS Load Balancer Controller, "
        "Cluster Autoscaler, multi-region DR) — these are not yet implemented and "
        "are referenced only as forward-looking direction (Section 12).",
    ])

    doc.add_heading2("1.3 Intended audience")
    doc.add_bullets([
        "Platform/DevOps engineers evaluating or extending this repository.",
        "Reviewers and hiring managers assessing the Darviq Systems portfolio.",
        "Anyone onboarding onto the repository who needs an architectural map "
        "before reading Terraform/Helm/script source directly.",
    ])

    doc.add_heading2("1.4 Definitions & abbreviations")
    doc.add_table(
        headers=["Term", "Definition"],
        rows=[
            ["EKS", "Amazon Elastic Kubernetes Service — AWS's managed Kubernetes control plane."],
            ["VPC", "Virtual Private Cloud — the isolated AWS network the cluster runs in."],
            ["IaC", "Infrastructure as Code — infrastructure defined and provisioned via Terraform."],
            ["IRSA", "IAM Roles for Service Accounts — mechanism for granting AWS IAM permissions to individual Kubernetes pods."],
            ["Helm", "The Kubernetes package manager used to install MySQL, Keycloak, and the monitoring stack."],
            ["SRE", "Site Reliability Engineering."],
            ["CI/CD", "Continuous Integration / Continuous Deployment — implemented here via GitHub Actions."],
            ["RPO / RTO", "Recovery Point Objective / Recovery Time Objective — backup and disaster-recovery targets."],
            ["PVC", "Persistent Volume Claim — a Kubernetes request for durable storage."],
            ["SSO", "Single Sign-On — provided in this platform by Keycloak."],
            ["NAT Gateway", "AWS component allowing private-subnet resources outbound internet access."],
            ["tfvars", "A Terraform variables file (e.g. terraform/environments/dev/variables.tfvars)."],
        ],
    )

    # 2. System overview
    doc.add_heading1("2. System overview")

    doc.add_heading2("2.1 Problem statement")
    doc.add_paragraph(
        "Running a Kubernetes-based platform in production requires more than a "
        "running cluster: it requires reproducible infrastructure provisioning, a "
        "consistent way to deploy shared platform services (a stateful database, an "
        "identity provider, observability tooling), a CI/CD path from a git push to "
        "a running change, and a defined story for backing up stateful data. Darviq "
        "Enterprise exists to demonstrate this platform-engineering discipline end to "
        "end — Terraform for infrastructure, Helm for service lifecycle, GitHub "
        "Actions for automation, and small Python utilities for backup and health "
        "checking — using the same tools and shapes a small platform team would "
        "reach for, at a scale appropriate to a portfolio project rather than a "
        "large multi-tenant production estate."
    )

    doc.add_heading2("2.2 Proposed solution summary")
    doc.add_paragraph(
        "The repository provisions a multi-AZ VPC and an EKS cluster via Terraform, "
        "then uses a single Helm script to install MySQL (Bitnami chart), Keycloak "
        "(Bitnami chart), and the kube-prometheus-stack chart (which bundles "
        "Prometheus, Alertmanager, and Grafana). A GitHub Actions workflow runs on "
        "every push to main to validate the Terraform configuration and re-run the "
        "Helm deployment against a cluster addressed via a stored kubeconfig secret. "
        "Two standalone Python scripts provide operational tooling: one performs "
        "logical MySQL dumps for backup, and one queries the Kubernetes API to "
        "surface unhealthy pods and restart loops. Terraform remote state is stored "
        "in S3 with DynamoDB locking, and a terraform/environments/{dev,stage,prod} "
        "directory structure sketches out multi-environment separation for future use."
    )

    # 3. Architecture overview
    doc.add_heading1("3. Architecture overview")
    doc.add_table(
        headers=["Component", "Responsibility", "Technology"],
        rows=[
            ["VPC & networking", "Multi-AZ network with public/private subnet split and NAT egress for the cluster", "terraform-aws-modules/vpc/aws v5.0.0"],
            ["EKS cluster", "Managed Kubernetes control plane and a managed worker node group", "terraform-aws-modules/eks/aws v19.0.0, Kubernetes 1.29"],
            ["MySQL", "Stateful relational data store for platform/application use", "Bitnami mysql Helm chart"],
            ["Keycloak", "Identity provider / SSO for platform services", "Bitnami keycloak Helm chart"],
            ["Prometheus + Grafana", "Metrics collection, alerting components, and dashboards", "prometheus-community/kube-prometheus-stack Helm chart"],
            ["CI/CD pipeline", "Validates Terraform and re-applies the Helm deployment on every push to main", "GitHub Actions (.github/workflows/platform.yml)"],
            ["Backup automation", "Logical MySQL dumps for a fixed list of databases", "Python script (backup/backup.py)"],
            ["Cluster health monitor", "Ad hoc scan for non-running pods and restart loops", "Python script using the kubernetes client (monitoring/cluster_monitor.py)"],
            ["Terraform remote state", "Shared state storage and locking for the Terraform configuration", "AWS S3 (encrypted) + DynamoDB (terraform/backend.tf)"],
        ],
    )

    doc.add_heading2("3.1 Component descriptions")
    doc.add_heading3("VPC & EKS cluster")
    doc.add_paragraph(
        "terraform/main.tf declares a VPC module (\"enterprise-platform-vpc\", CIDR "
        "10.10.0.0/16) spanning ap-south-1a/b/c with three private and three public "
        "subnets and a NAT gateway, and an EKS module (\"enterprise-platform-cluster\", "
        "Kubernetes 1.29) that places its managed node group in the private subnets "
        "with IRSA enabled and a single \"default\" node group sized min 3 / desired 6 "
        "/ max 9 t3.medium instances."
    )
    doc.add_heading3("MySQL, Keycloak, monitoring stack")
    doc.add_paragraph(
        "helm/deploy.sh adds the bitnami, prometheus-community, and grafana chart "
        "repositories and installs three releases with unmodified chart defaults: "
        "mysql (bitnami/mysql), keycloak (bitnami/keycloak), and monitoring "
        "(prometheus-community/kube-prometheus-stack). The kube-prometheus-stack "
        "chart itself bundles Grafana, so no separate grafana/grafana release is "
        "installed even though the grafana repo is added."
    )
    doc.add_heading3("CI/CD pipeline")
    doc.add_paragraph(
        "The \"Enterprise Platform Pipeline\" workflow triggers on every push to main, "
        "installs kubectl and Helm, writes a kubeconfig from a GitHub secret, runs "
        "terraform validate, and then runs helm/deploy.sh. It validates Terraform "
        "syntax and re-applies the Helm release set on every push; it does not run "
        "terraform plan or terraform apply, so cluster/infrastructure provisioning "
        "remains a manual operator step (README Step 1)."
    )
    doc.add_heading3("Backup and monitoring scripts")
    doc.add_paragraph(
        "backup/backup.py runs mysqldump for a hardcoded set of three databases "
        "(users, orders, payments) into dated files under /backup. "
        "monitoring/cluster_monitor.py connects to the cluster via a local "
        "kubeconfig and lists all pods, flagging any not in the Running phase. Both "
        "are standalone scripts run manually today rather than services or "
        "scheduled jobs defined inside this repository."
    )

    # 4. End-to-end functional workflow
    doc.add_heading1("4. End-to-end functional workflow")
    doc.add_figure_placeholder("Figure 1 — Change/deployment flow: push to main through GitHub Actions to Helm-deployed services")
    doc.add_paragraph(
        "A developer pushes a change to the main branch. GitHub Actions checks out "
        "the repository, installs kubectl and Helm, and loads a kubeconfig from a "
        "stored secret so it can reach the target cluster. It then runs "
        "terraform validate to catch configuration errors, and runs helm/deploy.sh, "
        "which re-applies the mysql, keycloak, and monitoring Helm releases against "
        "the cluster. Because there is no terraform apply step in the pipeline, "
        "infrastructure changes (VPC/EKS changes) must be applied manually by an "
        "operator running terraform apply from the terraform/ directory before the "
        "pipeline's Helm step can target a cluster that reflects them."
    )
    doc.add_figure_placeholder("Figure 2 — Backup workflow: manual/scheduled invocation through mysqldump to dated dump files")
    doc.add_paragraph(
        "Separately, an operator (or an external scheduler not defined in this "
        "repository) invokes python backup/backup.py. The script iterates over a "
        "fixed list of three database names, running mysqldump for each into a file "
        "named for the database and the current date under /backup. A checksum() "
        "helper capable of computing an MD5 hash is defined in the same file but is "
        "not invoked by the script's main flow, so no checksum validation, upload, "
        "or retention/cleanup currently happens as part of this workflow."
    )

    # 5. Module-wise design overview
    doc.add_heading1("5. Module-wise design overview")

    doc.add_heading2("5.1 EKS / Terraform provisioning")
    doc.add_paragraph(
        "terraform/main.tf composes the community terraform-aws-modules/vpc/aws and "
        "terraform-aws-modules/eks/aws modules to stand up the network and cluster. "
        "terraform/backend.tf configures an S3 + DynamoDB remote backend for shared, "
        "locked state. terraform/environments/{dev,stage,prod}/variables.tfvars "
        "sketch per-environment cluster naming and node counts, though these values "
        "are not yet consumed by main.tf (see Section 11)."
    )

    doc.add_heading2("5.2 MySQL Helm deployment")
    doc.add_paragraph(
        "A single Bitnami mysql chart is installed with default values via "
        "helm/deploy.sh, providing a stateful MySQL instance for platform or "
        "application use. No custom values file or app-specific schema is "
        "committed to the repository (see Section 6, Data design)."
    )

    doc.add_heading2("5.3 Keycloak identity deployment")
    doc.add_paragraph(
        "A single Bitnami keycloak chart is installed with default values, giving "
        "the platform an identity provider with the chart's default \"master\" "
        "realm. No realm/client export is checked into the repository."
    )

    doc.add_heading2("5.4 Prometheus / Grafana monitoring")
    doc.add_paragraph(
        "The prometheus-community/kube-prometheus-stack chart is installed as the "
        "\"monitoring\" release, bundling Prometheus, Alertmanager, and Grafana with "
        "chart-default scrape configuration and dashboards for node, pod, container, "
        "and API server metrics."
    )

    doc.add_heading2("5.5 CI/CD pipeline")
    doc.add_paragraph(
        "The GitHub Actions workflow in .github/workflows/platform.yml automates "
        "Terraform validation and Helm re-deployment on every push to main, as "
        "described in Sections 3.1 and 4."
    )

    doc.add_heading2("5.6 Automated DB backups")
    doc.add_paragraph(
        "backup/backup.py provides logical MySQL backups via mysqldump for a fixed "
        "set of database names, writing dated dump files to /backup, as described "
        "in Section 4."
    )

    doc.add_heading2("5.7 Cluster health monitoring")
    doc.add_paragraph(
        "monitoring/cluster_monitor.py provides an ad hoc scan of all pods in the "
        "cluster, flagging non-Running pods, with restart-loop detection also "
        "intended (see the Low-Level Design for a note on its current implementation)."
    )

    doc.add_heading2("5.8 Multi-environment scaffolding")
    doc.add_paragraph(
        "terraform/environments/dev, /stage, and /prod each hold a variables.tfvars "
        "file with a cluster_name and node_count pair, establishing the intended "
        "shape of environment separation. As of this document, terraform/main.tf "
        "does not declare input variables or reference these files via -var-file, "
        "so today the module always provisions the single hardcoded "
        "\"enterprise-platform-cluster\" configuration regardless of environment."
    )

    # 6. Data design
    doc.add_heading1("6. Data design")
    doc.add_paragraph(
        "This repository does not define or seed an application database schema. "
        "MySQL is deployed as a generic Bitnami-chart-managed instance. The only "
        "hint of a data model is the hardcoded list of three database names in "
        "backup/backup.py — users, orders, and payments — which implies these "
        "databases belong to an external, companion application that is out of "
        "scope for this repository; no DDL, migration, or seed script for them is "
        "present here."
    )
    doc.add_paragraph(
        "Keycloak similarly ships with no custom realm or client configuration "
        "checked into the repository. It runs with the Bitnami chart's default "
        "\"master\" realm, and any realm/client/role model an integrating "
        "application would need must be created out-of-band (e.g., via the "
        "Keycloak admin console or REST API) rather than being bootstrapped by "
        "anything in this repository today."
    )

    # 7. Technology stack
    doc.add_heading1("7. Technology stack")
    doc.add_table(
        headers=["Layer", "Technology", "Notes"],
        rows=[
            ["Cloud", "AWS", "ap-south-1 region"],
            ["IaC", "Terraform (~ modules v5.0.0 VPC / v19.0.0 EKS)", "terraform/main.tf, terraform/backend.tf"],
            ["Container orchestration", "Kubernetes 1.29 (Amazon EKS)", "Managed control plane, one managed node group"],
            ["Package manager", "Helm", "Bitnami + prometheus-community charts, chart defaults only"],
            ["CI/CD", "GitHub Actions", ".github/workflows/platform.yml, triggers on push to main"],
            ["Monitoring", "Prometheus + Grafana (kube-prometheus-stack)", "Bundled chart, default dashboards/scrape config"],
            ["Identity", "Keycloak", "Bitnami chart, default realm"],
            ["Data store", "MySQL", "Bitnami chart, no custom schema in-repo"],
            ["Backup automation", "Python (mysqldump + hashlib)", "backup/backup.py, run manually today"],
            ["Cluster health tooling", "Python (kubernetes client)", "monitoring/cluster_monitor.py, run manually today"],
            ["Remote state", "AWS S3 + DynamoDB", "terraform/backend.tf, bucket/table assumed pre-provisioned"],
        ],
    )

    # 8. Deployment architecture
    doc.add_heading1("8. Deployment architecture")
    doc.add_figure_placeholder("Figure 3 — VPC/EKS topology: 3 AZs, private subnets hosting the EKS node group, public subnets with NAT egress, Helm releases running inside the cluster")
    doc.add_paragraph(
        "The VPC spans three availability zones (ap-south-1a/b/c) with one private "
        "and one public subnet per zone. The EKS managed node group runs in the "
        "private subnets, with outbound internet access via a NAT gateway; the "
        "public subnets exist for the NAT gateway and any future internet-facing "
        "load balancers. The EKS control plane is managed by AWS. Inside the "
        "cluster, three Helm releases run as ordinary workloads: mysql, keycloak, "
        "and monitoring (kube-prometheus-stack, which schedules Prometheus, "
        "Alertmanager, and Grafana pods). There is no ingress controller, DNS "
        "automation, or load balancer controller configured in this repository "
        "today (see Section 12, Future enhancements)."
    )
    doc.add_table(
        headers=["Parameter", "Value / source"],
        rows=[
            ["AWS region", "ap-south-1 (hardcoded in terraform/main.tf and terraform/backend.tf)"],
            ["VPC CIDR", "10.10.0.0/16 (terraform/main.tf)"],
            ["Availability zones", "ap-south-1a, ap-south-1b, ap-south-1c"],
            ["Cluster name (active)", "enterprise-platform-cluster (hardcoded in terraform/main.tf)"],
            ["Kubernetes version", "1.29"],
            ["Node group sizing", "min 3 / desired 6 / max 9, instance type t3.medium"],
            ["Terraform state backend", "S3 bucket enterprise-devops-tf-state, key platform/eks/terraform.tfstate, DynamoDB table terraform-locks"],
            ["CI kubeconfig source", "GitHub Actions secret KUBECONFIG (.github/workflows/platform.yml)"],
        ],
    )

    # 9. Security design
    doc.add_heading1("9. Security design")
    doc.add_paragraph(
        "Identity and SSO: Keycloak is deployed via the Bitnami chart and provides "
        "the platform's identity/SSO capability, currently running with the chart's "
        "default realm and administrator account rather than a custom-bootstrapped "
        "realm/client configuration."
    )
    doc.add_paragraph(
        "IAM: the EKS module is configured with enable_irsa, enabling IAM Roles "
        "for Service Accounts at the cluster level. No specific IRSA role bindings "
        "or IAM policy attachments for individual workloads (MySQL, Keycloak, "
        "monitoring) are defined elsewhere in the repository, so pod-level AWS "
        "permissions for those services are not yet wired up beyond this "
        "cluster-level capability being available."
    )
    doc.add_paragraph(
        "Network: workloads run in private subnets behind a NAT gateway; no "
        "Kubernetes NetworkPolicy resources are defined in the repository to "
        "restrict pod-to-pod traffic between the MySQL, Keycloak, and monitoring "
        "namespaces/workloads."
    )
    doc.add_paragraph(
        "Secrets management: MySQL and Keycloak credentials are not defined in "
        "any file in this repository. Both are installed via unmodified Bitnami "
        "chart defaults, which auto-generate root/admin credentials and store them "
        "as native Kubernetes Secrets at install time; retrieving them requires an "
        "out-of-band kubectl get secret command. There is no Sealed Secrets, "
        "External Secrets, or Vault integration yet (already flagged as future "
        "work in the repository's own README)."
    )
    doc.add_paragraph(
        "State security: Terraform state is stored in an encrypted S3 bucket with "
        "DynamoDB-based locking, protecting state contents at rest and preventing "
        "concurrent-apply corruption."
    )

    # 10. Non-functional requirements
    doc.add_heading1("10. Non-functional requirements")
    doc.add_table(
        headers=["Attribute", "Target / approach"],
        rows=[
            ["Availability", "AWS-managed EKS control plane; node group spans 3 AZs with min 3 nodes. No pod disruption budgets, readiness/liveness tuning, or multi-region failover defined."],
            ["Backup RPO", "Depends entirely on how often an operator (or an external, not-yet-defined scheduler) runs backup/backup.py — no cron/CronJob is committed to the repository, so there is no guaranteed RPO today."],
            ["Backup RTO", "Manual: restore requires an operator to load the most recent dated .sql dump with a MySQL client; no automated restore tooling exists in the repository."],
            ["Scalability", "EKS managed node group can scale between 3 and 9 t3.medium instances; no Cluster Autoscaler / Karpenter / HPA is deployed to drive that scaling automatically (listed as future work)."],
            ["Observability", "kube-prometheus-stack default scrape targets and dashboards cover node/pod/container/API-server metrics; no custom Grafana dashboards or Alertmanager routing are defined in-repo."],
            ["Multi-environment isolation", "dev/stage/prod tfvars directories exist as scaffolding but are not yet wired into terraform/main.tf, so only one environment can actually be provisioned as written."],
            ["Security posture", "IRSA enabled at cluster level, encrypted Terraform state; secrets rely on Bitnami chart defaults rather than a dedicated secrets manager."],
        ],
    )

    # 11. Assumptions & constraints
    doc.add_heading1("11. Assumptions & constraints")
    doc.add_bullets([
        "The S3 bucket (enterprise-devops-tf-state) and DynamoDB table "
        "(terraform-locks) referenced by terraform/backend.tf are assumed to "
        "already exist; this repository does not provision its own remote-state "
        "bootstrap resources.",
        "terraform/main.tf currently hardcodes the VPC CIDR, cluster name, and "
        "node group sizing; the terraform/environments/{dev,stage,prod} tfvars "
        "files are not yet consumed by a variables.tf/-var-file mechanism, so "
        "multi-environment provisioning is scaffolding for future work rather "
        "than active behavior today.",
        "terraform/main.tf uses capitalized True for the enable_nat_gateway and "
        "enable_irsa arguments; valid HCL requires lowercase true, so this file "
        "as currently written would need that correction before it would pass "
        "terraform validate/plan.",
        "No provider \"aws\" / required_providers block exists under terraform/; "
        "AWS credentials and default provider configuration must be supplied by "
        "the operator's environment for terraform init/apply to succeed.",
        "helm/deploy.sh installs all three releases with unmodified chart "
        "defaults — there is no values.yaml override in the repository for "
        "MySQL, Keycloak, or the monitoring stack, and no separate \"web "
        "application\" Helm release exists despite being mentioned as a deployed "
        "component in the README.",
        "Neither backup/backup.py nor monitoring/cluster_monitor.py is wired to "
        "a scheduler (no Kubernetes CronJob, no cron entry, no CI schedule) "
        "inside this repository; both are run manually per the README's "
        "documented commands.",
        "The CI/CD workflow validates Terraform syntax and re-applies Helm "
        "releases on every push to main, but does not run terraform plan/apply "
        "— actual infrastructure changes remain a manual operator step.",
    ])

    # 12. Future enhancements
    doc.add_heading1("12. Future enhancements")
    doc.add_paragraph("Directly carried over from the repository's own README:")
    doc.add_bullets([
        "ArgoCD GitOps deployment",
        "Secrets encryption via Sealed Secrets",
        "ExternalDNS automation",
        "AWS Load Balancer Controller integration",
        "Cluster Autoscaler enablement",
        "Multi-region DR architecture",
    ])
    doc.add_paragraph("Additional opportunities identified while preparing this document:")
    doc.add_bullets([
        "Wire terraform/environments/*/variables.tfvars into terraform/main.tf "
        "via declared input variables and a -var-file flag per environment.",
        "Correct the True/False casing in terraform/main.tf and add an explicit "
        "provider \"aws\" / required_providers block.",
        "Add a Kubernetes CronJob (or CI schedule) to actually run backup.py and "
        "cluster_monitor.py on a recurring basis, and invoke the existing "
        "checksum() helper as part of the backup flow with S3 upload and "
        "retention/rotation of old dumps.",
        "Add a terraform plan/apply stage to the CI/CD pipeline (behind a manual "
        "approval gate for prod) so infrastructure changes flow through the same "
        "pipeline as Helm changes.",
        "Author custom Helm values files (and a Keycloak realm export) instead "
        "of relying on chart defaults, and integrate a secrets manager for "
        "MySQL/Keycloak credentials.",
    ])

    # 13. Appendix
    doc.add_heading1("13. Appendix")
    doc.add_heading2("13.1 References")
    doc.add_bullets([
        "Darviq Enterprise repository README.md",
        "terraform/main.tf, terraform/backend.tf",
        "terraform/environments/{dev,stage,prod}/variables.tfvars",
        "helm/deploy.sh",
        ".github/workflows/platform.yml",
        "backup/backup.py",
        "monitoring/cluster_monitor.py",
        "Companion document: Darviq_Enterprise_Low_Level_Design.docx",
    ])
    doc.add_heading2("13.2 Change history")
    doc.add_table(
        headers=["Version", "Date", "Description"],
        rows=[["1.0", DATE, "Initial high-level design document"]],
    )

    doc.save(f"{REPO_ROOT}/Docs/Darviq_Enterprise_High_Level_Design.docx")


# =====================================================================
# LLD
# =====================================================================

def build_lld():
    doc = DesignDoc(
        project_name="Darviq Enterprise",
        subtitle="Enterprise DevOps Platform on AWS EKS",
        doc_kind="Low-Level Design (LLD)",
        version=VERSION,
        date=DATE,
    )
    doc.add_document_control()
    doc.add_toc_field()

    # 1. Introduction
    doc.add_heading1("1. Introduction")
    doc.add_heading2("1.1 Purpose")
    doc.add_paragraph(
        "This Low-Level Design (LLD) expands the companion Darviq_Enterprise_"
        "High_Level_Design.docx into concrete, file-level detail: the actual "
        "Terraform resource composition, Helm release commands, backup script "
        "logic, monitoring script logic, and CI/CD job steps as they exist in the "
        "repository today, including specific values, exact file paths, and known "
        "gaps or defects worth being explicit about."
    )
    doc.add_heading2("1.2 Scope")
    doc.add_paragraph(
        "Covers every file in the repository that carries design-relevant logic: "
        "terraform/main.tf, terraform/backend.tf, the three "
        "terraform/environments/*/variables.tfvars files, helm/deploy.sh, "
        ".github/workflows/platform.yml, backup/backup.py, and "
        "monitoring/cluster_monitor.py."
    )
    doc.add_heading2("1.3 References")
    doc.add_bullets([
        "Darviq_Enterprise_High_Level_Design.docx (companion HLD, version 1.0)",
        "terraform/main.tf, terraform/backend.tf",
        "terraform/environments/dev/variables.tfvars",
        "terraform/environments/stage/variables.tfvars",
        "terraform/environments/prod/variables.tfvars",
        "helm/deploy.sh",
        ".github/workflows/platform.yml",
        "backup/backup.py",
        "monitoring/cluster_monitor.py",
        "README.md",
    ])

    # 2. Detailed module design
    doc.add_heading1("2. Detailed module design")

    doc.add_heading2("2.1 VPC & EKS provisioning — terraform/main.tf, terraform/backend.tf")
    doc.add_paragraph(
        "module \"vpc\" (source terraform-aws-modules/vpc/aws, version 5.0.0): "
        "name = \"enterprise-platform-vpc\", cidr = \"10.10.0.0/16\", "
        "azs = [ap-south-1a, ap-south-1b, ap-south-1c], private_subnets = "
        "[10.10.1.0/24, 10.10.2.0/24, 10.10.3.0/24], public_subnets = "
        "[10.10.4.0/24, 10.10.5.0/24, 10.10.6.0/24], enable_nat_gateway = True "
        "(as authored — note this uses the capitalized Python-style boolean; "
        "valid HCL requires lowercase true)."
    )
    doc.add_paragraph(
        "module \"eks\" (source terraform-aws-modules/eks/aws, version 19.0.0): "
        "cluster_name = \"enterprise-platform-cluster\", cluster_version = \"1.29\", "
        "vpc_id and subnet_ids taken from module.vpc's private subnets, "
        "enable_irsa = True (same casing note as above). eks_managed_node_groups "
        "declares a single group \"default\" with desired_capacity = 6, "
        "min_capacity = 3, max_capacity = 9, instance_types = [\"t3.medium\"]."
    )
    doc.add_paragraph(
        "terraform/backend.tf configures the S3 backend: bucket = "
        "\"enterprise-devops-tf-state\", key = \"platform/eks/terraform.tfstate\", "
        "region = \"ap-south-1\", encrypt = true, dynamodb_table = "
        "\"terraform-locks\". These resources are assumed pre-existing; this "
        "repository contains no bootstrap Terraform for the state bucket/table "
        "themselves."
    )
    doc.add_paragraph(
        "No provider \"aws\" block, no required_providers/versions.tf, no root "
        "variables.tf, and no outputs.tf exist under terraform/ — the module is "
        "self-contained with two files (main.tf, backend.tf) and relies on the "
        "operator's ambient AWS credentials/region configuration."
    )

    doc.add_heading2("2.2 Multi-environment tfvars — terraform/environments/{dev,stage,prod}")
    doc.add_table(
        headers=["Environment", "cluster_name", "node_count"],
        rows=[
            ["dev (terraform/environments/dev/variables.tfvars)", "enterprise-dev-cluster", "7"],
            ["stage (terraform/environments/stage/variables.tfvars)", "enterprise-stage-cluster", "3"],
            ["prod (terraform/environments/prod/variables.tfvars)", "enterprise-dev-cluster (as authored)", "12"],
        ],
    )
    doc.add_paragraph(
        "Each file declares only two flat key/value pairs. Note that the prod "
        "file's cluster_name literally reads \"enterprise-dev-cluster\" rather "
        "than an environment-specific name — reproduced here exactly as it "
        "appears in the repository rather than silently corrected, since this "
        "document is meant to describe the platform as-built. None of these "
        "files is referenced by a -var-file flag or a variables.tf declaration "
        "anywhere in terraform/main.tf, helm/deploy.sh, or "
        ".github/workflows/platform.yml, so as written they do not currently "
        "influence what terraform apply provisions."
    )

    doc.add_heading2("2.3 MySQL Helm deployment — helm/deploy.sh")
    doc.add_code_block(
        "helm repo add bitnami https://charts.bitnami.com/bitnami\n"
        "helm upgrade --install mysql bitnami/mysql"
    )
    doc.add_paragraph(
        "Installed with no values.yaml override, so all configuration (root "
        "password generation, persistence size/class, resource requests) comes "
        "from the bitnami/mysql chart's own defaults."
    )

    doc.add_heading2("2.4 Keycloak identity deployment — helm/deploy.sh")
    doc.add_code_block("helm upgrade --install keycloak bitnami/keycloak")
    doc.add_paragraph(
        "Also installed with chart defaults only. No realm export JSON, no "
        "client/role definitions, and no admin-credential override exist "
        "anywhere in the repository — the deployment produces the chart's "
        "default single \"master\" realm and an auto-generated admin password "
        "stored in a Kubernetes Secret."
    )

    doc.add_heading2("2.5 Prometheus / Grafana monitoring — helm/deploy.sh")
    doc.add_code_block(
        "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts\n"
        "helm repo add grafana https://grafana.github.io/helm-charts\n"
        "helm upgrade --install monitoring prometheus-community/kube-prometheus-stack"
    )
    doc.add_paragraph(
        "Only the kube-prometheus-stack chart is actually installed as the "
        "\"monitoring\" release; it bundles the Prometheus Operator, Prometheus, "
        "Alertmanager, and Grafana. The grafana Helm repo is added by the script "
        "but no grafana/grafana chart is ever installed from it — that repo add "
        "line is currently unused."
    )

    doc.add_heading2("2.6 CI/CD pipeline — .github/workflows/platform.yml")
    doc.add_paragraph(
        "Workflow \"Enterprise Platform Pipeline\", trigger: push to the main "
        "branch. Single job \"deploy\" on ubuntu-latest with these steps, in order:"
    )
    doc.add_bullets([
        "actions/checkout@v3",
        "azure/setup-kubectl@v3",
        "azure/setup-helm@v3",
        "Configure kubeconfig: writes ${{ secrets.KUBECONFIG }} to ~/.kube/config",
        "Validate Terraform: runs terraform validate",
        "Helm Deploy Platform: runs bash helm/deploy.sh",
    ])
    doc.add_paragraph(
        "The terraform validate step runs without a preceding cd terraform or "
        "terraform init step, so it executes from the repository root rather "
        "than the terraform/ directory that actually contains the .tf files — "
        "as written, this step does not validate terraform/main.tf against an "
        "initialized working directory. There is no terraform plan or "
        "terraform apply step in this workflow at all: it only validates syntax "
        "and re-applies the Helm release set, so actual infrastructure "
        "provisioning stays a manual operator action per the README."
    )

    doc.add_heading2("2.7 Automated DB backups — backup/backup.py")
    doc.add_code_block(
        "date = datetime.datetime.now().strftime(\"%Y%m%d\")\n"
        "databases = [\"users\",\"orders\",\"payments\"]\n\n"
        "for db in databases:\n"
        "    subprocess.run([\"mysqldump\",\"-u\",\"root\",db,\"-r\",f\"/backup/{db}_{date}.sql\"])\n\n"
        "def checksum(file):\n"
        "    h = hashlib.md5()\n"
        "    with open(file,'rb') as f:\n"
        "        h.update(f.read())\n"
        "    return h.hexdigest()"
    )
    doc.add_paragraph(
        "The script hardcodes three database names and shells out to mysqldump "
        "as the root MySQL user for each, writing to /backup/<db>_<YYYYMMDD>.sql. "
        "date has day-level granularity only, so re-running the script more than "
        "once on the same calendar day overwrites that day's dump rather than "
        "versioning it. The checksum() function is defined but never called by "
        "the script's top-level flow — it computes an MD5 digest of a given file "
        "but nothing in backup.py currently invokes it, logs its output, or "
        "persists it as a manifest. There is no S3 upload call and no retention/"
        "cleanup of old dump files; subprocess.run() calls do not pass "
        "check=True, so a failed mysqldump does not raise or otherwise surface "
        "as a script-level error."
    )

    doc.add_heading2("2.8 Cluster health monitoring — monitoring/cluster_monitor.py")
    doc.add_code_block(
        "from kubernetes import client, config\n"
        "config.load_kube_config()\n"
        "v1 = client.CoreV1Api()\n\n"
        "for pod in v1.list_pod_for_all_namespaces().items:\n"
        "    if pod.status.phase != \"Running\":\n"
        "        print(\"ALERT:\", pod.metadata.name)\n\n"
        "    if pod.status.container_statuses:\n"
        "    for c in pod.status.container_statuses:\n"
        "        if c.restart_count > 3:\n"
        "            print(\"ALERT: Restart loop detected:\", pod.metadata.name)"
    )
    doc.add_paragraph(
        "Authenticates via config.load_kube_config() — i.e. the operator's local "
        "kubeconfig context, not an in-cluster service account — then lists every "
        "pod across all namespaces with v1.list_pod_for_all_namespaces() and "
        "prints an ALERT line for any pod whose status.phase is not \"Running\". "
        "As reproduced above (verbatim from the source file), the nested "
        "for c in pod.status.container_statuses: loop sits at the same "
        "indentation level as its guarding if pod.status.container_statuses: "
        "line instead of nested one level inside it — this is invalid Python "
        "indentation and would raise an IndentationError the moment the script "
        "is executed, so the restart-loop detection branch cannot currently run "
        "at all. The README's claim of \"PVC visibility\" is not implemented "
        "anywhere in this file — there is no code that lists or inspects "
        "PersistentVolumeClaims. The script performs one pass over the pod list "
        "and exits; there is no loop, no polling interval, and no alerting "
        "integration (e.g. Slack, webhook, or Alertmanager) wired to its output."
    )

    # 3. Database schema design
    doc.add_heading1("3. Database schema design (data store configuration)")
    doc.add_paragraph(
        "This repository defines no SQL DDL, ORM models, or migration scripts. "
        "MySQL is deployed purely as a generic Bitnami-chart-managed instance "
        "with no values.yaml override (Section 2.3). The only evidence of an "
        "intended data model is the hardcoded list of three database names in "
        "backup/backup.py, presumed to belong to an external, out-of-scope "
        "application:"
    )
    doc.add_table(
        headers=["Database (as named in backup.py)", "Inferred purpose", "Defined in this repo?"],
        rows=[
            ["users", "Presumably application user/account records", "No — name only, referenced solely by backup/backup.py"],
            ["orders", "Presumably order records for a companion application", "No — name only"],
            ["payments", "Presumably payment/transaction records", "No — name only"],
        ],
    )
    doc.add_paragraph(
        "Because there is no DDL in the repository, any schema, table, or seed "
        "data for these three databases must be created by whatever external "
        "application or manual process actually uses this MySQL instance."
    )

    # 4. API specification / Helm values & Terraform variable reference
    doc.add_heading1("4. Helm values & Terraform variable reference")
    doc.add_paragraph(
        "This repository exposes no custom REST/HTTP API of its own. In place "
        "of an API specification, this section catalogs the configurable "
        "parameters that actually exist across the Terraform and Helm layers, "
        "and whether each is presently active."
    )
    doc.add_table(
        headers=["Parameter", "Source", "Value", "Currently active?"],
        rows=[
            ["cluster_name", "terraform/main.tf (module.eks, hardcoded)", "enterprise-platform-cluster", "Yes — this is what terraform apply provisions"],
            ["cluster_version", "terraform/main.tf (module.eks, hardcoded)", "1.29", "Yes"],
            ["node group sizing", "terraform/main.tf (module.eks, hardcoded)", "min 3 / desired 6 / max 9, t3.medium", "Yes"],
            ["vpc cidr", "terraform/main.tf (module.vpc, hardcoded)", "10.10.0.0/16", "Yes"],
            ["cluster_name (dev)", "terraform/environments/dev/variables.tfvars", "enterprise-dev-cluster", "No — not referenced by main.tf"],
            ["node_count (dev)", "terraform/environments/dev/variables.tfvars", "7", "No — not referenced by main.tf"],
            ["cluster_name (stage)", "terraform/environments/stage/variables.tfvars", "enterprise-stage-cluster", "No — not referenced by main.tf"],
            ["node_count (stage)", "terraform/environments/stage/variables.tfvars", "3", "No — not referenced by main.tf"],
            ["cluster_name (prod)", "terraform/environments/prod/variables.tfvars", "enterprise-dev-cluster (as authored)", "No — not referenced by main.tf"],
            ["node_count (prod)", "terraform/environments/prod/variables.tfvars", "12", "No — not referenced by main.tf"],
            ["S3 state bucket / key / DynamoDB table", "terraform/backend.tf", "enterprise-devops-tf-state / platform/eks/terraform.tfstate / terraform-locks", "Yes — assumed pre-provisioned"],
            ["Helm release values (mysql, keycloak, monitoring)", "helm/deploy.sh", "chart defaults (no values.yaml in repo)", "Yes — this is what is actually installed"],
            ["KUBECONFIG", "GitHub Actions secret, consumed in .github/workflows/platform.yml", "operator-supplied", "Yes"],
        ],
    )

    # 5. Sequence flows / process flows
    doc.add_heading1("5. Sequence flows / process flows")

    doc.add_heading2("5.1 CI/CD push-to-deploy flow")
    doc.add_table(
        headers=["Step", "Actor / Component", "Action"],
        rows=[
            ["1", "Developer", "git push to the main branch"],
            ["2", "GitHub Actions", "platform.yml workflow triggers on the push event"],
            ["3", "GitHub Actions runner", "Checks out the repo; installs kubectl and Helm via azure/setup-kubectl and azure/setup-helm"],
            ["4", "GitHub Actions runner", "Writes the KUBECONFIG secret's contents to ~/.kube/config"],
            ["5", "GitHub Actions runner", "Runs terraform validate (repo-root scope — see Section 2.6)"],
            ["6", "GitHub Actions runner", "Runs bash helm/deploy.sh against the cluster addressed by the injected kubeconfig"],
            ["7", "Helm", "Installs/upgrades the mysql, keycloak, and monitoring releases with chart defaults"],
        ],
    )

    doc.add_heading2("5.2 Manual infrastructure provisioning flow")
    doc.add_table(
        headers=["Step", "Actor", "Action"],
        rows=[
            ["1", "Operator", "cd terraform && terraform init — reads backend.tf, connects to the S3 bucket and DynamoDB lock table"],
            ["2", "Operator", "terraform apply — provisions module.vpc, then module.eks (managed node group)"],
            ["3", "Operator", "aws eks update-kubeconfig --region ap-south-1 --name enterprise-platform-cluster"],
            ["4", "Operator", "kubectl get nodes to confirm cluster/node readiness"],
            ["5", "Operator", "bash helm/deploy.sh to install MySQL, Keycloak, and the monitoring stack"],
        ],
    )

    doc.add_heading2("5.3 Backup execution flow")
    doc.add_table(
        headers=["Step", "Actor / Component", "Action"],
        rows=[
            ["1", "Operator (manual — no in-repo scheduler)", "Runs python backup/backup.py"],
            ["2", "backup.py", "Computes date as today's date in YYYYMMDD form"],
            ["3", "backup.py", "For each of users, orders, payments: runs mysqldump -u root <db> -r /backup/<db>_<date>.sql via subprocess.run"],
            ["4", "backup.py", "checksum() is defined but not invoked — no validation, upload, or cleanup occurs after the dumps are written"],
        ],
    )

    doc.add_heading2("5.4 Cluster health check flow")
    doc.add_table(
        headers=["Step", "Actor / Component", "Action"],
        rows=[
            ["1", "Operator", "Runs python monitoring/cluster_monitor.py (loads local kubeconfig)"],
            ["2", "cluster_monitor.py", "Lists all pods across all namespaces via CoreV1Api.list_pod_for_all_namespaces()"],
            ["3", "cluster_monitor.py", "Prints ALERT: <pod name> for any pod whose phase is not Running"],
            ["4", "cluster_monitor.py", "Intends to print a restart-loop ALERT for containers with restart_count > 3 — currently blocked by the indentation defect described in Section 2.8"],
        ],
    )

    # 6. Key algorithms & business logic
    doc.add_heading1("6. Key algorithms & business logic")
    doc.add_heading2("6.1 Backup file naming and the (unused) checksum helper")
    doc.add_paragraph(
        "Dump files are named <db>_<YYYYMMDD>.sql — day-level granularity means a "
        "second run on the same day silently overwrites the first. The "
        "checksum(file) helper computes an MD5 digest of a given file's bytes "
        "and returns the hex digest; its intended purpose (verifying dump "
        "integrity, e.g. for detecting truncated or corrupted dumps before "
        "upload) is not realized today because nothing in the script calls it."
    )
    doc.add_heading2("6.2 Restart-loop detection threshold")
    doc.add_paragraph(
        "cluster_monitor.py hardcodes a restart_count > 3 threshold for flagging "
        "a container as being in a restart loop, with no configurability (no "
        "environment variable, CLI flag, or config file). As noted in Section "
        "2.8, this branch is currently unreachable due to an indentation defect."
    )
    doc.add_heading2("6.3 Node group scaling range")
    doc.add_paragraph(
        "The EKS managed node group is declared with min_capacity = 3, "
        "desired_capacity = 6, max_capacity = 9. This is a static, Terraform-"
        "declared range rather than workload-driven autoscaling: no Cluster "
        "Autoscaler, Karpenter, or HPA manifests are present in the repository, "
        "so scaling within that band would need to be triggered by an operator "
        "re-running Terraform with a different desired_capacity, or by the "
        "managed node group's own baseline behavior, rather than automatically "
        "in response to pending pods."
    )

    # 7. Validation & error handling
    doc.add_heading1("7. Validation & error handling")
    doc.add_bullets([
        "backup/backup.py: subprocess.run() calls omit check=True, so a failed "
        "mysqldump (bad credentials, disk full, database not found) does not "
        "raise an exception or otherwise fail the script — it fails silently "
        "from the script's perspective. There is no logging module usage, only "
        "whatever output the mysqldump subprocess itself produces.",
        "monitoring/cluster_monitor.py: no try/except around the Kubernetes API "
        "calls, and — more fundamentally — the indentation defect noted in "
        "Section 2.8 means the script cannot reach its restart-loop check at "
        "all as currently written; running it as-is would raise a Python "
        "IndentationError on module load.",
        "CI/CD pipeline: no failure notification step (no Slack/email/other "
        "integration) — a failed terraform validate or helm upgrade --install "
        "step simply fails the GitHub Actions job, visible only in the Actions "
        "tab of the repository.",
        "Terraform: no terraform plan step gates terraform apply in any "
        "automated way (apply is manual per the README), and there is no drift "
        "detection. The True/False casing issue in terraform/main.tf (Section "
        "2.1) would surface as an HCL parse error the first time terraform "
        "validate or terraform plan is actually run against that file.",
    ])

    # 8. Non-functional implementation details
    doc.add_heading1("8. Non-functional implementation details")
    doc.add_heading2("8.1 Security implementation specifics")
    doc.add_paragraph(
        "enable_irsa is turned on at the EKS module level, which enables the "
        "IRSA mechanism cluster-wide, but no IAM policy attachments or "
        "service-account annotations are defined anywhere in the repository for "
        "the actual workloads (MySQL, Keycloak, monitoring) — so none of them "
        "currently receive scoped AWS permissions via IRSA; the capability is "
        "enabled but unused. Terraform state is encrypted at rest in S3 with "
        "DynamoDB locking. MySQL and Keycloak credentials are entirely "
        "delegated to Bitnami chart defaults (auto-generated, stored as native "
        "Kubernetes Secrets) rather than managed by any tooling in this "
        "repository."
    )
    doc.add_heading2("8.2 Performance / scaling considerations")
    doc.add_paragraph(
        "The only scaling lever presently configured is the static node group "
        "range (3-9 t3.medium instances across 3 AZs). No resource "
        "requests/limits are set via custom Helm values for MySQL, Keycloak, or "
        "the monitoring stack (chart defaults apply), and no HPA, Cluster "
        "Autoscaler, or Karpenter automation exists to react to actual load."
    )

    # 9. Appendix
    doc.add_heading1("9. Appendix")
    doc.add_heading2("9.1 Repository module / file map")
    doc.add_code_block(
        "Darviq-Enterprise/\n"
        "├── .github/\n"
        "│   └── workflows/\n"
        "│       └── platform.yml        # CI/CD: terraform validate + helm/deploy.sh on push to main\n"
        "├── backup/\n"
        "│   └── backup.py                # mysqldump for users/orders/payments; checksum() defined, unused\n"
        "├── helm/\n"
        "│   └── deploy.sh                # helm upgrade --install for mysql, keycloak, monitoring\n"
        "├── monitoring/\n"
        "│   └── cluster_monitor.py       # pod health / restart-loop scan via kubernetes client\n"
        "├── terraform/\n"
        "│   ├── backend.tf               # S3 + DynamoDB remote state config\n"
        "│   ├── main.tf                  # module.vpc + module.eks\n"
        "│   └── environments/\n"
        "│       ├── dev/variables.tfvars\n"
        "│       ├── stage/variables.tfvars\n"
        "│       └── prod/variables.tfvars\n"
        "├── Docs/\n"
        "│   ├── Darviq_Enterprise_High_Level_Design.docx\n"
        "│   ├── Darviq_Enterprise_Low_Level_Design.docx\n"
        "│   ├── docx_builder.py          # shared doc-generation helper (kept for regeneration)\n"
        "│   └── generate_docs.py         # this pair's generation script (kept for regeneration)\n"
        "└── README.md"
    )

    doc.add_heading2("9.2 Configuration reference")
    doc.add_table(
        headers=["Name", "Type", "Where used", "Notes"],
        rows=[
            ["KUBECONFIG", "GitHub Actions secret", ".github/workflows/platform.yml", "Written to ~/.kube/config for kubectl/Helm auth"],
            ["AWS region", "hardcoded string", "terraform/main.tf, terraform/backend.tf", "ap-south-1 throughout"],
            ["cluster_name / node_count", "tfvars pair", "terraform/environments/{dev,stage,prod}", "Not currently consumed by terraform/main.tf"],
            ["S3 bucket / DynamoDB table", "backend config", "terraform/backend.tf", "Assumed pre-provisioned outside this repo"],
        ],
    )

    doc.add_heading2("9.3 Change history")
    doc.add_table(
        headers=["Version", "Date", "Description"],
        rows=[["1.0", DATE, "Initial low-level design document"]],
    )

    doc.save(f"{REPO_ROOT}/Docs/Darviq_Enterprise_Low_Level_Design.docx")


if __name__ == "__main__":
    build_hld()
    build_lld()
    print("Generated HLD and LLD.")
