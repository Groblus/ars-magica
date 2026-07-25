"""Serialization contracts for the Phase 1 Pydantic models."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ars_magica.models import (
    AdvancementEvent,
    ArtifactSpec,
    AudioAsset,
    CharacterState,
    CovenantState,
    MagusState,
    MapLayer,
    MapSpec,
    Person,
    PrintPreset,
    Relationship,
    Secret,
    SourceReference,
    SpellKnowledge,
    VisualAsset,
    Visibility,
)


class ModelRoundTripTests(unittest.TestCase):
    def test_magus_round_trip_preserves_catalog_links_and_state(self) -> None:
        magus = MagusState(
            id="character.ada",
            name="Ada of Bonisagus",
            house="Bonisagus",
            arts=[{"art_id": "art.creo", "score": 8, "experience": 52}],
            abilities=[{"ability_id": "ability.magic_theory", "score": 5, "experience": 75}],
            known_spells=[SpellKnowledge(spell_id="spell.pilum_of_fire", mastery_score=1)],
            source_refs=[SourceReference(id="source.core.magic", title="Definitive Edition", locator="Hermetic Magic")],
            visibility=Visibility.PLAYER,
        )

        restored = MagusState.model_validate_json(magus.model_dump_json())
        self.assertEqual(restored, magus)
        self.assertEqual(restored.arts[0].art_id, "art.creo")
        self.assertEqual(restored.source_refs[0].locator, "Hermetic Magic")

    def test_covenant_and_advancement_round_trip(self) -> None:
        covenant = CovenantState(
            id="covenant.durenmar",
            name="Durenmar",
            members=["character.ada"],
            laboratories=[{"id": "laboratory.ada", "name": "Ada's laboratory", "owner_id": "character.ada"}],
        )
        advancement = AdvancementEvent(
            id="advancement.ada.1220.spring",
            character_id="character.ada",
            season_id="season.1220.spring",
            activity="study",
            art_id="art.creo",
            experience_awarded=10,
        )

        self.assertEqual(CovenantState.model_validate(covenant.model_dump()), covenant)
        self.assertEqual(AdvancementEvent.model_validate_json(advancement.model_dump_json()), advancement)

    def test_saga_records_round_trip_with_storyguide_secrets(self) -> None:
        person = Person(id="person.ada", name="Ada", roles=["maga"])
        relationship = Relationship(
            id="relationship.ada.covenant",
            source_entity_id=person.id,
            target_entity_id="covenant.durenmar",
            relationship_type="member_of",
            strength=4,
        )
        secret = Secret(id="secret.ada", name="Hidden debt", details="Ada owes a favor to a faerie.")

        self.assertEqual(Person.model_validate_json(person.model_dump_json()), person)
        self.assertEqual(Relationship.model_validate_json(relationship.model_dump_json()), relationship)
        self.assertEqual(secret.visibility, Visibility.STORYGUIDE)
        self.assertEqual(Secret.model_validate(secret.model_dump()), secret)

    def test_publishing_and_media_round_trip(self) -> None:
        preset = PrintPreset(id="preset.home_a4", name="Home A4", page_size="A4")
        artifact = ArtifactSpec(
            id="artifact.ada.sheet",
            template_id="character-sheet",
            title="Ada character sheet",
            content_ids=["character.ada"],
            print_preset_id=preset.id,
        )
        map_spec = MapSpec(
            id="map.rhine.player",
            title="Rhine Tribunal",
            map_kind="regional",
            layers=[MapLayer(id="layer.covenants", name="Covenants")],
        )
        portrait = VisualAsset(id="asset.ada.portrait", title="Ada portrait", uri="assets/ada.png", entity_id="person.ada")
        ambience = AudioAsset(id="asset.durenmar.ambience", title="Durenmar dawn", uri="assets/dawn.ogg")

        self.assertEqual(ArtifactSpec.model_validate_json(artifact.model_dump_json()), artifact)
        self.assertEqual(MapSpec.model_validate_json(map_spec.model_dump_json()), map_spec)
        self.assertEqual(VisualAsset.model_validate_json(portrait.model_dump_json()), portrait)
        self.assertEqual(AudioAsset.model_validate_json(ambience.model_dump_json()), ambience)

    def test_artifact_accepts_compact_publishing_aliases(self) -> None:
        artifact = ArtifactSpec.model_validate(
            {
                "id": "artifact.ada.cards",
                "title": "Ada spell cards",
                "template": "spell-card-deck",
                "theme": "clear-ledger",
                "preset": "poker-cards",
                "content": {"cards": []},
            }
        )

        self.assertEqual(artifact.template_id, "spell-card-deck")
        self.assertEqual(artifact.style_profile_id, "clear-ledger")
        self.assertEqual(artifact.print_preset_id, "poker-cards")
        self.assertEqual(artifact.data, {"cards": []})
        self.assertEqual(artifact.model_dump(by_alias=True)["content"], {"cards": []})


if __name__ == "__main__":
    unittest.main()
