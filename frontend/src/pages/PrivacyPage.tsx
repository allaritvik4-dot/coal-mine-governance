import React from 'react';
import styles from './PrivacyPage.module.css';

export const PrivacyPage: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Data Protection & Privacy Policy</h1>
        <p className={styles.meta}>
          Coal Mine Smart Governance & Compliance Monitoring System &bull; Effective Date: January 1, 2026 &bull; Statutory Version 2.4
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>1. Information Collection and Use</h2>
        <p className={styles.text}>
          This Smart Governance System processes statutory operational, technical, environmental, and personnel data required under the Mines Act, 1952, Coal Mines Regulations (CMR) 2017, and Directorate General of Mines Safety (DGMS) guidelines. Data processed includes:
        </p>
        <ul className={styles.list}>
          <li>
            <strong>Personnel & Certification Records:</strong> Worker identity identifiers, statutory qualifications, Vocational Training Rules (VTR) certifications, medical fitness records, and mine site shift assignments.
          </li>
          <li>
            <strong>Operational & Environmental Telemetry:</strong> Real-time and logged sensor readings for methane (CH4), carbon monoxide (CO), air velocity, roof sag telemetry, water pump flowrates, and seismic monitoring.
          </li>
          <li>
            <strong>Statutory Inspection & Incident Data:</strong> Findings recorded by DGMS inspectors, internal safety officers, accident investigation reports (Forms IV-A/B), and corrective directives.
          </li>
          <li>
            <strong>System Audit Logs:</strong> User session identifiers, client IP addresses, authentication attempts, and cryptographic change ledgers for all regulatory filings.
          </li>
        </ul>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>2. Data Storage and Security</h2>
        <p className={styles.text}>
          All data is housed within secure, sovereign operational environments adhering to enterprise cybersecurity standards. Local installations within mine site local area networks (LAN) utilize encrypted SQLite data stores, TLS 1.3 encrypted REST communication channels, and bcrypt hashed credential storage. Knowledge embeddings utilized by the automated regulatory assistant are strictly indexed in localized ChromaDB vector stores with no external transmission of sensitive mine schematics or blast designs.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>3. Access Controls</h2>
        <p className={styles.text}>
          Access to this platform is governed strictly by Role-Based Access Control (RBAC). Roles are partitioned as follows:
        </p>
        <ul className={styles.list}>
          <li><strong>System Administrator:</strong> User account lifecycle management, system backups, and database configuration.</li>
          <li><strong>Mine Manager / Agent:</strong> Overall colliery statutory oversight, inspection review, and sign-off on major corrective action plans.</li>
          <li><strong>Safety Officer:</strong> Hazard reporting, air measurement entries, incident investigation submissions, and training log validation.</li>
          <li><strong>Statutory Inspector:</strong> Read-only compliance audit access and generation of formal regulatory notices.</li>
          <li><strong>Viewer / Operator:</strong> Restricted view of immediate machinery status and active hazard alerts.</li>
        </ul>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>4. Data Retention</h2>
        <p className={styles.text}>
          Pursuant to CMR 2017 Regulation 145 and related provisions, statutory inspection registers, accident inquiries, and worker health surveillance records must be maintained indefinitely or for a minimum of thirty (30) years from the date of creation. The system enforces write-once immutable audit logs that prevent premature truncation or deletion of historical incident registers.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>5. User Rights</h2>
        <p className={styles.text}>
          Authorized workers and managers have the right to inspect their individual certification records and dispute factual inaccuracies in training expiration dates or badge credentials. Requests for corrections must be routed through the Colliery Vocational Training Officer with authenticated documentary proof.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>6. Third-Party Services</h2>
        <p className={styles.text}>
          The Coal Mine Governance System is designed for high-reliability air-gapped or closed-loop operational deployments. It does not transmit telemetric or proprietary geological data to commercial third-party advertisers, external LLM public cloud APIs, or cross-site tracking engines.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>7. Updates to Privacy Policy</h2>
        <p className={styles.text}>
          This policy is reviewed annually or whenever amendments to the Mines Act, CMR, or statutory digital record-keeping guidelines are promulgated by the Ministry of Coal or DGMS. Notification of revisions will be delivered via an administrative broadcast alert within the system top bar.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>8. Contact Information</h2>
        <p className={styles.text}>
          For regulatory inquiries, statutory data verification, or security incident disclosures, contact the designated Colliery Data Protection Officer and Safety Directorate at:
          <br />
          <strong>Colliery Safety & IT Compliance Directorate</strong>
          <br />
          Email: <span style={{ color: '#0284c7' }}>compliance-directorate@coalmine-governance.internal</span>
          <br />
          Emergency Operations Control Room: +91 (0) 7752-246810
        </p>
      </div>
    </div>
  );
};

export default PrivacyPage;
