"""BDD & Contract Tests for CKPA-46 (CRM-G1-SUB01): Isolated Test Env & 4-Role IAM."""

import pytest
from fastapi.testclient import TestClient

from src.config import Settings, settings
from src.main import app
from src.modules.identity.router import service as identity_service
from src.modules.identity.service import SSO_ASSERTION_PREFIX
from src.shared.auth import (
    G1_NAMED_USERS_DIRECTORY,
    SECTION2_CORE_SYSTEM_ROLES,
    AuthenticatedUser,
    create_access_token,
    ensure_partition_access,
    validate_compatible_roles,
    verify_access_token,
)
from src.shared.enums import EvalPartition, UserRole
from src.shared.exceptions import AccessDenied


def test_g1_sub01_sec06_dev_test_isolated_from_prod_and_sec04_training_locked() -> None:
    """Given DEL01-F & DEL 06, verify Dev/Test is 100% isolated from Prod & SEC 04 locked."""
    report = settings.verify_sec06_test_prod_isolation()
    assert report["isolated_from_production"] is True
    assert report["isolation_layers"] == {
        "vpc": True,
        "db": True,
        "storage": True,
        "keys": True,
    }
    assert report["llm_allow_training"] is False
    assert report["llm_zero_data_retention"] is True
    assert report["llm_telemetry_enabled"] is False
    assert report["pilot_max_named_users"] == 20
    assert report["pilot_max_concurrent_sessions"] == 5

    # SEC 06: VPC network pointing to prod or Storage pointing to prod must fail closed.
    bad_vpc = Settings(ISOLATED_VPC_NETWORK="songnhat-prod-vpc")
    with pytest.raises(ValueError, match="SEC 06 violation"):
        bad_vpc.verify_sec06_test_prod_isolation()

    bad_storage = Settings(IMPORT_OUTPUT_DIR="s3://songnhat-prod/exports")
    with pytest.raises(ValueError, match="SEC 06 violation"):
        bad_storage.verify_sec06_test_prod_isolation()

    # SEC 04: enabling model training or disabling ZDR must fail closed.
    bad_training = Settings(LLM_ALLOW_TRAINING=True)
    with pytest.raises(ValueError, match="SEC 04 violation"):
        bad_training.verify_sec06_test_prod_isolation()

    bad_zdr = Settings(LLM_ZERO_DATA_RETENTION=False)
    with pytest.raises(ValueError, match="SEC 04 violation"):
        bad_zdr.verify_sec06_test_prod_isolation()

    # SEC 06: Test/Dev pointing to a production database host must fail closed.
    leaked_prod_db = Settings(
        APP_ENV="test",
        DATABASE_URL="postgresql+asyncpg://u:p@prod-db.songnhat.vn:5432/prod",
    )
    with pytest.raises(ValueError, match="SEC 06 violation"):
        leaked_prod_db.verify_sec06_test_prod_isolation()

    # SEC 06: Production using default/weak secret or dev/test DB must fail closed.
    weak_prod_secret = Settings(
        APP_ENV="production",
        APP_SECRET_KEY="change-me-in-production",
        DATABASE_URL="postgresql+asyncpg://u:strong@db.internal:5432/ckpa_prod",
    )
    with pytest.raises(ValueError, match="SEC 06 violation"):
        weak_prod_secret.verify_sec06_test_prod_isolation()

    prod_on_dev_db = Settings(
        APP_ENV="production",
        APP_SECRET_KEY="prod-super-strong-secret-key-2026",
        DATABASE_URL="postgresql+asyncpg://ckpa:ckpa_pass@localhost:5432/ckpa_db",
    )
    with pytest.raises(ValueError, match="SEC 06 violation"):
        prod_on_dev_db.verify_sec06_test_prod_isolation()

    # SEC 06: Cross-environment token reuse (token minted for 'production' used in 'test') fails.
    admin_user = G1_NAMED_USERS_DIRECTORY["s5-ngoc-duy"]
    prod_token = create_access_token(admin_user, app_env="production")
    with pytest.raises(Exception) as exc_info:
        verify_access_token(prod_token)
    assert "SEC 06 environment boundary violation" in str(exc_info.value)


