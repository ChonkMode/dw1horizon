# Digimon asset-library roadmap

## Status key

| Status | Meaning |
|---|---|
| Not started | No matching species record or named import recipe was found in the inspected repository snapshot. This is a proposed addition; it does not describe private or unmerged work. |
| in-progress | A record/recipe exists or work has begun, but the complete art and gameplay acceptance below has not been evidenced here. It may already be playable. |
| art complete | Reviewed model, texture, rig, required animations and attack effects pass the intended role's visual and resource checks; evidence is linked in the row. Gameplay integration may still be pending. |
| gameplay complete | Art is complete and the intended role passes the gameplay, balance, save/options and resource checks below; evidence is linked in the row. |

## Purpose and release boundary

This is a proposed order for building a reusable Digimon library: **Vanilla-like → Vanilla-like Megas → Adventure 02 → Tamers**. It prioritizes complete, recognizable families and useful regional inhabitants over raw species count. It is a contribution for discussion, not a promise that every entry ships in V1.0.

For V1.0, first finish and test the species already shipping: models, care and battle animations, attacks, evolution routes, balance and bugs. Select a finite accepted roster for that release. New entries below are a longer-term library backlog; missing babies or a late-series boss must not delay fixes to existing playable species. Retain the ability to release a smaller polished roster and continue the backlog afterwards.

The library should work without the beta demonstration story. A modder should be able to select a species, place an encounter or resident, and configure a raising route without inheriting that story's recruitment flags or map edits. Removing the demonstration must preserve existing save identities or have an explicit migration policy.

Within each tier, the numbered rows are the recommended queue. Complete the core families first, then nursery gaps, then the selected supporting roster; optional bosses and film variants come last. Shared animation work can batch adjacent species, but donor convenience alone should not move a later tier ahead of an earlier one. Fixes to already released content take precedence across all tiers. Names use common English/localized names, with aliases where useful.

### What the status snapshot establishes

