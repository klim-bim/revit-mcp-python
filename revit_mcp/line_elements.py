# -*- coding: UTF-8 -*-
"""
Line-based element creation (e.g. Walls)
"""

from pyrevit import routes, revit, DB
import json
import logging

logger = logging.getLogger(__name__)

def register_line_routes(api):
    """Register line-based element routes"""

    @api.route('/create_line_based_element/', methods=["POST"])
    def create_line_based_element(doc, request):
        """
        Creates a line-based element (e.g. Wall) between two points.
        JSON body:
        {
          "category": "Walls",
          "start": {"x":0,"y":0,"z":0},
          "end": {"x":5000,"y":0,"z":0},
          "level_name": "Ebene 0",
          "properties": {"wall_type": "Basic Wall: Generic - 200mm"}
        }
        """
        try:
            data = json.loads(request.data) if isinstance(request.data, str) else request.data
            category = data.get("category")
            start = data.get("start")
            end = data.get("end")
            level_name = data.get("level_name")
            props = data.get("properties", {})

            if not category or not start or not end or not level_name:
                return routes.make_response(
                    data={"error": "Missing required parameters"},
                    status=400
                )

            # Level suchen
            level = None
            for lvl in DB.FilteredElementCollector(doc).OfClass(DB.Level):
                if lvl.Name == level_name:
                    level = lvl
                    break
            if not level:
                return routes.make_response(
                    data={"error": "Level not found: {}".format(level_name)},
                    status=400
                )

            # WallType finden
            wall_type_name = props.get("wall_type", "Generic - 200mm")
            wall_type = None
            for wt in DB.FilteredElementCollector(doc).OfClass(DB.WallType):
                if wt.Name == wall_type_name:
                    wall_type = wt
                    break
            if not wall_type:
                return routes.make_response(
                    data={"error": "WallType not found: {}".format(wall_type_name)},
                    status=400
                )

            # Geometrie erzeugen
            start_pt = DB.XYZ(float(start["x"]), float(start["y"]), float(start["z"]))
            end_pt = DB.XYZ(float(end["x"]), float(end["y"]), float(end["z"]))
            line = DB.Line.CreateBound(start_pt, end_pt)

            # Transaktion starten
            t = DB.Transaction(doc, "Create Line-Based Element")
            t.Start()
            try:
                new_wall = DB.Wall.Create(doc, line, wall_type.Id, level.Id, 3000.0, 0.0, False, False)
                t.Commit()
                return routes.make_response(
                    data={"status": "success", "element_id": new_wall.Id.IntegerValue}
                )
            except Exception as tx_error:
                if t.HasStarted() and not t.HasEnded():
                    t.RollBack()
                raise tx_error

        except Exception as e:
            logger.error("Wall creation failed: {}".format(str(e)))
            return routes.make_response(data={"error": str(e)}, status=500)
