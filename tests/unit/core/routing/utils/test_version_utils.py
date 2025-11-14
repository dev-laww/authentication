"""
Unit tests for version utilities and VersionRegistry.
"""

import pytest
from semver import Version

from authentication.core.routing.utils.version import parse_version, VersionRegistry


# Test parse_version function
def test_parse_version_full_semver():
    """parse_version parses full semantic version."""
    version = parse_version("1.2.3")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.prerelease is None
    assert version.build is None


def test_parse_version_with_v_prefix():
    """parse_version handles 'v' prefix."""
    version = parse_version("v1.2.3")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3


def test_parse_version_without_patch():
    """parse_version handles version without patch number."""
    version = parse_version("1.2")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 0


def test_parse_version_without_minor():
    """parse_version handles version without minor number."""
    version = parse_version("1")
    assert version.major == 1
    assert version.minor == 0
    assert version.patch == 0


def test_parse_version_with_prerelease():
    """parse_version handles prerelease identifier."""
    version = parse_version("1.2.3-alpha")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.prerelease == "alpha"


def test_parse_version_with_build():
    """parse_version handles build metadata."""
    version = parse_version("1.2.3+build.123")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.build == "build.123"


def test_parse_version_with_prerelease_and_build():
    """parse_version handles both prerelease and build."""
    version = parse_version("1.2.3-alpha+build.123")
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.prerelease == "alpha"
    assert version.build == "build.123"


def test_parse_version_invalid_format():
    """parse_version raises ValueError for invalid format."""
    with pytest.raises(ValueError, match="Invalid version string"):
        parse_version("invalid")


def test_parse_version_empty_string():
    """parse_version raises ValueError for empty string."""
    with pytest.raises(ValueError):
        parse_version("")


# Test VersionRegistry singleton
def test_version_registry_is_singleton():
    """VersionRegistry is a singleton."""
    registry1 = VersionRegistry()
    registry2 = VersionRegistry()

    assert registry1 is registry2


def test_version_registry_get_instance():
    """VersionRegistry.get_instance returns singleton."""
    registry1 = VersionRegistry.get_instance()
    registry2 = VersionRegistry.get_instance()

    assert registry1 is registry2


# Test VersionRegistry.add_version
def test_add_version_with_string():
    """add_version accepts version string."""
    registry = VersionRegistry()
    registry.clear()

    result = registry.add_version("1.0.0")
    assert result is True
    assert registry.has_version("1.0.0")


def test_add_version_with_version_object():
    """add_version accepts Version object."""
    registry = VersionRegistry()
    registry.clear()

    version = Version.parse("2.0.0")
    result = registry.add_version(version)
    assert result is True
    assert registry.has_version(version)


def test_add_version_returns_false_if_exists():
    """add_version returns False if version already exists."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    result = registry.add_version("1.0.0")

    assert result is False


def test_add_version_sets_default():
    """add_version sets default version when set_default=True."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0", set_default=True)
    assert registry.default_version == Version.parse("1.0.0")


def test_add_version_sets_first_as_default():
    """add_version sets first version as default if none exists."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    assert registry.default_version == Version.parse("1.0.0")


# Test VersionRegistry.remove_version
def test_remove_version():
    """remove_version removes version from registry."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    result = registry.remove_version("1.0.0")

    assert result is True
    assert not registry.has_version("1.0.0")


def test_remove_version_returns_false_if_not_exists():
    """remove_version returns False if version doesn't exist."""
    registry = VersionRegistry()
    registry.clear()

    result = registry.remove_version("1.0.0")
    assert result is False


def test_remove_version_clears_default():
    """remove_version clears default if it was the default."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0", set_default=True)
    registry.remove_version("1.0.0")

    assert registry.default_version is None


# Test VersionRegistry.has_version
def test_has_version():
    """has_version checks if version exists."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    assert registry.has_version("1.0.0")
    assert not registry.has_version("2.0.0")


# Test VersionRegistry.is_valid
def test_is_valid_returns_true_for_registered_version():
    """is_valid returns True for registered, non-deprecated version."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    assert registry.is_valid("1.0.0")


def test_is_valid_returns_false_for_deprecated_version():
    """is_valid returns False for deprecated version."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.deprecate_version("1.0.0")
    assert not registry.is_valid("1.0.0")


def test_is_valid_returns_false_for_unregistered_version():
    """is_valid returns False for unregistered version."""
    registry = VersionRegistry()
    registry.clear()

    assert not registry.is_valid("1.0.0")


# Test VersionRegistry.get_versions
def test_get_versions_returns_all_versions():
    """get_versions returns all registered versions."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.add_version("3.0.0")

    versions = registry.get_versions()
    assert len(versions) == 3


def test_get_versions_excludes_deprecated():
    """get_versions excludes deprecated versions by default."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.deprecate_version("2.0.0")

    versions = registry.get_versions()
    assert len(versions) == 1
    assert versions[0] == Version.parse("1.0.0")


def test_get_versions_includes_deprecated_when_requested():
    """get_versions includes deprecated versions when requested."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.deprecate_version("2.0.0")

    versions = registry.get_versions(include_deprecated=True)
    assert len(versions) == 2


def test_get_versions_returns_sorted():
    """get_versions returns sorted versions."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("3.0.0")
    registry.add_version("1.0.0")
    registry.add_version("2.0.0")

    versions = registry.get_versions()
    assert versions == [Version.parse("1.0.0"), Version.parse("2.0.0"), Version.parse("3.0.0")]


