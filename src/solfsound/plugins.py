"""
Plugin System

Extensible plugin architecture for adding custom processors and features.
"""

import logging
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import inspect

logger = logging.getLogger(__name__)


class PluginInterface(ABC):
    """Base plugin interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass

    @abstractmethod
    def initialize(self):
        """Initialize the plugin."""
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup resources."""
        pass


class AudioProcessorPlugin(PluginInterface):
    """Base class for audio processor plugins."""

    @abstractmethod
    def process(self, audio_file: Path, parameters: Dict[str, Any]) -> Any:
        """
        Process audio file.

        Args:
            audio_file: Input audio file path
            parameters: Processing parameters

        Returns:
            Processing result
        """
        pass

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        """
        Get parameters schema (JSON Schema format).

        Returns:
            Parameters schema
        """
        return {}


class AnalyzerPlugin(PluginInterface):
    """Base class for audio analyzer plugins."""

    @abstractmethod
    def analyze(self, audio_file: Path, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze audio file.

        Args:
            audio_file: Input audio file path
            parameters: Analysis parameters

        Returns:
            Analysis results
        """
        pass


class ExporterPlugin(PluginInterface):
    """Base class for export plugins."""

    @abstractmethod
    def export(self, data: Any, output_file: Path, parameters: Dict[str, Any]) -> Path:
        """
        Export data to file.

        Args:
            data: Data to export
            output_file: Output file path
            parameters: Export parameters

        Returns:
            Path to exported file
        """
        pass


class PluginManager:
    """Plugin manager for loading and managing plugins."""

    def __init__(self, plugins_dir: Optional[Path] = None):
        """
        Initialize plugin manager.

        Args:
            plugins_dir: Directory containing plugins
        """
        if plugins_dir is None:
            plugins_dir = Path.home() / '.solfsound' / 'plugins'

        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        # Loaded plugins
        self.plugins: Dict[str, PluginInterface] = {}

        # Plugin categories
        self.processors: Dict[str, AudioProcessorPlugin] = {}
        self.analyzers: Dict[str, AnalyzerPlugin] = {}
        self.exporters: Dict[str, ExporterPlugin] = {}

        logger.info(f"Plugin manager initialized: {self.plugins_dir}")

    def load_plugin(self, plugin_path: Path) -> Optional[PluginInterface]:
        """
        Load a plugin from file.

        Args:
            plugin_path: Path to plugin file (.py)

        Returns:
            Loaded plugin instance or None
        """
        try:
            # Load module
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_path.stem}",
                plugin_path
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find plugin classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Skip base classes
                    if obj in [PluginInterface, AudioProcessorPlugin, AnalyzerPlugin, ExporterPlugin]:
                        continue

                    # Check if it's a plugin
                    if issubclass(obj, PluginInterface) and obj != PluginInterface:
                        # Instantiate
                        plugin = obj()

                        # Initialize
                        plugin.initialize()

                        # Store
                        self.plugins[plugin.name] = plugin

                        # Categorize
                        if isinstance(plugin, AudioProcessorPlugin):
                            self.processors[plugin.name] = plugin
                        elif isinstance(plugin, AnalyzerPlugin):
                            self.analyzers[plugin.name] = plugin
                        elif isinstance(plugin, ExporterPlugin):
                            self.exporters[plugin.name] = plugin

                        logger.info(f"Plugin loaded: {plugin.name} v{plugin.version}")
                        return plugin

        except Exception as e:
            logger.error(f"Error loading plugin from {plugin_path}: {e}")

        return None

    def load_all_plugins(self):
        """Load all plugins from plugins directory."""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return

        plugin_files = list(self.plugins_dir.glob("*.py"))

        if not plugin_files:
            logger.info("No plugins found")
            return

        loaded_count = 0

        for plugin_file in plugin_files:
            if plugin_file.stem.startswith('_'):
                continue

            if self.load_plugin(plugin_file):
                loaded_count += 1

        logger.info(f"Loaded {loaded_count}/{len(plugin_files)} plugins")

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Plugin name

        Returns:
            True if unloaded successfully
        """
        plugin = self.plugins.get(plugin_name)

        if not plugin:
            logger.warning(f"Plugin not found: {plugin_name}")
            return False

        try:
            # Cleanup
            plugin.cleanup()

            # Remove from storage
            del self.plugins[plugin_name]

            # Remove from categories
            if plugin_name in self.processors:
                del self.processors[plugin_name]
            if plugin_name in self.analyzers:
                del self.analyzers[plugin_name]
            if plugin_name in self.exporters:
                del self.exporters[plugin_name]

            logger.info(f"Plugin unloaded: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Get plugin by name."""
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> List[Dict[str, str]]:
        """
        List all loaded plugins.

        Returns:
            List of plugin info dictionaries
        """
        return [
            {
                'name': plugin.name,
                'version': plugin.version,
                'description': plugin.description,
                'type': plugin.__class__.__bases__[0].__name__
            }
            for plugin in self.plugins.values()
        ]

    def execute_processor(
        self,
        processor_name: str,
        audio_file: Path,
        parameters: Dict[str, Any] = None
    ) -> Any:
        """
        Execute an audio processor plugin.

        Args:
            processor_name: Processor plugin name
            audio_file: Input audio file
            parameters: Processing parameters

        Returns:
            Processing result
        """
        processor = self.processors.get(processor_name)

        if not processor:
            raise ValueError(f"Processor plugin not found: {processor_name}")

        logger.info(f"Executing processor: {processor_name}")

        try:
            result = processor.process(audio_file, parameters or {})
            logger.info(f"Processor completed: {processor_name}")
            return result

        except Exception as e:
            logger.error(f"Processor failed: {processor_name} - {e}")
            raise

    def execute_analyzer(
        self,
        analyzer_name: str,
        audio_file: Path,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute an analyzer plugin.

        Args:
            analyzer_name: Analyzer plugin name
            audio_file: Input audio file
            parameters: Analysis parameters

        Returns:
            Analysis results
        """
        analyzer = self.analyzers.get(analyzer_name)

        if not analyzer:
            raise ValueError(f"Analyzer plugin not found: {analyzer_name}")

        logger.info(f"Executing analyzer: {analyzer_name}")

        try:
            result = analyzer.analyze(audio_file, parameters or {})
            logger.info(f"Analyzer completed: {analyzer_name}")
            return result

        except Exception as e:
            logger.error(f"Analyzer failed: {analyzer_name} - {e}")
            raise


# Global plugin manager instance
_plugin_manager = None


def get_plugin_manager(plugins_dir: Optional[Path] = None) -> PluginManager:
    """Get the global plugin manager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager(plugins_dir)
        _plugin_manager.load_all_plugins()
    return _plugin_manager


# Example plugin template (for documentation)
EXAMPLE_PLUGIN_TEMPLATE = '''"""
Example SolfSound Plugin

This is a template for creating custom plugins.
"""

from pathlib import Path
from typing import Dict, Any
from solfsound.plugins import AudioProcessorPlugin


class ExampleProcessor(AudioProcessorPlugin):
    """Example audio processor plugin."""

    @property
    def name(self) -> str:
        return "example_processor"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "An example audio processor"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "parameter1": {"type": "string"},
                "parameter2": {"type": "number"},
            }
        }

    def initialize(self):
        """Initialize plugin."""
        print(f"Initializing {self.name}")

    def cleanup(self):
        """Cleanup resources."""
        print(f"Cleaning up {self.name}")

    def process(self, audio_file: Path, parameters: Dict[str, Any]) -> Any:
        """Process audio file."""
        print(f"Processing: {audio_file}")
        print(f"Parameters: {parameters}")

        # Your processing logic here

        return {"success": True}
'''
