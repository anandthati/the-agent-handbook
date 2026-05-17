
---
![Agent Orchestration Styles](Agent%20Orchestration%20styles.jpg)

## 1. Centralized Orchestration (Supervisor Pattern)

In this pattern, all communication and state management are routed through a single, dominant controller agent.

* **Communication Flow:** Hub-and-spoke model. The **Master/Supervisor Agent** receives the user input, analyzes the task using its decision logic, and delegates specific jobs to sub-agents (e.g., Coder, Tester, Researcher). Sub-agents *never* talk to each other; they only report their status and results back to the Supervisor.
* **Memory Management:** **Centralized / Shared Memory**. The Master Agent acts as the single source of truth and memory manager. It maintains the global state and context history, deciding exactly what portion of that state or RAG context to pass down to a sub-agent when triggering a task.

---

## 2. Decentralized Orchestration (Choreography Pattern)

This pattern eliminates the central leader entirely. Agents operate as equal peers in a collaborative network.

* **Communication Flow:** Event-driven or point-to-point negotiation. Agents broadcast events or message peer agents directly when they finish a step or require assistance. For example, Agent A might broadcast an event that Agent B listens for, consumes, processes, and hands off to Agent C.
* **Memory Management:** **Isolated / Local Memory**. There is no global state. Each peer agent maintains its own isolated local memory and internal context. Information is shared strictly via message payloads during direct peer negotiations or event broadcasts.

---

## 3. Federated Orchestration (Autonomous Nodes)

Federation brings together distinct, independent agent systems—often managed by different teams, domains, or organizations—under a loosely coupled governance contract.

* **Communication Flow:** Boundary-guarded request/response. Each "Federated Agent" is actually an enclosed cell containing its own local specialist agents. A high-level **Shared Agent Manager** acts as a gateway, passing high-level requests to a federated cell and receiving a structured response once the cell completes the task internally.
* **Memory Management:** **Segmented / Restricted Memory**. Each federated unit has its own private Local Memory and Local Knowledge Base. They do not share their internal thoughts or raw data. They only expose a tiny, heavily sanitized slice of data to a limited Shared Memory space or via the final API response to protect data boundaries.

---

## 4. Hierarchical Orchestration (Tiered Pattern)

This architecture scales the supervisor pattern by nesting agent teams into multi-layered organizational trees.

* **Communication Flow:** Top-down vertical tree. **Level 1** features a Master Orchestrator that breaks a massive problem into large components and assigns them to **Level 2 Supervisor Agents**. These mid-level supervisors further break down the tasks and direct their respective **Worker Agents** (e.g., a Tech Lead Supervisor managing a Coder Worker and a Tester Worker). Communication moves strictly up and down the localized branch.
* **Memory Management:** **Scoped / Tiered Memory**. This uses a multi-layered memory scope:
* **Global State / Memory:** Fully accessible only by the top-level Master Orchestrator.
* **Group / Branch Memory:** Mid-level supervisors share a limited context window relevant only to their specific pod's goals.
* **Worker Memory:** Isolated local context for individual task execution.
