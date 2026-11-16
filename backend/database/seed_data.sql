-- Coal Mine Smart Governance & Compliance Monitoring System
-- Seed Data for Development/Testing

-- ============================================================
-- MINES
-- ============================================================
INSERT INTO mines (name, type, location, state, district, license_number, owner_company, status, created_at) VALUES
('Jharia Coalfield Mine #4', 'underground', 'Jharia, Dhanbad', 'Jharkhand', 'Dhanbad', 'JH-COAL-2019-0042', 'Bharat Coking Coal Limited', 'active', '2025-01-15T08:00:00Z'),
('Singrauli Open Cast Mine', 'opencast', 'Singrauli Basin', 'Madhya Pradesh', 'Singrauli', 'MP-COAL-2020-0118', 'Northern Coalfields Limited', 'active', '2025-02-20T09:30:00Z'),
('Korba Underground Mine', 'underground', 'Korba Coalfield', 'Chhattisgarh', 'Korba', 'CG-COAL-2018-0067', 'South Eastern Coalfields Limited', 'active', '2025-03-10T10:00:00Z');

-- ============================================================
-- SECTIONS
-- ============================================================
INSERT INTO sections (mine_id, name, type, depth_meters, status, created_at) VALUES
(1, 'Panel A - Longwall', 'extraction', 285.0, 'active', '2025-01-20T08:00:00Z'),
(1, 'Panel B - Bord and Pillar', 'extraction', 210.5, 'active', '2025-01-20T08:30:00Z'),
(1, 'Main Shaft Ventilation', 'ventilation', 290.0, 'active', '2025-01-20T09:00:00Z'),
(2, 'OC Bench 1 - North', 'extraction', NULL, 'active', '2025-02-25T08:00:00Z'),
(2, 'OC Bench 2 - South', 'extraction', NULL, 'active', '2025-02-25T08:30:00Z'),
(2, 'Overburden Dump Area', 'dumping', NULL, 'active', '2025-02-25T09:00:00Z'),
(3, 'Dip Side Panel 1', 'extraction', 340.0, 'active', '2025-03-15T08:00:00Z'),
(3, 'Rise Side Panel 2', 'extraction', 195.0, 'active', '2025-03-15T08:30:00Z');

-- ============================================================
-- USERS  (password: demo123)
-- ============================================================
INSERT INTO users (username, password_hash, full_name, role, email, mine_id, is_active, created_at) VALUES
('admin', '$2b$12$MXvIP11BnXZZoXq72PmBn.EptV4PNZvi4vt5Ligwa78L3lIHqJ5hC', 'Rajesh Kumar Singh', 'admin', 'admin@coalmine.gov.in', NULL, 1, '2025-01-10T06:00:00Z'),
('mgr_jharia', '$2b$12$MXvIP11BnXZZoXq72PmBn.EptV4PNZvi4vt5Ligwa78L3lIHqJ5hC', 'Anil Prasad Verma', 'mine_manager', 'anil.verma@bccl.gov.in', 1, 1, '2025-01-16T07:00:00Z'),
('mgr_singrauli', '$2b$12$MXvIP11BnXZZoXq72PmBn.EptV4PNZvi4vt5Ligwa78L3lIHqJ5hC', 'Priya Sharma', 'mine_manager', 'priya.sharma@ncl.gov.in', 2, 1, '2025-02-22T07:00:00Z'),
('safety_jharia', '$2b$12$MXvIP11BnXZZoXq72PmBn.EptV4PNZvi4vt5Ligwa78L3lIHqJ5hC', 'Deepak Chandra Mishra', 'safety_officer', 'deepak.mishra@bccl.gov.in', 1, 1, '2025-01-18T07:00:00Z'),
('safety_korba', '$2b$12$MXvIP11BnXZZoXq72PmBn.EptV4PNZvi4vt5Ligwa78L3lIHqJ5hC', 'Sunita Devi Patel', 'safety_officer', 'sunita.patel@secl.gov.in', 3, 1, '2025-03-12T07:00:00Z'),
('insp_dgms', '$2b$12$MXvIP11BnXZZoXq72PmBn.EptV4PNZvi4vt5Ligwa78L3lIHqJ5hC', 'Vikram Rathore', 'inspector', 'vikram.rathore@dgms.gov.in', NULL, 1, '2025-01-12T06:30:00Z');

