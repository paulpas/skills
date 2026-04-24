# Skill Relationship Fixes Summary

**Generated:** 2026-04-24 17:43:46

## 📊 Statistics

| Metric | Count |
|--------|-------|
| Total Skills Updated | 98 |
| Dead References Removed | 94 |
| Reciprocal Relationships Added | 58 |
| Semantic Suggestions Added | 71 |
| Validation Errors | 1 |

---

## 📝 Updated Skills

### agent-add-new-skill

**Before:** (none)

**After:** agent-autoscaling-advisor, agent-ci-cd-pipeline-analyzer, agent-confidence-based-selector, agent-container-inspector

**Added:** agent-autoscaling-advisor, agent-ci-cd-pipeline-analyzer, agent-confidence-based-selector, agent-container-inspector


### cncf-aws-ec2

**Before:** cncf-aws-auto-scaling, cncf-aws-cloudformation, cncf-aws-cloudwatch, cncf-spire cncf-aws-elb

**After:** cncf-aws-auto-scaling, cncf-aws-cloudformation, cncf-aws-cloudwatch

**Removed:** cncf-spire cncf-aws-elb


### cncf-aws-rds

**Before:** cncf-aws-auto-scaling, cncf-aws-cloudformation, cncf-aws-cloudwatch, cncf-cubefs cncf-aws-iam

**After:** cncf-aws-auto-scaling, cncf-aws-cloudformation, cncf-aws-cloudwatch

**Removed:** cncf-cubefs cncf-aws-iam


### cncf-azure-key-vault

**Before:** cncf-azure-automation, cncf-azure-blob-storage, cncf-azure-functions, cncf-azure-sql-database cncf-azure-rbac

**After:** cncf-azure-automation, cncf-azure-blob-storage, cncf-azure-functions

**Removed:** cncf-azure-sql-database cncf-azure-rbac


### cncf-azure-monitor

**Before:** cncf-azure-aks, cncf-azure-automation, cncf-azure-blob-storage, cncf-fluentd cncf-azure-functions

**After:** cncf-azure-aks, cncf-azure-automation, cncf-azure-blob-storage

**Removed:** cncf-fluentd cncf-azure-functions


### cncf-azure-rbac

**Before:** cncf-azure-aks, cncf-azure-automation, cncf-azure-blob-storage, cncf-gcp-iam cncf-azure-key-vault

**After:** cncf-azure-aks, cncf-azure-automation, cncf-azure-blob-storage, cncf-gcp-iam

**Added:** cncf-gcp-iam

**Removed:** cncf-gcp-iam cncf-azure-key-vault


### cncf-calico

**Before:** cncf-cilium, cncf-container-network-interface-cni, cncf-contour, cncf-kuma cncf-in-toto

**After:** cncf-cilium, cncf-container-network-interface-cni, cncf-contour, cncf-in-toto

**Added:** cncf-in-toto

**Removed:** cncf-kuma cncf-in-toto


### cncf-cilium

**Before:** cncf-calico, cncf-container-network-interface-cni, cncf-contour, cncf-kuma cncf-kong

**After:** cncf-calico, cncf-container-network-interface-cni, cncf-contour, cncf-kong

**Added:** cncf-kong

**Removed:** cncf-kuma cncf-kong


### cncf-gcp-deployment-manager

**Before:** cncf-azure-resource-manager, cncf-gcp-cloud-sql, cncf-gcp-compute-engine cncf-gcp-gke

**After:** cncf-azure-resource-manager, cncf-gcp-cloud-sql

**Removed:** cncf-gcp-compute-engine cncf-gcp-gke


### cncf-kong

**Before:** cncf-calico, cncf-cilium, cncf-kong-ingress-controller

**After:** cncf-calico, cncf-cilium, cncf-kong-ingress-controller, cncf-longhorn

**Added:** cncf-longhorn


### cncf-lima

**Before:** cncf-calico, cncf-cilium, cncf-container-network-interface-cni, cncf-krustlet cncf-krustlet

**After:** cncf-calico, cncf-cilium, cncf-container-network-interface-cni, cncf-longhorn

**Added:** cncf-longhorn

**Removed:** cncf-krustlet cncf-krustlet


### cncf-longhorn

