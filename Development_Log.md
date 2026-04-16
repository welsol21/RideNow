# Development Log

This log records the use of tools, prompts, changes, outputs, and lessons learned during the development of the Assignment 2 submission.

## Log Table

| No. | Date | Task | Tool Used | Prompt (summary or snippet) | Changes made | Output quality (your observation) | What you learned |
|---|---|---|---|---|---|---|---|
| 1 | 2026-04-16 | Create the initial architecture document | ChatGPT (GPT-5.4 Thinking) | "Design a client-oriented architecture for RideNow using bounded contexts, hexagonal architecture, notifications, eventual consistency, routing, timing rules, and node-level configuration." | Produced the first full draft of the **RideNow Ride-Hailing Platform Architecture Proposal** in markdown. Defined the client-oriented principle, identified the main service-nodes, described responsibilities and owned data, and outlined happy/failure paths. | Strong initial output. The structure was coherent and aligned well with the assignment topic, but some service boundaries still needed refinement. | A strong first draft is useful for shaping the overall architecture, but bounded-context boundaries often need iteration. |
| 2 | 2026-04-16 | Refine the customer-facing coordination model | ChatGPT (GPT-5.4 Thinking) | "Clarify the role of the Broker so that customer actions enter through one main coordination point and customer-relevant updates return through the same point." | Strengthened the role of the Broker as the single customer-facing coordination service. Reduced ambiguity about which internal services communicate directly with the customer. | Improved clarity significantly. The architecture became easier to explain and more client-oriented. | In a client-oriented design, one main coordination service improves usability and simplifies the external model. |
| 3 | 2026-04-16 | Remove unnecessary service complexity | ChatGPT (GPT-5.4 Thinking) | "Reassess whether a separate Support node is really necessary given the Broker-centric model." | Removed the Support Node from the architecture and reassigned issue/complaint handling to a flow involving Broker plus the relevant domain services such as Payment and Tracking. | Better than the previous version. The architecture became leaner and more defensible. | Not every possible bounded context needs to become a separate service. Simplicity improves the quality of the proposal. |
| 4 | 2026-04-16 | Add routing as a first-class capability | ChatGPT (GPT-5.4 Thinking) | "Introduce a Route node that links the driver location, pickup point, and drop-off point and selects the fastest route." | Added the Route Node as a dedicated bounded capability. Extended the model to include route selection, ETA, distance estimation, and route recalculation. | Strong improvement. The platform became more realistic and mathematically grounded. | Routing is not a minor helper function in a ride-hailing system; it is a core capability with its own logic and state. |
| 5 | 2026-04-16 | Add temporal and operational policy handling | ChatGPT (GPT-5.4 Thinking) | "Make timeouts, intervals, and thresholds part of the architecture and externalise them into node-level configuration." | Added a temporal model, driver location update policy, and node-level externalised configuration for timing windows, retries, and thresholds. Chose node-level configuration rather than a separate Policy Node. | Strong and practical. The proposal became more operationally realistic. | Architectural quality is improved when operational constants are treated as configuration rather than hard-coded logic. |
| 6 | 2026-04-16 | Integrate ROS 2-inspired communication ideas carefully | ChatGPT (GPT-5.4 Thinking) | "Explain that the system is formally microservices, but consciously borrows selected ROS 2 communication ideas to strengthen node boundaries and data-driven behaviour." | Updated the introduction and architectural style to explain that the platform remains a microservice system while using a graph-of-service-nodes perspective inspired by ROS 2 communication concepts. | Strong final framing. It preserved the language of the module while showing a more advanced design influence. | Borrowing ideas from another architectural tradition works best when it strengthens the model without displacing the main vocabulary expected by the assignment. |
| 7 | 2026-04-16 | Produce the final architecture proposal document | ChatGPT (GPT-5.4 Thinking) | "Generate a clean markdown document titled 'RideNow Ride-Hailing Platform Architecture Proposal' without author remarks or process commentary." | Produced the cleaned markdown version of the architecture proposal, including introduction, architectural style, node catalogue, graph model, hexagonal structure, timing model, events, flows, deployment, and testing strategy. | High quality final output. Clean, coherent, and ready to include in the submission pack. | Final presentation quality matters. Removing process commentary makes the document more academic and submission-ready. |

## First Document Produced

1. **RideNow Ride-Hailing Platform Architecture Proposal**

Current file:
- `RideNow_Ride-Hailing_Platform_Architecture_Proposal.md`

## Notes

This development log is intended to record:
- the task carried out,
- the tool used,
- the prompt or prompt summary,
- the changes made,
- the observed quality of the output,
- and the lesson learned from the iteration.

Additional rows can be added as more documents are created.
