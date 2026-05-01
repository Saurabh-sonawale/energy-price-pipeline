# GCP Deployment Guide

This repository runs locally with Docker Compose and can be adapted to Google Cloud.

## Production-oriented GCP mapping

| Local component | GCP service option |
|---|---|
| Kafka | Managed Kafka partner, Confluent Cloud, or Pub/Sub with adapter |
| PostgreSQL | Cloud SQL for PostgreSQL |
| App containers | Cloud Run or GKE |
| Model artifacts | Cloud Storage |
| Secrets | Secret Manager |
| Logs | Cloud Logging |
| Schedules | Cloud Scheduler or Cloud Composer |
| MLflow | Cloud Run + Cloud SQL backend + GCS artifact store |
| Dashboard | Tableau Cloud connected to Cloud SQL or exported CSVs in GCS |

## Suggested deployment steps

1. Build and push containers to Artifact Registry.
2. Create Cloud SQL PostgreSQL instance and apply `database/schema.sql`.
3. Store API keys and database credentials in Secret Manager.
4. Deploy producers, processor, and prediction service to Cloud Run jobs/services or GKE deployments.
5. Use Cloud Scheduler for retraining jobs.
6. Connect Tableau Cloud/Desktop to Cloud SQL using secure networking.

## Notes

For a data engineering portfolio, keep both the local Docker path and cloud architecture documented. Hiring teams can run the project locally while still seeing cloud deployment readiness.