**Before:** cncf-calico, cncf-cilium, cncf-container-network-interface-cni, cncf-open-telemetry cncf-nats

**After:** cncf-calico, cncf-cilium, cncf-container-network-interface-cni, cncf-contour

**Added:** cncf-contour

**Removed:** cncf-open-telemetry cncf-nats


### cncf-nats

**Before:** cncf-calico, cncf-cilium, cncf-cloudevents, cncf-longhorn

**After:** cncf-calico, cncf-cilium, cncf-cloudevents, cncf-container-network-interface-cni

**Added:** cncf-container-network-interface-cni

**Removed:** cncf-longhorn


### cncf-open-telemetry

**Before:** cncf-calico, cncf-cilium, cncf-longhorn, cncf-nats

**After:** cncf-calico, cncf-cilium, cncf-container-network-interface-cni, cncf-contour

**Added:** cncf-container-network-interface-cni, cncf-contour

**Removed:** cncf-longhorn, cncf-nats


### cncf-zot

**Before:** cncf-calico, cncf-cilium, cncf-container-network-interface-cni cncf-lima

**After:** cncf-calico, cncf-cilium, cncf-container-network-interface-cni, cncf-lima

**Added:** cncf-container-network-interface-cni, cncf-lima

**Removed:** cncf-container-network-interface-cni cncf-lima


### trading-ai-anomaly-detection

**Before:** trading-ai-explainable-ai, trading-ai-feature-engineering, trading-ai-time-series-forecasting, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-explainable-ai, trading-ai-feature-engineering, trading-ai-time-series-forecasting

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-explainable-ai

**Before:** trading-ai-anomaly-detection, trading-ai-feature-engineering, trading-ai-time-series-forecasting, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-feature-engineering, trading-ai-time-series-forecasting

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-feature-engineering

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-hyperparameter-tuning

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-live-model-monitoring

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-llm-orchestration

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-model-ensemble

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-multi-asset-model

**Before:** trading-backtest-drawdown-analysis, trading-fundamentals-risk-management-basics, trading-risk-correlation-risk trading-backtest-position-sizing

**After:** trading-backtest-drawdown-analysis, trading-fundamentals-risk-management-basics

**Removed:** trading-risk-correlation-risk trading-backtest-position-sizing


### trading-ai-news-embedding

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-order-flow-analysis

**Before:** trading-data-order-book, trading-data-validation, trading-exchange-health, trading-exchange-order-execution-api, trading-fundamentals-market-structure trading-exchange-order-book-sync

**After:** trading-data-order-book, trading-data-validation, trading-exchange-health, trading-exchange-order-execution-api

**Removed:** trading-fundamentals-market-structure trading-exchange-order-book-sync


### trading-ai-regime-classification

**Before:** trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-technical-indicator-confluence, trading-technical-intermarket-analysis

**After:** trading-technical-cycle-analysis, trading-technical-intermarket-analysis

**Removed:** trading-technical-false-signal-filtering trading-technical-indicator-confluence


### trading-ai-reinforcement-learning

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-sentiment-analysis

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-sentiment-features

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-synthetic-data

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-time-series-forecasting

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-ai-volatility-prediction

**Before:** trading-ai-anomaly-detection, trading-ai-explainable-ai, trading-technical-cycle-analysis trading-technical-false-signal-filtering

**After:** trading-ai-anomaly-detection, trading-ai-explainable-ai

**Removed:** trading-technical-cycle-analysis trading-technical-false-signal-filtering


### trading-backtest-drawdown-analysis

**Before:** trading-backtest-position-sizing, trading-exchange-order-execution-api, trading-fundamentals-risk-management-basics, trading-risk-position-sizing, trading-risk-stop-loss trading-exchange-order-book-sync

**After:** trading-backtest-position-sizing, trading-exchange-order-execution-api, trading-fundamentals-risk-management-basics, trading-risk-position-sizing

**Removed:** trading-risk-stop-loss trading-exchange-order-book-sync


### trading-backtest-lookahead-bias

**Before:** trading-backtest-position-exits, trading-backtest-sharpe-ratio, trading-backtest-walk-forward, trading-fundamentals-trading-plan, trading-paper-performance-attribution trading-fundamentals-trading-edge

