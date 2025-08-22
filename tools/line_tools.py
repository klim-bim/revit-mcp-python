# tools/line_tools.py
# -*- coding: utf-8 -*-
"""Tools for line-based elements"""

from mcp.server.fastmcp import Context
from .utils import format_response

def register_line_tools(mcp, revit_get, revit_post, revit_image=None):
    @mcp.tool()
    async def create_line_based_element(
        start: dict,
        end: dict,
        level_name: str,
        wall_type: str = "Generic - 200mm",
        ctx: Context = None
    ) -> str:
        """
        Creates a wall between two points.

        Args:
            start: {"x":..., "y":..., "z":...}
            end:   {"x":..., "y":..., "z":...}
            level_name: Name of the Revit level
            wall_type: Name of the wall type
        """
        payload = {
            "category": "Walls",
            "start": start,
            "end": end,
            "level_name": level_name,
            "properties": {"wall_type": wall_type}
        }
        response = await revit_post("/create_line_based_element/", payload, ctx)
        return format_response(response)
    
    