-- ============================================================
-- INSPECTIONS
-- ============================================================
INSERT INTO inspections (mine_id, section_id, inspector_id, type, scheduled_date, completed_date, status, findings, risk_level, evidence_attached, created_at, updated_at) VALUES
(1, 1, 6, 'safety_audit', '2025-06-15', '2025-06-15', 'completed', 'Longwall face supports inspected. Two hydraulic props showing signs of fatigue at positions 14 and 22. Recommended replacement within 30 days.', 'medium', 1, '2025-06-01T08:00:00Z', '2025-06-15T16:30:00Z'),
(1, 2, 6, 'ventilation', '2025-07-10', '2025-07-10', 'completed', 'Airflow velocity at intake measured 1.8 m/s, within acceptable range. Methane levels at 0.3% — well below statutory 1.25% limit. All auxiliary fans operational.', 'low', 1, '2025-07-01T08:00:00Z', '2025-07-10T15:00:00Z'),
(1, 3, 6, 'electrical', '2025-08-20', '2025-08-20', 'completed', 'Flameproof enclosures on main shaft motors checked. One enclosure on Fan #2 had loose bolts — tightened on site. Cable insulation satisfactory.', 'low', 0, '2025-08-10T08:00:00Z', '2025-08-20T14:00:00Z'),
(2, 4, 6, 'safety_audit', '2025-09-05', '2025-09-05', 'completed', 'Bench stability assessed. Slope angle at 62 degrees on north face — exceeds recommended 55 degrees. Immediate corrective action required to reduce slope angle.', 'high', 1, '2025-08-25T08:00:00Z', '2025-09-05T17:00:00Z'),
(2, 5, 6, 'environmental', '2025-10-12', '2025-10-12', 'completed', 'Dust suppression systems operational. Water sprinklers on haul road functioning. SPM levels at 385 µg/m³ — marginally above 350 µg/m³ CPCB limit. Additional measures recommended.', 'medium', 1, '2025-10-01T08:00:00Z', '2025-10-12T16:00:00Z'),
(2, 6, 6, 'structural', '2025-11-01', NULL, 'scheduled', NULL, NULL, 0, '2025-10-20T08:00:00Z', NULL),
(3, 7, 6, 'safety_audit', '2025-11-18', '2025-11-18', 'completed', 'Dip side panel supports checked. Roof bolting pattern adequate. Water seepage observed at chainage 450m — pumping arrangements in place. No immediate danger.', 'medium', 1, '2025-11-05T08:00:00Z', '2025-11-18T15:30:00Z'),
(3, 8, 6, 'ventilation', '2025-12-10', '2025-12-10', 'completed', 'Rise side panel ventilation satisfactory. Methane at 0.15%. Booster fan #3 vibration slightly elevated — schedule preventive maintenance.', 'low', 0, '2025-12-01T08:00:00Z', '2025-12-10T14:30:00Z'),
(1, 1, 6, 'safety_audit', '2026-01-20', '2026-01-20', 'completed', 'Follow-up inspection on hydraulic props. Replacements completed for positions 14 and 22. All face supports now compliant. Roof convergence monitoring stations installed.', 'low', 1, '2026-01-10T08:00:00Z', '2026-01-20T16:00:00Z'),
(1, 2, 6, 'gas_monitoring', '2026-03-15', '2026-03-15', 'completed', 'Continuous gas monitoring system calibrated. All 12 sensors functional. Telemetry system transmitting to surface control room. Battery backup tested — 4 hrs autonomy confirmed.', 'low', 1, '2026-03-05T08:00:00Z', '2026-03-15T13:00:00Z'),
(2, 4, 6, 'safety_audit', '2026-05-10', NULL, 'overdue', NULL, NULL, 0, '2026-04-28T08:00:00Z', NULL),
(3, 7, 6, 'roof_stability', '2026-06-01', NULL, 'scheduled', NULL, NULL, 0, '2026-05-15T08:00:00Z', NULL);

