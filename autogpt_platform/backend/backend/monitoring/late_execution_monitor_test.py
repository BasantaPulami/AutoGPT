from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from backend.data.execution import ExecutionStatus
from backend.monitoring.late_execution_monitor import LateExecutionMonitor
from backend.util.metrics import DiscordChannel


def test_late_execution_alert_uses_stable_correlation_id():
    queued_execution = SimpleNamespace(
        id="exec-1",
        graph_id="graph-1",
        graph_version=1,
        user_id="user-1",
        status=ExecutionStatus.QUEUED,
        started_at=None,
    )
    running_execution = SimpleNamespace(
        id="exec-2",
        graph_id="graph-2",
        graph_version=1,
        user_id="user-2",
        status=ExecutionStatus.RUNNING,
        started_at=datetime.now(timezone.utc),
    )

    with patch(
        "backend.monitoring.late_execution_monitor.get_database_manager_client"
    ) as mock_get_database_manager_client, patch(
        "backend.monitoring.late_execution_monitor.get_notification_manager_client"
    ) as mock_get_notification_manager_client, patch(
        "backend.monitoring.late_execution_monitor.sentry_capture_error"
    ):
        mock_db_client = MagicMock()
        mock_db_client.get_graph_executions.side_effect = [
            [queued_execution],
            [running_execution],
        ]
        mock_get_database_manager_client.return_value = mock_db_client

        mock_notification_client = MagicMock()
        mock_get_notification_manager_client.return_value = mock_notification_client

        monitor = LateExecutionMonitor()
        monitor.check_late_executions()

    mock_notification_client.system_alert.assert_called_once()
    assert mock_notification_client.system_alert.call_args.kwargs["channel"] == (
        DiscordChannel.PLATFORM
    )
    assert mock_notification_client.system_alert.call_args.kwargs["correlation_id"] == (
        f"late_execution_queued_running_{monitor.config.execution_late_notification_threshold_secs}s"
    )
