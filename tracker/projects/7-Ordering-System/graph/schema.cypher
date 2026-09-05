// Constraints/indexes for Phase 8's knowledge graph (02-ARCHITECTURE.md
// Section 5). Two separate graphs, sharing one Neo4j instance:
//
// 5.1 Entity relationship graph (the cross-system join problem, made a
// real graph traversal instead of manual application-code joins):
//   (:Customer)-[:PLACED]->(:Order)-[:REQUIRES]->(:Circuit)-[:ASSIGNED_TO]->(:Address)
//   (:Order)-[:HAS_STATUS]->(:ProvisioningState)
//
// 5.2 GraphRAG knowledge base (documented cause/resolution/incident
// relationships that plain vector search can't express):
//   (:ErrorCode)-[:CAUSED_BY]->(:Cause)-[:RESOLVED_BY]->(:Resolution)
//   (:ErrorCode)-[:RELATED_INCIDENT]->(:Incident)
//
// 04-BUILD-PLAN.md's Phase 8 spec names 5 node types for constraints
// (Customer, Order, Circuit, Address, ErrorCode) -- ProvisioningState,
// Cause, Resolution, and Incident are added here too since they're the
// actual endpoints of "the relationships from Section 5.1/5.2" that same
// spec also asks for -- a relationship needs both its endpoint types
// constrained to be meaningful, not just the 5 explicitly named nodes.

// --- Entity relationship graph (5.1) ---

CREATE CONSTRAINT customer_id_unique IF NOT EXISTS
FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE;

CREATE CONSTRAINT order_id_unique IF NOT EXISTS
FOR (o:Order) REQUIRE o.order_id IS UNIQUE;

CREATE CONSTRAINT circuit_id_unique IF NOT EXISTS
FOR (c:Circuit) REQUIRE c.circuit_id IS UNIQUE;

CREATE CONSTRAINT address_unique IF NOT EXISTS
FOR (a:Address) REQUIRE a.full_address IS UNIQUE;

// One ProvisioningState per order -- keyed by order_id (not its own
// generated ID) since it's a 1:1 attribute-of-Order relationship, not an
// independently-identified entity.
CREATE CONSTRAINT provisioning_state_order_unique IF NOT EXISTS
FOR (p:ProvisioningState) REQUIRE p.order_id IS UNIQUE;

// --- GraphRAG knowledge base (5.2) ---

CREATE CONSTRAINT error_code_unique IF NOT EXISTS
FOR (e:ErrorCode) REQUIRE e.code IS UNIQUE;

CREATE CONSTRAINT incident_ticket_unique IF NOT EXISTS
FOR (i:Incident) REQUIRE i.ticket_id IS UNIQUE;

// Cause/Resolution nodes don't have a natural external unique key (they're
// free-text descriptions, not identifiers) -- an index (not a uniqueness
// constraint) still speeds up any future lookup by description text.
CREATE INDEX cause_description_idx IF NOT EXISTS
FOR (c:Cause) ON (c.description);

CREATE INDEX resolution_description_idx IF NOT EXISTS
FOR (r:Resolution) ON (r.description);