Inventory inspected at [`614aa016570494150fc86ddd33acc88e4d816be8`](https://github.com/felixcarmona/dw1horizon/tree/614aa016570494150fc86ddd33acc88e4d816be8), 2026-11-03. Existing rows link their species record. IDs are Horizon IDs, not proposed national catalogue numbers. Do not allocate new IDs from row order.

Existing records start at **in-progress** because this is an inventory and prioritization review, not a per-species visual/gameplay sign-off. This does not revoke previous acceptance or claim every existing species is defective. The [species proof index](docs/data/species-proof.json) records a limited set of checks and is not by itself proof of all care animations, all attacks, balanced raising or every option combination. A maintainer can advance a row by linking the corresponding evidence; record an accepted native asset as reuse rather than importing it again.

For entries without an asset, investigate the existing [import pipeline](docs/reference/imported-species.md) and supported source discs first. No suitable donor is assumed. If none exists, record an authored-asset plan or a justified new-source proposal before committing to a release. A source model that fights correctly still needs DW1's eating, sleeping, toilet, training and field interactions.

## Family coverage and scope

The Adventure target covers the eight original partners from Fresh through Ultimate, their familiar original-series variants, and the Mega candidates in tier 2. It is not every cross-evolution, recolor or form introduced by later reboots. These are library coverage goals, not mandatory linear evolution trees: preserve DW1's branching raising choices. The family associations follow the [1999 Adventure cast](https://wikimon.net/Digimon_Adventure); later game/card-era Mega alternatives are listed explicitly rather than claimed as appearances in the original TV series.

| Family | Fresh → In-Training → Rookie → Champion → Ultimate | Coverage work |
|---|---|---|
| Tentomon | Pabumon → Motimon → Tentomon → Kabuterimon → MegaKabuterimon (red) | Reuse Kabuterimon; finish the promoted Tentomon and imported Ultimate; add both babies. |
| Gomamon | Pichimon → Bukamon → Gomamon → Ikkakumon → Zudomon | Finish the existing Rookie/Champion/Ultimate records; add both babies. |
| Gatomon | YukimiBotamon → Nyaromon → Salamon → Gatomon → Angewomon | Finish the three existing records; add both babies. Gatomon is a Champion. |
| Palmon | Yuramon → Tanemon → Palmon → Togemon → Lillymon | Reuse the vanilla nursery and Rookie; finish Champion/Ultimate. |
| Biyomon | Nyokimon → Yokomon → Biyomon → Birdramon → Garudamon | Reuse vanilla Rookie/Champion; finish Ultimate and add both babies. |
| Patamon | Poyomon → Tokomon → Patamon → Angemon → MagnaAngemon | Reuse the vanilla early family; finish Ultimate. |
| Agumon | Botamon → Koromon → Agumon → Greymon → MetalGreymon (Vaccine/orange) | Finish the existing orange variant. Retain native MetalGreymon (Virus) and SkullGreymon as separate branches. |
| Gabumon | Punimon → Tsunomon → Gabumon → Garurumon → WereGarurumon | Reuse native assets; WereGarurumon already exists as an original item evolution. Validate Horizon's broader route. |

Other useful Adventure inhabitants already available in vanilla, such as Leomon, Ogremon, Devimon, Whamon, Piximon, Etemon, Andromon and the Seadramon family, are reuse candidates rather than missing imports. Include them in a region's integration tests without creating duplicate asset tasks.

## 1. Vanilla-like: complete the Adventure families

The first fourteen rows close the principal Rookie/Champion/Ultimate gaps or finish their existing conversions. The next eight close the missing nursery forms. Regional inhabitants follow.

| Priority | Digimon / form | Existing asset / record | Status | Next acceptance work / reason |
|---|---|---|---|---|
| 1.01 | Tentomon | [111](content/species/111-tentomon.json) | in-progress | Promoted vanilla NPC; finish the partner care, movement and attack audit. |
| 1.02 | MegaKabuterimon (red) | [205](content/species/205-megakabuterimon.json) | in-progress | Complete Tentomon's familiar Ultimate; check horn and wing motion, hit timing and silhouette. |
| 1.03 | Gomamon | [217](content/species/217-gomamon.json) | in-progress | Complete the aquatic Rookie's care and locomotion set. |
| 1.04 | Ikkakumon | [218](content/species/218-ikkakumon.json) | in-progress | Make the large quadruped work in narrow paths, care scenes and battle ranges. |
| 1.05 | Zudomon | [219](content/species/219-zudomon.json) | in-progress | Finish hammer contacts, effects and field scale; close the core Gomamon family. |
| 1.06 | Salamon | [221](content/species/221-salamon.json) | in-progress | Complete the small quadruped's care and movement set. |
| 1.07 | Gatomon (Tailmon) | [234](content/species/234-gatomon.json) | in-progress | Champion partner despite small size; check claw contacts, tail/ring and care interactions. |
| 1.08 | Angewomon | [190](content/species/190-angewomon.json) | in-progress | Close the Gatomon family; audit wings, bow/arrow origin, recovery and care poses. |
| 1.09 | Togemon | [208](content/species/208-togemon.json) | in-progress | Fill Palmon's Champion route; verify glove contacts and movement footprint. |
| 1.10 | Lillymon | [209](content/species/209-lillymon.json) | in-progress | Close Palmon's Ultimate route; check flight height and flower-cannon origin. |
| 1.11 | Garudamon | [460](content/species/460-garudamon.json) | in-progress | Close Biyomon's Ultimate route; audit wing/body scale and aerial attack recovery. |
| 1.12 | MagnaAngemon | [206](content/species/206-magnaangemon.json) | in-progress | Close Patamon's Ultimate route; verify sword, gate effect and target/damage timing. |
| 1.13 | MetalGreymon (Vaccine/orange) | [224](content/species/224-metalgreymonvaccine.json) | in-progress | Use the existing variant; preserve the separate vanilla Virus form and audit missiles/finisher. |
| 1.14 | WereGarurumon | [62](content/species/62-weregarurumon.json) | in-progress | Already an original item evolution; validate Horizon's natural route and completed animation work. |
| 1.15 | Pabumon | No record identified | Not started | Add Tentomon's Fresh form; establish a reproducible asset recipe and care set. |
| 1.16 | Motimon | No record identified | Not started | Add Tentomon's In-Training form; connect and test the nursery route. |
| 1.17 | Pichimon | No record identified | Not started | Add Gomamon's Fresh form; establish a reproducible asset recipe and care set. |
| 1.18 | Bukamon | No record identified | Not started | Add Gomamon's In-Training form; connect and test the nursery route. |
| 1.19 | YukimiBotamon | No record identified | Not started | Add Salamon's Fresh form; establish a reproducible asset recipe and care set. |
| 1.20 | Nyaromon | No record identified | Not started | Add Salamon's In-Training form; connect and test the nursery route. |
| 1.21 | Nyokimon | No record identified | Not started | Add Biyomon's Fresh form; establish a reproducible asset recipe and care set. |
| 1.22 | Yokomon | No record identified | Not started | Add Biyomon's In-Training form; retain existing DW1 nursery routes as a separate compatibility decision. |
| 1.23 | Wizardmon | [241](content/species/241-wizardmon.json) | in-progress | High-value village/ruins ally and partner; finish staff, spell and care animations. |
| 1.24 | DemiDevimon | [236](content/species/236-demidevimon.json) | in-progress | Recognizable early enemy/partner; validate airborne locomotion and small target contacts. |
| 1.25 | Myotismon | [66](content/species/66-myotismon.json) | in-progress | Reuse the vanilla NPC; complete partner-specific coverage before adding another model. |
| 1.26 | Gotsumon | [68](content/species/68-gotsumon.json) | in-progress | Reuse the vanilla NPC as a regional resident/partner; audit raising coverage. |
| 1.27 | Pumpkinmon | [280](content/species/280-pumpkinmon.json) | in-progress | Pairs naturally with Gotsumon; check axe, head/body motion and care poses. |
| 1.28 | Gazimon | [285](content/species/285-gazimon.json) | in-progress | Useful Rookie for regional encounters and branching evolution routes. |
| 1.29 | DarkTyrannomon | [265](content/species/265-darktyrannomon.json) | in-progress | Fits forest/desert encounters and a familiar alternate Champion branch. |
| 1.30 | Gizamon | [239](content/species/239-gizamon.json) | in-progress | Early coastal enemy/partner; validate ground movement and aquatic silhouette. |
| 1.31 | Gesomon | [240](content/species/240-gesomon.json) | in-progress | Coastal Champion; check tentacle deformation, collision footprint and care interactions. |
| 1.32 | Raremon | [264](content/species/264-raremon.json) | in-progress | Industrial/swamp encounter; check low-body movement and effects. |
| 1.33 | Phantomon | [229](content/species/229-phantomon.json) | in-progress | Ruins/horror-region Ultimate; check scythe range and effect origin. |
| 1.34 | LadyDevimon | [223](content/species/223-ladydevimon.json) | in-progress | Late regional adversary/partner; audit wings, limb deformation and attack recovery. |
| 1.35 | Cherrymon | [121](content/species/121-cherrymon.json) | in-progress | Reuse the vanilla NPC; finish raising coverage and large-body navigation. |
| 1.36 | Blossomon | [274](content/species/274-blossomon.json) | in-progress | Forest Ultimate; validate tendrils and fit in field/battle/care scenes. |
| 1.37 | Floramon | [273](content/species/273-floramon.json) | in-progress | Forest Rookie and friendly resident with reusable plant-family routes. |
| 1.38 | Deramon | [286](content/species/286-deramon.json) | in-progress | Forest resident/partner; check ornate body silhouette and ground contacts. |
| 1.39 | Scorpiomon (Anomalocarimon) | [275](content/species/275-scorpiomon.json) | in-progress | Coastal/desert regional Ultimate; verify identity, tail strike and large footprint. |
| 1.40 | Datamon | [294](content/species/294-datamon.json) | in-progress | Factory/ruins resident; check small-body attacks and partner interactions. |
| 1.41 | Mammothmon | [267](content/species/267-mammothmon.json) | in-progress | Snow-region landmark enemy/partner; large-model fit is the first acceptance check. |
| 1.42 | SkullMeramon | [277](content/species/277-skullmeramon.json) | in-progress | Late volcanic/industrial Ultimate; check flame effects and damage timing. |
| 1.43 | Garbagemon | [269](content/species/269-garbagemon.json) | in-progress | Industrial region variety; verify bin/bazooka movement and care poses. |

## 2. Vanilla-like Megas: Adventure endgame library

“Mega” here describes the proposed expanded-library role, not an instruction to rewrite vanilla levels. Phoenixmon, HerculesKabuterimon and MetalEtemon are vanilla Ultimates, and Horizon currently also labels Machinedramon Ultimate. Keep classic behavior and any new Mega progression as separate, reviewed decisions. A new level must earn its place through raising time, lifespan, costs and encounters, not just larger stats.

Magnadramon and Ophanimon, and Vikemon and Plesiomon, are alternative coverage choices from wider media; do not force both alternatives into a single linear route. The official profiles classify [Phoenixmon](https://digimon.net/reference_en/detail.php?directory_name=hououmon) and [HerculesKabuterimon](https://digimon.net/reference_en/detail.php?directory_name=heraklekabuterimon) as Mega; this does not change their existing DW1 gameplay level or establish a unique evolution tree.

| Priority | Digimon / form | Existing asset / record | Status | Next acceptance work / reason |
|---|---|---|---|---|
| 2.01 | WarGreymon | [373](content/species/373-wargreymon.json) | in-progress | First core Mega acceptance sample: claws, shield, finisher, care and comparable endgame balance. |
| 2.02 | MetalGarurumon | [191](content/species/191-metalgarurumon.json) | in-progress | Second core sample: quadruped motion, missile origins, care and ranged balance. |
| 2.03 | HerculesKabuterimon | [60](content/species/60-herculeskabuterimon.json) | in-progress | Reuse the vanilla Ultimate asset; decide expanded-profile Mega treatment separately from classic behavior. |
| 2.04 | Phoenixmon | [59](content/species/59-phoenixmon.json) | in-progress | Reuse the vanilla Ultimate asset; preserve classic level/routes while assessing an expanded Mega role. |
| 2.05 | Rosemon | [230](content/species/230-rosemon.json) | in-progress | Plant-family capstone; complete whip, effects, care and late-game balance. |
| 2.06 | Vikemon | [220](content/species/220-vikemon.json) | in-progress | Primary proposed Gomamon-family capstone; hammer, fur/body silhouette and large-model fit. |
| 2.07 | Seraphimon | [207](content/species/207-seraphimon.json) | in-progress | Patamon-family capstone; wings, projectile origins and care animations. |
| 2.08 | Magnadramon (Holydramon) | [215](content/species/215-magnadramon.json) | in-progress | First proposed Gatomon-family capstone; long-body flight and field/care fit. |
| 2.09 | Ophanimon | No record identified | Not started | Alternative Gatomon-family capstone from wider media; donor/authoring feasibility before scheduling. |
| 2.10 | Plesiomon | [271](content/species/271-plesiomon.json) | in-progress | Alternative aquatic capstone from wider media; distinct role from Vikemon, not a required replacement. |
| 2.11 | SaberLeomon | [258](content/species/258-saberleomon.json) | in-progress | Recognizable ally and beast-family capstone; quadruped care and tooth/claw contacts. |
| 2.12 | MetalSeadramon | [211](content/species/211-metalseadramon.json) | in-progress | Dark Master for a coastal endgame region; long-body bounds and breath origin. |
| 2.13 | Puppetmon | [181](content/species/181-puppetmon.json) | in-progress | Dark Master for a forest region; hammer/firearm timing and puppet deformation. |
| 2.14 | Machinedramon | [115](content/species/115-machinedramon.json) | in-progress | Reuse vanilla boss geometry; finish partner coverage and define expanded level without changing classic assumptions. |
| 2.15 | Piedmon | [245](content/species/245-piedmon.json) | in-progress | Dark Master for a ruins/castle region; sword and teleport effects with readable recovery. |
| 2.16 | VenomMyotismon | [212](content/species/212-venommyotismon.json) | in-progress | Large boss first; partner release also requires acceptable field and care scale. |
| 2.17 | MetalEtemon | [65](content/species/65-metaletemon.json) | in-progress | Already a vanilla Ultimate/item evolution; reuse it and review an expanded Mega role independently. |
| 2.18 | Apocalymon | [400](content/species/400-apocalymon.json) | in-progress | Late boss candidate; assess geometry/effect budget before committing to normal partner use. |
| 2.19 | Omnimon (Omegamon) | [461](content/species/461-omnimon.json) | in-progress | Adventure-film bonus after core Megas; dual-weapon attacks and a documented unlock route. |

## 3. Series 2: Adventure 02 regional library

The main cast and Armor/DNA forms follow the [Adventure 02 roster](https://wikimon.net/Digimon_Adventure_02). Patamon/Gatomon and their earlier forms reuse tiers 1–2. Armor and DNA are source-fiction categories: the library proposal does not require implementing armor-item mechanics or a two-partner fusion system. Specify a DW1-compatible acquisition route separately. Horizon currently represents most Armor forms as Champion and Magnamon as Ultimate; record those engine choices independently of lore labels.

| Priority | Digimon / form | Existing asset / record | Status | Next acceptance work / reason |
|---|---|---|---|---|
| 3.01 | Veemon | [180](content/species/180-veemon.json) | in-progress | Complete the core Rookie's full care, movement and battle acceptance. |
| 3.02 | ExVeemon | [194](content/species/194-exveemon.json) | in-progress | Primary Champion; wing and punch contacts, then the DNA-family route. |
| 3.03 | Wormmon | [183](content/species/183-wormmon.json) | in-progress | Core insect Rookie; body deformation and care poses. |
| 3.04 | Stingmon | [187](content/species/187-stingmon.json) | in-progress | Primary Champion; aerial motion and spike contacts. |
| 3.05 | Hawkmon | [184](content/species/184-hawkmon.json) | in-progress | Core bird Rookie; walking/flight transitions and care poses. |
| 3.06 | Aquilamon | [188](content/species/188-aquilamon.json) | in-progress | Primary Champion; horn/wing attacks and large airborne footprint. |
| 3.07 | Armadillomon | [185](content/species/185-armadillomon.json) | in-progress | Core armored Rookie; rolling and care motion. |
| 3.08 | Ankylomon | [189](content/species/189-ankylomon.json) | in-progress | Primary Champion; tail contacts, ground footprint and camera fit. |
| 3.09 | Paildramon | [199](content/species/199-paildramon.json) | in-progress | Principal shared Ultimate for Veemon/Wormmon; projectile origins and a DW1-compatible unlock. |
| 3.10 | Silphymon | [226](content/species/226-silphymon.json) | in-progress | Shared Ultimate for Hawkmon/Gatomon; flight and arm-cannon contacts. |
| 3.11 | Shakkoumon | [214](content/species/214-shakkoumon.json) | in-progress | Shared Ultimate for Armadillomon/Patamon; bulky field/care fit and beam origins. |
| 3.12 | Imperialdramon (Dragon Mode) | [192](content/species/192-imperialdramon.json) | in-progress | Current Imperialdramon record; confirm model/mode identity and finish dragon-form acceptance. |
| 3.13 | Imperialdramon (Fighter Mode) | No record identified | Not started | Separate mode asset and attack/care set; do not mark Dragon Mode's record as covering this form. |
| 3.14 | Flamedramon | [195](content/species/195-flamedramon.json) | in-progress | Courage Armor form; melee/fire effects and an unlock independent of story flags. |
| 3.15 | Lighdramon (Raidramon) | [201](content/species/201-lighdramon.json) | in-progress | Friendship Armor form; quadruped motion and lightning origins. |
| 3.16 | Halsemon | [196](content/species/196-halsemon.json) | in-progress | Love Armor form; hovering, body bounds and attack effects. |
| 3.17 | Shurimon | [225](content/species/225-shurimon.json) | in-progress | Sincerity Armor form; extended-limb deformation and throwing-star timing. |
| 3.18 | Digmon | [193](content/species/193-digmon.json) | in-progress | Knowledge Armor form; drill contacts and care interactions. |
| 3.19 | Submarimon | [202](content/species/202-submarimon.json) | in-progress | Reliability Armor form; deliberate land-motion solution and field/care scale. |
| 3.20 | Pegasusmon | [200](content/species/200-pegasusmon.json) | in-progress | Hope Armor form; reuse Patamon's family and finish winged-quadruped coverage. |
| 3.21 | Nefertimon | [198](content/species/198-nefertimon.json) | in-progress | Light Armor form; reuse Gatomon's family and finish winged-quadruped coverage. |
| 3.22 | Magnamon | [197](content/species/197-magnamon.json) | in-progress | Miracles Armor form; decide power/unlock policy explicitly instead of equating Armor with Champion. |
| 3.23 | Chicomon | No record identified | Not started | Veemon Fresh; author/reconstruct the asset before adding a nursery route. |
| 3.24 | DemiVeemon (Chibimon) | No record identified | Not started | Veemon In-Training; nursery and care acceptance. |
| 3.25 | Leafmon | No record identified | Not started | Wormmon Fresh; asset and nursery acceptance. |
| 3.26 | Minomon | No record identified | Not started | Wormmon In-Training; nursery and care acceptance. |
| 3.27 | Pururumon | No record identified | Not started | Hawkmon Fresh; asset and nursery acceptance. |
| 3.28 | Poromon | No record identified | Not started | Hawkmon In-Training; nursery and care acceptance. |
| 3.29 | Tsubumon | No record identified | Not started | Armadillomon Fresh; asset and nursery acceptance. |
| 3.30 | Upamon | No record identified | Not started | Armadillomon In-Training; nursery and care acceptance. |
| 3.31 | Kimeramon | [182](content/species/182-kimeramon.json) | in-progress | First regional boss candidate; multiple limbs, effect budget and fit. |
| 3.32 | BlackWarGreymon | [404](content/species/404-blackwargreymon.json) | in-progress | Prominent regional adversary/ally; keep a distinct attack/balance identity. |
| 3.33 | Arukenimon | [311](content/species/311-arukenimon.json) | in-progress | Regional adversary; leg deformation and large footprint. |
| 3.34 | Mummymon | [334](content/species/334-mummymon.json) | in-progress | Regional adversary; firearm timing, bandages and care poses. |
| 3.35 | MaloMyotismon | [406](content/species/406-malomyotismon.json) | in-progress | Late regional boss; verify shoulder weapons, effects and memory budget. |
| 3.36 | Azulongmon | No record identified | Not started | Supporting world guardian; start with encounter/NPC feasibility because of size. |
| 3.37 | SkullSatamon | [314](content/species/314-skullsatamon.json) | in-progress | Late regional adversary; staff strike and effect acceptance. |
| 3.38 | MarineDevimon | [279](content/species/279-marinedevimon.json) | in-progress | Coastal regional adversary; large-body fit and tentacle motion. |
| 3.39 | Creepymon (Daemon) | [312](content/species/312-creepymon.json) | in-progress | Optional late boss; identify the modeled form before promising TV cloaked-form coverage. |
| 3.40 | Keramon | No record identified | Not started | Adventure-film/02-film extension after the TV roster; fill the missing Rookie before expanding this family. |
| 3.41 | Kurisarimon (Chrysalimon) | [431](content/species/431-kurisarimon.json) | in-progress | Movie-family Champion; care and locomotion coverage. |
| 3.42 | Infermon | [246](content/species/246-infermon.json) | in-progress | Movie-family Ultimate; long-limbed fit and projectile timing. |
| 3.43 | Diaboromon | [237](content/species/237-diaboromon.json) | in-progress | Movie-family Mega; readable attacks and restrained encounter scale. |
| 3.44 | Armageddemon | [407](content/species/407-armageddemon.json) | in-progress | Optional film boss after the above family; size/effect budget first. |
| 3.45 | Imperialdramon (Paladin Mode) | No record identified | Not started | Optional film capstone; separate mode asset, unlock and balance review. |

## 4. Series 3: Tamers regional library

The main and supporting cast follow the [Tamers roster](https://wikimon.net/Digimon_Tamers). Reuse native Leomon, Guardromon and Andromon; Azulongmon is already tracked in tier 3. Terriermon’s missing lower forms take priority over additional Mega-only imports. The selected Devas/guardians are a bounded regional shortlist, not a commitment to every Tamers enemy or a D-Reaper subsystem.

| Priority | Digimon / form | Existing asset / record | Status | Next acceptance work / reason |
|---|---|---|---|---|
| 4.01 | Guilmon | [433](content/species/433-guilmon.json) | in-progress | Finish the existing Rookie's full partner acceptance. |
| 4.02 | Growlmon | [320](content/species/320-growlmon.json) | in-progress | Champion; claw and blade contacts, tail and field fit. |
| 4.03 | WarGrowlmon | [326](content/species/326-wargrowlmon.json) | in-progress | Ultimate; arm blades, chest cannons and large-body fit. |
| 4.04 | Gallantmon | [318](content/species/318-gallantmon.json) | in-progress | Mega; lance/shield effects, recovery and complete care set. |
| 4.05 | Terriermon | No record identified | Not started | Main-cast gap; select a viable source or authored PS1-scale asset first. |
| 4.06 | Gargomon | No record identified | Not started | Complete Terriermon's Champion; firearm origins and locomotion/care. |
| 4.07 | Rapidmon (green) | No record identified | Not started | Complete the Ultimate; distinguish it from the gold Armor variant. |
| 4.08 | MegaGargomon | [335](content/species/335-megagargomon.json) | in-progress | Existing Mega; finish heavy-body animation, weapon effects and field/care fit. |
| 4.09 | Renamon | [354](content/species/354-renamon.json) | in-progress | Finish the existing Rookie's movement and care acceptance. |
| 4.10 | Kyubimon | [409](content/species/409-kyubimon.json) | in-progress | Champion; multi-tail deformation, flames and quadruped care. |
| 4.11 | Taomon | [315](content/species/315-taomon.json) | in-progress | Ultimate; talisman/brush attacks, sleeves and care interactions. |
| 4.12 | Sakuyamon | [316](content/species/316-sakuyamon.json) | in-progress | Mega; staff/effects, recovery and complete care set. |
| 4.13 | Impmon | No record identified | Not started | Prominent supporting Rookie; source/authoring feasibility and full care set. |
| 4.14 | Beelzemon | [403](content/species/403-beelzemon.json) | in-progress | Existing Mega; firearm timing and a documented route from the supporting roster. |
| 4.15 | Monodramon | No record identified | Not started | Ryo-family Rookie for DW1 raising; asset and full partner acceptance. |
| 4.16 | Strikedramon | No record identified | Not started | Proposed wider-media Champion bridge; not a claimed on-screen Tamers evolution. |
| 4.17 | Cyberdramon | No record identified | Not started | Ryo's principal partner; claw/wing motion and a complete care set. |
| 4.18 | Justimon | No record identified | Not started | Ryo-family capstone; arm modes, effects and release-sized animation budget. |
| 4.19 | Lopmon | No record identified | Not started | Supporting Rookie; separate design/animation review from Terriermon. |
| 4.20 | Antylamon | [309](content/species/309-antylamon.json) | in-progress | Verify that the current model represents the intended Deva form before crediting Tamers coverage. |
| 4.21 | MarineAngemon | [248](content/species/248-marineangemon.json) | in-progress | Supporting partner; tiny-body readability, effects and field/care interactions. |
| 4.22 | Calumon (Culumon) | No record identified | Not started | Prioritize an NPC/recruitment role; do not invent a conventional battle/evolution line as a completion requirement. |
| 4.23 | Dobermon | No record identified | Not started | Supporting ally; quadruped coverage and a reusable encounter role. |
| 4.24 | Jyarimon | No record identified | Not started | Guilmon Fresh; optional nursery-completion pass after the main family. |
| 4.25 | Gigimon | No record identified | Not started | Guilmon In-Training; nursery and care acceptance. |
| 4.26 | Zerimon | No record identified | Not started | Terriermon Fresh; optional nursery-completion pass. |
| 4.27 | Gummymon | No record identified | Not started | Terriermon In-Training; nursery and care acceptance. |
| 4.28 | Relemon | No record identified | Not started | Renamon Fresh; optional nursery-completion pass. |
| 4.29 | Viximon (Pokomon) | No record identified | Not started | Renamon In-Training; nursery and care acceptance. |
| 4.30 | Megidramon | No record identified | Not started | Optional dark-evolution boss after the main cast; large-model/effect feasibility first. |
| 4.31 | Gallantmon (Crimson Mode) | No record identified | Not started | Late capstone after base Gallantmon; separate wing/weapon/mode acceptance. |
| 4.32 | Beelzemon (Blast Mode) | No record identified | Not started | Late capstone after base Beelzemon; separate wing/cannon/mode acceptance. |
| 4.33 | Makuramon | No record identified | Not started | Selected Deva for regional encounters; model and attack feasibility first. |
| 4.34 | Indramon | No record identified | Not started | Selected Deva; large-body and instrument/attack feasibility first. |
| 4.35 | Zhuqiaomon | No record identified | Not started | Regional boss/guardian; budget a bounded encounter before a partner version. |
| 4.36 | Baihumon | [276](content/species/276-baihumon.json) | in-progress | Existing guardian asset; validate scale and encounter role, then optional partner coverage. |
| 4.37 | Ebonwumon | No record identified | Not started | Complete the guardian set only after the core region works; large multi-head model feasibility. |

## Acceptance: when a row advances

Use the intended role to scope acceptance: partner, enemy, NPC or several. **Partner is the default**; a row explicitly scoped first to a boss/NPC can be accepted for that role, but must say so and cannot be advertised as a complete raisable partner. If roles finish separately, split the row or link a role checklist; do not hide partial completion behind one status.

1. **Reconstructible asset.** Record the source/authoring recipe, tool revision and content identity. The supported local build reproduces the asset; publish the permitted authored inputs/recipes and evidence metadata, not donor disc data. Reuse existing native assets and IDs when appropriate.
2. **Art complete.** Review silhouette, texture/palette, rig deformation, scale and contacts in the game. For partners, cover idle, walk/run/turn, follow, eating, sleeping, toilet, happiness/refusal/sickness, training, evolution and battle states that the runtime calls. Review every assigned technique and finisher: anticipation, contact/projectile origin, effect, hit/damage timing and recovery. For babies and NPCs, document legitimate non-applicable states. Export success and one idle screenshot are insufficient.
3. **Gameplay complete.** Validate raising requirements and competing branches, natural and item evolution where supported, rebirth, care/food/sleep/training behavior, technique learning/equipping, all assigned attacks, battle completion and save/reload. Use an actual raising route as well as forced-species smoke tests. Check enemy/NPC-only roles through their real placement, interaction and persistence paths. Compare balance with named vanilla peers and a defined profile; define a useful regional role rather than making every addition stronger.
4. **Options and capacity.** Exercise NEW DIGIMON on/off with a valid fallback and restoration; EXTENDED STORY on/off with library use independent of demo flags; NORMAL/EASY for battle roles; 20/60 FPS for motion/effects. Check the supported 2 MB configuration, model/animation/heap limits, dense scenes and overlay transitions. Record emulator/CPU/RAM settings and distinguish optional overclock/8 MB results from the standard configuration.
5. **Evidence and regression.** Link the exact tested commit, build configuration, commands, results and visual-review evidence from the row. Check unaffected peers when shared retargeting/effect code changes. Reopen acceptance when its model, animation, attack, evolution or shared runtime dependencies change materially.

## Decisions to make before expanding the commitment

- **V1.0 roster:** choose the finite shipping set and its acceptance owners. Tier order is a reusable-library priority; it is not a requirement to finish all four tiers before release.
- **Profiles:** define the supported roster, balance and story combinations. NEW DIGIMON OFF currently limits species; it does not undo the unconditional care/economy rebalancing described in [balance.md](docs/mods/balance.md). EASY/NORMAL is a combat multiplier, not a complete classic/expanded ruleset switch.
- **Save semantics:** keep species IDs and mod-owned flags stable. Document fallbacks, restored partners, retained recruitment and story-removal behavior using the existing [options](docs/mods/options.md) and [compatibility](docs/mods/compatibility.md) contracts. Test two saves with different options, not only one save round trips.
- **Library boundary:** demonstrate one standalone mini-mod using a polished family, one encounter/resident and a save round trip with the beta story disabled. This is a practical acceptance test for the framework claim. A new story, a fusion system and every late boss can remain separate consumers of that library.