-- ============================================================
-- HAZARDS
-- ============================================================
INSERT INTO hazards (mine_id, section_id, reported_by, hazard_type, description, severity, location_detail, status, reported_date, resolved_date, created_at) VALUES
(1, 1, 4, 'roof_fall', 'Minor roof spalling observed near face junction at position 18. Loose rock fragments of 10-15 cm. Temporary support installed.', 'high', 'Longwall face junction, position 18', 'mitigated', '2025-07-22', '2025-07-25', '2025-07-22T09:30:00Z'),
(1, 3, 4, 'gas_emission', 'Methane concentration spike to 0.9% detected by sensor MV-03 at main return airway. Spike lasted 12 minutes before normalizing.', 'high', 'Main return airway, sensor MV-03', 'closed', '2025-08-14', '2025-08-15', '2025-08-14T11:00:00Z'),
(2, 4, 3, 'slope_instability', 'Tension cracks observed 2m behind crest of north bench. Crack width approximately 5 cm, length 8m. Slope monitoring prisms installed.', 'critical', 'North bench crest, chainage 120-128m', 'under_review', '2025-09-06', NULL, '2025-09-06T08:45:00Z'),
(2, 5, 3, 'dust_exposure', 'Excessive dust generation during overburden loading. Respirable dust at 4.2 mg/m³ — exceeds 3 mg/m³ occupational limit. Water truck requested.', 'medium', 'South bench loading point', 'mitigated', '2025-10-14', '2025-10-16', '2025-10-14T10:00:00Z'),
(3, 7, 5, 'water_inrush', 'Moderate water seepage from goaf area at chainage 450m in dip side panel. Flow rate estimated at 2.5 L/min. Pumping capacity adequate.', 'medium', 'Dip Side Panel 1, chainage 450m', 'mitigated', '2025-11-20', '2025-11-28', '2025-11-20T14:00:00Z'),
(1, 2, 4, 'electrical', 'Damaged cable insulation found on 550V trailing cable near shuttle car. Exposed conductor length ~3 cm. Cable isolated and tagged.', 'high', 'Bord and Pillar panel, shuttle car bay', 'closed', '2026-01-10', '2026-01-11', '2026-01-10T07:30:00Z'),
(3, 8, 5, 'ground_movement', 'Floor heave of approximately 15 cm observed over 20m length in rise side panel. Passage height reduced to 1.6m in affected zone.', 'medium', 'Rise Side Panel 2, chainage 280-300m', 'reported', '2026-04-05', NULL, '2026-04-05T09:15:00Z'),
(1, 1, 4, 'gas_emission', 'Elevated CO readings (28 ppm) detected in sealed off area adjacent to Panel A. Normal background is 5-8 ppm. Possible indication of spontaneous heating.', 'critical', 'Sealed area adjacent to Panel A longwall', 'under_review', '2026-05-20', NULL, '2026-05-20T06:00:00Z');

