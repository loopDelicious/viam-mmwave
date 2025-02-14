import asyncio
import time
import logging
from typing import Any, ClassVar, Final, List, Mapping, Optional, Sequence, Dict
from typing_extensions import Self
from viam.components.sensor import *
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import Geometry, ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, ValueTypes
from viam.logging import getLogger

from serial import Serial
from LD2410 import LD2410, PARAM_BAUD_256000

LOGGER = getLogger(__name__)

class Mmwave(Sensor, EasyResource):
    MODEL: ClassVar[Model] = Model(ModelFamily("joyce", "mmwave"), "mmwave")

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Sensor component and initializes LD2410.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        instance = super().new(config, dependencies)
        instance.radar = None  # Initialize radar as None
        instance.reconfigure(config, dependencies)  # Call reconfigure to initialize sensor
        return instance
        # return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        return []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        try:
            if self.radar:
                self.radar.stop()  # Stop previous instance if reconfiguring
                LOGGER.info("Stopping previous LD2410 instance...")

            # Initialize LD2410 radar
            self.radar = LD2410("/dev/ttyUSB0", PARAM_BAUD_256000, verbosity=logging.INFO)
            self.radar.start()
            time.sleep(2)  # Allow time for initialization
            LOGGER.info("LD2410 radar initialized successfully")
        except Exception as e:
            LOGGER.error(f"Error initializing LD2410 radar: {e}")
            self.radar = None
        # return super().reconfigure(config, dependencies)

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, Any]:  # ✅ Changed return type to Mapping[str, Any]
        """Fetches data from the LD2410 sensor and returns motion/distance readings."""
        
        if not self.radar:
            logging.error("Radar is not initialized")
            return {
                "detection_status": "Error",
                "moving_distance_cm": 0,
                "moving_energy": 0,
                "static_distance_cm": 0,
                "static_energy": 0,
                "overall_distance_cm": 0
            }

        data = self.radar.get_data()

        if data and isinstance(data[0], list):
            detection_type, move_dist, move_energy, static_dist, static_energy, overall_dist = data[0]

            # Map detection type to readable string
            detection_status = {
                0: "No Target",
                1: "Moving Target",
                2: "Static Target",
                3: "Moving and Static Targets"
            }.get(detection_type, "Unknown")

            # ✅ Return raw values instead of `SensorReading`
            return {
                "detection_status": detection_status,
                "moving_distance_cm": move_dist,
                "moving_energy": move_energy,
                "static_distance_cm": static_dist,
                "static_energy": static_energy,
                "overall_distance_cm": overall_dist
            }

        logging.warning("No valid data received from LD2410.")
        return {
            "detection_status": "No Data",
            "moving_distance_cm": 0,
            "moving_energy": 0,
            "static_distance_cm": 0,
            "static_energy": 0,
            "overall_distance_cm": 0
        }

            # return {
            #     "motion_detected": True,
            #     "distance_cm": 150,
            #     "signal_strength": 85
            # }

        async def do_command(
            self,
            command: Mapping[str, ValueTypes],
            *,
            timeout: Optional[float] = None,
            **kwargs
        ) -> Mapping[str, ValueTypes]:
            raise NotImplementedError()

        async def get_geometries(
            self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None
        ) -> List[Geometry]:
            raise NotImplementedError()


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
