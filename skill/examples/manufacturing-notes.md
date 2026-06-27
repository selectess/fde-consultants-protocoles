# Manufacturing Customer Interview Notes

The customer is a mid-size automotive parts manufacturer. They make brake discs.

Their main process is quality control on the assembly line. They have 3 production lines, each running 8 hours/day, 5 days/week. Each line produces about 500 brake discs per day.

A brake disc passes through visual inspection by a human operator. The operator looks for surface defects: cracks, scratches, and dimensional issues. There are 4 operators total, one per line plus a floater.

Each inspection takes about 12 seconds. The current defect detection rate is about 94%. False positive rate is about 3% — meaning 3% of good discs are sent to rework.

When a defective disc gets through, it costs the customer about €45 in warranty claims. They have about 12 warranty claims per month related to defective discs that should have been caught in QC.

A defect is also tied to a specific production batch. The batch information includes the line number, operator, timestamp, raw material lot, and machine settings.

The customer wants to add computer vision to the inspection process. They've heard about AI but are worried about accuracy, especially for the trickier defects like hairline cracks.

They currently have no machine learning infrastructure. They do have an MES (Manufacturing Execution System) that tracks batch data, and a SCADA system for machine data. Both are on-prem.

Quality data (defect images) is stored for 90 days then archived. They have about 50,000 labeled defect images from the past 2 years, plus a much larger pool of unlabeled "good" disc images.

The plant manager is the decision maker. The quality director is the operational owner. The IT manager is concerned about edge deployment and network connectivity.

They have budget of about €200K for this project. Timeline is "as soon as possible" but they want to see a POC within 8 weeks.

Compliance: ISO 9001, IATF 16949 (automotive quality), and they're exploring AI Act EU 2026 implications since they're a supplier to EU OEMs.
