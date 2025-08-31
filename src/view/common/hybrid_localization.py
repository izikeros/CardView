"""
Hybrid Localization System for CardView Plugin

This module provides a hybrid translation system that combines Gramps' built-in
localization with plugin-specific translations. It allows the plugin to use
existing Gramps translations while adding its own translated strings.

Usage:
    from view.common.hybrid_localization import _, _plugin

    # For strings that might exist in Gramps
    translated = _("Edit")

    # For plugin-specific strings
    plugin_string = _plugin("Card Statistics")
"""

import os
import gettext
from gramps.gen.const import GRAMPS_LOCALE as glocale


class HybridTranslation:
    """
    Hybrid translation class that tries plugin translations first,
    then falls back to Gramps translations.
    """

    def __init__(self):
        """Initialize the hybrid translation system."""
        self.gramps_gettext = glocale.translation.sgettext
        self.plugin_gettext = self._load_plugin_translations()
        self._current_language = self._get_current_language()

    def _get_current_language(self):
        """Get the current language code from Gramps locale."""
        try:
            return glocale.language[0][:2] if glocale.language else "en"
        except (IndexError, AttributeError):
            return "en"

    def _load_plugin_translations(self):
        """
        Load plugin-specific translations if available.

        Returns:
            function: Translation function for plugin strings
        """
        try:
            # Get the plugin root directory
            plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            locale_dir = os.path.join(plugin_dir, "..", "..", "locale")

            # Try to load plugin translations
            translation = gettext.translation(
                "cardview",
                locale_dir,
                languages=[self._current_language],
                fallback=True,
            )
            return translation.gettext
        except Exception:
            # Return identity function if loading fails
            return lambda x: x

    def _(self, text):
        """
        Smart translation with fallback.

        Tries plugin translation first, then falls back to Gramps.

        Args:
            text (str): Text to translate

        Returns:
            str: Translated text
        """
        # Try plugin translation first
        plugin_result = self.plugin_gettext(text)
        if plugin_result != text:
            return plugin_result

        # Fall back to Gramps translation
        return self.gramps_gettext(text)

    def _plugin_only(self, text):
        """
        Plugin-specific translation only.

        Use this for strings that are definitely plugin-specific
        and won't exist in Gramps translations.

        Args:
            text (str): Text to translate

        Returns:
            str: Translated text from plugin translations only
        """
        return self.plugin_gettext(text)

    def reload_translations(self):
        """
        Reload translations (useful if language changed).
        """
        self._current_language = self._get_current_language()
        self.plugin_gettext = self._load_plugin_translations()


# Global instance for easy import
_translator = HybridTranslation()

# Export the translation functions
_ = _translator._
_plugin = _translator._plugin_only

# Export the translator instance for advanced usage
__all__ = ["_", "_plugin", "_translator"]
