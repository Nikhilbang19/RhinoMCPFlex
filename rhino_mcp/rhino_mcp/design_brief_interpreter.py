"""
Design-Brief Interpreter for RhinoMCP

This module translates natural-language design briefs into structured parametric operations
that can be executed in Rhino and Grasshopper.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional, Union
import json

logger = logging.getLogger("DesignBriefInterpreter")

class DesignBriefInterpreter:
    """
    Interprets natural language design briefs and converts them into 
    structured parametric operations for Rhino and Grasshopper.
    """
    
    def __init__(self):
        # Design parameters and their default values
        self.default_params = {
            "grid_size": 1.0,            # Base grid size in meters
            "floor_height": 3.0,          # Default floor height in meters
            "panel_depth": 0.2,           # Default panel depth in meters
            "facade_offset": 0.5,         # Offset from building envelope in meters
            "story_count": 5,             # Default number of stories
            "responsive_panels": True,    # Whether panels respond to environment
            "panel_density": 0.8,         # Density of panels (0.0-1.0)
            "view_priority": 0.7,         # Priority for views (0.0-1.0)
            "sun_priority": 0.8,          # Priority for sun angle response (0.0-1.0)
            "panel_rotation_limit": 45,   # Maximum panel rotation in degrees
            "panel_type": "rectangular",  # Default panel geometry
            "material": "glass",          # Default material
            "structural_system": "frame", # Default structural system
        }
        
        # Common design brief keywords and their parameter mappings
        self.keyword_mappings = {
            # Building scale and form
            "high-rise": {"story_count": 30, "panel_density": 0.9},
            "mid-rise": {"story_count": 15, "panel_density": 0.8},
            "low-rise": {"story_count": 5, "panel_density": 0.7},
            "tower": {"story_count": 40, "panel_density": 0.85, "form": "tower"},
            
            # Panel types and systems
            "dynamic": {"responsive_panels": True, "panel_rotation_limit": 60},
            "static": {"responsive_panels": False, "panel_rotation_limit": 0},
            "kinetic": {"responsive_panels": True, "panel_rotation_limit": 90},
            "adaptive": {"responsive_panels": True, "panel_rotation_limit": 75},
            "responsive": {"responsive_panels": True},
            "louvres": {"panel_type": "louvre", "panel_density": 0.9},
            "sunshade": {"panel_type": "louvre", "sun_priority": 0.9, "view_priority": 0.5},
            
            # Environmental responses
            "sun angle": {"sun_priority": 0.9},
            "solar": {"sun_priority": 0.9},
            "daylight": {"sun_priority": 0.8, "panel_type": "perforated"},
            "shadowing": {"sun_priority": 0.9, "panel_density": 0.9},
            
            # View and aesthetic elements
            "views": {"view_priority": 0.9},
            "framing views": {"view_priority": 0.95, "panel_density": 0.7},
            "transparent": {"material": "glass", "panel_density": 0.6},
            "opaque": {"material": "solid", "panel_density": 0.9},
            
            # Materials
            "glass": {"material": "glass"},
            "metal": {"material": "metal"},
            "wood": {"material": "wood"},
            "aluminum": {"material": "aluminum"},
            "concrete": {"material": "concrete"},
            
            # Patterns and density
            "dense": {"panel_density": 0.9},
            "sparse": {"panel_density": 0.5},
            "porous": {"panel_density": 0.6, "panel_type": "perforated"},
            "pattern": {"panel_type": "patterned"},
            "parametric": {"panel_type": "parametric"},
            
            # Structural considerations
            "lightweight": {"structural_system": "lightweight"},
            "modular": {"grid_size": 1.2, "structural_system": "modular"},
            "prefab": {"structural_system": "modular"},
        }
        
        # Brief analysis regex patterns
        self.patterns = {
            "building_type": r"(high-rise|mid-rise|low-rise|tower|building)",
            "facade_type": r"(dynamic|kinetic|adaptive|responsive|static|louvres|sunshade)",
            "environment": r"(sun angle|solar|daylight|shadowing|climate|weather|temperature)",
            "views": r"(views|framing views|panorama|outlook|vista)",
            "materials": r"(glass|metal|wood|aluminum|concrete|transparent|opaque)",
            "pattern": r"(dense|sparse|porous|pattern|parametric)",
            "structure": r"(lightweight|modular|prefab)",
        }
    
    def _extract_keywords(self, brief: str) -> Dict[str, List[str]]:
        """Extract relevant keywords from the design brief using regex patterns."""
        results = {}
        
        # Convert to lowercase for matching
        brief_lower = brief.lower()
        
        # Extract keywords for each category
        for category, pattern in self.patterns.items():
            matches = re.findall(pattern, brief_lower)
            if matches:
                results[category] = matches
        
        return results
    
    def _derive_parameters(self, keywords: Dict[str, List[str]]) -> Dict[str, Any]:
        """Derive design parameters from extracted keywords."""
        # Start with default parameters
        params = self.default_params.copy()
        
        # Update based on keywords
        for category, words in keywords.items():
            for word in words:
                if word in self.keyword_mappings:
                    # Update params with the mappings for this keyword
                    for key, value in self.keyword_mappings[word].items():
                        params[key] = value
        
        return params
    
    def _generate_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a sequence of parametric operations based on the parameters and design domain."""
        operations = []
        
        # Determine which design domain to use
        design_domain = params.get("design_domain", "facade")
        
        # Common initial operations for all domains
        operations.append({
            "operation": "initialize_design",
            "params": {
                "design_domain": design_domain,
                "grid_size": params["grid_size"],
                "material": params["material"],
                "color_scheme": params["color_scheme"]
            }
        })
        
        # Domain-specific operations
        if design_domain == "facade":
            operations.extend(self._generate_facade_operations(params))
        elif design_domain == "floor_plan":
            operations.extend(self._generate_floor_plan_operations(params))
        elif design_domain == "urban":
            operations.extend(self._generate_urban_operations(params))
        elif design_domain == "landscape":
            operations.extend(self._generate_landscape_operations(params))
        elif design_domain == "structure":
            operations.extend(self._generate_structure_operations(params))
        elif design_domain == "parametric_form":
            operations.extend(self._generate_parametric_form_operations(params))
        
        # Final operation for all domains
        operations.append({
            "operation": "finalize_design",
            "params": {
                "design_domain": design_domain,
                "export_format": "3dm",
                "add_metadata": True
            }
        })
        
        return operations
    
    def _generate_facade_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate operations specific to facade design."""
        operations = []
        
        # Define the building envelope
        operations.append({
            "operation": "create_building_envelope",
            "params": {
                "story_count": params["story_count"],
                "floor_height": params["floor_height"],
                "grid_size": params["grid_size"]
            }
        })
        
        # Create the facade system
        operations.append({
            "operation": "create_facade_system",
            "params": {
                "offset": params["facade_offset"],
                "panel_type": params["panel_type"],
                "panel_density": params["panel_density"],
                "material": params["material"],
                "structural_system": params["structural_system"]
            }
        })
        
        # If responsive, add environmental analysis
        if params["responsive_panels"]:
            operations.append({
                "operation": "analyze_sun_angles",
                "params": {
                    "priority": params["sun_priority"]
                }
            })
            
            operations.append({
                "operation": "analyze_view_corridors",
                "params": {
                    "priority": params["view_priority"]
                }
            })
            
            operations.append({
                "operation": "generate_panel_rotations",
                "params": {
                    "rotation_limit": params["panel_rotation_limit"],
                    "sun_priority": params["sun_priority"],
                    "view_priority": params["view_priority"]
                }
            })
        
        # Generate the facade geometry
        operations.append({
            "operation": "generate_facade_geometry",
            "params": params
        })
        
        return operations
    
    def _generate_floor_plan_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate operations specific to floor plan design."""
        operations = []
        
        # Create the floor boundary
        operations.append({
            "operation": "create_floor_boundary",
            "params": {
                "area": params["floor_area"],
                "proportions": "rectangular"
            }
        })
        
        # Generate program zones
        operations.append({
            "operation": "generate_program_zones",
            "params": {
                "program_type": params["program_type"],
                "room_count": params["room_count"],
                "open_plan": params["open_plan"]
            }
        })
        
        # Create circulation
        operations.append({
            "operation": "create_circulation",
            "params": {
                "corridor_width": params["corridor_width"],
                "room_division": params["room_division"]
            }
        })
        
        # Create interior partitions
        if not params["open_plan"]:
            operations.append({
                "operation": "create_partitions",
                "params": {
                    "room_division": params["room_division"],
                    "room_count": params["room_count"]
                }
            })
        
        # Place furniture and fixtures
        operations.append({
            "operation": "place_furniture",
            "params": {
                "program_type": params["program_type"],
                "density": 0.7
            }
        })
        
        return operations
    
    def _generate_urban_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate operations specific to urban design."""
        operations = []
        
        # Create site boundary
        operations.append({
            "operation": "create_site_boundary",
            "params": {
                "site_area": params["block_size"] * params["block_size"] * 4,
                "site_proportions": "rectangular"
            }
        })
        
        # Generate street network
        operations.append({
            "operation": "generate_street_network",
            "params": {
                "block_size": params["block_size"],
                "street_width": params["street_width"],
                "network_type": "grid"
            }
        })
        
        # Create building footprints
        operations.append({
            "operation": "create_building_footprints",
            "params": {
                "coverage": params["building_coverage"],
                "density": params["density"]
            }
        })
        
        # Generate building massing
        operations.append({
            "operation": "generate_building_massing",
            "params": {
                "height_avg": params["building_height_avg"],
                "height_variation": 0.3,
                "mixed_use": params["mixed_use"]
            }
        })
        
        # Add public spaces
        operations.append({
            "operation": "add_public_spaces",
            "params": {
                "ratio": 0.2,
                "distribution": "central"
            }
        })
        
        return operations
    
    def _generate_landscape_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate operations specific to landscape design."""
        operations = []
        
        # Create site terrain
        operations.append({
            "operation": "create_terrain",
            "params": {
                "area": 10000,
                "complexity": params["terrain_complexity"],
                "height_variation": params["topography_variation"]
            }
        })
        
        # Generate path network
        operations.append({
            "operation": "generate_path_network",
            "params": {
                "complexity": params["path_complexity"],
                "path_width": 2.0
            }
        })
        
        # Add vegetation
        operations.append({
            "operation": "add_vegetation",
            "params": {
                "density": params["vegetation_density"],
                "types": ["trees", "shrubs", "ground_cover"]
            }
        })
        
        # Add water features if requested
        if params["water_features"]:
            operations.append({
                "operation": "add_water_features",
                "params": {
                    "type": "pond",
                    "area_ratio": 0.15
                }
            })
        
        # Add site furniture
        operations.append({
            "operation": "add_site_furniture",
            "params": {
                "density": 0.5
            }
        })
        
        return operations
    
    def _generate_structure_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate operations specific to structural design."""
        operations = []
        
        # Create structural grid
        operations.append({
            "operation": "create_structural_grid",
            "params": {
                "grid_size": params["structural_grid"],
                "system_type": params["structural_system"]
            }
        })
        
        # Generate columns
        operations.append({
            "operation": "generate_columns",
            "params": {
                "dimensions": params["column_dimensions"],
                "material": params["structural_material"]
            }
        })
        
        # Generate beams
        operations.append({
            "operation": "generate_beams",
            "params": {
                "depth": params["beam_depth"],
                "material": params["structural_material"]
            }
        })
        
        # Generate floor slabs
        operations.append({
            "operation": "generate_floor_slabs",
            "params": {
                "thickness": 0.2,
                "material": params["structural_material"]
            }
        })
        
        # Create lateral system
        operations.append({
            "operation": "create_lateral_system",
            "params": {
                "type": "bracing",
                "material": params["structural_material"]
            }
        })
        
        return operations
    
    def _generate_parametric_form_operations(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate operations specific to parametric form generation."""
        operations = []
        
        # Create base geometry
        operations.append({
            "operation": "create_base_geometry",
            "params": {
                "type": "box",
                "dimensions": [10, 10, 10]
            }
        })
        
        # Apply subdivision
        operations.append({
            "operation": "apply_subdivision",
            "params": {
                "level": params["subdivision_level"],
                "method": "catmull-clark"
            }
        })
        
        # Create attractor points
        operations.append({
            "operation": "create_attractors",
            "params": {
                "count": params["attractor_points"],
                "influence": 0.7
            }
        })
        
        # Apply deformation
        operations.append({
            "operation": "apply_deformation",
            "params": {
                "iterations": params["iterations"],
                "strength": params["complexity"]
            }
        })
        
        # Apply symmetry if requested
        if params["symmetry"] != "none":
            operations.append({
                "operation": "apply_symmetry",
                "params": {
                    "type": params["symmetry"],
                    "preserve_original": True
                }
            })
        
        return operations
    
    def _generate_rhino_code(self, operations: List[Dict[str, Any]]) -> str:
        """Generate Rhino Python code from operations list."""
        if not operations:
            return "# No operations to generate code from"
        
        # Extract design domain from the first operation
        design_domain = operations[0]["params"].get("design_domain", "facade")
        
        # Common header code
        header_code = """
import rhinoscriptsyntax as rs
import random
import math
import System.Drawing  # For colors

# Clear existing geometry
if not 'preserve_existing' in locals() or not preserve_existing:
    # Delete all objects except those on locked layers
    unlocked_layers = [layer for layer in rs.LayerNames() if not rs.IsLayerLocked(layer)]
    for layer in unlocked_layers:
        rs.DeleteObjects(rs.ObjectsByLayer(layer))

# Create a layer for the design
design_layer = "Design_{0}"
if not rs.IsLayer(design_layer):
    rs.AddLayer(design_layer)
rs.CurrentLayer(design_layer)

# Helper function to add metadata to objects
def add_object_metadata(obj_id, name, description):
    if obj_id:
        rs.SetUserText(obj_id, "Name", name)
        rs.SetUserText(obj_id, "Description", description)
        rs.SetUserText(obj_id, "CreatedAt", str(System.DateTime.Now))
""".format(design_domain.replace(" ", "_"))

        # Select the appropriate domain-specific code generator
        domain_code = ""
        if design_domain == "facade":
            domain_code = self._generate_facade_rhino_code(operations)
        elif design_domain == "floor_plan" or design_domain == "floor layout":
            domain_code = self._generate_floor_plan_rhino_code(operations)
        elif design_domain == "urban" or design_domain == "urban design":
            domain_code = self._generate_urban_rhino_code(operations)
        elif design_domain == "landscape" or design_domain == "landscape design":
            domain_code = self._generate_landscape_rhino_code(operations)
        elif design_domain == "structure" or design_domain == "structural":
            domain_code = self._generate_structure_rhino_code(operations)
        elif design_domain == "parametric_form" or design_domain == "form":
            domain_code = self._generate_parametric_form_rhino_code(operations)
        else:
            # Default to facade if unknown domain
            domain_code = self._generate_facade_rhino_code(operations)
            
        # Common ending code
        ending_code = """
# Zoom extents to show the entire design
rs.ZoomExtents()

# Final message
print("Design generated successfully")
"""
        
        # Combine all code sections
        full_code = header_code + domain_code + ending_code
        
        return full_code
    
    def _generate_facade_rhino_code(self, operations: List[Dict[str, Any]]) -> str:
        """Generate Rhino code for facade design operations."""
        code = ""
        
        # Extract parameters from operations
        params = {}
        for op in operations:
            # This will gather all parameters into one dictionary
            params.update(op.get("params", {}))
        
        # Create building envelope
        code += """
# Create building envelope
width = 20.0  # Building width in meters
length = 30.0  # Building length in meters
height = {0} * {1}  # Total height

# Create base rectangle
base_rect = rs.AddRectangle(rs.WorldXYPlane(), width, length)
base_srf = rs.AddPlanarSrf(base_rect)
add_object_metadata(base_srf, "BuildingBase", "Base of the building")

# Extrude to create building volume
building_volume = rs.ExtrudeSurface(base_srf, rs.VectorScale(rs.WorldZVector(), height))
add_object_metadata(building_volume, "BuildingVolume", "Main building volume")
""".format(params.get("story_count", 5), params.get("floor_height", 3.0))

        # Create facade system
        code += """
# Create facade grid with panels
grid_size = {0}  # Size of each grid cell
panel_density = {1}  # Probability of creating a panel at a grid position

# North facade
north_face = rs.CopyObject(rs.AddRectangle(rs.PlaneFromPoints([0,length,0], [width,length,0], [0,length,height]), width, height))
north_facade_grid = []

# Create grid for north facade
for x in range(int(width/grid_size)):
    for z in range(int(height/grid_size)):
        # Apply panel density
        if random.random() < panel_density:
            # Create panel at this position
            panel_center = [x*grid_size + grid_size/2, length + {2}, z*grid_size + grid_size/2]
            panel = rs.AddRectangle(rs.PlaneFromPoints(
                [panel_center[0]-grid_size*0.4, panel_center[1], panel_center[2]-grid_size*0.4],
                [panel_center[0]+grid_size*0.4, panel_center[1], panel_center[2]-grid_size*0.4],
                [panel_center[0]-grid_size*0.4, panel_center[1], panel_center[2]+grid_size*0.4]
            ), grid_size*0.8, grid_size*0.8)
            
            # Extrude to create 3D panel
            panel_srf = rs.AddPlanarSrf(panel)
            panel_obj = rs.ExtrudeSurface(panel_srf, rs.VectorScale([0,-1,0], {3}))
            
            # Add metadata
            panel_name = "Panel_N_{0}_{1}".format(x, z)  # Using .format instead of f-string
            add_object_metadata(panel_obj, panel_name, "North Facade Panel")
            north_facade_grid.append({{"obj": panel_obj, "pos": [x, z], "center": panel_center}})

# Similarly for other facades...
""".format(
            params.get("grid_size", 1.0),
            params.get("panel_density", 0.8),
            params.get("facade_offset", 0.5),
            params.get("panel_depth", 0.2)
        )

        # Add sun analysis if responsive
        if params.get("responsive_panels", True):
            code += """
# Simulate sun angle analysis
sun_priority = {0}  # Priority for sun shading (0-1)

# Create a sun vector for analysis (pointing south at 45-degree altitude)
sun_vector = rs.VectorUnitize([0, -1, -1])

# Add visualization arrow for sun direction
sun_arrow = rs.AddLine([width/2, length/2, height+5], 
                       [width/2 + sun_vector[0]*10, length/2 + sun_vector[1]*10, height+5 + sun_vector[2]*10])
rs.ObjectColor(sun_arrow, [255, 200, 0])
add_object_metadata(sun_arrow, "SunVector", "Visualization of sun direction used for analysis")
""".format(params.get("sun_priority", 0.8))

            code += """
# Simulate view corridor analysis
view_priority = {0}  # Priority for preserving views (0-1)

# Define key view directions (e.g., toward north)
view_vector = rs.VectorUnitize([0, 1, 0])

# Add visualization arrow for main view direction
view_arrow = rs.AddLine([width/2, length/2, height/2], 
                        [width/2 + view_vector[0]*10, length/2 + view_vector[1]*10, height/2 + view_vector[2]*0])
rs.ObjectColor(view_arrow, [0, 200, 255])
add_object_metadata(view_arrow, "ViewVector", "Visualization of main view direction")
""".format(params.get("view_priority", 0.7))

            # Panel rotations
            code += """
# Apply panel rotations based on environmental factors
max_rotation = {0}  # Maximum rotation angle in degrees
sun_priority = {1}
view_priority = {2}

# Apply rotations to north facade panels
for panel in north_facade_grid:
    # Calculate rotation based on position
    # This is a simplified example - in reality, would be based on detailed analysis
    x_pos = panel["pos"][0] / (width/grid_size)  # Normalized x position (0-1)
    z_pos = panel["pos"][1] / (height/grid_size)  # Normalized z position (0-1)
    
    # Calculate rotation angle based on position, sun and view priorities
    # This creates a wave pattern that's different for each panel
    angle = max_rotation * math.sin(x_pos * math.pi * 2) * math.cos(z_pos * math.pi * 3)
    
    # Adjust based on sun priority (more closed on south facade)
    angle += max_rotation * 0.5 * sun_priority
    
    # Adjust based on view priority (more open on facades with good views)
    view_factor = math.sin(x_pos * math.pi) * view_priority
    angle -= max_rotation * 0.3 * view_factor
    
    # Apply rotation
    rotation_axis = rs.AddLine(
        [panel["center"][0], panel["center"][1] + {3}/2, panel["center"][2]],
        [panel["center"][0], panel["center"][1] - {3}/2, panel["center"][2]]
    )
    rs.RotateObject(panel["obj"], panel["center"], angle, rotation_axis, copy=False)
    
    # Delete the temporary rotation axis
    rs.DeleteObject(rotation_axis)
""".format(
                params.get("panel_rotation_limit", 45),
                params.get("sun_priority", 0.8),
                params.get("view_priority", 0.7),
                params.get("panel_depth", 0.2)
            )

        # Material application
        code += """
# Add colorization by material
material_color = {{
    "glass": [150, 210, 255, 100],
    "metal": [180, 180, 190, 255],
    "wood": [185, 122, 87, 255],
    "aluminum": [200, 200, 210, 255],
    "concrete": [180, 180, 170, 255],
    "solid": [120, 120, 120, 255]
}}["{0}"]

# Apply material color to all panels
all_panels = rs.ObjectsByLayer(design_layer)
for panel in all_panels:
    if "Panel" in rs.GetUserText(panel, "Name", ""):
        rs.ObjectColor(panel, material_color)
""".format(params.get("material", "glass"))

        return code
    
    def _generate_floor_plan_rhino_code(self, operations: List[Dict[str, Any]]) -> str:
        """Generate Rhino code for floor plan operations."""
        code = ""
        
        # Extract parameters from operations
        params = {}
        for op in operations:
            params.update(op.get("params", {}))
        
        # Set default parameters
        width = params.get("width", 15.0)
        depth = params.get("depth", 12.0)
        room_count = params.get("room_count", 4)
        has_balcony = params.get("has_balcony", True)
        has_bathroom = params.get("has_bathroom", True)
        has_kitchen = params.get("has_kitchen", True)
        open_plan = params.get("open_plan", False)
        unit_type = params.get("unit_type", "apartment")
        
        # Create floor plan outline
        code += """
# Create floor plan boundary
width = {0}  # Width in meters
depth = {1}  # Depth in meters
outline = rs.AddRectangle(rs.WorldXYPlane(), width, depth)
outline_srf = rs.AddPlanarSrf(outline)
add_object_metadata(outline_srf, "FloorPlanBoundary", "Main apartment boundary")

# Create walls layer
walls_layer = "Walls"
if not rs.IsLayer(walls_layer):
    rs.AddLayer(walls_layer)
rs.CurrentLayer(walls_layer)

# Wall properties
wall_thickness = 0.2  # Wall thickness in meters
ceiling_height = 3.0  # Ceiling height in meters
""".format(width, depth)

        # Generate different layouts based on unit_type
        if unit_type == "studio" or (room_count == 1 and open_plan):
            code += """
# Generate studio apartment layout
# Single open space with bathroom

# Main living space
main_area_width = width - 2 * wall_thickness
main_area_depth = depth - 3.5 - 2 * wall_thickness
main_space = rs.AddRectangle(
    rs.MovePlane(rs.WorldXYPlane(), [wall_thickness, wall_thickness, 0]),
    main_area_width,
    main_area_depth
)
main_space_srf = rs.AddPlanarSrf(main_space)
add_object_metadata(main_space_srf, "LivingSpace", "Combined living/sleeping area")

# Bathroom
bath_width = 2.0
bath_depth = 3.0
bath_x = width - bath_width - wall_thickness
bath_y = depth - bath_depth - wall_thickness
bathroom = rs.AddRectangle(
    rs.MovePlane(rs.WorldXYPlane(), [bath_x, bath_y, 0]),
    bath_width,
    bath_depth
)
bathroom_srf = rs.AddPlanarSrf(bathroom)
add_object_metadata(bathroom_srf, "Bathroom", "Bathroom")

# Kitchen area
kitchen_width = 3.0
kitchen_depth = 2.0
kitchen_x = wall_thickness
kitchen_y = depth - kitchen_depth - wall_thickness
kitchen = rs.AddRectangle(
    rs.MovePlane(rs.WorldXYPlane(), [kitchen_x, kitchen_y, 0]),
    kitchen_width,
    kitchen_depth
)
kitchen_srf = rs.AddPlanarSrf(kitchen)
add_object_metadata(kitchen_srf, "Kitchen", "Kitchen area")

# Create walls by extruding curves
wall_curves = []

# Exterior walls
wall_curves.append(outline)

# Interior walls
# Bathroom walls
bath_wall1 = rs.AddLine([bath_x, bath_y, 0], [bath_x + bath_width, bath_y, 0])
bath_wall2 = rs.AddLine([bath_x, bath_y, 0], [bath_x, bath_y + bath_depth, 0])
wall_curves.extend([bath_wall1, bath_wall2])

# Kitchen separation (half wall or counter)
kitchen_wall = rs.AddLine([kitchen_x + kitchen_width, kitchen_y, 0], [kitchen_x + kitchen_width, kitchen_y + kitchen_depth, 0])
wall_curves.append(kitchen_wall)

# Door openings
door_width = 0.9
# Bathroom door
bath_door_center = [bath_x + bath_width/2, bath_y, 0]
bath_door = rs.AddLine(
    [bath_door_center[0] - door_width/2, bath_door_center[1], 0],
    [bath_door_center[0] + door_width/2, bath_door_center[1], 0]
)
rs.AddTextDot("Door", bath_door_center)

# Main entrance door
entrance_door_center = [width / 2, wall_thickness, 0]
entrance_door = rs.AddLine(
    [entrance_door_center[0] - door_width/2, entrance_door_center[1], 0],
    [entrance_door_center[0] + door_width/2, entrance_door_center[1], 0]
)
rs.AddTextDot("Entrance", entrance_door_center)
"""
        elif unit_type == "apartment" or not open_plan:
            code += """
# Generate apartment layout with separate rooms
# Calculate room dimensions based on total room count
avg_room_width = width / 2
avg_room_depth = (depth - 5) / 2  # Reserve space for kitchen, bathroom, hallway

# Create a hallway down the middle
hall_width = 1.2
hall_x = (width - hall_width) / 2
hall_y = wall_thickness
hall_length = depth - 2 * wall_thickness
hallway = rs.AddRectangle(
    rs.MovePlane(rs.WorldXYPlane(), [hall_x, hall_y, 0]),
    hall_width,
    hall_length
)
hallway_srf = rs.AddPlanarSrf(hallway)
add_object_metadata(hallway_srf, "Hallway", "Central hallway")

# Add rooms
room_coords = []
room_names = ["LivingRoom", "MasterBedroom", "Bedroom", "Study", "DiningRoom"]

if room_count > 0:
    # Living room (always included)
    living_width = avg_room_width * 1.5
    living_depth = avg_room_depth * 1.3
    living_x = wall_thickness
    living_y = wall_thickness
    living = rs.AddRectangle(
        rs.MovePlane(rs.WorldXYPlane(), [living_x, living_y, 0]),
        living_width,
        living_depth
    )
    living_srf = rs.AddPlanarSrf(living)
    add_object_metadata(living_srf, room_names[0], "Living room")
    room_coords.append({{"x": living_x, "y": living_y, "width": living_width, "depth": living_depth, "name": room_names[0]}})

if room_count > 1:
    # Master bedroom
    master_width = avg_room_width * 1.2
    master_depth = avg_room_depth * 1.2
    master_x = width - master_width - wall_thickness
    master_y = depth - master_depth - wall_thickness
    master = rs.AddRectangle(
        rs.MovePlane(rs.WorldXYPlane(), [master_x, master_y, 0]),
        master_width,
        master_depth
    )
    master_srf = rs.AddPlanarSrf(master)
    add_object_metadata(master_srf, room_names[1], "Master bedroom")
    room_coords.append({{"x": master_x, "y": master_y, "width": master_width, "depth": master_depth, "name": room_names[1]}})

if room_count > 2:
    # Second bedroom
    bed2_width = avg_room_width * 0.9
    bed2_depth = avg_room_depth
    bed2_x = width - bed2_width - wall_thickness
    bed2_y = wall_thickness
    bed2 = rs.AddRectangle(
        rs.MovePlane(rs.WorldXYPlane(), [bed2_x, bed2_y, 0]),
        bed2_width,
        bed2_depth
    )
    bed2_srf = rs.AddPlanarSrf(bed2)
    add_object_metadata(bed2_srf, room_names[2], "Second bedroom")
    room_coords.append({{"x": bed2_x, "y": bed2_y, "width": bed2_width, "depth": bed2_depth, "name": room_names[2]}})

if room_count > 3:
    # Study or additional room
    study_width = avg_room_width * 0.8
    study_depth = avg_room_depth * 0.8
    study_x = wall_thickness
    study_y = depth - study_depth - wall_thickness
    study = rs.AddRectangle(
        rs.MovePlane(rs.WorldXYPlane(), [study_x, study_y, 0]),
        study_width,
        study_depth
    )
    study_srf = rs.AddPlanarSrf(study)
    add_object_metadata(study_srf, room_names[3], "Study/small bedroom")
    room_coords.append({{"x": study_x, "y": study_y, "width": study_width, "depth": study_depth, "name": room_names[3]}})

# Kitchen and bathroom
if has_kitchen:
    kitchen_width = 3.5
    kitchen_depth = 3.0
    kitchen_x = wall_thickness + living_width + hall_width
    kitchen_y = hall_y
    kitchen = rs.AddRectangle(
        rs.MovePlane(rs.WorldXYPlane(), [kitchen_x, kitchen_y, 0]),
        kitchen_width, 
        kitchen_depth
    )
    kitchen_srf = rs.AddPlanarSrf(kitchen)
    add_object_metadata(kitchen_srf, "Kitchen", "Kitchen")
    room_coords.append({{"x": kitchen_x, "y": kitchen_y, "width": kitchen_width, "depth": kitchen_depth, "name": "Kitchen"}})

if has_bathroom:
    bath_width = 2.5
    bath_depth = 2.0
    bath_x = width - bath_width - wall_thickness
    bath_y = master_y - bath_depth
    bathroom = rs.AddRectangle(
        rs.MovePlane(rs.WorldXYPlane(), [bath_x, bath_y, 0]),
        bath_width,
        bath_depth
    )
    bathroom_srf = rs.AddPlanarSrf(bathroom)
    add_object_metadata(bathroom_srf, "Bathroom", "Bathroom")
    room_coords.append({{"x": bath_x, "y": bath_y, "width": bath_width, "depth": bath_depth, "name": "Bathroom"}})

# Add a second bathroom if the apartment is large enough
if room_count > 3 and has_bathroom:
    bath2_width = 2.0
    bath2_depth = 2.0
    bath2_x = wall_thickness
    bath2_y = living_y + living_depth
    bathroom2 = rs.AddRectangle(
        rs.MovePlane(rs.WorldXYPlane(), [bath2_x, bath2_y, 0]),
        bath2_width,
        bath2_depth
    )
    bathroom2_srf = rs.AddPlanarSrf(bathroom2)
    add_object_metadata(bathroom2_srf, "Bathroom2", "Second bathroom")
    room_coords.append({{"x": bath2_x, "y": bath2_y, "width": bath2_width, "depth": bath2_depth, "name": "Bathroom2"}})

# Create walls by extruding curves
wall_curves = []

# Exterior walls
wall_curves.append(outline)

# Interior walls (between rooms)
for room in room_coords:
    # Horizontal walls
    if room["name"] != "Hallway":
        wall_h1 = rs.AddLine([room["x"], room["y"], 0], [room["x"] + room["width"], room["y"], 0])
        wall_h2 = rs.AddLine([room["x"], room["y"] + room["depth"], 0], [room["x"] + room["width"], room["y"] + room["depth"], 0])
        # Vertical walls
        wall_v1 = rs.AddLine([room["x"], room["y"], 0], [room["x"], room["y"] + room["depth"], 0])
        wall_v2 = rs.AddLine([room["x"] + room["width"], room["y"], 0], [room["x"] + room["width"], room["y"] + room["depth"], 0])
        wall_curves.extend([wall_h1, wall_h2, wall_v1, wall_v2])

# Door openings
door_width = 0.9
# Add doors to each room
for room in room_coords:
    if room["name"] != "Hallway":
        # Add door on the hallway side of the room
        if room["x"] <= hall_x and (room["x"] + room["width"]) >= hall_x:
            # Room is on the left of hallway
            door_center = [hall_x, room["y"] + room["depth"]/2, 0]
        elif room["x"] <= (hall_x + hall_width) and (room["x"] + room["width"]) >= (hall_x + hall_width):
            # Room is on the right of hallway
            door_center = [hall_x + hall_width, room["y"] + room["depth"]/2, 0]
        elif room["y"] <= hall_y and (room["y"] + room["depth"]) >= hall_y:
            # Room is above the hallway
            door_center = [room["x"] + room["width"]/2, hall_y, 0]
        elif room["y"] <= (hall_y + hall_length) and (room["y"] + room["depth"]) >= (hall_y + hall_length):
            # Room is below the hallway
            door_center = [room["x"] + room["width"]/2, hall_y + hall_length, 0]
        else:
            # Default door location
            door_center = [room["x"] + room["width"]/2, room["y"], 0]
        
        rs.AddTextDot(room["name"], [room["x"] + room["width"]/2, room["y"] + room["depth"]/2, 0])
        rs.AddTextDot("Door", door_center)

# Main entrance door
entrance_door_center = [hall_x + hall_width/2, wall_thickness, 0]
rs.AddTextDot("Entrance", entrance_door_center)
"""
        
        # Add balcony if requested
        if has_balcony:
            code += """
# Add balcony
balcony_depth = 2.0
balcony_width = width / 3
balcony_x = width - balcony_width - wall_thickness
balcony_y = -balcony_depth
balcony = rs.AddRectangle(
    rs.MovePlane(rs.WorldXYPlane(), [balcony_x, balcony_y, 0]),
    balcony_width,
    balcony_depth
)
balcony_srf = rs.AddPlanarSrf(balcony)
add_object_metadata(balcony_srf, "Balcony", "Outdoor balcony")
"""

        # Extrude walls
        code += """
# Extrude walls
walls_layer = "Walls"
if not rs.IsLayer(walls_layer):
    rs.AddLayer(walls_layer)
rs.CurrentLayer(walls_layer)

for curve in wall_curves:
    # Create wall surface
    swept_wall = rs.ExtrudeCurve(curve, rs.AddLine([0,0,0], [0,0,ceiling_height]))
    if swept_wall:
        add_object_metadata(swept_wall, "Wall", "Wall element")
        rs.ObjectColor(swept_wall, [200, 200, 200])

# Add room labels
text_layer = "Labels"
if not rs.IsLayer(text_layer):
    rs.AddLayer(text_layer)
rs.CurrentLayer(text_layer)

# Add furniture (simplified blocks)
furniture_layer = "Furniture"
if not rs.IsLayer(furniture_layer):
    rs.AddLayer(furniture_layer, [150, 120, 100])
rs.CurrentLayer(furniture_layer)

# Add some basic furniture depending on room type
for room in room_coords:
    room_center_x = room["x"] + room["width"]/2
    room_center_y = room["y"] + room["depth"]/2
    
    if room["name"] == "LivingRoom":
        # Add sofa
        sofa_width = min(room["width"] * 0.7, 3.0)
        sofa_depth = 1.0
        sofa_x = room_center_x - sofa_width/2
        sofa_y = room["y"] + room["depth"] - sofa_depth - 0.5
        
        sofa = rs.AddBox(
            rs.WorldXYPlane(),
            sofa_width, sofa_depth, 0.8,
            [sofa_x, sofa_y, 0]
        )
        add_object_metadata(sofa, "Sofa", "Living room sofa")
        rs.ObjectColor(sofa, [180, 150, 120])
        
        # Add coffee table
        table_size = 1.2
        table_x = room_center_x - table_size/2
        table_y = sofa_y - table_size - 0.3
        
        table = rs.AddBox(
            rs.WorldXYPlane(),
            table_size, table_size, 0.5,
            [table_x, table_y, 0]
        )
        add_object_metadata(table, "CoffeeTable", "Living room coffee table")
        rs.ObjectColor(table, [150, 120, 90])
        
    elif "Bedroom" in room["name"]:
        # Add bed
        bed_width = min(room["width"] * 0.8, 1.8)
        bed_length = min(room["depth"] * 0.7, 2.2)
        bed_x = room_center_x - bed_width/2
        bed_y = room_center_y - bed_length/2
        
        bed = rs.AddBox(
            rs.WorldXYPlane(),
            bed_width, bed_length, 0.5,
            [bed_x, bed_y, 0]
        )
        add_object_metadata(bed, "Bed_{0}".format(room["name"]), "Bed")
        rs.ObjectColor(bed, [200, 190, 170])
        
    elif room["name"] == "Kitchen":
        # Add kitchen counter along walls
        counter_depth = 0.6
        counter_height = 0.9
        
        # Counter along back wall
        counter1 = rs.AddBox(
            rs.WorldXYPlane(),
            room["width"] - 1.0, counter_depth, counter_height,
            [room["x"] + 0.5, room["y"] + room["depth"] - counter_depth, 0]
        )
        add_object_metadata(counter1, "KitchenCounter1", "Kitchen counter")
        rs.ObjectColor(counter1, [180, 180, 180])
        
        # Counter along side wall
        counter2 = rs.AddBox(
            rs.WorldXYPlane(),
            counter_depth, room["depth"] - counter_depth - 1.0, counter_height,
            [room["x"], room["y"] + 0.5, 0]
        )
        add_object_metadata(counter2, "KitchenCounter2", "Kitchen counter")
        rs.ObjectColor(counter2, [180, 180, 180])
"""

        return code
    
    def _generate_urban_rhino_code(self, operations: List[Dict[str, Any]]) -> str:
        """Generate Rhino code for urban design operations."""
        code = ""
        
        # Extract parameters from operations
        params = {}
        for op in operations:
            params.update(op.get("params", {}))
        
        # Create urban grid
        code += """
# Create urban design grid
grid_size = {0}  # Size of city blocks in meters
grid_rows = {1}
grid_columns = {2}
road_width = {3}
site_boundary = {4}  # Size of overall site boundary

# Create site boundary
site_rect = rs.AddRectangle(rs.WorldXYPlane(), site_boundary, site_boundary)
site_srf = rs.AddPlanarSrf(site_rect)
add_object_metadata(site_srf, "SiteBoundary", "Overall urban design site")

# Add main roads
urban_blocks = []
for row in range(grid_rows):
    for col in range(grid_columns):
        # Calculate block position
        x = col * (grid_size + road_width)
        y = row * (grid_size + road_width)
        
        # Create block footprint
        block_rect = rs.AddRectangle(
            rs.MovePlane(rs.WorldXYPlane(), [x, y, 0]), 
            grid_size, grid_size
        )
        block_srf = rs.AddPlanarSrf(block_rect)
        add_object_metadata(block_srf, "Block_{0}_{1}".format(row, col), "Urban block footprint")
        
        urban_blocks.append({{"id": block_srf, "row": row, "col": col, "x": x, "y": y}})
""".format(
            params.get("grid_size", 100.0),
            params.get("grid_rows", 5),
            params.get("grid_columns", 5),
            params.get("road_width", 20.0),
            params.get("site_boundary", 600.0)
        )
        
        # Generate buildings on blocks
        code += """
# Generate buildings on blocks
max_height = {0}  # Maximum building height
min_height = {1}  # Minimum building height
density = {2}  # Building density (0-1)
building_setback = {3}  # Building setback from block edge

# Create a layer for buildings
buildings_layer = "Buildings"
if not rs.IsLayer(buildings_layer):
    rs.AddLayer(buildings_layer)
rs.CurrentLayer(buildings_layer)

for block in urban_blocks:
    # Determine if this block gets a building based on density
    if random.random() < density:
        # Calculate building footprint with setback
        x, y = block["x"], block["y"]
        footprint_rect = rs.AddRectangle(
            rs.MovePlane(rs.WorldXYPlane(), [x + building_setback, y + building_setback, 0]), 
            grid_size - 2 * building_setback, 
            grid_size - 2 * building_setback
        )
        footprint_srf = rs.AddPlanarSrf(footprint_rect)
        
        # Determine building height based on rules
        # Central blocks are taller than edge blocks
        center_row = grid_rows / 2
        center_col = grid_columns / 2
        
        # Calculate distance from center (0-1 normalized)
        dist_from_center = math.sqrt((block["row"] - center_row)**2 + (block["col"] - center_col)**2)
        max_dist = math.sqrt(center_row**2 + center_col**2)
        norm_dist = dist_from_center / max_dist if max_dist > 0 else 0
        
        # Height decreases with distance from center
        height_factor = 1 - (norm_dist * {4})  # Height distribution factor
        height = min_height + (max_height - min_height) * height_factor
        
        # Apply some randomness to heights
        height = height * (0.8 + 0.4 * random.random())
        
        # Extrude to create building volume
        building = rs.ExtrudeSurface(footprint_srf, rs.VectorScale(rs.WorldZVector(), height))
        add_object_metadata(
            building, 
            "Building_{0}_{1}".format(block["row"], block["col"]), 
            "Urban building, height: {0}m".format(round(height, 1))
        )
        
        # Delete the temporary footprint surface
        rs.DeleteObject(footprint_srf)
        
        # Color buildings based on height
        color_factor = (height - min_height) / (max_height - min_height) if max_height > min_height else 0.5
        building_color = [int(120 + 135 * color_factor), int(120 + 80 * (1-color_factor)), int(140 + 40 * color_factor)]
        rs.ObjectColor(building, building_color)
""".format(
            params.get("max_building_height", 100.0),
            params.get("min_building_height", 10.0),
            params.get("building_density", 0.7),
            params.get("building_setback", 5.0),
            params.get("height_distribution", 0.8)
        )
        
        # Add landscape and green areas
        if params.get("include_green_areas", True):
            code += """
# Add parks and green spaces
green_layer = "GreenSpaces"
if not rs.IsLayer(green_layer):
    rs.AddLayer(green_layer, [0, 180, 0])
rs.CurrentLayer(green_layer)

# Create a central park
central_row = int(grid_rows / 2)
central_col = int(grid_columns / 2)

# Find blocks to convert to parks
for block in urban_blocks:
    # Central park
    if block["row"] == central_row and block["col"] == central_col:
        # Delete any building on this block
        building_obj = rs.ObjectsByName("Building_{0}_{1}".format(block["row"], block["col"]))
        if building_obj:
            rs.DeleteObjects(building_obj)
            
        # Create park surface
        park_surface = rs.CopyObject(block["id"])
        rs.ObjectColor(park_surface, [0, 180, 0])
        
        # Add some trees to the park
        tree_count = 20
        park_bounds = rs.BoundingBox(park_surface)
        min_pt, max_pt = park_bounds[0], park_bounds[6]
        
        for i in range(tree_count):
            # Random position within park
            tree_x = min_pt[0] + random.random() * (max_pt[0] - min_pt[0])
            tree_y = min_pt[1] + random.random() * (max_pt[1] - min_pt[1])
            
            # Create a tree (simplified as a cylinder and sphere)
            tree_trunk = rs.AddCylinder(
                [tree_x, tree_y, 0],
                [tree_x, tree_y, 3 + random.random() * 2],
                0.2 + random.random() * 0.3
            )
            tree_canopy = rs.AddSphere([tree_x, tree_y, 5 + random.random() * 3], 1.5 + random.random() * 2)
            
            # Color the tree parts
            rs.ObjectColor(tree_trunk, [120, 80, 40])
            rs.ObjectColor(tree_canopy, [0, 150 + random.randint(0, 50), 0])
            
            # Add metadata
            add_object_metadata(tree_trunk, "Tree_Trunk_{0}".format(i), "Tree trunk in central park")
            add_object_metadata(tree_canopy, "Tree_Canopy_{0}".format(i), "Tree canopy in central park")
"""
        
        # Add infrastructure
        code += """
# Add main roads network
roads_layer = "Roads"
if not rs.IsLayer(roads_layer):
    rs.AddLayer(roads_layer, [50, 50, 50])
rs.CurrentLayer(roads_layer)

road_width = {0}
grid_size_with_road = grid_size + road_width

# Create horizontal roads
for row in range(grid_rows + 1):
    road_y = row * grid_size_with_road - road_width/2
    start_point = [0, road_y, 0.1]  # Slightly above ground
    end_point = [grid_columns * grid_size_with_road, road_y, 0.1]
    road = rs.AddRectangle(
        rs.PlaneFromPoints(
            start_point,
            [start_point[0] + 1, start_point[1], start_point[2]],
            [start_point[0], start_point[1] + road_width, start_point[2]]
        ),
        grid_columns * grid_size_with_road,
        road_width
    )
    road_srf = rs.AddPlanarSrf(road)
    rs.ObjectColor(road_srf, [50, 50, 50])
    add_object_metadata(road_srf, "Road_H_{0}".format(row), "Horizontal road")

# Create vertical roads
for col in range(grid_columns + 1):
    road_x = col * grid_size_with_road - road_width/2
    start_point = [road_x, 0, 0.1]  # Slightly above ground
    end_point = [road_x, grid_rows * grid_size_with_road, 0.1]
    road = rs.AddRectangle(
        rs.PlaneFromPoints(
            start_point,
            [start_point[0] + road_width, start_point[1], start_point[2]],
            [start_point[0], start_point[1] + 1, start_point[2]]
        ),
        road_width,
        grid_rows * grid_size_with_road
    )
    road_srf = rs.AddPlanarSrf(road)
    rs.ObjectColor(road_srf, [50, 50, 50])
    add_object_metadata(road_srf, "Road_V_{0}".format(col), "Vertical road")
""".format(params.get("road_width", 20.0))
        
        return code
    
    def _generate_landscape_rhino_code(self, operations: List[Dict[str, Any]]) -> str:
        """Generate Rhino code for landscape design operations."""
        # Placeholder for demo
        code = """
# Placeholder for landscape generation code
print("Landscape generation would happen here")
"""
        return code
    
    def _generate_structure_rhino_code(self, operations: List[Dict[str, Any]]) -> str:
        """Generate Rhino code for structural design operations."""
        code = ""
        
        # Extract parameters from operations
        params = {}
        for op in operations:
            params.update(op.get("params", {}))
        
        # Default values if not provided
        grid_size = params.get("grid_size", 6.0)
        system_type = params.get("system_type", "column_beam")
        column_dimensions = params.get("dimensions", [0.4, 0.4])
        beam_depth = params.get("beam_depth", 0.5)
        material = params.get("material", "concrete")
        num_floors = params.get("num_floors", 3)
        grid_x = params.get("grid_x", 5)
        grid_y = params.get("grid_y", 4)
        floor_height = params.get("floor_height", 3.5)
        slab_thickness = params.get("thickness", 0.2)
        
        # Create material layer
        code += """
# Create a layer for structural elements
struct_layer = "Structural"
if not rs.IsLayer(struct_layer):
    rs.AddLayer(struct_layer)

# Create sub-layers for different elements
columns_layer = "Structural::Columns"
if not rs.IsLayer(columns_layer):
    rs.AddLayer(columns_layer)
    
beams_layer = "Structural::Beams"
if not rs.IsLayer(beams_layer):
    rs.AddLayer(beams_layer)
    
slabs_layer = "Structural::Slabs"
if not rs.IsLayer(slabs_layer):
    rs.AddLayer(slabs_layer)
    
bracing_layer = "Structural::Bracing"
if not rs.IsLayer(bracing_layer):
    rs.AddLayer(bracing_layer)

# Material colors
if "{0}" == "concrete":
    material_color = [200, 200, 200]
elif "{0}" == "steel":
    material_color = [100, 100, 120]
elif "{0}" == "timber":
    material_color = [180, 150, 100]
else:
    material_color = [180, 180, 180]
""".format(material)

        # Create structural grid
        code += """
# Create structural grid
grid_size = {0}  # Grid spacing in meters
grid_x = {1}     # Number of grid lines in X direction
grid_y = {2}     # Number of grid lines in Y direction
num_floors = {3} # Number of floors
floor_height = {4} # Height per floor

# Create grid points
grid_points = []
for i in range(grid_x):
    for j in range(grid_y):
        grid_points.append([i * grid_size, j * grid_size, 0])

# Create grid lines to visualize the grid (optional)
grid_lines_layer = "Structural::GridLines"
if not rs.IsLayer(grid_lines_layer):
    rs.AddLayer(grid_lines_layer, [150, 150, 150])
rs.CurrentLayer(grid_lines_layer)

# Horizontal grid lines (X direction)
for j in range(grid_y):
    start_point = [0, j * grid_size, 0]
    end_point = [(grid_x - 1) * grid_size, j * grid_size, 0]
    grid_line = rs.AddLine(start_point, end_point)
    rs.ObjectColor(grid_line, [150, 150, 150])
    add_object_metadata(grid_line, "GridLine_X_{0}".format(j), "Structural grid line in X direction")

# Vertical grid lines (Y direction)
for i in range(grid_x):
    start_point = [i * grid_size, 0, 0]
    end_point = [i * grid_size, (grid_y - 1) * grid_size, 0]
    grid_line = rs.AddLine(start_point, end_point)
    rs.ObjectColor(grid_line, [150, 150, 150])
    add_object_metadata(grid_line, "GridLine_Y_{0}".format(i), "Structural grid line in Y direction")
""".format(grid_size, grid_x, grid_y, num_floors, floor_height)

        # Create columns
        code += """
# Create columns
rs.CurrentLayer(columns_layer)
column_width = {0}
column_depth = {1}
columns = []

for pt in grid_points:
    for floor in range(num_floors + 1):  # +1 for ground floor
        # Column base point at this floor
        base_pt = [pt[0], pt[1], floor * floor_height]
        
        # Create column
        if "{2}" == "concrete" or "{2}" == "timber":
            # Rectangular column for concrete/timber
            column = rs.AddBox(
                rs.MovePlane(rs.WorldXYPlane(), base_pt),
                column_width, column_depth, floor_height
            )
        else:
            # I-beam or H-column for steel
            # Simplified as rectangular for now
            column = rs.AddBox(
                rs.MovePlane(rs.WorldXYPlane(), base_pt),
                column_width, column_depth, floor_height
            )
        
        rs.ObjectColor(column, material_color)
        add_object_metadata(
            column, 
            "Column_X{0}_Y{1}_F{2}".format(int(pt[0]/grid_size), int(pt[1]/grid_size), floor),
            "Structural column at grid ({0}, {1}), floor {2}"
        )
        columns.append({{"id": column, "x": pt[0], "y": pt[1], "floor": floor}})
""".format(column_dimensions[0], column_dimensions[1], material)

        # Create beams
        code += """
# Create beams
rs.CurrentLayer(beams_layer)
beam_depth = {0}
beam_width = {1}

# Function to create a beam between two points
def create_beam(start_pt, end_pt, floor, beam_index):
    # Create a line representing the beam centerline
    beam_line = rs.AddLine(start_pt, end_pt)
    
    # Create a plane aligned with the beam
    beam_dir = rs.VectorCreate(end_pt, start_pt)
    beam_dir = rs.VectorUnitize(beam_dir)
    beam_plane = rs.PlaneFromNormal(start_pt, [0, 0, 1], beam_dir)
    
    # Create rectangular profile
    beam_rect = rs.AddRectangle(
        beam_plane,
        beam_width,
        beam_depth
    )
    
    # Move the rectangle to center it on the line
    rs.MoveObject(beam_rect, [0, 0, -beam_depth/2])
    
    # Create beam by extruding along the path
    beam_crv = rs.AddLine(start_pt, end_pt)
    beam = rs.ExtrudeCurve(beam_rect, beam_crv)
    
    # Clean up temp objects
    rs.DeleteObjects([beam_rect, beam_crv, beam_line])
    
    rs.ObjectColor(beam, material_color)
    add_object_metadata(
        beam, 
        "Beam_{0}_Floor{1}".format(beam_index, floor),
        "Structural beam at floor {0}".format(floor)
    )
    return beam

# Create beams in X direction
beam_index = 0
for j in range(grid_y):
    for i in range(grid_x - 1):
        for floor in range(1, num_floors + 1):  # Start from 1st floor (above ground)
            start_pt = [i * grid_size, j * grid_size, floor * floor_height]
            end_pt = [(i + 1) * grid_size, j * grid_size, floor * floor_height]
            beam = create_beam(start_pt, end_pt, floor, beam_index)
            beam_index += 1

# Create beams in Y direction
for i in range(grid_x):
    for j in range(grid_y - 1):
        for floor in range(1, num_floors + 1):  # Start from 1st floor
            start_pt = [i * grid_size, j * grid_size, floor * floor_height]
            end_pt = [i * grid_size, (j + 1) * grid_size, floor * floor_height]
            beam = create_beam(start_pt, end_pt, floor, beam_index)
            beam_index += 1
""".format(beam_depth, column_dimensions[0] * 0.8)

        # Create floor slabs
        code += """
# Create floor slabs
rs.CurrentLayer(slabs_layer)
slab_thickness = {0}

for floor in range(1, num_floors + 1):  # Start from 1st floor
    # Create the corners of the floor slab
    slab_corners = [
        [0, 0, floor * floor_height - slab_thickness/2],
        [(grid_x - 1) * grid_size, 0, floor * floor_height - slab_thickness/2],
        [(grid_x - 1) * grid_size, (grid_y - 1) * grid_size, floor * floor_height - slab_thickness/2],
        [0, (grid_y - 1) * grid_size, floor * floor_height - slab_thickness/2]
    ]
    
    # Create slab as a box
    slab_width = (grid_x - 1) * grid_size
    slab_length = (grid_y - 1) * grid_size
    slab = rs.AddBox(
        rs.MovePlane(
            rs.WorldXYPlane(), 
            [0, 0, floor * floor_height - slab_thickness]
        ),
        slab_width, slab_length, slab_thickness
    )
    
    # Color slightly different from structural elements
    slab_color = [min(material_color[0] + 20, 255), 
                 min(material_color[1] + 20, 255), 
                 min(material_color[2] + 20, 255)]
    rs.ObjectColor(slab, slab_color)
    
    add_object_metadata(
        slab,
        "FloorSlab_{0}".format(floor),
        "Floor slab at level {0}".format(floor)
    )
""".format(slab_thickness)

        # Create lateral bracing if specified
        code += """
# Create lateral system (bracing)
rs.CurrentLayer(bracing_layer)

if "{0}" == "bracing":
    # Add diagonal bracing on perimeter
    bracing_width = 0.15  # Width of bracing elements
    
    # Function to create a diagonal brace
    def create_brace(start_pt, end_pt, brace_index):
        # Create brace centerline
        brace_line = rs.AddLine(start_pt, end_pt)
        
        # Create a circular profile
        profile = rs.AddCircle(rs.MovePlane(rs.WorldXYPlane(), start_pt), bracing_width/2)
        
        # Extrude along path
        brace = rs.ExtrudeCurve(profile, brace_line)
        
        # Clean up
        rs.DeleteObjects([profile, brace_line])
        
        # Style the brace
        if "{1}" == "steel":
            brace_color = [80, 80, 100]  # Darker for steel
        else:
            brace_color = [min(material_color[0] - 30, 255), 
                         min(material_color[1] - 30, 255), 
                         min(material_color[2] - 30, 255)]
            
        rs.ObjectColor(brace, brace_color)
        add_object_metadata(
            brace,
            "Brace_{0}".format(brace_index),
            "Lateral bracing element"
        )
        return brace
    
    # Add X-bracing on end bays
    brace_index = 0
    
    # Front facade X-bracing
    for i in range(grid_x - 1):
        for floor in range(num_floors):
            # Lower-left to upper-right diagonal
            start_pt = [i * grid_size, 0, floor * floor_height]
            end_pt = [(i + 1) * grid_size, 0, (floor + 1) * floor_height]
            brace = create_brace(start_pt, end_pt, brace_index)
            brace_index += 1
            
            # Upper-left to lower-right diagonal
            start_pt = [i * grid_size, 0, (floor + 1) * floor_height]
            end_pt = [(i + 1) * grid_size, 0, floor * floor_height]
            brace = create_brace(start_pt, end_pt, brace_index)
            brace_index += 1
    
    # Back facade X-bracing
    for i in range(grid_x - 1):
        for floor in range(num_floors):
            # Lower-left to upper-right diagonal
            start_pt = [i * grid_size, (grid_y - 1) * grid_size, floor * floor_height]
            end_pt = [(i + 1) * grid_size, (grid_y - 1) * grid_size, (floor + 1) * floor_height]
            brace = create_brace(start_pt, end_pt, brace_index)
            brace_index += 1
            
            # Upper-left to lower-right diagonal
            start_pt = [i * grid_size, (grid_y - 1) * grid_size, (floor + 1) * floor_height]
            end_pt = [(i + 1) * grid_size, (grid_y - 1) * grid_size, floor * floor_height]
            brace = create_brace(start_pt, end_pt, brace_index)
            brace_index += 1
            
    # Left side X-bracing
    for j in range(grid_y - 1):
        for floor in range(num_floors):
            # Lower-left to upper-right diagonal
            start_pt = [0, j * grid_size, floor * floor_height]
            end_pt = [0, (j + 1) * grid_size, (floor + 1) * floor_height]
            brace = create_brace(start_pt, end_pt, brace_index)
            brace_index += 1
            
            # Upper-left to lower-right diagonal
            start_pt = [0, j * grid_size, (floor + 1) * floor_height]
            end_pt = [0, (j + 1) * grid_size, floor * floor_height]
            brace = create_brace(start_pt, end_pt, brace_index)
            brace_index += 1
            
    # Right side X-bracing
    for j in range(grid_y - 1):
        for floor in range(num_floors):
            # Lower-left to upper-right diagonal
            start_pt = [(grid_x - 1) * grid_size, j * grid_size, floor * floor_height]
            end_pt = [(grid_x - 1) * grid_size, (j + 1) * grid_size, (floor + 1) * floor_height]
            brace = create_brace(start_pt, end_pt, brace_index)
            brace_index += 1
            
            # Upper-left to lower-right diagonal
            start_pt = [(grid_x - 1) * grid_size, j * grid_size, (floor + 1) * floor_height]
            end_pt = [(grid_x - 1) * grid_size, (j + 1) * grid_size, floor * floor_height]
            brace = create_brace(start_pt, end_pt, brace_index)
            brace_index += 1
""".format(system_type, material)

        return code
    
    def _generate_parametric_form_rhino_code(self, operations: List[Dict[str, Any]]) -> str:
        """Generate Rhino code for parametric form generation operations."""
        # Placeholder for demo
        code = """
# Placeholder for parametric form generation code
print("Parametric form generation would happen here")
"""
        return code
    
    def _generate_grasshopper_code(self, operations: List[Dict[str, Any]]) -> str:
        """Generate Grasshopper Python component code from operations."""
        # Get the design domain from the first operation
        design_domain = operations[0]["params"]["design_domain"]
        
        # Extracting common parameters
        params = {}
        for op in operations:
            params.update(op.get("params", {}))
        
        # Start with common GH code based on the design domain
        gh_code = """
import Rhino.Geometry as rg
import scriptcontext as sc
import Grasshopper.Kernel.Data.GH_Path as GH_Path
import Grasshopper.DataTree as DataTree
import System
import math
import random

# This is a parametric {0} design generator
# Input parameters (can be connected to Grasshopper sliders/components)
""".format(design_domain)

        # Rest of GH code would be similar to Rhino code but adapted for Grasshopper
        # Placeholder for demo
        gh_code += """
# Placeholder for Grasshopper code generation
# Would be specific to the {0} design domain

# Set outputs
output = "{0} design generation would happen in Grasshopper"
""".format(design_domain)
        
        return gh_code
    
    def interpret_brief(self, brief: str) -> Dict[str, Any]:
        """
        Main method to interpret a design brief and generate a structured response.
        
        Args:
            brief: A natural language design brief
            
        Returns:
            A dictionary containing the interpreted brief with operations
        """
        try:
            logger.info("Processing design brief: {0}".format(brief))
            
            # Extract keywords from brief
            keywords = self._extract_keywords(brief)
            logger.debug("Extracted keywords: {0}".format(keywords))
            
            # Derive parameters from keywords
            params = self._derive_parameters(keywords)
            logger.debug("Derived parameters: {0}".format(params))
            
            # Generate operations sequence
            operations = self._generate_operations(params)
            logger.debug("Generated {0} operations".format(len(operations)))
            
            # Generate code
            rhino_code = self._generate_rhino_code(operations)
            grasshopper_code = self._generate_grasshopper_code(operations)
            
            # Create the response
            response = {
                "brief": brief,
                "interpretation": {
                    "keywords": keywords,
                    "parameters": params
                },
                "operations": operations,
                "code": {
                    "rhino": rhino_code,
                    "grasshopper": grasshopper_code
                }
            }
            
            return response
            
        except Exception as e:
            logger.error("Error interpreting design brief: {0}".format(str(e)))
            return {
                "error": str(e),
                "brief": brief
            }


def register_design_brief_tool(app):
    """Register the design brief interpreter with the MCP server."""
    interpreter = DesignBriefInterpreter()
    
    @app.tool()
    def interpret_design_brief(ctx, brief: str) -> str:
        """
        Interpret a natural language design brief and convert it into
        parametric operations and code for Rhino and Grasshopper.
        
        Args:
            brief: A natural language design brief (e.g., "I need a dynamic façade that responds to sun angle and frames views")
            
        Returns:
            A JSON string containing the interpreted brief, operations sequence, and generated code
        """
        response = interpreter.interpret_brief(brief)
        return json.dumps(response, indent=2) 