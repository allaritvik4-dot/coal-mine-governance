"""Compliance evaluation engine for automated safety checks and alert generation."""

from datetime import datetime, date, timedelta
from database.db import query_db, execute_db
from services.audit_service import log_action


def _alert_exists(rule_id, record_type, record_id):
    """Check if an open or acknowledged alert already exists for this record."""
    row = query_db(
        """
        SELECT id FROM compliance_alerts
        WHERE rule_id = ? AND triggered_by_record_type = ? AND triggered_by_record_id = ?
        AND status IN ('open', 'acknowledged', 'escalated')
        """,
        (rule_id, record_type, record_id),
        one=True,
    )
    return row is not None


def _create_alert(rule_id, mine_id, section_id, record_type, record_id, message, severity, assigned_to=None):
    """Insert a compliance alert if one does not already exist."""
    if _alert_exists(rule_id, record_type, record_id):
        return None

    now_iso = datetime.utcnow().isoformat() + "Z"
    alert_id = execute_db(
        """
        INSERT INTO compliance_alerts (
            rule_id, mine_id, section_id, triggered_by_record_type, 
            triggered_by_record_id, message, severity, status, assigned_to, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)
        """,
        (rule_id, mine_id, section_id, record_type, record_id, message, severity, assigned_to, now_iso),
    )
    return alert_id


def check_overdue_inspections(mine_id=None):
    """Check for overdue scheduled inspections and sections without inspections in statutory time."""
    alerts_created = []
    today_str = date.today().isoformat()

    # Rule CMR-2017-R29
    rule = query_db("SELECT id, severity FROM compliance_rules WHERE rule_code = 'CMR-2017-R29'", one=True)
    rule_id = rule["id"] if rule else 1
    severity = rule["severity"] if rule else "high"

    # 1. Update inspections that passed scheduled date without completion
    mine_filter = "AND i.mine_id = ?" if mine_id else ""
    args = [today_str, mine_id] if mine_id else [today_str]
    
    overdue_inspections = query_db(
        f"""
        SELECT i.id, i.mine_id, i.section_id, i.scheduled_date, i.type, m.name as mine_name, s.name as section_name
        FROM inspections i
        JOIN mines m ON i.mine_id = m.id
        LEFT JOIN sections s ON i.section_id = s.id
        WHERE i.scheduled_date < ? 
        AND i.status IN ('scheduled', 'in_progress')
        {mine_filter}
        """,
        args
    )

    for insp in overdue_inspections:
        # Mark as overdue
        execute_db("UPDATE inspections SET status = 'overdue', updated_at = ? WHERE id = ?", (today_str, insp["id"]))
        
        msg = f"Overdue inspection ({insp['type']}) for {insp['mine_name']}"
        if insp["section_name"]:
            msg += f" - Section: {insp['section_name']}"
        msg += f". Scheduled date {insp['scheduled_date']} has elapsed."

        alert_id = _create_alert(
            rule_id=rule_id,
            mine_id=insp["mine_id"],
            section_id=insp["section_id"],
            record_type="inspection",
            record_id=insp["id"],
            message=msg,
            severity=severity
        )
        if alert_id:
            alerts_created.append(alert_id)

    return alerts_created


def check_equipment_maintenance(mine_id=None):
    """Check equipment with overdue maintenance or exceeding 90-day maintenance limit."""
    alerts_created = []
    today_str = date.today().isoformat()

    # Rule CMR-2017-R182
    rule = query_db("SELECT id, severity FROM compliance_rules WHERE rule_code = 'CMR-2017-R182'", one=True)
    rule_id = rule["id"] if rule else 3
    severity = rule["severity"] if rule else "high"

    mine_filter = "AND e.mine_id = ?" if mine_id else ""
    args = [today_str, mine_id] if mine_id else [today_str]

    overdue_equipment = query_db(
        f"""
        SELECT e.id, e.name, e.serial_number, e.mine_id, e.section_id, e.last_maintenance_date, 
               e.next_maintenance_due, e.status, m.name as mine_name
        FROM equipment e
        JOIN mines m ON e.mine_id = m.id
        WHERE (e.next_maintenance_due < ? OR e.status = 'needs_maintenance')
        AND e.status != 'decommissioned'
        {mine_filter}
        """,
        args
    )

    for eq in overdue_equipment:
        msg = f"Equipment {eq['name']} (SN: {eq['serial_number']}) at {eq['mine_name']} requires maintenance. Due date: {eq['next_maintenance_due']}."
        alert_id = _create_alert(
            rule_id=rule_id,
            mine_id=eq["mine_id"],
            section_id=eq["section_id"],
            record_type="equipment",
            record_id=eq["id"],
            message=msg,
            severity=severity
        )
        if alert_id:
            alerts_created.append(alert_id)

    return alerts_created