-- ============================================================
-- INCIDENTS
-- ============================================================
INSERT INTO incidents (mine_id, section_id, reported_by, incident_type, description, severity, casualties, injuries, date_occurred, date_reported, root_cause, status, created_at) VALUES
(1, 1, 4, 'roof_fall', 'Small roof fall (approx. 0.5 m³) occurred at face junction position 18 during shift change. No personnel in immediate vicinity. Area barricaded.', 'medium', 0, 0, '2025-07-23', '2025-07-23', 'Geological discontinuity intersecting longwall face. Inadequate forward probing.', 'closed', '2025-07-23T10:00:00Z'),
(2, 4, 3, 'slope_failure', 'Partial bench failure on north face. Approximately 200 m³ of material slid down. Dumper operator evacuated safely. Haul road blocked for 6 hours.', 'high', 0, 0, '2025-09-08', '2025-09-08', 'Over-steepened slope angle (62°) combined with monsoon rainfall saturation of overburden material.', 'resolved', '2025-09-08T11:30:00Z'),
(1, 2, 2, 'electrical_shock', 'Shuttle car operator received minor electric shock from trailing cable. First aid administered. Operator resumed duty after medical clearance.', 'medium', 0, 1, '2026-01-10', '2026-01-10', 'Damaged cable insulation from repeated dragging over rough floor. Inspection frequency inadequate.', 'resolved', '2026-01-10T08:00:00Z'),
(3, 7, 5, 'inundation', 'Water inflow rate increased suddenly to 15 L/min from goaf area. Panel evacuated as precaution. Additional pumps deployed. Flow stabilized within 4 hours.', 'high', 0, 0, '2025-12-05', '2025-12-05', 'Intersection of uncharted old workings containing accumulated water. Pre-mining borehole survey was not extended to full goaf boundary.', 'resolved', '2025-12-05T13:00:00Z'),
(1, 3, 4, 'fire', 'Minor fire in cable junction box at main shaft bottom. Fire extinguished within 8 minutes by first responders. Shaft evacuation drill activated.', 'high', 0, 0, '2026-02-18', '2026-02-18', 'Overloaded junction box due to unauthorized additional connection. Circuit breaker failed to trip.', 'investigating', '2026-02-18T15:00:00Z'),
(2, 5, 3, 'vehicle_accident', 'Collision between empty dumper and water tanker on haul road. Both drivers sustained minor bruises. Vehicles with moderate damage.', 'medium', 0, 2, '2026-03-22', '2026-03-22', 'Restricted visibility due to dust. Haul road speed limit not enforced. Missing traffic signage at curve.', 'resolved', '2026-03-22T16:00:00Z');

-- ============================================================
-- EQUIPMENT
-- ============================================================
INSERT INTO equipment (mine_id, section_id, name, type, serial_number, manufacturer, installation_date, last_maintenance_date, next_maintenance_due, status, created_at) VALUES
(1, 1, 'Longwall Shearer LS-200', 'shearer', 'LS200-BCCL-2019-001', 'Eickhoff', '2019-06-15', '2026-03-10', '2026-06-10', 'operational', '2025-01-20T08:00:00Z'),
(1, 1, 'Powered Roof Support PRS-180', 'roof_support', 'PRS180-BCCL-2019-014', 'Caterpillar', '2019-06-15', '2026-02-20', '2026-05-20', 'needs_maintenance', '2025-01-20T08:00:00Z'),
(1, 2, 'Shuttle Car SC-12', 'haulage', 'SC12-BCCL-2020-003', 'Joy Global', '2020-03-10', '2026-01-15', '2026-04-15', 'operational', '2025-01-20T08:30:00Z'),
(1, 3, 'Main Ventilation Fan MVF-01', 'ventilation', 'MVF01-BCCL-2018-001', 'Howden', '2018-09-20', '2025-12-05', '2026-03-05', 'operational', '2025-01-20T09:00:00Z'),
(2, 4, 'Excavator EX-350 Komatsu', 'excavator', 'EX350-NCL-2021-007', 'Komatsu', '2021-01-10', '2026-04-01', '2026-07-01', 'operational', '2025-02-25T08:00:00Z'),
(2, 4, 'Dumper HD-785 #1', 'dumper', 'HD785-NCL-2020-012', 'Komatsu', '2020-07-22', '2026-02-15', '2026-05-15', 'operational', '2025-02-25T08:00:00Z'),
(2, 5, 'Dumper HD-785 #2', 'dumper', 'HD785-NCL-2020-013', 'Komatsu', '2020-07-22', '2026-03-28', '2026-06-28', 'under_repair', '2025-02-25T08:30:00Z'),
(2, 6, 'Dozer D375A', 'dozer', 'D375A-NCL-2019-005', 'Komatsu', '2019-11-05', '2025-11-20', '2026-02-20', 'needs_maintenance', '2025-02-25T09:00:00Z'),
(3, 7, 'Continuous Miner CM-12', 'continuous_miner', 'CM12-SECL-2020-002', 'Sandvik', '2020-05-15', '2026-01-22', '2026-04-22', 'operational', '2025-03-15T08:00:00Z'),
(3, 8, 'Booster Fan BF-03', 'ventilation', 'BF03-SECL-2021-001', 'TLT-Turbo', '2021-02-28', '2025-12-10', '2026-03-10', 'operational', '2025-03-15T08:30:00Z');