def test_g1_sub01_sec01_four_core_roles_and_20_named_users_directory() -> None:
    """Verify 4 RFP Section 2 core roles across 20 named users and RULE-11-04/05 SoD rules."""
    assert SECTION2_CORE_SYSTEM_ROLES == frozenset(
        {
            UserRole.READER,
            UserRole.POLICY_OWNER,
            UserRole.STEWARD,
            UserRole.ADMINISTRATOR,
        }
    )
    assert len(G1_NAMED_USERS_DIRECTORY) == 20
    assert len(G1_NAMED_USERS_DIRECTORY) == settings.PILOT_MAX_NAMED_USERS

    # Every one of the 4 core roles is represented in the 20 named users directory.
    present_core_roles = {
        role
        for user in G1_NAMED_USERS_DIRECTORY.values()
        for role in user.roles
        if role in SECTION2_CORE_SYSTEM_ROLES
    }
    assert present_core_roles == SECTION2_CORE_SYSTEM_ROLES

    # Every named user in the G1 directory passes RULE-11-04/05 role compatibility.
    for user in G1_NAMED_USERS_DIRECTORY.values():
        assert validate_compatible_roles(user.roles) is True

    # RULE-11-05 SoD: Independent evaluator (S4) cannot combine with Steward or Policy Owner.
    assert (
        validate_compatible_roles(
            frozenset({UserRole.INDEPENDENT_EVALUATOR, UserRole.STEWARD})
        )
        is False
    )
    sod_violating_user = AuthenticatedUser(
        user_id="bad-sod",
        email="bad@songnhat.vn",
        roles=frozenset({UserRole.INDEPENDENT_EVALUATOR, UserRole.POLICY_OWNER}),
    )
    with pytest.raises(ValueError, match="RULE-11-04/05"):
        create_access_token(sod_violating_user)


