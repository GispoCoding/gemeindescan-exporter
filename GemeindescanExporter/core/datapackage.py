#  Gispo Ltd., hereby disclaims all copyright interest in the program GemeindescanExporter
#  Copyright (C) 2020 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of GemeindescanExporter.
#
#  GemeindescanExporter is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  GemeindescanExporter is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with GemeindescanExporter.  If not, see <https://www.gnu.org/licenses/>.
import json
import logging
from typing import List, Optional, Tuple

from ..model.config import Config
from ..model.snapshot import Snapshot, Resource, Legend
from ..model.styled_layer import StyledLayer
from ..qgis_plugin_tools.tools.resources import plugin_name, resources_path

LOGGER = logging.getLogger(plugin_name())


class DatapackageWriter:

    def __init__(self, config: Config, snapshot_template: Optional[Snapshot] = None,
                 legend_template: Optional[Legend] = None) -> None:
        self.config = config

        snap_temp, leg_temp = self._load_default_template()
        self.snapshot_template: Snapshot = snapshot_template if snapshot_template is not None else snap_temp
        self.legend_template: Legend = legend_template if legend_template is not None else leg_temp

    def _load_default_template(self) -> Tuple[Snapshot, Legend]:
        with open(resources_path('templates', 'snapshot-template.json')) as f:
            template = json.load(f)

        return Snapshot.from_dict(template['snapshot']), Legend.from_dict(template['legend'])

    def create_snapshot(self, styled_layers: List[StyledLayer]):
        snapshot = Snapshot.from_dict(self.snapshot_template.to_dict())

        LOGGER.debug('Updating resources')
        initial_resources = snapshot.resources
        snapshot.resources = []

        for styled_layer in styled_layers:
            resource = Resource(styled_layer.resource_name, mediatype='application/geo+json',
                                data=styled_layer.get_geojson_data())
            snapshot.resources.append(resource)

        snapshot.resources += initial_resources
        snapshot.views[0].resources = [res.name for res in snapshot.resources]

        LOGGER.debug('Updating legends')
        for styled_layer in styled_layers:
            snapshot.views[0].spec.legend += styled_layer.legend

        return snapshot