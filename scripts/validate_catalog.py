#!/usr/bin/env python3
"""Public metadata-only catalog gate; stdlib only, no network."""
import json
import re
import sys
from pathlib import Path

SCHEMA = "rafaelia.public-feature-catalog/v1"
ALLOWED_REPOS = {
    "rafaelmeloreisnovo/RafGitTools",
    "rafaelmeloreisnovo/catalogos",
    "rafaelmeloreisnovo/conhecimentos",
}
STATES = {"USER_REPORTED", "SOURCE_PROPOSAL", "SOURCE_OBSERVED", "CI_SCOPED",
          "DEVICE_SELF_REPORTED", "TOKEN_VAZIO"}
DEVICE_STATES = {"TOKEN_VAZIO", "DEVICE_SELF_REPORTED", "INDEPENDENT_ATTESTED"}
KEYS = {"feature_id", "producer_repo", "source_ref", "state",
        "device_evidence_state", "description", "evidence_refs", "claim_allowed"}
SENSITIVE = re.compile(r"(?i)(github_pat_|ghp_|gho_|ghu_|ghs_|ghr_|"
                       r"bearer\\s+|authorization\\s*:|"
                       r"-----begin [a-z ]*private key-----|"
                       r"[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,})")
ID = re.compile(r"^rafgittools\\.[a-z][a-z0-9.-]{2,90}$")


class InvalidCatalog(ValueError):
    pass


def unique_object_pairs(pairs):
    value = {}
    for key, val in pairs:
        if key in value:
            raise InvalidCatalog("duplicate_json_key")
        value[key] = val
    return value


def validate(data):
    if type(data) is not dict or set(data) != {"schema", "features"}:
        raise InvalidCatalog("invalid_document_shape")
    if data["schema"] != SCHEMA:
        raise InvalidCatalog("schema_mismatch")
    records = data["features"]
    if type(records) is not list or not (1 <= len(records) <= 1000):
        raise InvalidCatalog("feature_list_invalid")
    seen = set()
    for entry in records:
        if type(entry) is not dict or set(entry) != KEYS:
            raise InvalidCatalog("feature_shape_invalid")
        fid = entry["feature_id"]
        if type(fid) is not str or not ID.fullmatch(fid) or fid in seen:
            raise InvalidCatalog("feature_id_invalid_or_duplicate")
        seen.add(fid)
        repo = entry["producer_repo"]
        if repo not in ALLOWED_REPOS:
            raise InvalidCatalog("unknown_or_private_producer")
        ref = entry["source_ref"]
        if type(ref) is not str or not (
            ref == "https://github.com/" + repo or
            ref.startswith("https://github.com/" + repo + "/")
        ) or len(ref) > 350 or ".." in ref:
            raise InvalidCatalog("source_ref_invalid")
        if entry["state"] not in STATES or entry["device_evidence_state"] not in DEVICE_STATES:
            raise InvalidCatalog("state_invalid")
        if entry["claim_allowed"] is not False:
            raise InvalidCatalog("claim_inflation")
        desc = entry["description"]
        if type(desc) is not str or not (10 <= len(desc) <= 300):
            raise InvalidCatalog("description_invalid")
        refs = entry["evidence_refs"]
        if type(refs) is not list or len(refs) > 8 or any(
            type(r) is not str or len(r) > 350 or not r.startswith("https://github.com/")
            or not any(r.startswith("https://github.com/" + allowed + "/") for allowed in ALLOWED_REPOS)
            for r in refs
        ):
            raise InvalidCatalog("evidence_refs_not_public_allowlisted")
    serialized = json.dumps(data, ensure_ascii=False)
    if SENSITIVE.search(serialized):
        raise InvalidCatalog("private_or_secret_pattern")
    if len(serialized.encode("utf8")) > 120000:
        raise InvalidCatalog("catalog_oversize")
    return len(seen)


def validate_file(path):
    raw = Path(path).read_text(encoding="utf-8")
    return validate(json.loads(raw, object_pairs_hook=unique_object_pairs))


if __name__ == "__main__":
    paths = [Path(p) for p in sys.argv[1:]] or sorted(Path("catalog").glob("*.json"))
    if not paths:
        sys.exit("FAIL no catalog files")
    try:
        total = sum(validate_file(path) for path in paths)
    except (ValueError, OSError) as exc:
        sys.exit("FAIL catalog: " + str(exc))
    print(f"PASS_SCOPED public_catalog_files={len(paths)} features={total}; DEVICE_E2E=NOT_RUN")
