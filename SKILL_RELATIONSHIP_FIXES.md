# Skill Relationship Fixes Summary

**Generated:** 2026-04-25 08:06:52

## 📊 Statistics

| Metric | Count |
|--------|-------|
| Total Skills Updated | 28 |
| Dead References Removed | 34 |
| Reciprocal Relationships Added | 31 |
| Semantic Suggestions Added | 0 |
| Validation Errors | 1 |

---

## 📝 Updated Skills

### cncf-azure-aks

**Before:** cncf-azure-container-registry, cncf-azure-monitor, cncf-azure-rbac, cncf-azure-virtual-networks

**After:** cncf-azure-container-registry, cncf-azure-monitor, cncf-azure-resource-manager, cncf-azure-traffic-manager

**Added:** cncf-azure-resource-manager, cncf-azure-traffic-manager

**Removed:** cncf-azure-rbac, cncf-azure-virtual-networks


### cncf-azure-automation

**Before:** cncf-azure-key-vault, cncf-azure-monitor, cncf-azure-rbac, cncf-azure-virtual-machines

**After:** cncf-azure-monitor

**Removed:** cncf-azure-key-vault, cncf-azure-rbac, cncf-azure-virtual-machines


### cncf-azure-blob-storage

**Before:** cncf-azure-cdn, cncf-azure-key-vault, cncf-azure-monitor, cncf-azure-rbac

**After:** cncf-azure-cdn, cncf-azure-monitor

**Removed:** cncf-azure-key-vault, cncf-azure-rbac


### cncf-azure-cdn

**Before:** cncf-azure-blob-storage, cncf-azure-monitor, cncf-azure-virtual-machines, cncf-cni

**After:** cncf-azure-blob-storage, cncf-azure-monitor

**Removed:** cncf-azure-virtual-machines, cncf-cni


### cncf-azure-container-registry

**Before:** cncf-azure-aks, cncf-azure-functions, cncf-azure-monitor, cncf-azure-rbac

**After:** cncf-azure-aks, cncf-azure-functions, cncf-azure-monitor

**Removed:** cncf-azure-rbac


### cncf-azure-cosmos-db

**Before:** cncf-azure-functions, cncf-azure-key-vault, cncf-azure-monitor, cncf-azure-rbac

**After:** cncf-azure-functions, cncf-azure-monitor

**Removed:** cncf-azure-key-vault, cncf-azure-rbac


### cncf-azure-functions

**Before:** cncf-azure-cosmos-db, cncf-azure-monitor, cncf-azure-rbac, cncf-azure-service-bus

**After:** cncf-azure-container-registry, cncf-azure-cosmos-db, cncf-azure-event-hubs, cncf-azure-keyvault-secrets

**Added:** cncf-azure-container-registry, cncf-azure-event-hubs, cncf-azure-keyvault-secrets

**Removed:** cncf-azure-monitor, cncf-azure-rbac, cncf-azure-service-bus


### cncf-azure-keyvault-secrets

**Before:** cncf-azure-functions, cncf-azure-key-vault, cncf-azure-rbac, cncf-azure-virtual-machines

**After:** cncf-azure-functions

**Removed:** cncf-azure-key-vault, cncf-azure-rbac, cncf-azure-virtual-machines


### cncf-azure-load-balancer

**Before:** cncf-azure-monitor, cncf-azure-scale-sets, cncf-azure-virtual-machines, cncf-azure-virtual-networks

**After:** cncf-azure-monitor, cncf-azure-scale-sets, cncf-azure-traffic-manager, cncf-azure-virtual-networks

**Added:** cncf-azure-traffic-manager

**Removed:** cncf-azure-virtual-machines


### cncf-azure-monitor

**Before:** cncf-azure-aks, cncf-azure-automation, cncf-azure-blob-storage

**After:** cncf-azure-aks, cncf-azure-automation, cncf-azure-blob-storage, cncf-azure-cdn

**Added:** cncf-azure-cdn


### cncf-azure-resource-manager

**Before:** cncf-azure-aks, cncf-azure-sql-database, cncf-azure-virtual-machines, cncf-azure-virtual-networks

**After:** cncf-azure-aks, cncf-azure-sql-database, cncf-azure-virtual-networks

**Removed:** cncf-azure-virtual-machines


### cncf-azure-scale-sets

**Before:** cncf-azure-load-balancer, cncf-azure-monitor, cncf-azure-virtual-machines, cncf-azure-virtual-networks

**After:** cncf-azure-load-balancer, cncf-azure-monitor, cncf-azure-virtual-networks

**Removed:** cncf-azure-virtual-machines


### cncf-azure-service-bus

**Before:** cncf-azure-event-hubs, cncf-azure-functions, cncf-azure-monitor, cncf-azure-rbac

**After:** cncf-azure-event-hubs, cncf-azure-functions, cncf-azure-monitor

**Removed:** cncf-azure-rbac


### cncf-azure-sql-database

**Before:** cncf-azure-key-vault, cncf-azure-monitor, cncf-azure-rbac, cncf-azure-virtual-networks

**After:** cncf-azure-monitor, cncf-azure-resource-manager, cncf-azure-virtual-networks

**Added:** cncf-azure-resource-manager

**Removed:** cncf-azure-key-vault, cncf-azure-rbac


### cncf-azure-traffic-manager

**Before:** cncf-azure-aks, cncf-azure-load-balancer, cncf-azure-monitor, cncf-azure-virtual-machines

**After:** cncf-azure-aks, cncf-azure-load-balancer, cncf-azure-monitor

**Removed:** cncf-azure-virtual-machines


