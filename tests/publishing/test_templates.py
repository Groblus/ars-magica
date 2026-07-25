from ars_magica.publishing import inspect_template_requirements, list_templates


def test_all_expected_templates_are_discoverable():
    template_ids = {item["id"] for item in list_templates()}
    assert template_ids == {
        "magus-character-sheet",
        "companion-grog-sheet",
        "spell-card-deck",
        "condensed-npc-card",
        "storyguide-session-packet",
    }


def test_spell_cards_declare_separate_artwork_policy():
    requirements = inspect_template_requirements("spell-card-deck")
    assert requirements["version"] == "1.0.0"
    assert "artwork" in requirements["asset_policy"].lower()
