"""Board generation service for Teyuna game."""
import random
from typing import Optional
from app.schemas.game import TerrainType, PortType


class BoardGenerator:
    """
    Generates the game board based on Tayrona geography.
    
    The board represents the Sierra Nevada de Santa Marta region:
    - Mountains (Sierra) in the center and highlands
    - Jungle (Selva) at lower elevations
    - Valleys (Valles) for agriculture
    - Quarries (Canteras) for stone
    - Highland cotton fields (Tierras Altas)
    - A ceremonial center (Centro Ceremonial) - the "desert"
    """
    
    # Standard board has 19 hexes in a specific pattern
    # 4 Wood (Selva), 4 Stone (Canteras), 4 Maize (Valles), 
    # 3 Cotton (Tierras Altas), 3 Gold (Sierra), 1 Ceremonial Center
    TERRAIN_DISTRIBUTION = [
        TerrainType.SELVA, TerrainType.SELVA, TerrainType.SELVA, TerrainType.SELVA,
        TerrainType.CANTERAS, TerrainType.CANTERAS, TerrainType.CANTERAS, TerrainType.CANTERAS,
        TerrainType.VALLES, TerrainType.VALLES, TerrainType.VALLES, TerrainType.VALLES,
        TerrainType.TIERRAS_ALTAS, TerrainType.TIERRAS_ALTAS, TerrainType.TIERRAS_ALTAS,
        TerrainType.SIERRA, TerrainType.SIERRA, TerrainType.SIERRA,
        TerrainType.CENTRO_CEREMONIAL
    ]
    
    # Number tokens (excluding 7) - probability distribution
    NUMBER_TOKENS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
    
    # Hex positions in axial coordinates for standard board
    # Arranged in concentric rings around center
    HEX_POSITIONS = [
        # Center
        (0, 0),
        # Inner ring (6 hexes)
        (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1),
        # Outer ring (12 hexes)
        (2, -2), (2, -1), (2, 0), (1, 1), (0, 2), (-1, 2),
        (-2, 2), (-2, 1), (-2, 0), (-1, -1), (0, -2), (1, -2)
    ]
    
    # Port positions (9 ports around the board)
    PORT_TYPES = [
        PortType.GENERAL, PortType.GENERAL, PortType.GENERAL, PortType.GENERAL,
        PortType.GOLD, PortType.STONE, PortType.COTTON, PortType.MAIZE, PortType.WOOD
    ]
    
    @classmethod
    def generate_board(cls, seed: Optional[int] = None) -> dict:
        """
        Generate a random board configuration.
        
        Returns a dict containing:
        - hexes: list of hex tiles with terrain, number tokens, and positions
        - vertices: list of vertex positions for buildings
        - edges: list of edge positions for roads
        - ports: list of port positions and types
        - conquistador_position: starting hex for the conquistador (ceremonial center)
        """
        if seed is not None:
            random.seed(seed)
        
        # Shuffle terrain and number tokens
        terrains = cls.TERRAIN_DISTRIBUTION.copy()
        random.shuffle(terrains)
        
        numbers = cls.NUMBER_TOKENS.copy()
        random.shuffle(numbers)
        
        # Generate hexes
        hexes = []
        number_idx = 0
        conquistador_position = 0
        
        for i, (q, r) in enumerate(cls.HEX_POSITIONS):
            terrain = terrains[i]
            
            # Ceremonial center doesn't get a number token
            if terrain == TerrainType.CENTRO_CEREMONIAL:
                number_token = None
                conquistador_position = i
            else:
                number_token = numbers[number_idx]
                number_idx += 1
            
            hexes.append({
                "id": i,
                "terrain": terrain.value,
                "number_token": number_token,
                "has_conquistador": terrain == TerrainType.CENTRO_CEREMONIAL,
                "q": q,
                "r": r
            })
        
        # Generate vertices (54 vertices for standard board)
        vertices = cls._generate_vertices()
        
        # Generate edges (72 edges for standard board)
        edges = cls._generate_edges()
        
        # Generate ports
        ports = cls._generate_ports()
        
        return {
            "hexes": hexes,
            "vertices": vertices,
            "edges": edges,
            "ports": ports,
            "conquistador_position": conquistador_position
        }
    
    @classmethod
    def _generate_vertices(cls) -> list[dict]:
        """Generate all vertex positions on the board."""
        vertices = []
        vertex_id = 0
        
        # Each hex has 6 vertices, but they're shared between hexes
        # We'll generate unique vertices based on position
        vertex_positions = set()
        
        for hex_q, hex_r in cls.HEX_POSITIONS:
            # 6 vertices around each hex (using cube coordinates offset)
            for direction in range(6):
                # Calculate vertex position (simplified - actual math would be more complex)
                vq = hex_q * 3 + [1, 2, 1, -1, -2, -1][direction]
                vr = hex_r * 3 + [1, 0, -1, -1, 0, 1][direction]
                
                if (vq, vr) not in vertex_positions:
                    vertex_positions.add((vq, vr))
                    vertices.append({
                        "id": vertex_id,
                        "q": vq,
                        "r": vr,
                        "building": None,
                        "player_id": None,
                        "is_port": False,
                        "port_type": None
                    })
                    vertex_id += 1
        
        return vertices
    
    @classmethod
    def _generate_edges(cls) -> list[dict]:
        """Generate all edge positions on the board."""
        edges = []
        edge_id = 0
        edge_positions = set()
        
        for hex_q, hex_r in cls.HEX_POSITIONS:
            # 6 edges around each hex
            for direction in range(6):
                # Edge position (simplified)
                eq = hex_q * 2 + [1, 1, 0, -1, -1, 0][direction]
                er = hex_r * 2 + [0, 1, 1, 0, -1, -1][direction]
                ed = direction % 3  # Edge direction (0, 1, or 2)
                
                if (eq, er, ed) not in edge_positions:
                    edge_positions.add((eq, er, ed))
                    edges.append({
                        "id": edge_id,
                        "q": eq,
                        "r": er,
                        "direction": ed,
                        "has_road": False,
                        "player_id": None
                    })
                    edge_id += 1
        
        return edges
    
    @classmethod
    def _generate_ports(cls) -> list[dict]:
        """Generate port positions around the board."""
        port_types = cls.PORT_TYPES.copy()
        random.shuffle(port_types)
        
        # Port positions are on specific vertices around the edge
        # These indices are simplified - actual implementation would map to real vertices
        port_vertex_pairs = [
            (0, 1), (3, 4), (7, 8), (11, 12), (15, 16),
            (19, 20), (23, 24), (27, 28), (31, 32)
        ]
        
        ports = []
        for i, (v1, v2) in enumerate(port_vertex_pairs):
            ports.append({
                "id": i,
                "port_type": port_types[i].value,
                "vertex_ids": [v1, v2]
            })
        
        return ports
    
    @classmethod
    def get_terrain_resource(cls, terrain: TerrainType) -> Optional[str]:
        """Get the resource type produced by a terrain."""
        terrain_resources = {
            TerrainType.SIERRA: "gold",
            TerrainType.CANTERAS: "stone",
            TerrainType.TIERRAS_ALTAS: "cotton",
            TerrainType.VALLES: "maize",
            TerrainType.SELVA: "wood",
            TerrainType.CENTRO_CEREMONIAL: None
        }
        return terrain_resources.get(terrain)