**After:** trading-backtest-position-exits, trading-backtest-sharpe-ratio, trading-backtest-walk-forward, trading-fundamentals-trading-plan

**Removed:** trading-paper-performance-attribution trading-fundamentals-trading-edge


### trading-backtest-position-exits

**Before:** trading-backtest-lookahead-bias, trading-backtest-sharpe-ratio, trading-backtest-walk-forward, trading-fundamentals-trading-plan, trading-paper-performance-attribution trading-fundamentals-trading-edge

**After:** trading-backtest-lookahead-bias, trading-backtest-sharpe-ratio, trading-backtest-walk-forward, trading-fundamentals-trading-plan

**Removed:** trading-paper-performance-attribution trading-fundamentals-trading-edge


### trading-backtest-position-sizing

**Before:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api, trading-fundamentals-risk-management-basics, trading-risk-position-sizing, trading-risk-stop-loss trading-exchange-order-book-sync

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api, trading-fundamentals-risk-management-basics, trading-risk-position-sizing

**Removed:** trading-risk-stop-loss trading-exchange-order-book-sync


### trading-backtest-sharpe-ratio

**Before:** trading-backtest-lookahead-bias, trading-backtest-position-exits trading-fundamentals-trading-edge, trading-fundamentals-trading-plan

**After:** trading-backtest-lookahead-bias, trading-fundamentals-trading-plan

**Removed:** trading-backtest-position-exits trading-fundamentals-trading-edge


### trading-backtest-walk-forward

**Before:** trading-backtest-lookahead-bias, trading-backtest-position-exits trading-fundamentals-trading-edge, trading-fundamentals-trading-plan

**After:** trading-backtest-lookahead-bias, trading-fundamentals-trading-plan

**Removed:** trading-backtest-position-exits trading-fundamentals-trading-edge


### trading-data-alternative-data

**Before:** trading-ai-order-flow-analysis, trading-data-backfill-strategy, trading-data-candle-data, trading-data-validation trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-backfill-strategy, trading-data-candle-data

**Removed:** trading-data-validation trading-data-order-book


### trading-data-backfill-strategy

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-candle-data, trading-data-validation trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-candle-data

**Removed:** trading-data-validation trading-data-order-book


### trading-data-candle-data

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-data-enrichment

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-data-feature-store

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-data-lake

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-data-order-book

**Before:** trading-ai-order-flow-analysis, trading-exchange-order-execution-api, trading-fundamentals-market-structure, trading-technical-market-microstructure trading-exchange-order-book-sync

**After:** trading-ai-order-flow-analysis, trading-exchange-order-execution-api, trading-fundamentals-market-structure

**Removed:** trading-technical-market-microstructure trading-exchange-order-book-sync


### trading-data-stream-processing

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-data-time-series-database

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-data-validation

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-exchange-ccxt-patterns

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-exchange-failover-handling

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-exchange-health

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-exchange-market-data-cache

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-exchange-order-book-sync

**Before:** trading-exchange-order-execution-api, trading-exchange-rate-limiting, trading-execution-vwap, trading-fundamentals-market-structure trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-execution-api, trading-exchange-rate-limiting, trading-execution-vwap, trading-technical-false-signal-filtering

**Removed:** trading-fundamentals-market-structure trading-technical-cycle-analysis


### trading-exchange-order-execution-api

**Before:** trading-exchange-order-book-sync, trading-exchange-rate-limiting, trading-execution-twap, trading-execution-vwap trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-exchange-rate-limiting, trading-execution-twap, trading-technical-false-signal-filtering

**Removed:** trading-execution-vwap trading-technical-cycle-analysis


### trading-exchange-rate-limiting

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-exchange-trade-reporting

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-exchange-websocket-handling

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-exchange-websocket-streaming

**Before:** trading-ai-order-flow-analysis, trading-data-alternative-data, trading-data-backfill-strategy trading-data-order-book

**After:** trading-ai-order-flow-analysis, trading-data-alternative-data

**Removed:** trading-data-backfill-strategy trading-data-order-book


### trading-execution-order-book-impact

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-execution-rate-limiting

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-execution-slippage-modeling

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-execution-twap

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-execution-twap-vwap

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-execution-vwap

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-fundamentals-market-regimes

