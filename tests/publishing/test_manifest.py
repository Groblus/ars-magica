from ars_magica.models import ArtifactSpec, SourceReference
from ars_magica.publishing import (
    SourceReferenceError,
    build_attribution,
    build_manifest,
    package_material,
    render_html,
)
import zipfile


SPEC = {
    "title": "A Test Magus",
    "template": "magus-character-sheet",
    "theme": "clear-ledger",
    "preset": "home-a4",
    "content": {
        "identity": {"name": "Aelia", "house": "Bonisagus"},
        "characteristics": {"Int": 3, "Per": 0, "Pre": -1, "Com": 1, "Str": -2},
        "arts": [],
        "abilities": [],
    },
    "assets": [
        {
            "id": "art:aelia",
            "kind": "artwork",
            "creator": "Example artist",
            "license": "CC-BY-4.0",
            "source": "https://example.invalid/aelia",
            "modified": True,
        }
    ],
}


def test_manifest_is_deterministic_for_identical_inputs():
    assert build_manifest(SPEC) == build_manifest(dict(SPEC))


def test_attribution_keeps_assets_out_of_rules_content():
    attribution = build_attribution(SPEC)
    assert attribution["entries"][0]["id"] == "art:aelia"
    assert "Example artist" in attribution["markdown"]


def test_phase_one_artifact_spec_renders_without_translation():
    artifact = ArtifactSpec(
        id="artifact.aelia.sheet",
        title="Aelia character sheet",
        template_id="magus-character-sheet",
        style_profile_id="style.clear-ledger",
        print_preset_id="preset.home_a4",
        data=SPEC["content"],
        source_refs=[
            SourceReference(
                id="source.core",
                title="Core Rules",
                locator="500-510",
            )
        ],
    )

    html = render_html(artifact)
    assert "Aelia" in html
    assert "Core Rules, 500-510" in html


def test_audience_filtering_removes_secret_content_assets_and_sources(tmp_path):
    spec = {
        "title": "Safe NPC card",
        "template": "condensed-npc-card",
        "theme": "clear-ledger",
        "preset": "poker-cards",
        "audience": "player",
        "content": {
            "npc": {"name": "Marcus", "description": "Public description"},
            "secret": "SECRET-CONTENT",
            "nested": [
                {"visibility": "storyguide", "value": "SECRET-NESTED"},
                {"visibility": "player", "value": "Visible nested value"},
            ],
        },
        "assets": [
            {"id": "asset.public", "creator": "Public artist"},
            {"id": "asset.secret", "visibility": "storyguide", "creator": "SECRET-ASSET"},
        ],
        "source_references": [
            "reviewed/Core.md:500-510",
            {"title": "Secret dossier", "locator": "1", "visibility": "storyguide", "notes": "SECRET-SOURCE"},
        ],
    }

    html = render_html(spec)
    package = package_material(spec, tmp_path / "player.zip")
    with zipfile.ZipFile(package) as archive:
        package_contents = "\n".join(
            archive.read(name).decode("utf-8", errors="ignore") for name in archive.namelist()
        )
    for secret in ("SECRET-CONTENT", "SECRET-NESTED", "SECRET-ASSET", "SECRET-SOURCE"):
        assert secret not in html
        assert secret not in package_contents
    assert "Visible nested value" not in html

    storyguide = dict(spec, audience="storyguide")
    storyguide_html = render_html(storyguide)
    assert "SECRET-CONTENT" in storyguide_html


def test_source_references_normalize_early_and_reject_ambiguous_inputs():
    spec = dict(SPEC, source_references=["reviewed/Core.md:500-510"])
    reference = build_manifest(spec)["source_references"][0]
    assert reference == {
        "id": reference["id"],
        "title": "Core",
        "locator": "500-510",
        "citation": "reviewed/Core.md:500-510",
        "url": None,
        "authority": "definitive",
        "notes": None,
    }

    try:
        build_manifest(dict(SPEC, source_references=["Core Rules"]))
    except SourceReferenceError as error:
        assert "precise citation" in str(error)
    else:
        raise AssertionError("ambiguous source reference was accepted")
