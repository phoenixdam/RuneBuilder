from typing import Dict, List


class RuneDataModel:
    """Model containing all rune tree and stat shard data"""
    
    def __init__(self):
        self._init_rune_descriptions()
        self.rune_trees = {
            'Precision': {
                'color': '#C8AA6E',
                'keystones': ['Press the Attack', 'Lethal Tempo', 'Fleet Footwork', 'Conqueror'],
                'row1': ['Absorb Life', 'Triumph', 'Presence of Mind'],
                'row2': ['Legend: Alacrity', 'Legend: Haste', 'Legend: Bloodline'],
                'row3': ['Coup de Grace', 'Cut Down', 'Last Stand']
            },
            'Domination': {
                'color': '#C83E3A',
                'keystones': ['Electrocute', 'Dark Harvest', 'Hail of Blades'],
                'row1': ['Cheap Shot', 'Taste of Blood', 'Sudden Impact'],
                'row2': ['Sixth Sense', 'Grisly Mementos', 'Deep Ward'],
                'row3': ['Treasure Hunter', 'Relentless Hunter', 'Ultimate Hunter']
            },
            'Sorcery': {
                'color': '#6AA0CB',
                'keystones': ['Summon Aery', 'Arcane Comet', 'Phase Rush'],
                'row1': ['Axiom Arcanist', 'Manaflow Band', 'Nimbus Cloak'],
                'row2': ['Transcendence', 'Celerity', 'Absolute Focus'],
                'row3': ['Scorch', 'Waterwalking', 'Gathering Storm']
            },
            'Resolve': {
                'color': '#A1D586',
                'keystones': ['Grasp of the Undying', 'Aftershock', 'Guardian'],
                'row1': ['Demolish', 'Font of Life', 'Shield Bash'],
                'row2': ['Conditioning', 'Second Wind', 'Bone Plating'],
                'row3': ['Overgrowth', 'Revitalize', 'Unflinching']
            },
            'Inspiration': {
                'color': '#C0C0C0',
                'keystones': ['Glacial Augment', 'Unsealed Spellbook', 'First Strike'],
                'row1': ['Hextech Flashtraption', 'Magical Footwear', 'Cash Back'],
                'row2': ['Triple Tonic', 'Time Warp Tonic', 'Biscuit Delivery'],
                'row3': ['Cosmic Insight', 'Approach Velocity', 'Jack of All Trades']
            }
        }
        
        self.stat_shards = {
            'offense': ['Adaptive Force', 'Attack Speed', 'Ability Haste'],
            'flex': ['Adaptive Force', 'Movement Speed', 'Health Scaling'],
            'defense': ['Health', 'Health Scaling', 'Tenacity and Slow Resist']
        }
        
    def get_tree_data(self, tree_name: str) -> Dict:
        """Get data for a specific rune tree"""
        return self.rune_trees.get(tree_name, {})
        
    def get_tree_color(self, tree_name: str) -> str:
        """Get color for a specific rune tree"""
        return self.rune_trees.get(tree_name, {}).get('color', '#3C3C41')
        
    def get_tree_names(self) -> List[str]:
        """Get list of all rune tree names"""
        return list(self.rune_trees.keys())
        
    def get_stat_shards_by_type(self, shard_type: str) -> List[str]:
        """Get stat shards for a specific type"""
        return self.stat_shards.get(shard_type, [])
        
    def get_stat_shard_color(self, shard_name: str) -> str:
        """Get color for a stat shard based on its type"""
        shard_colors = {
            'offense': '#C83E3A',
            'flex': '#C8AA6E', 
            'defense': '#A1D586'
        }
        
        offense_keywords = ['Force', 'Speed', 'Haste']
        flex_keywords = ['Armor', 'Resist']
        
        if any(keyword in shard_name for keyword in offense_keywords):
            return shard_colors['offense']
        elif any(keyword in shard_name for keyword in flex_keywords):
            return shard_colors['flex']
        else:
            return shard_colors['defense']
            
    def _init_rune_descriptions(self):
        """Initialize rune descriptions for tooltips"""
        self.rune_descriptions = {
            # Precision Keystones
            'Press the Attack': 'Basic attacks against enemy champions apply stacks for 4 seconds, stacking up to 3 times. At 3 stacks, deal 40-160 (based on level) bonus adaptive damage and grant 8% increased damage against champions until you are no longer in combat with them.',
            'Lethal Tempo': 'Basic attacks against enemy champions grant stacks for 6 seconds, stacking up to 6 times. Gain 6% (melee) or 4.8% (ranged) bonus attack speed per stack. At maximum stacks, basic attacks fire a bolt that deals 9-30 (melee) or 6-24 (ranged) bonus adaptive damage.',
            'Fleet Footwork': 'Moving and basic attacking generates Charges up to 100. At 100 Charges, become Energized, empowering your next basic attack to heal for 10-130 (melee) or 6-78 (ranged) and grant 20% (melee) or 15% (ranged) bonus movement speed for 1 second.',
            'Conqueror': 'Dealing damage to enemy champions grants stacks for 5 seconds, stacking up to 12 times. Each stack grants 1.08-2.4 bonus AD or 1.8-4 AP (Adaptive). At maximum stacks, heal for 8% (melee) or 5% (ranged) of post-mitigation damage dealt to champions.',
            
            # Precision Row 1
            'Absorb Life': 'Heal for 8% of the damage dealt by your abilities.',
            'Triumph': 'Scoring a takedown against an enemy champion heals you for 2.5% of your maximum health plus 5% of your missing health and grants 20 additional gold after a 1-second delay.',
            'Presence of Mind': 'Scoring a takedown restores 15% of your maximum mana or energy after 1 second. Damaging enemy champions restores 6-50 (melee) or 4.8-40 (ranged) mana or 6 energy (8 second cooldown).',
            
            # Precision Row 2
            'Legend: Alacrity': 'Gain 3% bonus attack speed plus 1.5% per Legend stack, up to 18% at maximum stacks. Gain Legend stacks for champion takedowns (100 points), epic monsters (100 points), large monsters (25 points), or minions (4 points).',
            'Legend: Haste': 'Gain 5 Ability Haste plus an additional 2.5 for each Legend stack (max 10 stacks). Earn progress toward Legend stacks for every champion takedown, epic monster takedown, or 20 enemy minion kills.',
            'Legend: Bloodline': 'Gain 0.6% Life Steal plus an additional 0.6% for each Legend stack (max 10 stacks). Earn progress toward Legend stacks for every champion takedown, epic monster takedown, or 20 enemy minion kills.',
            
            # Precision Row 3
            'Coup de Grace': 'Deal 8% more damage to champions who have less than 40% health.',
            'Cut Down': 'Deal 5% - 15% more damage to champions with more current health than you.',
            'Last Stand': 'Deal 5% - 11% more damage based on your missing health.',
            
            # Domination Keystones
            'Electrocute': 'Damaging basic attacks, abilities, and effects generate stacks against enemy champions. Applying 3 stacks within 3 seconds deals 70-240 (based on level) (+10% bonus AD) (+5% AP) adaptive damage after a 0.25-second delay. 20 second cooldown.',
            'Dark Harvest': 'Damaging enemy champions below 50% health deals 30 (+11 per Soul) (+10% bonus AD) (+5% AP) bonus adaptive damage and reaps 1 Soul after 1.75 seconds. 35 second cooldown, resets to 1 second on takedown.',
            'Hail of Blades': 'Starting an attack against an enemy champion grants 2 stacks for 3 seconds. Stacks are consumed per basic attack, granting 140% (melee) or 80% (ranged) bonus attack speed and increasing the attack speed cap. 10 second cooldown.',
            
            # Domination Row 1
            'Cheap Shot': 'Deal 10 - 45 bonus true damage to enemy champions with impaired movement or actions.',
            'Taste of Blood': 'Heal when you damage an enemy champion (20s cooldown).',
            'Sudden Impact': 'After exiting stealth or using a dash, leap, blink, teleport, or when leaving terrain, deal 7 bonus magic penetration and 6 bonus lethality for 5 seconds.',
            
            # Domination Row 2
            'Sixth Sense': 'Automatically tracks nearby untracked wards and, post-level 11, also reveals stealth wards for 10 seconds. It has a large cooldown: ~275 s (melee) / ~350 s (ranged).',
            'Grisly Mementos': 'Grants up to 18 stacks from champion takedowns. Each stack gives +6 trinket haste. In game types without trinkets, each gives +3 summoner haste instead',
            'Deep Ward': 'Ward duration is increased. Gain movement speed near allied wards.',
            
            # Domination Row 3
            'Treasure Hunter': 'Gain additional gold when taking down enemy champions.',
            'Relentless Hunter': 'Gain 5 Move Speed plus an additional 8 Move Speed for each unique enemy champion takedown.',
            'Ultimate Hunter': 'Gain 6 Ability Haste plus an additional 5 Ability Haste for each unique enemy champion takedown.',
            
            # Sorcery Keystones
            'Summon Aery': 'Attacks and abilities send Aery to a target, damaging enemies or shielding allies. Damage: 10–40 (+15% AP, +10% bonus AD), Shield: 20–80 (+25% AP, +40% bonus AD).',
            'Arcane Comet': 'Damaging a champion with an ability hurls a comet at their location, dealing 30–100 (+20% AP, +35% bonus AD) adaptive damage. 20s cooldown, reduced by CDR and slows.',
            'Phase Rush': 'Hitting a champion with 3 separate attacks or abilities within 4s grants 30–60% movement speed and 75% slow resistance for 3s (melee: 3s, ranged: 1.5s).',

            # Sorcery Row 1
            'Manaflow Band': 'Hitting an enemy champion with an ability permanently increases your maximum mana by 25, up to 250 mana. After reaching the cap, restore 1% missing mana every 5s.',
            'Nimbus Cloak': 'After casting a Summoner Spell, gain 5%–25% movement speed for 2.5s based on cooldown. Grants ghosting and ignores unit collision.',
            'Axiom Arcanist': 'Takedowns against champions refund 10% of your ultimate’s total cooldown and grant 5% increased damage for 10s.',

            # Sorcery Row 2
            'Transcendence': 'Gain 5 ability haste at level 5 and 10. At level 11, champion takedowns reduce your remaining basic ability cooldowns by 20%.',
            'Celerity': 'All movement speed bonuses are 7% more effective, and you gain 1% bonus movement speed.',
            'Absolute Focus': 'While above 70% health, gain 1.8–18 adaptive force (based on level).',

            # Sorcery Row 3
            'Scorch': 'Your first ability hit on an enemy champion burns them for 15–35 (+20% AP) bonus magic damage after 1s. 10s cooldown.',
            'Waterwalking': 'Gain 25 movement speed and up to 18 adaptive force in the river, based on level.',
            'Gathering Storm': 'Every 10 minutes, gain increasing adaptive force: +8/24/48/80/120/168 based on elapsed game time.',

            # Resolve Keystones
            'Grasp of the Undying': 'Every 4s in combat, your next attack on a champion deals bonus magic damage equal to 3% of your max HP, heals you, and permanently grants 5 HP.',
            'Aftershock': 'After immobilizing an enemy, gain bonus armor and MR for 2.5s, then explode dealing magic damage to nearby enemies.',
            'Guardian': 'If you or a nearby ally take damage, both gain a shield (70–150 +15% AP +9% bonus HP) for 1.5s. 70–40s cooldown.',

            # Resolve Row 1
            'Demolish': 'Charge up a powerful attack against a tower over 3s while within 600 range. The next attack deals 100 (+35% max HP) bonus physical damage.',
            'Font of Life': 'Impairing the movement of an enemy marks them for 4s. Allied champions who attack marked enemies heal for 5 + 1% of your max HP.',
            'Shield Bash': 'While shielded, gain 1–10 bonus armor and MR and your next basic attack deals bonus adaptive damage.',

            # Resolve Row 2
            'Conditioning': 'After 12 minutes, gain +9 bonus armor and MR and increase your total armor and MR by 4%.',
            'Second Wind': 'After taking damage from an enemy champion, regenerate 6 + (4% missing health) over 10s.',
            'Bone Plating': 'After taking damage from an enemy champion, the next 3 abilities or attacks deal 30–60 less damage. 55s cooldown.',

            # Resolve Row 3
            'Overgrowth': 'Gain 3 max HP for every 8 monsters or minions that die near you. At 120 stacks, gain an additional 3.5% max HP.',
            'Revitalize': 'Heals and shields you cast or receive are 5% stronger and increased by up to 10% on targets below 40% HP.',
            'Unflinching': 'Gain 10% Tenacity and Slow Resist. Gains up to 20% more based on missing HP.',

            # Inspiration Keystones
            'Glacial Augment': 'Immobilizing an enemy summons 3 glacial rays that slow enemies by 30–40% and reduce their damage dealt by 15% for 3s.',
            'Unsealed Spellbook': 'Swap one Summoner Spell for another at the shop. After using 3 different spells, reduce its cooldown.',
            'First Strike': 'Dealing damage to a champion before they damage you grants 5 gold and First Strike for 3s, causing you to deal 7% bonus damage and gain gold equal to that amount.',

            # Inspiration Row 1
            'Hextech Flashtraption': 'While Flash is on cooldown, it is replaced with Hexflash: channel for 2s to blink to a nearby location. 20s cooldown.',
            'Magical Footwear': 'Gain free boots at 12 minutes, which grant +10 MS. Each takedown before reduces the timer by 45s.',
            'Cash Back': 'Receive 100 gold back after buying your first legendary item.',

            # Inspiration Row 2
            'Biscuit Delivery': 'Gain a Total Biscuit of Everlasting Will every 2 mins until 6 mins. Consuming or selling a biscuit permanently increases mana cap and restores 10% missing health and mana.',
            'Time Warp Tonic': 'Potions grant 30% of their health/mana instantly and give 5% bonus movement speed while active.',
            'Triple Tonic': 'Receive a bonus potion at level 3, 6, and 9: Rejuvenation Tonic, Iron Tonic, and Elixir of Skill.',

            # Inspiration Row 3
            'Cosmic Insight': 'Gain +18 Summoner Spell Haste and +10 Item Haste.',
            'Approach Velocity': 'Gain 7.5% bonus movement speed when moving toward an impaired enemy champion. Doubled if you applied the CC.',
            'Jack of All Trades': 'Gain 5 adaptive force and 5 ability haste if you have at least 3 different stat bonuses from items.',
            
            # Stat Shards
            # Offense (Tier 1)
            'Adaptive Force': 'Gain +5.4 adaptive force (either Attack Damage or Ability Power based on which is higher).',
            'Attack Speed': 'Gain +10% attack speed.',
            'Ability Haste': 'Gain +8 ability haste.',
            
            # Flex (Tier 2)
            'Movement Speed': 'Gain +2% bonus movement speed.',
            'Health Scaling': 'Gain +10–180 bonus health based on champion level.',
            
            # Defense (Tier 3)
            'Health': 'Gain +65 bonus health.',
            'Tenacity and Slow Resist': 'Gain +10% tenacity and slow resist.',
        }
        
    def get_rune_description(self, rune_name: str) -> str:
        """Get description for a specific rune"""
        return self.rune_descriptions.get(rune_name, f"Description for {rune_name}")
        
    def get_tree_description(self, tree_name: str) -> str:
        """Get description for a rune tree"""
        tree_descriptions = {
            'Precision': 'Improved attacks and sustained damage',
            'Domination': 'Burst damage and target access',
            'Sorcery': 'Empowered abilities and resource manipulation',
            'Resolve': 'Durability and crowd control',
            'Inspiration': 'Creative tools and rule bending'
        }
        return tree_descriptions.get(tree_name, f"Description for {tree_name}")