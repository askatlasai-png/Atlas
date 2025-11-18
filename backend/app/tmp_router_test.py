from atlas_core.atlas_query_router import _parse_sort, _plan_operational
print("parse_sort:", _parse_sort("sorted by available descending"))
p = {"filters":[{"col":"site_id","op":"eq","value":"101"}]}
plan = _plan_operational(p, "Show items at site 101 sorted by available descending")
print("plan intent:", plan.intent)
print("steps:", [ (s.op, s.source, s.params) for s in plan.steps ])
