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
            'Sixth Sense': 'Gain a shield when damaged by an enemy champion.',
            'Grisly Mementos': 'Collect trophies when enemies die and gain permanent AD or AP.',
            'Deep Ward': 'Ward duration is increased. Gain movement speed near allied wards.',
            
            # Domination Row 3
            'Treasure Hunter': 'Gain additional gold when taking down enemy champions.',
            'Relentless Hunter': 'Gain 5 Move Speed plus an additional 8 Move Speed for each unique enemy champion takedown.',
            'Ultimate Hunter': 'Gain 6 Ability Haste plus an additional 5 Ability Haste for each unique enemy champion takedown.',
            
            # Add more rune descriptions as needed...
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