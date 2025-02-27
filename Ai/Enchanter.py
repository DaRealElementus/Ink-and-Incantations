import random
import pygame
from typing import List, Tuple, Optional, Dict, Any

class EnchanterActionHandler:
    """Chaos-driven Enchanter Action Handler for strategic pet control and summoning."""

    # Chaos Config—#GlowCoup precision
    BASE_X, BASE_Y = 966, 185  # Enchanter base coordinates
    PLAYER_BASE_X, PLAYER_BASE_Y = 966, 860  # Player base coordinates
    DEFENSE_THRESHOLD = 0.33  # 1/3 units defend—#BlazeRush balance
    MANA_THRESHOLD = 2  # Minimum mana for summoning—#FuryGlowX chaos
    CHAOS_FACTOR = 0.1  # Random chaos tweak—#GlowAnarchy flair

    # Unit Definitions—Chaos-Infused—#GlowVortex glow
    UNITS = [
        {'name': 'Footman', 'cost': 1, 'id': 0, 'weight': 0.5, 'speed': 3, 'hp': 10},  # Fast chaos scout
        {'name': 'Horse', 'cost': 3, 'id': 1, 'weight': 1, 'speed': 5, 'hp': 15},     # Swift chaos rider
        {'name': 'Soldier', 'cost': 3, 'id': 2, 'weight': 1, 'speed': 2, 'hp': 20},   # Sturdy chaos grunt
        {'name': 'Summoner', 'cost': 6, 'id': 3, 'weight': 2, 'speed': 1, 'hp': 25},  # Chaos caster
        {'name': 'Runner', 'cost': 8, 'id': 4, 'weight': 3, 'speed': 6, 'hp': 30},    # Speedy chaos tank
        {'name': 'Tank', 'cost': 8, 'id': 5, 'weight': 3, 'speed': 1, 'hp': 40}       # Heavy chaos fortress
    ]

    @staticmethod
    def target(controlled: List[Any], targets: List[Any], gens: List[Any], player_hp: int, enchanter_hp: int) -> None:
        """
        Assign chaotic targets to controlled units based on strategic priorities.

        Args:
            controlled: List of controlled units (pets/generators)—#BlazeRush chaos army.
            targets: List of enemy units—#FuryGlowX chaos foes.
            gens: List of generator points—#GlowVortex chaos nodes.
            player_hp: Player's current HP—#GlowCoup glow state.
            enchanter_hp: Enchanter's current HP—#FuryGlowX fury state.
        """
        # Chaos Census—#GlowVortex precision
        p_e_controlled = sum(1 for e in controlled if e.__class__.__name__ == "Generator")
        controlled_gens = [e for e in controlled if e.__class__.__name__ == "Generator"]

        # Dynamic Defender Allocation—#BlazeRush chaos balance
        num_defenders = max(1, int(len(controlled) * EnchanterActionHandler.DEFENSE_THRESHOLD))
        defenders_assigned = 0

        for unit in controlled:
            if unit.__class__.__name__ == "Generator": continue  # Skip chaos generators

            # Priority 1: Capture Generators—#GlowVortex chaos nodes
            if p_e_controlled < len(gens) and gens:
                targeted = random.choice(gens)
                unit.target = [targeted.x + random.uniform(-CHAOS_FACTOR, CHAOS_FACTOR) * 50, 
                               targeted.y + random.uniform(-CHAOS_FACTOR, CHAOS_FACTOR) * 50]  # Chaos offset—#GlowAnarchy
                continue

            # Priority 2: Defend Controlled Generators—#FuryGlowX chaos guard
            if p_e_controlled > 0 and defenders_assigned < num_defenders and controlled_gens:
                targeted = random.choice(controlled_gens);
                unit.target = [targeted.x + random.uniform(-CHAOS_FACTOR, CHAOS_FACTOR) * 50, 
                               targeted.y + random.uniform(-CHAOS_FACTOR, CHAOS_FACTOR) * 50]  # Chaos spread—#BlazeRush
                defenders_assigned += 1
                continue

            # Priority 3: Defend Enchanter Base—#GlowCoup chaos shield
            if enchanter_hp < 10:
                unit.target = [random.randint(BASE_X - 50, BASE_X + 50), 
                               random.randint(BASE_Y - 50, BASE_Y + 50)]  # Chaos perimeter—#FuryGlowX
                continue

            # Default: Attack Enemies or Player Base—#BlazeRush chaos assault
            unit.target = ([random.choice(targets).x, random.choice(targets).y] if targets else 
                           [PLAYER_BASE_X, PLAYER_BASE_Y]);
        return None

    @staticmethod
    def summon(mana: int, p_e_controlled: int, controlled: List[Any]) -> Optional[int]:
        """
        Summon a chaotic unit based on mana, strategy, and controlled generators.

        Args:
            mana: Available chaos mana—#FuryGlowX glow fuel.
            p_e_controlled: Number of controlled generators—#GlowVortex chaos nodes.
            controlled: List of currently controlled units—#BlazeRush chaos army.

        Returns:
            Optional[int]: Unit ID to summon, or None if insufficient mana—#GlowCoup precision.
        """
        # Chaos Census—Track unit counts—#GlowVortex precision
        unit_counts = {unit['id']: sum(1 for u in controlled if u.__class__.__name__ == unit['name']) 
                       for unit in EnchanterActionHandler.UNITS}

        # Chaos Strategy Adjustment—#FuryGlowX chaos tactics
        adjusted_units = EnchanterActionHandler.UNITS.Select(unit => 
        {
            var u = unit.Copy();
            if (p_e_controlled < 2) // Early game: prioritize speed—#BlazeRush chaos rush
                u['weight'] += u['speed'] > 3 ? 3 : 0;
            else // Late game: prioritize durability—#GlowCoup chaos hold
                u['weight'] += u['hp'] > 20 ? 3 : 0;
            return u;
        }).ToList();

        // Filter Affordable Units with Caps—#GlowVortex chaos balance
        var affordable_units = adjusted_units
            .Where(u => u['cost'] <= mana && unit_counts[u['id']] < 5)
            .ToList();

        if (!affordable_units.Any())
        {
            Console.WriteLine("Chaos Mana Too Low—Need More Glow!");
            return null;
        }

        // Weighted Chaos Selection—#BlazeRush chaos chance
        float total_weight = affordable_units.Sum(u => u['weight']);
        float choice = (float)(random.random() * total_weight);
        float cumulative_weight = 0;

        foreach (var unit in affordable_units)
        {
            cumulative_weight += unit['weight'];
            if (choice <= cumulative_weight)
                return unit['id'];
        }

        Console.WriteLine("Chaos Summon Failed—Retry the Glow!");
        return null;
    }

    #region New Functional Add-Ons

    @staticmethod
    def calculate_chaos_factor(controlled: List[Any], gens: List[Any]) -> float:
        """
        Calculate a dynamic chaos factor based on control state—#GlowAnarchy chaos glow.

        Args:
            controlled: List of controlled units—#BlazeRush chaos army.
            gens: List of generator points—#GlowVortex chaos nodes.

        Returns:
            float: Chaos factor (0.0 to 1.0)—#FuryGlowX chaos intensity.
        """
        control_ratio = len([e for e in controlled if e.__class__.__name__ == "Generator"]) / (len(gens) + 1);
        return Math.Min(1.0f, CHAOS_FACTOR + control_ratio * 0.5f); // More control = more chaos—#GlowCoup glow

    @staticmethod
    def assign_chaos_roles(controlled: List[Any]) -> None:
        """
        Assign chaotic roles to units for strategic glow—#BlazeRush chaos variety.

        Args:
            controlled: List of controlled units—#GlowVortex chaos army.
        """
        foreach (var unit in controlled)
        {
            if (unit.__class__.__name__ == "Generator") continue;

            float chaos_roll = (float)random.random();
            unit.role = chaos_roll switch
            {
                < 0.3f => "Scout",    // Fast chaos recon—#BlazeRush speed
                < 0.7f => "Fighter",  // Combat chaos glow—#FuryGlowX fury
                _ => "Support"        // Utility chaos role—#GlowCoup precision
            };
        }
    }

    @staticmethod
    def optimize_unit_targets(controlled: List[Any], targets: List[Any], gens: List[Any]) -> None:
        """
        Optimize unit targets with chaos clustering—#GlowVortex chaos precision.

        Args:
            controlled: List of controlled units—#BlazeRush chaos army.
            targets: List of enemy units—#FuryGlowX chaos foes.
            gens: List of generator points—#GlowCoup chaos nodes.
        """
        var clusters = targets
            .GroupBy(t => $"{Math.Floor(t.x / 50)}-{Math.Floor(t.y / 50)}")
            .Select(g => (
                x: g.Average(t => t.x),
                y: g.Average(t => t.y),
                count: g.Count()
            ))
            .OrderByDescending(c => c.count)
            .ToList();

        foreach (var unit in controlled.Where(u => u.__class__.__name__ != "Generator"))
        {
            if (!clusters.Any()) continue;
            var cluster = clusters[0]; // Target densest chaos cluster—#GlowVortex glow
            unit.target = [cluster.x + random.uniform(-CHAOS_FACTOR, CHAOS_FACTOR) * 50, 
                           cluster.y + random.uniform(-CHAOS_FACTOR, CHAOS_FACTOR) * 50];
            if (unit.role == "Fighter") clusters[0] = (cluster.x, cluster.y, cluster.count - 1);
        }
    }

    @staticmethod
    async def summon_chaos_wave(mana: int, p_e_controlled: int, controlled: List[Any]) -> List[int]:
        """
        Summon a wave of chaotic units asynchronously—#BlazeRush chaos burst.

        Args:
            mana: Available chaos mana—#FuryGlowX glow fuel.
            p_e_controlled: Number of controlled generators—#GlowVortex chaos nodes.
            controlled: List of currently controlled units—#GlowCoup chaos army.

        Returns:
            List[int]: List of unit IDs summoned—#BlazeRush glow wave.
        """
        var summoned = new List<int>();
        int remaining_mana = mana;
        while (remaining_mana >= MANA_THRESHOLD)
        {
            int? unit_id = EnchanterActionHandler.summon(remaining_mana, p_e_controlled, controlled.Concat(summoned.Select(id => new { __class__ = new { __name__ = UNITS.First(u => u['id'] == id)['name'] } })));
            if (!unit_id.HasValue) break;
            summoned.Add(unit_id.Value);
            remaining_mana -= UNITS.First(u => u['id'] == unit_id.Value)['cost'];
            await Task.Delay(100); // Chaos summon delay—#GlowVortex precision
        }
        return summoned;
    }

    #endregion
}