**Before:** trading-fundamentals-trading-edge, trading-paper-commission-model, trading-paper-market-impact, trading-paper-realistic-simulation trading-fundamentals-trading-plan

**After:** trading-fundamentals-trading-edge, trading-paper-commission-model, trading-paper-market-impact

**Removed:** trading-paper-realistic-simulation trading-fundamentals-trading-plan


### trading-fundamentals-market-structure

**Before:** trading-ai-order-flow-analysis, trading-data-order-book, trading-exchange-order-book-sync trading-exchange-order-execution-api

**After:** trading-ai-order-flow-analysis, trading-data-order-book

**Removed:** trading-exchange-order-book-sync trading-exchange-order-execution-api


### trading-fundamentals-risk-management-basics

**Before:** trading-backtest-drawdown-analysis, trading-backtest-position-sizing trading-exchange-order-book-sync, trading-exchange-order-execution-api

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api

**Removed:** trading-backtest-position-sizing trading-exchange-order-book-sync


### trading-fundamentals-trading-edge

**Before:** trading-fundamentals-market-regimes, trading-fundamentals-trading-plan, trading-fundamentals-trading-psychology trading-ai-multi-asset-model, trading-risk-correlation-risk

**After:** trading-fundamentals-market-regimes, trading-fundamentals-trading-plan, trading-risk-correlation-risk

**Removed:** trading-fundamentals-trading-psychology trading-ai-multi-asset-model


### trading-fundamentals-trading-plan

**Before:** trading-fundamentals-trading-edge, trading-fundamentals-trading-psychology trading-ai-multi-asset-model, trading-risk-correlation-risk

**After:** trading-fundamentals-trading-edge, trading-risk-correlation-risk

**Removed:** trading-fundamentals-trading-psychology trading-ai-multi-asset-model


### trading-fundamentals-trading-psychology

**Before:** trading-fundamentals-trading-edge, trading-fundamentals-trading-plan trading-ai-multi-asset-model, trading-risk-correlation-risk

**After:** trading-fundamentals-trading-edge, trading-risk-correlation-risk

**Removed:** trading-fundamentals-trading-plan trading-ai-multi-asset-model


### trading-paper-commission-model

**Before:** trading-fundamentals-market-regimes, trading-fundamentals-trading-plan, trading-paper-market-impact, trading-paper-realistic-simulation trading-fundamentals-trading-edge

**After:** trading-fundamentals-market-regimes, trading-fundamentals-trading-plan, trading-paper-market-impact

**Removed:** trading-paper-realistic-simulation trading-fundamentals-trading-edge


### trading-paper-fill-simulation

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-paper-market-impact

**Before:** trading-fundamentals-market-regimes, trading-fundamentals-trading-plan, trading-paper-commission-model trading-fundamentals-trading-edge

**After:** trading-fundamentals-market-regimes, trading-fundamentals-trading-plan

**Removed:** trading-paper-commission-model trading-fundamentals-trading-edge


### trading-paper-performance-attribution

**Before:** trading-backtest-lookahead-bias, trading-backtest-position-exits trading-fundamentals-trading-edge, trading-fundamentals-trading-plan

**After:** trading-backtest-lookahead-bias, trading-fundamentals-trading-plan

**Removed:** trading-backtest-position-exits trading-fundamentals-trading-edge


### trading-paper-realistic-simulation

**Before:** trading-fundamentals-market-regimes, trading-fundamentals-trading-plan, trading-paper-commission-model trading-fundamentals-trading-edge

**After:** trading-fundamentals-market-regimes, trading-fundamentals-trading-plan

**Removed:** trading-paper-commission-model trading-fundamentals-trading-edge


### trading-paper-slippage-model

**Before:** trading-exchange-order-book-sync, trading-exchange-order-execution-api trading-technical-cycle-analysis, trading-technical-false-signal-filtering

**After:** trading-exchange-order-book-sync, trading-technical-false-signal-filtering

**Removed:** trading-exchange-order-execution-api trading-technical-cycle-analysis


### trading-risk-correlation-risk

**Before:** trading-ai-multi-asset-model, trading-backtest-drawdown-analysis trading-backtest-position-sizing, trading-fundamentals-risk-management-basics

