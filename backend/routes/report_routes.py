"""Statutory compliance reporting, safety analytics, and audit logging routes."""

from flask import Blueprint, request, jsonify
from services.auth_service import jwt_required
from database.db import query_db
from services.audit_service import get_audit_log

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@report_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_summary_report():
    """Retrieve aggregate safety governance KPIs and historical compliance rates."""
    mine_id = request.args.get("mine_id")
    mine_filter = "WHERE mine_id = ?" if mine_id else ""
    args = [mine_id] if mine_id else []

    # Basic tallies
    inspections_total = query_db(f"SELECT COUNT(*) as count FROM inspections {mine_filter}", args, one=True)["count"]
    inspections_completed = query_db(
        f"SELECT COUNT(*) as count FROM inspections WHERE status = 'completed' {'AND mine_id = ?' if mine_id else ''}",
        args,
        one=True,
    )["count"]
    inspections_overdue = query_db(
        f"SELECT COUNT(*) as count FROM inspections WHERE status = 'overdue' {'AND mine_id = ?' if mine_id else ''}",
        args,
        one=True,
    )["count"]

    hazards_total = query_db(f"SELECT COUNT(*) as count FROM hazards {mine_filter}", args, one=True)["count"]
    hazards_mitigated = query_db(
        f"SELECT COUNT(*) as count FROM hazards WHERE status IN ('mitigated', 'closed') {'AND mine_id = ?' if mine_id else ''}",
        args,
        one=True,
    )["count"]

    alerts_total = query_db(f"SELECT COUNT(*) as count FROM compliance_alerts {mine_filter}", args, one=True)["count"]
    alerts_resolved = query_db(
        f"SELECT COUNT(*) as count FROM compliance_alerts WHERE status = 'resolved' {'AND mine_id = ?' if mine_id else ''}",
        args,
        one=True,
    )["count"]

    compliance_score = round((alerts_resolved / alerts_total * 100) if alerts_total > 0 else 100.0, 1)

    return jsonify({
        "success": True,
        "data": {
            "compliance_score_percentage": compliance_score,
            "inspections": {
                "total": inspections_total,
                "completed": inspections_completed,
                "overdue": inspections_overdue,
                "completion_rate": round((inspections_completed / inspections_total * 100) if inspections_total > 0 else 100.0, 1),
            },
            "hazards": {
                "total": hazards_total,
                "mitigated_or_closed": hazards_mitigated,
                "pending": hazards_total - hazards_mitigated,
            },
            "alerts": {
                "total": alerts_total,
                "resolved": alerts_resolved,
                "open_or_escalated": alerts_total - alerts_resolved,
            },
        },
        "message": "Summary safety report retrieved"
    }), 200


@report_bp.route("/compliance", methods=["GET"])
@jwt_required()
def get_compliance_report():
    """Detailed compliance analysis broken down by rule categories and severity levels."""
    mine_id = request.args.get("mine_id")
    where_sql = "WHERE ca.mine_id = ?" if mine_id else ""
    args = [mine_id] if mine_id else []

    by_category = query_db(
        f"""
        SELECT cr.category,
               COUNT(ca.id) as total_alerts,
               SUM(CASE WHEN ca.status = 'resolved' THEN 1 ELSE 0 END) as resolved_count,
               SUM(CASE WHEN ca.status IN ('open', 'escalated') THEN 1 ELSE 0 END) as open_count,
               SUM(CASE WHEN ca.severity = 'critical' THEN 1 ELSE 0 END) as critical_count
        FROM compliance_rules cr
        LEFT JOIN compliance_alerts ca ON cr.id = ca.rule_id
        {where_sql}
        GROUP BY cr.category
        """,
        args
    )

    by_severity = query_db(
        f"""
        SELECT ca.severity, COUNT(*) as count
        FROM compliance_alerts ca
        {where_sql}
        GROUP BY ca.severity
        """,
        args
    )

    by_mine = query_db(
        """
        SELECT m.name as mine_name, m.type as mine_type,
               COUNT(ca.id) as total_alerts,
               SUM(CASE WHEN ca.status = 'resolved' THEN 1 ELSE 0 END) as resolved_alerts,
               SUM(CASE WHEN ca.status = 'open' THEN 1 ELSE 0 END) as open_alerts
        FROM mines m
        LEFT JOIN compliance_alerts ca ON m.id = ca.mine_id
        GROUP BY m.id
        """
    )

    return jsonify({
        "success": True,
        "data": {
            "by_category": by_category,
            "by_severity": by_severity,
            "by_mine": by_mine,
        },
        "message": "Compliance report generated"
    }), 200


@report_bp.route("/incidents", methods=["GET"])
@jwt_required()
def get_incident_report():
    """Incident frequency, casualty rates, and root cause distributions."""
    mine_id = request.args.get("mine_id")
    where_sql = "WHERE inc.mine_id = ?" if mine_id else ""
    args = [mine_id] if mine_id else []

    by_type = query_db(
        f"""
        SELECT inc.incident_type, COUNT(*) as total_count,
               SUM(inc.casualties) as total_casualties,
               SUM(inc.injuries) as total_injuries
        FROM incidents inc
        {where_sql}
        GROUP BY inc.incident_type
        ORDER BY total_count DESC
        """,
        args
    )

    by_severity = query_db(
        f"""
        SELECT inc.severity, COUNT(*) as count
        FROM incidents inc
        {where_sql}
        GROUP BY inc.severity
        """,
        args
    )

    return jsonify({
        "success": True,
        "data": {
            "by_type": by_type,
            "by_severity": by_severity,
        },
        "message": "Incident report generated"
    }), 200


@report_bp.route("/audit-log", methods=["GET"])
@jwt_required()
def get_audit_log_route():
    """Retrieve paginated audit log trail."""
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 20)
    filters = {
        "user_id": request.args.get("user_id"),
        "entity_type": request.args.get("entity_type"),
        "action": request.args.get("action"),
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
    }
    result = get_audit_log(page=page, per_page=per_page, filters=filters)
    return jsonify({"success": True, "data": result, "message": "Audit log retrieved"}), 200