-- ============================================================
-- MAINTENANCE ACTIVITIES
-- ============================================================
INSERT INTO maintenance_activities (equipment_id, performed_by, type, description, date_performed, next_due_date, cost, parts_replaced, status, created_at) VALUES
(1, 2, 'preventive', 'Quarterly shearer maintenance — cutting drum picks replaced (64 nos.), ranging arm hydraulic seals checked, electrical cable connections inspected.', '2026-03-10', '2026-06-10', 285000.00, 'Cutting drum picks (64), hydraulic seals (4)', 'completed', '2026-03-10T07:00:00Z'),
(2, 2, 'corrective', 'Hydraulic prop #14 cylinder replaced due to fatigue cracks identified during inspection. Pressure test completed at 350 bar.', '2025-07-28', '2025-10-28', 125000.00, 'Hydraulic cylinder assembly (1)', 'completed', '2025-07-28T08:00:00Z'),
(3, 2, 'corrective', 'Trailing cable repair — damaged section replaced with new 50m length. Insulation resistance test passed at 500V DC.', '2026-01-12', '2026-04-12', 45000.00, 'Trailing cable section (50m)', 'completed', '2026-01-12T09:00:00Z'),
(4, 2, 'preventive', 'Annual main fan overhaul — bearing replacement, impeller balance check, motor winding insulation test. Vibration within limits.', '2025-12-05', '2026-03-05', 520000.00, 'Main bearings (2), coupling elastomers', 'completed', '2025-12-05T06:00:00Z'),
(5, 3, 'preventive', 'Excavator 2000-hour service — engine oil change, hydraulic filters, track tension adjustment, boom cylinder pin greasing.', '2026-04-01', '2026-07-01', 180000.00, 'Engine oil (60L), hydraulic filters (4), air filters (2)', 'completed', '2026-04-01T07:00:00Z'),
(6, 3, 'preventive', 'Dumper #1 quarterly service — tyre pressure check, brake adjustment, engine tune-up, payload monitoring system calibration.', '2026-02-15', '2026-05-15', 95000.00, 'Brake pads (set), engine filters', 'completed', '2026-02-15T08:00:00Z'),
(7, 3, 'corrective', 'Dumper #2 — transmission failure repair. Torque converter rebuilt, planetary gear set replaced. Road test completed satisfactorily.', '2026-03-28', '2026-06-28', 750000.00, 'Torque converter assembly, planetary gear set', 'in_progress', '2026-03-28T07:00:00Z'),
(9, 5, 'preventive', 'Continuous miner chain maintenance — cutting chain replaced, gathering head arms inspected, tramming motor checked.', '2026-01-22', '2026-04-22', 340000.00, 'Cutting chain (1), gathering head bits (24)', 'completed', '2026-01-22T07:30:00Z');