def test_g1_sub01_bdd_iam_four_roles_session_cap_and_sec08_audit_log() -> None:
    """When S5 configures Test infra & 4-role IAM, Then 4 role groups work with SEC 08 audit."""
    identity_service.reset_sessions()
    client = TestClient(app)

    # 1. Invalid SSO assertion fails closed (401) and logs a SEC 08 audit event.
    bad_res = client.post("/api/v1/identity/token", json={"id_token": "invalid-assertion-token"})
    assert bad_res.status_code == 401

    # 2. Authenticate 4 distinct named users covering the 4 core roles (SYS-01..SYS-04):
    #    - SYS-01 reader: p4-tra-my
    #    - SYS-02 policy_owner: p2-huu-tai
    #    - SYS-03 steward: p3-chi-kha
    #    - SYS-04 administrator: s5-ngoc-duy
    four_role_users = [
        ("p4-tra-my", UserRole.READER),
        ("p2-huu-tai", UserRole.POLICY_OWNER),
        ("p3-chi-kha", UserRole.STEWARD),
        ("s5-ngoc-duy", UserRole.ADMINISTRATOR),
    ]
    tokens: dict[str, str] = {}
    for uid, expected_role in four_role_users:
        tok_res = client.post(
            "/api/v1/identity/token",
            json={"id_token": f"{SSO_ASSERTION_PREFIX}{uid}"},
        )
        assert tok_res.status_code == 200
        access_token = tok_res.json()["access_token"]
        tokens[uid] = access_token

        me_res = client.get(
            "/api/v1/identity/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_res.status_code == 200
        assert expected_role.value in me_res.json()["roles"]

    # 3. Verify least-privilege RBAC across endpoints:
    #    - reader (p4-tra-my) is forbidden (403) from /api/v1/identity/iam-status and /admin
    reader_headers = {"Authorization": f"Bearer {tokens['p4-tra-my']}"}
    assert client.get("/api/v1/identity/iam-status", headers=reader_headers).status_code == 403
    assert client.get("/api/v1/admin/ops-summary", headers=reader_headers).status_code == 403

    #    - reader audience check succeeds for 'sales', fails for 'steward'
    aud_ok = client.post(
        "/api/v1/identity/check-permission",
        json={"required_audiences": ["sales"]},
        headers=reader_headers,
    )
    assert aud_ok.status_code == 200 and aud_ok.json()["allowed"] is True
    aud_deny = client.post(
        "/api/v1/identity/check-permission",
        json={"required_audiences": ["steward"]},
        headers=reader_headers,
    )
    assert aud_deny.status_code == 200 and aud_deny.json()["allowed"] is False

    #    - steward (p3-chi-kha) and policy_owner (p2-huu-tai) can access /api/v1/admin/ops-summary
    steward_headers = {"Authorization": f"Bearer {tokens['p3-chi-kha']}"}
    owner_headers = {"Authorization": f"Bearer {tokens['p2-huu-tai']}"}
    assert client.get("/api/v1/admin/ops-summary", headers=steward_headers).status_code == 200
    assert client.get("/api/v1/admin/ops-summary", headers=owner_headers).status_code == 200

    #    - administrator (s5-ngoc-duy) can access /api/v1/identity/iam-status
    admin_headers = {"Authorization": f"Bearer {tokens['s5-ngoc-duy']}"}
    iam_res = client.get("/api/v1/identity/iam-status", headers=admin_headers)
    assert iam_res.status_code == 200
    iam_body = iam_res.json()
    assert iam_body["isolated_from_production"] is True
    assert iam_body["isolation_layers"] == {
        "vpc": True,
        "db": True,
        "storage": True,
        "keys": True,
    }
    assert iam_body["llm_allow_training"] is False
    assert iam_body["llm_zero_data_retention"] is True
    assert iam_body["named_users_count"] == 20
    assert iam_body["max_named_users"] == 20
    assert iam_body["active_sessions_count"] == 4
    assert iam_body["max_concurrent_sessions"] == 5
    assert set(iam_body["core_system_roles"]) == {
        "reader",
        "policy_owner",
        "steward",
        "administrator",
    }

    # 4. Enforce 5 concurrent sessions limit (RFP Section 2):
    #    5th session (p5-anh-khoa) succeeds; 6th session (p4-staff-sales-01) is blocked (429).
    fifth_res = client.post(
        "/api/v1/identity/token",
        json={"id_token": f"{SSO_ASSERTION_PREFIX}p5-anh-khoa"},
    )
    assert fifth_res.status_code == 200

    sixth_res = client.post(
        "/api/v1/identity/token",
        json={"id_token": f"{SSO_ASSERTION_PREFIX}p4-staff-sales-01"},
    )
    assert sixth_res.status_code == 429

    # Release one session and verify the next user can now authenticate.
    identity_service.release_session("p4-tra-my")
    retry_sixth = client.post(
        "/api/v1/identity/token",
        json={"id_token": f"{SSO_ASSERTION_PREFIX}p4-staff-sales-01"},
    )
    assert retry_sixth.status_code == 200

    # 5. Verify SEC 08 audit log events were recorded for all actions.
    audit_events = identity_service.get_recent_audit_events()
    recorded_actions = {str(e["action"]) for e in audit_events}
    assert "iam.token_exchange" in recorded_actions
    assert "iam.get_profile" in recorded_actions
    assert "iam.check_audience" in recorded_actions
    assert "sec08.verify_iam_and_env_isolation" in recorded_actions
    assert "iam.concurrent_session_check" in recorded_actions


def test_g1_sub01_logout_releases_session_slot_and_sealed100_denies_admin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify logout frees a slot, prod blocks static prefix, and SEALED_100 denies admin."""
    identity_service.reset_sessions()
    with TestClient(app) as client:
        # Fill all 5 concurrent session slots
        slot_users = [
            "p4-tra-my",
            "p2-huu-tai",
            "p3-chi-kha",
            "s5-ngoc-duy",
            "p5-anh-khoa",
        ]
        tokens: dict[str, str] = {}
        for uid in slot_users:
            res = client.post(
                "/api/v1/identity/token",
                json={"id_token": f"{SSO_ASSERTION_PREFIX}{uid}"},
            )
            assert res.status_code == 200
            tokens[uid] = res.json()["access_token"]

        # 6th user is rejected while 5 slots are active
        blocked = client.post(
            "/api/v1/identity/token",
            json={"id_token": f"{SSO_ASSERTION_PREFIX}p4-staff-sales-01"},
        )
        assert blocked.status_code == 429

        # Logout via API releases the slot and logs SEC 08 audit event
        logout_res = client.post(
            "/api/v1/identity/logout",
            headers={"Authorization": f"Bearer {tokens['p4-tra-my']}"},
        )
        assert logout_res.status_code == 200
        assert logout_res.json()["status"] == "logged_out"

        # 6th user can now authenticate
        admitted = client.post(
            "/api/v1/identity/token",
            json={"id_token": f"{SSO_ASSERTION_PREFIX}p4-staff-sales-01"},
        )
        assert admitted.status_code == 200
        assert any(
            e["action"] == "iam.logout" for e in identity_service.get_recent_audit_events()
        )

    # Static G1 SSO prefix is rejected in production (401)
    monkeypatch.setattr(settings, "APP_ENV", "production")
    monkeypatch.setattr(settings, "APP_SECRET_KEY", "prod-super-strong-secret-key-2026")
    monkeypatch.setattr(
        settings,
        "DATABASE_URL",
        "postgresql+asyncpg://u:strong@db.internal:5432/ckpa_prod",
    )
    with pytest.raises(Exception) as exc_info:
        identity_service.exchange_token(f"{SSO_ASSERTION_PREFIX}s5-ngoc-duy")
    assert "Static G1 SSO assertion prefix is forbidden in production." in str(exc_info.value)

    # Chinese Wall: SEALED_100 strictly denies ADMINISTRATOR and allows INDEPENDENT_EVALUATOR
    admin_user = G1_NAMED_USERS_DIRECTORY["s5-ngoc-duy"]
    evaluator_user = G1_NAMED_USERS_DIRECTORY["s4-quy-hai"]
    with pytest.raises(AccessDenied):
        ensure_partition_access(admin_user, EvalPartition.SEALED_100)
    ensure_partition_access(evaluator_user, EvalPartition.SEALED_100)