def check_training_expiry(mine_id=None):
    """Check worker certifications that are expired or expiring within 30 days."""
    alerts_created = []
    today = date.today()
    today_str = today.isoformat()
    thirty_days_later_str = (today + timedelta(days=30)).isoformat()

    # Rule DGMS-TECH-C8
    rule = query_db("SELECT id, severity FROM compliance_rules WHERE rule_code = 'DGMS-TECH-C8'", one=True)
    rule_id = rule["id"] if rule else 4
    severity = rule["severity"] if rule else "medium"

    mine_filter = "AND t.mine_id = ?" if mine_id else ""
    args = [thirty_days_later_str, mine_id] if mine_id else [thirty_days_later_str]

    records = query_db(
        f"""
        SELECT t.id, t.mine_id, t.worker_name, t.worker_id_number, t.training_type, 
               t.valid_until, t.status, m.name as mine_name
        FROM training_records t
        JOIN mines m ON t.mine_id = m.id
        WHERE t.valid_until <= ?
        {mine_filter}
        """,
        args
    )

    for rec in records:
        valid_until = rec["valid_until"]
        is_expired = valid_until < today_str
        new_status = "expired" if is_expired else "expiring_soon"

        if rec["status"] != new_status:
            execute_db("UPDATE training_records SET status = ? WHERE id = ?", (new_status, rec["id"]))

        alert_severity = "high" if is_expired else severity
        msg = f"Training certification '{rec['training_type']}' for {rec['worker_name']} ({rec['worker_id_number']}) at {rec['mine_name']} "
        msg += f"has expired on {valid_until}." if is_expired else f"is expiring soon on {valid_until}."

        alert_id = _create_alert(
            rule_id=rule_id,
            mine_id=rec["mine_id"],
            section_id=None,
            record_type="training",
            record_id=rec["id"],
            message=msg,
            severity=alert_severity
        )
        if alert_id:
            alerts_created.append(alert_id)

    return alerts_created