-- ============================================================
-- TRAINING RECORDS
-- ============================================================
INSERT INTO training_records (mine_id, worker_name, worker_id_number, training_type, description, trainer_name, date_completed, valid_until, certificate_number, status, created_at) VALUES
(1, 'Ramesh Kumar', 'BCCL-W-2018-0342', 'gas_testing', 'Certified gas testing and monitoring — methanometer operation, gas cap testing, use of multi-gas detector. DGMS approved syllabus.', 'Dr. S.K. Chowdhary', '2025-06-10', '2026-06-10', 'GT-JH-2025-0042', 'valid', '2025-06-10T16:00:00Z'),
(1, 'Suresh Mahto', 'BCCL-W-2019-0518', 'first_aid', 'Industrial first aid and emergency response — CPR, fracture management, burns treatment, mine rescue basics. Red Cross certified.', 'Dr. Meena Kumari', '2025-04-22', '2026-04-22', 'FA-JH-2025-0118', 'expiring_soon', '2025-04-22T16:00:00Z'),
(1, 'Ajay Singh Yadav', 'BCCL-W-2020-0091', 'roof_bolting', 'Roof bolting operator certification — resin bolt installation, torque testing, bolt pattern design, geological hazard recognition.', 'Er. P.K. Jha', '2025-08-15', '2026-08-15', 'RB-JH-2025-0033', 'valid', '2025-08-15T16:00:00Z'),
(2, 'Mohammed Irfan', 'NCL-W-2019-0267', 'hemm_operation', 'HEMM operator certification — excavator operation, safe loading practices, haul road discipline, pre-start checks.', 'Er. R.N. Dwivedi', '2025-03-08', '2026-03-08', 'HM-SG-2025-0055', 'expired', '2025-03-08T16:00:00Z'),
(2, 'Lakshmi Narayan', 'NCL-W-2020-0445', 'blasting', 'Shot-firer certification — charge calculation, initiation systems, misfires, exclusion zones, post-blast inspection. DGMS Exam passed.', 'Er. K.L. Meena', '2025-09-20', '2026-09-20', 'BL-SG-2025-0021', 'valid', '2025-09-20T16:00:00Z'),
(2, 'Geeta Devi', 'NCL-W-2021-0612', 'fire_fighting', 'Fire prevention and firefighting — fire triangle, extinguisher types, fire hydrant operation, evacuation procedures.', 'Er. S.P. Tiwari', '2025-05-14', '2026-05-14', 'FF-SG-2025-0078', 'expiring_soon', '2025-05-14T16:00:00Z'),
(3, 'Bhola Prasad', 'SECL-W-2018-0189', 'electrical_safety', 'Electrical safety in mines — permits to work, lock-out tag-out, flameproof equipment handling, cable management.', 'Er. D.K. Sahu', '2025-07-30', '2026-07-30', 'ES-KB-2025-0015', 'valid', '2025-07-30T16:00:00Z'),
(3, 'Kamla Bai', 'SECL-W-2019-0334', 'mine_rescue', 'Mine rescue team member training — Proto breathing apparatus, rescue room operation, casualty handling in confined spaces.', 'Cap. R.S. Thakur', '2025-02-18', '2026-02-18', 'MR-KB-2025-0009', 'expired', '2025-02-18T16:00:00Z'),
(1, 'Prakash Chandra', 'BCCL-W-2017-0156', 'induction', 'Initial induction training for underground coal mine — safety rules, emergency procedures, personal protective equipment, hazard recognition.', 'Er. A.K. Sinha', '2025-11-05', '2026-11-05', 'IN-JH-2025-0201', 'valid', '2025-11-05T16:00:00Z'),
(3, 'Dinesh Sahu', 'SECL-W-2020-0501', 'support_systems', 'Roof support systems — steel arch, rock bolting, wire mesh, timber props. Practical assessment in operational panel.', 'Er. M.L. Verma', '2025-10-12', '2026-10-12', 'SS-KB-2025-0044', 'valid', '2025-10-12T16:00:00Z');

-- ============================================================
-- COMPLIANCE RULES
-- ============================================================
INSERT INTO compliance_rules (rule_code, description, category, threshold_value, threshold_unit, check_frequency, severity, is_active, created_by, created_at) VALUES
('CMR-2017-R29', 'Safety inspection of every working face shall be conducted at least once every 15 days by a competent person.', 'inspection', 15.0, 'days', 'fortnightly', 'high', 1, 1, '2025-01-15T08:00:00Z'),
('CMR-2017-R106', 'Methane concentration in general body of air shall not exceed 1.25% at any time in an underground mine.', 'gas_monitoring', 1.25, 'percent', 'continuous', 'critical', 1, 1, '2025-01-15T08:00:00Z'),
('CMR-2017-R182', 'All HEMM (Heavy Earth Moving Machinery) shall undergo preventive maintenance as per manufacturer schedule, not exceeding 90 days.', 'equipment', 90.0, 'days', 'quarterly', 'high', 1, 1, '2025-01-15T08:00:00Z'),
('DGMS-TECH-C8', 'All workers shall receive refresher safety training at least once every 12 months. Certificate validity shall not lapse.', 'training', 365.0, 'days', 'annual', 'medium', 1, 1, '2025-01-15T08:00:00Z'),
('CMR-2017-R175', 'Slope angle of opencast benches shall not exceed 55 degrees unless geotechnical assessment permits higher angle.', 'structural', 55.0, 'degrees', 'monthly', 'high', 1, 1, '2025-01-15T08:00:00Z'),
('DGMS-CIRC-03-2020', 'All reportable incidents shall have root cause analysis completed and corrective actions initiated within 72 hours.', 'incident', 72.0, 'hours', 'per_incident', 'critical', 1, 1, '2025-01-15T08:00:00Z');