### cncf-azure-virtual-networks

**Before:** cncf-azure-aks, cncf-azure-monitor, cncf-azure-sql-database, cncf-azure-virtual-machines

**After:** cncf-azure-aks, cncf-azure-load-balancer, cncf-azure-monitor, cncf-azure-resource-manager

**Added:** cncf-azure-load-balancer, cncf-azure-resource-manager

**Removed:** cncf-azure-sql-database, cncf-azure-virtual-machines


### cncf-gcp-cloud-functions

**Before:** cncf-gcp-cloud-monitoring, cncf-gcp-cloud-pubsub, cncf-gcp-cloud-tasks, cncf-gcp-iam

**After:** cncf-gcp-cloud-monitoring

**Removed:** cncf-gcp-cloud-pubsub, cncf-gcp-cloud-tasks, cncf-gcp-iam


### cncf-gcp-cloud-kms

**Before:** cncf-gcp-cloud-sql, cncf-gcp-cloud-storage, cncf-gcp-iam, cncf-gcp-secret-manager

**After:** cncf-gcp-cloud-sql, cncf-gcp-cloud-storage, cncf-gcp-secret-manager

**Removed:** cncf-gcp-iam


### cncf-gcp-cloud-load-balancing

**Before:** cncf-gcp-cloud-monitoring, cncf-gcp-compute-engine, cncf-gcp-gke, cncf-gcp-vpc

**After:** cncf-gcp-autoscaling, cncf-gcp-cloud-cdn, cncf-gcp-cloud-dns, cncf-gcp-cloud-monitoring

**Added:** cncf-gcp-autoscaling, cncf-gcp-cloud-cdn, cncf-gcp-cloud-dns

**Removed:** cncf-gcp-compute-engine, cncf-gcp-gke, cncf-gcp-vpc


### cncf-gcp-cloud-monitoring

**Before:** cncf-gcp-cloud-functions, cncf-gcp-cloud-sql, cncf-gcp-compute-engine, cncf-gcp-gke

**After:** cncf-gcp-autoscaling, cncf-gcp-cloud-cdn, cncf-gcp-cloud-dns, cncf-gcp-cloud-functions

**Added:** cncf-gcp-autoscaling, cncf-gcp-cloud-cdn, cncf-gcp-cloud-dns

**Removed:** cncf-gcp-cloud-sql, cncf-gcp-compute-engine, cncf-gcp-gke


### cncf-gcp-cloud-sql

**Before:** cncf-gcp-cloud-kms, cncf-gcp-cloud-monitoring, cncf-gcp-iam, cncf-gcp-vpc

**After:** cncf-gcp-cloud-kms, cncf-gcp-cloud-monitoring, cncf-gcp-vpc

**Removed:** cncf-gcp-iam


### cncf-gcp-cloud-storage

**Before:** cncf-gcp-cloud-cdn, cncf-gcp-cloud-kms, cncf-gcp-cloud-monitoring, cncf-gcp-iam

**After:** cncf-gcp-cloud-cdn, cncf-gcp-cloud-kms, cncf-gcp-cloud-monitoring

**Removed:** cncf-gcp-iam


### cncf-gcp-compute-engine

**Before:** cncf-gcp-autoscaling, cncf-gcp-cloud-monitoring, cncf-gcp-iam, cncf-gcp-vpc

**After:** cncf-gcp-autoscaling, cncf-gcp-cloud-cdn, cncf-gcp-cloud-dns, cncf-gcp-cloud-monitoring

**Added:** cncf-gcp-cloud-cdn, cncf-gcp-cloud-dns

**Removed:** cncf-gcp-iam, cncf-gcp-vpc


### cncf-gcp-container-registry

**Before:** cncf-gcp-cloud-functions, cncf-gcp-cloud-monitoring, cncf-gcp-gke, cncf-gcp-iam

**After:** cncf-gcp-cloud-functions, cncf-gcp-cloud-monitoring, cncf-gcp-gke

**Removed:** cncf-gcp-iam


### cncf-gcp-firestore

**Before:** cncf-gcp-cloud-functions, cncf-gcp-cloud-kms, cncf-gcp-cloud-monitoring, cncf-gcp-iam

**After:** cncf-gcp-cloud-functions, cncf-gcp-cloud-kms, cncf-gcp-cloud-monitoring

**Removed:** cncf-gcp-iam


### cncf-gcp-gke

**Before:** cncf-gcp-cloud-monitoring, cncf-gcp-container-registry, cncf-gcp-iam, cncf-gcp-vpc

**After:** cncf-gcp-autoscaling, cncf-gcp-cloud-monitoring, cncf-gcp-container-registry, cncf-gcp-vpc

**Added:** cncf-gcp-autoscaling

**Removed:** cncf-gcp-iam


### cncf-gcp-secret-manager

**Before:** cncf-gcp-cloud-functions, cncf-gcp-cloud-kms, cncf-gcp-compute-engine, cncf-gcp-iam

**After:** cncf-gcp-cloud-functions, cncf-gcp-cloud-kms, cncf-gcp-compute-engine

**Removed:** cncf-gcp-iam


### cncf-gcp-vpc

**Before:** cncf-gcp-cloud-load-balancing, cncf-gcp-cloud-sql, cncf-gcp-compute-engine, cncf-gcp-gke

**After:** cncf-gcp-cloud-dns, cncf-gcp-cloud-load-balancing, cncf-gcp-cloud-sql, cncf-gcp-compute-engine

**Added:** cncf-gcp-cloud-dns

**Removed:** cncf-gcp-gke


