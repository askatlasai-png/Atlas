# 📘 Atlas Sprint — Day 2 Plan (FAISS Validation + Router Logic)

**Date:** *[today]*  
**Sprint:** 2-Week Deep Learning + Atlas Practicals  
**Day:** 2 of 14  
**Theme:** Finish FAISS validation, automate testing, start query-router logic.

---

## 🎯 Objectives
- Validate all 7 domain FAISS indexes (ONHAND done).  
- Automate QA across all indexes.  
- Lock the MVP query-router behavior.  
- Build one cross-domain “PO vs ONHAND” showcase.  
- Keep theory in sync with the 2-week learning track.

---

## 🧩 Block 1 — FAISS Coverage (2 h)
**Goal:** Verify PO, SO, IR, LPN, LPN_SERIAL, LPN_SERIALS_AGG.

**Commands**
```powershell
python tools\query_index.py --store .\rag_store\PO\faiss_index --query "purchase orders delayed past promised date" --k 8
python tools\query_index.py --store .\rag_store\SO\faiss_index --query "late deliveries by carrier" --k 8
python tools\query_index.py --store .\rag_store\IR\faiss_index --query "receipts pending or behind SLA" --k 8
python tools\query_index.py --store .\rag_store\LPN\faiss_index --query "active LPNs in transit" --k 8
python tools\query_index.py --store .\rag_store\LPN_SERIAL\faiss_index --query "serials for a given LPN" --k 8
python tools\query_index.py --store .\rag_store\LPN_SERIALS_AGG\faiss_index --query "aggregate LPN quantities by item" --k 8
```

**Success Criteria**
- Non-empty results  
- Correct metadata fields shown (`Qty`, `SLA_Flag`, `Carrier`, etc.)  
- No `UNKNOWN` or zeros in aggregates

---

## ⚙️ Block 2 — One-Click QA (1 h)
**Goal:** Create `tools/test_all_indexes.py`  
- Scans `rag_store/*/faiss_index`  
- Runs one sample query per domain  
- Prints ✔ Pass / ❌ Fail + missing metadata keys  
- Exit 1 if any fail

Run:
```powershell
python tools\test_all_indexes.py
```

---

## 🧭 Block 3 — Router Polish (1.5 h)
**Goal:** Lock rule-based intent routing for MVP.

**Rules**
| Pattern / Keyword | Domain | Retrieval Order |
|-------------------|---------|----------------|
| “ITEM-” or site/org present | ONHAND | Filter → Vector |
| “summarize”, “trend”, “issues”, “why” | Any | Vector → Filter |
| supplier/vendor | PO | Vector → Filter |
| carrier/customer | SO | Filter → Vector |
| LPN / serial | LPN | Filter → Vector |

**Deliverable:**  
`AtlasQueryRouter` class returning `{domain, retrieval_order, filters}` + log entry for audit.

---

## 🔗 Block 4 — Cross-Domain Demo (1 h)
**Goal:** Query → “Compare PO promised vs ONHAND available for ITEM-00004.”

Flow:
- Router: PO + ONHAND  
- Filter → Vector per domain  
- Retrieve → Aggregate → LLM summary

---

## 📚 Block 5 — Theory (45 min)
Watch **3Blue1Brown: Gradient Descent (Ep 2)**  
Take notes on:
- How gradient descent adjusts weights  
- Parallel between training vs. retrieval fine-tuning in Atlas

---

## 🧾 Block 6 — Wrap & Log (15 min)
- Record which indexes passed QA  
- Note rebuilds needed  
- Snapshot commands for tomorrow

---

### ✅ Stretch Goals
- Add `--group Site` to ONHAND aggregation (Subinventory × Site).  
- Add `--export csv` for UI integration.  
- Create `build_all_indexes.ps1` to rebuild every domain.