**After:** trading-ai-multi-asset-model, trading-fundamentals-risk-management-basics

**Removed:** trading-backtest-drawdown-analysis trading-backtest-position-sizing


### trading-risk-drawdown-control

**Before:** trading-backtest-drawdown-analysis, trading-backtest-position-sizing trading-exchange-order-book-sync, trading-exchange-order-execution-api

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api

**Removed:** trading-backtest-position-sizing trading-exchange-order-book-sync


### trading-risk-kill-switches

**Before:** trading-backtest-drawdown-analysis, trading-backtest-position-sizing trading-exchange-order-book-sync, trading-exchange-order-execution-api

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api

**Removed:** trading-backtest-position-sizing trading-exchange-order-book-sync


### trading-risk-liquidity-risk

**Before:** trading-backtest-drawdown-analysis, trading-backtest-position-sizing trading-exchange-order-book-sync, trading-exchange-order-execution-api

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api

**Removed:** trading-backtest-position-sizing trading-exchange-order-book-sync


### trading-risk-position-sizing

**Before:** trading-backtest-drawdown-analysis, trading-backtest-position-sizing trading-exchange-order-book-sync, trading-exchange-order-execution-api

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api

**Removed:** trading-backtest-position-sizing trading-exchange-order-book-sync


### trading-risk-stop-loss

**Before:** trading-backtest-drawdown-analysis, trading-backtest-position-sizing trading-exchange-order-book-sync, trading-exchange-order-execution-api

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api

**Removed:** trading-backtest-position-sizing trading-exchange-order-book-sync


### trading-risk-stress-testing

**Before:** trading-backtest-drawdown-analysis, trading-backtest-position-sizing trading-exchange-order-book-sync, trading-exchange-order-execution-api

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api

**Removed:** trading-backtest-position-sizing trading-exchange-order-book-sync


### trading-risk-tail-risk

**Before:** trading-backtest-drawdown-analysis, trading-backtest-position-sizing trading-exchange-order-book-sync, trading-exchange-order-execution-api

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api

**Removed:** trading-backtest-position-sizing trading-exchange-order-book-sync


### trading-risk-value-at-risk

**Before:** trading-backtest-drawdown-analysis, trading-backtest-position-sizing trading-exchange-order-book-sync, trading-exchange-order-execution-api

**After:** trading-backtest-drawdown-analysis, trading-exchange-order-execution-api

**Removed:** trading-backtest-position-sizing trading-exchange-order-book-sync


### trading-technical-cycle-analysis

**Before:** trading-ai-time-series-forecasting, trading-ai-volatility-prediction, trading-fundamentals-trading-plan, trading-technical-false-signal-filtering, trading-technical-indicator-confluence trading-fundamentals-trading-edge

**After:** trading-ai-time-series-forecasting, trading-ai-volatility-prediction, trading-fundamentals-trading-plan, trading-technical-false-signal-filtering

**Removed:** trading-technical-indicator-confluence trading-fundamentals-trading-edge


### trading-technical-false-signal-filtering

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-indicator-confluence, trading-technical-momentum-indicators, trading-technical-price-action-patterns trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-indicator-confluence, trading-technical-momentum-indicators

**Removed:** trading-technical-price-action-patterns trading-fundamentals-trading-edge


### trading-technical-indicator-confluence

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


### trading-technical-intermarket-analysis

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


### trading-technical-market-microstructure

**Before:** trading-ai-order-flow-analysis, trading-data-order-book, trading-exchange-order-book-sync trading-exchange-order-execution-api

**After:** trading-ai-order-flow-analysis, trading-data-order-book

**Removed:** trading-exchange-order-book-sync trading-exchange-order-execution-api


### trading-technical-momentum-indicators

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


### trading-technical-price-action-patterns

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


### trading-technical-regime-detection

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


### trading-technical-statistical-arbitrage

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


### trading-technical-support-resistance

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


### trading-technical-trend-analysis

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


### trading-technical-volatility-analysis

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


### trading-technical-volume-profile

**Before:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis, trading-technical-false-signal-filtering trading-fundamentals-trading-edge

**After:** trading-fundamentals-trading-plan, trading-technical-cycle-analysis

**Removed:** trading-technical-false-signal-filtering trading-fundamentals-trading-edge


