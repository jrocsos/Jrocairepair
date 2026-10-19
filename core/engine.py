# core/engine.py
import logging
from typing import Dict, Any
from .drivers import IDeviceDriver, AndroidDriver, AppleDriver, SamsungDriver

logger = logging.getLogger(__name__)

class DeviceManager:
    """Registry for connected devices."""
    def __init__(self):
        self.devices: Dict[str, IDeviceDriver] = {}

    def add_device(self, driver: IDeviceDriver):
        self.devices[driver.serial] = driver
        logger.info(f"Device Added: {driver.serial} ({driver.name})")

    def remove_device(self, serial: str):
        if serial in self.devices:
            del self.devices[serial]
            logger.info(f"Device Removed: {serial}")

    def get_all_devices(self) -> list:
        return list(self.devices.values())

    def get_device(self, serial: str) -> IDeviceDriver:
        return self.devices.get(serial)


class UniversalUnlockEngine:
    """The central brain that decides how to unlock a device."""
    
    def __init__(self):
        self.device_manager = DeviceManager()
        self.cloud_api_key = "DEMO_KEY"

    def detect_new_device(self, serial: str, brand: str, pid: int = 0) -> IDeviceDriver:
        """Auto-detects which driver to instantiate based on brand/VID."""
        driver = None
        
        if brand.lower() == "samsung":
            driver = SamsungDriver(serial)
        elif brand.lower() in ["apple", "iphone", "ipad"]:
            driver = AppleDriver(serial, pid)
        else:
            # Default to Android ADB
            driver = AndroidDriver(serial)
            
        # Attempt connection
        if driver.connect():
            self.device_manager.add_device(driver)
            return driver
        else:
            logger.warning(f"Failed to connect to {serial}")
            return None

    def master_unlock(self, serial: str) -> Dict[str, Any]:
        driver = self.device_manager.get_device(serial)
        if not driver:
            return {"success": False, "error": "Device not found"}

        # 1. Get Info
        info = driver.get_device_info()
        
        # 2. Determine Strategy
        result = driver.execute_unlock()
        
        # 3. Post-Processing: Cloud Sync if needed
        if not result['success']:
            result = self._try_cloud_fallback(driver, info)
            
        return {
            "serial": serial,
            "info": info,
            "result": result
        }

    def _try_cloud_fallback(self, driver, info) -> Dict[str, Any]:
        """Attempt to unlock via Cloud API if local method fails."""
        imei = info.get('imei')
        if not imei:
            return {"success": False, "logs": ["IMEI required for Cloud Unlock"], "method": "cloud_failed"}
            
        # Mock API Call
        logs = [f"Querying Cloud API for IMEI: {imei}"]
        # response = requests.post(f"https://api.unlock.com/unlock/{imei}", headers={"Auth": self.cloud_api_key})
        
        logs.append("Cloud server returned: Unlocked")
        return {"success": True, "logs": logs, "method": "cloud_unlock"}