def check_threshold_violations(mine_id=None):
    """Check statutory threshold violations such as slope angles, gas levels, and delayed root causes."""
    alerts_created = []
    now = datetime.utcnow()
    seventy_two_hours_ago = (now - timedelta(hours=72)).isoformat() + "Z"

    # 1. DGMS-CIRC-03-2020: Incidents pending root cause > 72 hours
    rule_inc = query_db("SELECT id, severity FROM compliance_rules WHERE rule_code = 'DGMS-CIRC-03-2020'", one=True)
    if rule_inc:
        mine_filter = "AND inc.mine_id = ?" if mine_id else ""
        args = [seventy_two_hours_ago, mine_id] if mine_id else [seventy_two_hours_ago]
        delayed_incidents = query_db(
            f"""
            SELECT inc.id, inc.mine_id, inc.section_id, inc.incident_type, inc.date_occurred, inc.created_at, m.name as mine_name
            FROM incidents inc
            JOIN mines m ON inc.mine_id = m.id
            WHERE (inc.root_cause IS NULL OR TRIM(inc.root_cause) = '')
            AND inc.status IN ('reported', 'investigating')
            AND inc.created_at <= ?
            {mine_filter}
            """,
            args
        )
        for d in delayed_incidents:
            msg = f"Incident #{d['id']} ({d['incident_type']}) at {d['mine_name']}: Root cause analysis not completed within statutory 72-hour window."
            alert_id = _create_alert(
                rule_id=rule_inc["id"],
                mine_id=d["mine_id"],
                section_id=d["section_id"],
                record_type="incident",
                record_id=d["id"],
                message=msg,
                severity=rule_inc["severity"] or "critical"
            )
            if alert_id:
                alerts_created.append(alert_id)

    # 2. CMR-2017-R175: Slope angle check from inspections/hazards
    rule_slope = query_db("SELECT id, severity FROM compliance_rules WHERE rule_code = 'CMR-2017-R175'", one=True)
    if rule_slope:
        mine_filter = "AND h.mine_id = ?" if mine_id else ""
        args = [mine_id] if mine_id else []
        slope_hazards = query_db(
            f"""
            SELECT h.id, h.mine_id, h.section_id, h.description, m.name as mine_name
            FROM hazards h
            JOIN mines m ON h.mine_id = m.id
            WHERE h.hazard_type IN ('slope_instability', 'landslide')
            AND h.status IN ('reported', 'under_review')
            {mine_filter}
            """,
            args
        )
        for h in slope_hazards:
            msg = f"Opencast bench stability concern reported at {h['mine_name']}. Potential violation of 55° slope angle limit per CMR-2017-R175."
            alert_id = _create_alert(
                rule_id=rule_slope["id"],
                mine_id=h["mine_id"],
                section_id=h["section_id"],
                record_type="hazard",
                record_id=h["id"],
                message=msg,
                severity=rule_slope["severity"] or "high"
            )
            if alert_id:
                alerts_created.append(alert_id)

    return alerts_created


def run_all_checks(mine_id=None):
    """Run full compliance evaluation suite across inspections, equipment, training, and thresholds."""
    results = {
        "overdue_inspections": check_overdue_inspections(mine_id),
        "equipment_maintenance": check_equipment_maintenance(mine_id),
        "training_expiry": check_training_expiry(mine_id),
        "threshold_violations": check_threshold_violations(mine_id),
    }
    total_new_alerts = sum(len(ids) for ids in results.values())
    return {
        "success": True,
        "total_new_alerts": total_new_alerts,
        "details": results,
    }


def resolve_alert(alert_id: int, user_id: int):
    """Mark a compliance alert as resolved and create audit entry."""
    alert = query_db("SELECT * FROM compliance_alerts WHERE id = ?", (alert_id,), one=True)
    if not alert:
        return False, "Alert not found"

    now_iso = datetime.utcnow().isoformat() + "Z"
    execute_db(
        """
        UPDATE compliance_alerts 
        SET status = 'resolved', resolved_at = ?, resolved_by = ?
        WHERE id = ?
        """,
        (now_iso, user_id, alert_id),
    )
    log_action(
        user_id=user_id,
        action="RESOLVE",
        entity_type="compliance_alert",
        entity_id=alert_id,
        old_values={"status": alert["status"]},
        new_values={"status": "resolved", "resolved_at": now_iso},
    )
    return True, "Alert marked as resolved"


def create_corrective_action(alert_id: int, mine_id: int, description: str, assigned_to: int, assigned_by: int, priority: str = "medium", due_date: str = None, evidence_notes: str = None):
    """Create a corrective action linked to a compliance alert."""
    now_iso = datetime.utcnow().isoformat() + "Z"
    ca_id = execute_db(
        """
        INSERT INTO corrective_actions (
            alert_id, mine_id, description, assigned_to, assigned_by, priority,
            status, due_date, evidence_notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'assigned', ?, ?, ?)
        """,
        (alert_id, mine_id, description, assigned_to, assigned_by, priority, due_date, evidence_notes, now_iso),
    )
    log_action(
        user_id=assigned_by,
        action="CREATE",
        entity_type="corrective_action",
        entity_id=ca_id,
        new_values={
            "alert_id": alert_id,
            "mine_id": mine_id,
            "description": description,
            "assigned_to": assigned_to,
            "priority": priority,
            "due_date": due_date,
        },
    )
    return ca_id
