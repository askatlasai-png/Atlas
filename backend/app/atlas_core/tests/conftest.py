# tests/conftest.py
import os, importlib, pytest

@pytest.fixture(autouse=True)
def _isolate_env_and_state(monkeypatch):
    # snapshot env
    snapshot = dict(os.environ)

    # sane defaults per test (tests can override)
    monkeypatch.setenv("ATLAS_DEBUG", "1")
    monkeypatch.setenv("ATLAS_ROUTER_MODE", "OPENAI_ONLY")
    monkeypatch.delenv("ATLAS_TAU_LOCAL", raising=False)

    yield

    # restore env
    os.environ.clear(); os.environ.update(snapshot)

    # reload modules that cache singletons/config
    for mod in (
        "atlas_core.atlas_query_router",
        "atlas_core.atlas_service",
        "atlas_core.atlas_api",
    ):
        if mod in list(globals()) or True:
            try: importlib.reload(importlib.import_module(mod))
            except Exception: pass