# Test VersionRegistry.default_version property
def test_default_version_property():
    """default_version property returns current default."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0", set_default=True)
    assert registry.default_version == Version.parse("1.0.0")


def test_default_version_setter():
    """default_version setter sets default version."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.default_version = "2.0.0"

    assert registry.default_version == Version.parse("2.0.0")


def test_default_version_setter_raises_for_unregistered():
    """default_version setter raises ValueError for unregistered version."""
    registry = VersionRegistry()
    registry.clear()

    with pytest.raises(ValueError, match="not found in registry"):
        registry.default_version = "1.0.0"


# Test VersionRegistry.latest_version
def test_latest_version_returns_highest():
    """latest_version returns highest version."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.add_version("1.5.0")

    assert registry.latest_version == Version.parse("2.0.0")


def test_latest_version_returns_none_when_empty():
    """latest_version returns None when no versions."""
    registry = VersionRegistry()
    registry.clear()

    assert registry.latest_version is None


def test_latest_version_excludes_deprecated():
    """latest_version excludes deprecated versions."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.deprecate_version("2.0.0")

    assert registry.latest_version == Version.parse("1.0.0")


# Test VersionRegistry.latest_stable_version
def test_latest_stable_version_returns_highest_stable():
    """latest_stable_version returns highest stable version."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0-alpha")
    registry.add_version("1.5.0")

    assert registry.latest_stable_version == Version.parse("1.5.0")


def test_latest_stable_version_returns_none_when_no_stable():
    """latest_stable_version returns None when no stable versions."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0-alpha")
    registry.add_version("2.0.0-beta")

    assert registry.latest_stable_version is None


# Test VersionRegistry.deprecate_version
def test_deprecate_version():
    """deprecate_version marks version as deprecated."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    result = registry.deprecate_version("1.0.0")

    assert result is True
    assert registry.is_deprecated("1.0.0")


def test_deprecate_version_returns_false_if_not_exists():
    """deprecate_version returns False if version doesn't exist."""
    registry = VersionRegistry()
    registry.clear()

    result = registry.deprecate_version("1.0.0")
    assert result is False


# Test VersionRegistry.undeprecate_version
def test_undeprecate_version():
    """undeprecate_version removes deprecation status."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.deprecate_version("1.0.0")
    result = registry.undeprecate_version("1.0.0")

    assert result is True
    assert not registry.is_deprecated("1.0.0")


def test_undeprecate_version_returns_false_if_not_exists():
    """undeprecate_version returns False if version doesn't exist."""
    registry = VersionRegistry()
    registry.clear()

    result = registry.undeprecate_version("1.0.0")
    assert result is False


# Test VersionRegistry.is_deprecated
def test_is_deprecated():
    """is_deprecated checks if version is deprecated."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    assert not registry.is_deprecated("1.0.0")

    registry.deprecate_version("1.0.0")
    assert registry.is_deprecated("1.0.0")


# Test VersionRegistry.get_versions_in_range
def test_get_versions_in_range():
    """get_versions_in_range returns versions within range."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("1.5.0")
    registry.add_version("2.0.0")
    registry.add_version("2.5.0")
    registry.add_version("3.0.0")

    versions = registry.get_versions_in_range("1.0.0", "2.0.0")
    assert len(versions) == 3
    assert Version.parse("1.0.0") in versions
    assert Version.parse("1.5.0") in versions
    assert Version.parse("2.0.0") in versions


def test_get_versions_in_range_includes_deprecated_when_requested():
    """get_versions_in_range includes deprecated when requested."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.deprecate_version("2.0.0")

    versions = registry.get_versions_in_range("1.0.0", "2.0.0", include_deprecated=True)
    assert len(versions) == 2


# Test VersionRegistry.clear
def test_clear_removes_all_versions():
    """clear removes all versions."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.clear()

    assert registry.count() == 0
    assert registry.default_version is None


# Test VersionRegistry.count
def test_count_returns_number_of_versions():
    """count returns number of registered versions."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.add_version("3.0.0")

    assert registry.count() == 3


def test_count_excludes_deprecated():
    """count excludes deprecated versions by default."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.deprecate_version("2.0.0")

    assert registry.count() == 1


def test_count_includes_deprecated_when_requested():
    """count includes deprecated when requested."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.deprecate_version("2.0.0")

    assert registry.count(include_deprecated=True) == 2


# Test VersionRegistry properties
def test_all_versions_property():
    """all_versions property returns all non-deprecated versions."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.deprecate_version("2.0.0")

    versions = registry.all_versions
    assert len(versions) == 1
    assert versions[0] == Version.parse("1.0.0")


def test_deprecated_versions_property():
    """deprecated_versions property returns all deprecated versions."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0")
    registry.add_version("2.0.0")
    registry.deprecate_version("2.0.0")

    versions = registry.deprecated_versions
    assert len(versions) == 1
    assert versions[0] == Version.parse("2.0.0")


# Test VersionRegistry.__repr__
def test_version_registry_repr():
    """VersionRegistry has informative __repr__."""
    registry = VersionRegistry()
    registry.clear()

    registry.add_version("1.0.0", set_default=True)
    repr_str = repr(registry)

    assert "VersionRegistry" in repr_str
    assert "1" in repr_str  # count

