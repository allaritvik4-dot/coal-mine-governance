import React from 'react';
import styles from './TermsPage.module.css';

export const TermsPage: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Statutory Terms & Conditions of Use</h1>
        <p className={styles.meta}>
          Coal Mine Smart Governance & Compliance Monitoring System &bull; Operational Release 2026.1
        </p>
      </div>

      <div className={styles.alertBox}>
        <strong>CRITICAL SAFETY MANDATE & STATUTORY NOTICE:</strong>
        <br />
        This system is an automated, computational decision-support tool. It DOES NOT replace statutory human inspections, certified Overman/Mining Sirdar examinations, or the statutory obligations of Mine Managers, Agents, or Owners under the Mines Act, 1952 and Coal Mines Regulations (CMR) 2017.
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>1. Acceptance of Terms</h2>
        <p className={styles.text}>
          By logging into, accessing, or entering records into the Coal Mine Smart Governance System, you agree to be legally bound by these Terms and Conditions. If you do not possess valid statutory qualifications or company authorization to access this platform, you must terminate access immediately.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>2. Description of Service</h2>
        <p className={styles.text}>
          The application aggregates sensor telemetry, inspection findings, accident notifications, machinery maintenance schedules, and worker training certifications to assist management in tracking regulatory compliance. All automated rules, alert triggers, and natural language recommendations provided by the Assistant are supplementary aids.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>3. User Responsibilities</h2>
        <p className={styles.text}>
          Every user is strictly accountable for all entries, modifications, and sign-offs executed under their authenticated account credentials. Users must:
        </p>
        <ul style={{ paddingLeft: '20px', fontSize: '13px', lineHeight: 1.6, color: '#334155' }}>
          <li>Input truthful, accurate, and scientifically validated physical measurements.</li>
          <li>Never share cryptographic passwords, tokens, or digital authentication badges.</li>
          <li>Immediately report any observed discrepancy between underground physical conditions and dashboard sensor indicators.</li>
        </ul>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>4. Access and Authentication</h2>
        <p className={styles.text}>
          Access is granted based on verified regulatory competence. The Colliery Manager reserves the right to suspend or revoke access rights immediately upon reassignment, disciplinary suspension, or termination of statutory appointment.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>5. Data Accuracy and Liability Limitations</h2>
        <p className={styles.text}>
          While the system integrates validation logic to flag erratic readings, the primary responsibility for validating air sample chemical analyses, roof bolt torque readings, and ventilation surveys resides with the appointed Ventilation Officer and Competent Persons.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>6. Intellectual Property</h2>
        <p className={styles.text}>
          The governance software architecture, database schemas, compliance evaluation algorithms, and operational interface are proprietary assets. Statutory forms, regulations, and official circulars reproduced herein remain the copyright of the Directorate General of Mines Safety (DGMS) and the Government of India.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>7. Disclaimer</h2>
        <p className={styles.text}>
          THE SYSTEM, ITS ALERTS, PREDICTIVE INSIGHTS, AND ASSISTANT ANSWERS ARE PROVIDED ON AN "AS IS" AND "AS AVAILABLE" BASIS. NEITHER THE SYSTEM DEVELOPERS NOR MINING MANAGEMENT WARRANT THAT AUTOMATED RULE CHECKS WILL PREDICT ALL UNFORESEEN GEOLOGICAL STRATA MOVEMENTS, GAS OUTBURSTS, OR EQUIPMENT FAILURES. SOUND MINING ENGINEERING PRACTICES AND IMMEDIATE SENSORY OBSERVATION TAKE PRECEDENCE OVER ANY SYSTEM OUTPUT.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>8. Limitation of Liability</h2>
        <p className={styles.text}>
          In no event shall software providers, systems engineers, or technical operators be held liable for punitive, secondary, or consequential damages resulting from operational decisions taken without independent physical verification by certified mine statutory staff.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>9. Governing Law</h2>
        <p className={styles.text}>
          These Terms and all regulatory filings conducted within the platform shall be interpreted and governed by the laws of India, specifically under the jurisdiction of the Mines Act 1952, Coal Mines Regulations 2017, and the competent courts of the respective mining state.
        </p>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>10. Modifications to Terms</h2>
        <p className={styles.text}>
          The system administrators may update these terms to reflect newly gazetted DGMS standards or statutory directives. Continued use following notification constitutes statutory acceptance.
        </p>
      </div>
    </div>
  );
};

export default TermsPage;