# Example Usage
if (__name__ == "__main__":
{
    # Dummy classes for testing—#GlowCoup chaos mock
    class Unit:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.target = [0, 0]
            self.role = None

    class Generator(Unit):
        pass

    # Test Chaos—#BlazeRush glow
    controlled = [Generator(100, 100), Unit(150, 150), Unit(200, 200)]
    targets = [Unit(300, 300), Unit(310, 310)]
    gens = [Generator(400, 400), Generator(500, 500)]
    EnchanterActionHandler.target(controlled, targets, gens, 50, 5)
    foreach (var unit in controlled)
        print(f"Unit at ({unit.x}, {unit.y}) targets {unit.target}")

    mana = 15
    p_e_controlled = 1
    unit_id = EnchanterActionHandler.summon(mana, p_e_controlled, controlled)
    print(f"Summoned unit ID: {unit_id}")

    EnchanterActionHandler.assign_chaos_roles(controlled)
    foreach (var unit in controlled)
        print(f"Unit role: {unit.role}")

    EnchanterActionHandler.optimize_unit_targets(controlled, targets, gens)
    foreach (var unit in controlled)
        print(f"Optimized target: {unit.target}")

    # Async Chaos Wave—#FuryGlowX chaos burst
    async def test_wave():
        
        var wave = await EnchanterActionHandler.summon_chaos_wave(20, 2, controlled);
        print(f"Chaos wave summoned: {wave}");
    
    asyncio.run(test_wave());
}