-- ============================================================
-- COMPLIANCE ALERTS
-- ============================================================
INSERT INTO compliance_alerts (rule_id, mine_id, section_id, triggered_by_record_type, triggered_by_record_id, message, severity, status, assigned_to, created_at, resolved_at, resolved_by) VALUES
(1, 2, 4, 'inspection', 11, 'Overdue safety inspection for Singrauli Open Cast Mine — OC Bench 1 North. Last inspection completed 2025-09-05. Scheduled inspection 2026-05-10 is overdue.', 'high', 'open', 3, '2026-05-12T08:00:00Z', NULL, NULL),
(3, 2, 6, 'equipment', 8, 'Dozer D375A (SN: D375A-NCL-2019-005) — maintenance overdue. Last maintenance 2025-11-20, next due 2026-02-20. Exceeded 90-day limit.', 'high', 'open', 3, '2026-02-22T08:00:00Z', NULL, NULL),
(5, 2, 4, 'inspection', 4, 'Slope angle at OC Bench 1 North measured at 62° — exceeds 55° threshold per CMR-2017-R175. Immediate corrective action required.', 'critical', 'escalated', 3, '2025-09-06T09:00:00Z', NULL, NULL),
(4, 2, NULL, 'training', 4, 'Training certificate expired — Mohammed Irfan (NCL-W-2019-0267), HEMM Operator Certification. Expired on 2026-03-08. Worker must not operate HEMM until recertified.', 'medium', 'acknowledged', 3, '2026-03-10T08:00:00Z', NULL, NULL),
(4, 3, NULL, 'training', 8, 'Training certificate expired — Kamla Bai (SECL-W-2019-0334), Mine Rescue. Expired on 2026-02-18. Worker must not serve on rescue team until recertified.', 'medium', 'open', 5, '2026-02-20T08:00:00Z', NULL, NULL),
(3, 1, 1, 'equipment', 2, 'Powered Roof Support PRS-180 (SN: PRS180-BCCL-2019-014) — maintenance overdue. Last maintenance 2026-02-20, next due 2026-05-20. Approaching limit.', 'high', 'acknowledged', 2, '2026-05-22T08:00:00Z', NULL, NULL),
(6, 1, 3, 'incident', 5, 'Incident #5 (Cable junction box fire) — root cause analysis not completed within 72-hour window. Incident reported 2026-02-18, still under investigation.', 'critical', 'open', 2, '2026-02-21T08:00:00Z', NULL, NULL),
(1, 1, 2, 'inspection', 10, 'Gas monitoring inspection at Bord and Pillar panel completed on 2026-03-15. Next safety inspection should be scheduled within 15 days.', 'medium', 'resolved', 2, '2026-03-31T08:00:00Z', '2026-04-02T10:00:00Z', 2);

