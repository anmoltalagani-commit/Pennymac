import os
import logging
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "365"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"


def lambda_handler(event, context):
    """
    Deletes EBS snapshots owned by this account that are older than RETENTION_DAYS.
    Notes:
      - Uses OwnerIds=['self'] so we only touch snapshots we own.
      - StartTime returned by boto3 is timezone-aware; compare with UTC-aware 'now'.
    """
    ec2 = boto3.client("ec2")
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=RETENTION_DAYS)

    logger.info("Snapshot cleanup started. retention_days=%s cutoff=%s dry_run=%s",
                RETENTION_DAYS, cutoff.isoformat(), DRY_RUN)

    deleted = 0
    examined = 0
    candidates = 0

    paginator = ec2.get_paginator("describe_snapshots")

    try:
        for page in paginator.paginate(OwnerIds=["self"]):
            for snap in page.get("Snapshots", []):
                examined += 1
                snapshot_id = snap.get("SnapshotId")
                start_time = snap.get("StartTime")  # datetime, tz-aware

                if not snapshot_id or not start_time:
                    continue

                if start_time < cutoff:
                    candidates += 1
                    logger.info("Deleting snapshot: %s (StartTime=%s)", snapshot_id, start_time.isoformat())

                    if DRY_RUN:
                        continue

                    try:
                        ec2.delete_snapshot(SnapshotId=snapshot_id)
                        deleted += 1
                    except ClientError as e:
                        # Common issues: snapshot in use, permissions, etc.
                        logger.error("Failed to delete snapshot %s: %s", snapshot_id, e, exc_info=True)

    except ClientError as e:
        logger.error("Failed to list snapshots: %s", e, exc_info=True)
        raise

    logger.info("Snapshot cleanup complete. examined=%d candidates=%d deleted=%d",
                examined, candidates, deleted)

    return {
        "examined": examined,
        "candidates": candidates,
        "deleted": deleted,
        "retention_days": RETENTION_DAYS,
        "dry_run": DRY_RUN,
        "cutoff": cutoff.isoformat(),
    }