-- ============================================================
-- CORRECTIVE ACTIONS
-- ============================================================
INSERT INTO corrective_actions (alert_id, mine_id, description, assigned_to, assigned_by, priority, status, due_date, completed_date, evidence_notes, created_at, updated_at) VALUES
(3, 2, 'Reduce slope angle at OC Bench 1 North from 62° to 55° by additional benching. Engage geotechnical consultant for redesign.', 3, 1, 'urgent', 'in_progress', '2025-09-20', NULL, 'Geotechnical consultant M/s GeoTech India engaged on 2025-09-08. Preliminary design submitted.', '2025-09-06T10:00:00Z', '2025-09-10T14:00:00Z'),
(2, 2, 'Schedule immediate preventive maintenance for Dozer D375A. Replace overdue filters, check hydraulics, update maintenance log.', 3, 1, 'high', 'assigned', '2026-03-05', NULL, NULL, '2026-02-22T09:00:00Z', NULL),
(4, 2, 'Schedule HEMM operator recertification training for Mohammed Irfan within 15 days. Worker restricted from HEMM operation until certified.', 3, 1, 'high', 'in_progress', '2026-03-25', NULL, 'Training scheduled for 2026-03-20 with Er. R.N. Dwivedi.', '2026-03-10T09:00:00Z', '2026-03-12T11:00:00Z'),
(5, 3, 'Arrange mine rescue refresher training for Kamla Bai. Coordinate with DGMS-approved training center.', 5, 1, 'medium', 'assigned', '2026-03-15', NULL, NULL, '2026-02-20T09:00:00Z', NULL),
(7, 1, 'Complete root cause analysis for cable junction box fire incident. Submit report to DGMS within 7 days. Implement corrective measures.', 2, 1, 'urgent', 'in_progress', '2026-02-25', NULL, 'Investigation team formed. Electrical audit of all junction boxes in progress.', '2026-02-21T09:00:00Z', '2026-02-23T16:00:00Z'),
(6, 1, 'Schedule preventive maintenance for Powered Roof Support PRS-180. Coordinate with Caterpillar service team for hydraulic system overhaul.', 2, 1, 'high', 'assigned', '2026-06-05', NULL, NULL, '2026-05-22T09:00:00Z', NULL);

-- ============================================================
-- AUDIT LOG
-- ============================================================
INSERT INTO audit_log (user_id, action, entity_type, entity_id, old_values, new_values, ip_address, timestamp) VALUES
(1, 'CREATE', 'mine', 1, NULL, '{"name":"Jharia Coalfield Mine #4","type":"underground"}', '192.168.1.10', '2025-01-15T08:00:00Z'),
(1, 'CREATE', 'mine', 2, NULL, '{"name":"Singrauli Open Cast Mine","type":"opencast"}', '192.168.1.10', '2025-02-20T09:30:00Z'),
(1, 'CREATE', 'mine', 3, NULL, '{"name":"Korba Underground Mine","type":"underground"}', '192.168.1.10', '2025-03-10T10:00:00Z'),
(6, 'CREATE', 'inspection', 1, NULL, '{"mine_id":1,"type":"safety_audit","status":"scheduled"}', '10.0.0.50', '2025-06-01T08:00:00Z'),
(6, 'UPDATE', 'inspection', 1, '{"status":"scheduled"}', '{"status":"completed","findings":"Longwall face supports inspected..."}', '10.0.0.50', '2025-06-15T16:30:00Z'),
(4, 'CREATE', 'hazard', 1, NULL, '{"hazard_type":"roof_fall","severity":"high","mine_id":1}', '10.0.1.20', '2025-07-22T09:30:00Z'),
(4, 'UPDATE', 'hazard', 1, '{"status":"reported"}', '{"status":"mitigated"}', '10.0.1.20', '2025-07-25T14:00:00Z'),
(3, 'CREATE', 'hazard', 3, NULL, '{"hazard_type":"slope_instability","severity":"critical","mine_id":2}', '10.0.2.15', '2025-09-06T08:45:00Z'),
(1, 'CREATE', 'compliance_alert', 3, NULL, '{"rule_id":5,"severity":"critical","mine_id":2}', '192.168.1.10', '2025-09-06T09:00:00Z'),
(1, 'CREATE', 'corrective_action', 1, NULL, '{"alert_id":3,"priority":"urgent","assigned_to":3}', '192.168.1.10', '2025-09-06T10:00:00Z'),
(2, 'UPDATE', 'compliance_alert', 8, '{"status":"open"}', '{"status":"resolved"}', '10.0.1.10', '2026-04-02T10:00:00Z'),
(6, 'CREATE', 'inspection', 11, NULL, '{"mine_id":2,"type":"safety_audit","status":"scheduled"}', '10.0.0.50', '2026-04-28T08:00:00Z');
