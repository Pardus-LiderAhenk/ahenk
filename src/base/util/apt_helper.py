#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility helpers for installing packages via the python-apt library.

This avoids shelling out to `apt install` while providing a small CLI
that can be used from shell scripts as well as within Python code.
"""

import argparse
import subprocess
import sys

try:
    import apt
    import apt.progress.text
except Exception as exc:  # pragma: no cover - guarded import
    # Keep the error explicit so callers can propagate a clear message.
    sys.stderr.write(f"Failed to import python-apt: {exc}\n")
    sys.exit(1)


def _get_logger():
    """Get logger from Scope if available, otherwise return None."""
    try:
        from base.scope import Scope
        return Scope.get_instance().get_logger()
    except Exception:
        return None


class AptHelper:
    """Lightweight wrapper around python-apt for installing packages."""

    @staticmethod
    def install_packages(
        packages, update_cache=False, run_dpkg_configure=True, versions=None
    ):
        """
        Install the given list of packages using python-apt.

        Args:
            packages (list[str]): Package names to install.
            update_cache (bool): Whether to refresh package indexes first.
            run_dpkg_configure (bool): Run `dpkg --configure -a` first to
                clean up half-configured packages. Enabled by default.
            versions (dict[str, str] | None): Optional package->version mapping
                for pinning specific versions.

        Returns:
            tuple: (result_code, stdout_msg, stderr_msg)
        """
        try:
            if run_dpkg_configure:
                # Ensure no interrupted dpkg state before proceeding
                proc = subprocess.run(
                    ["dpkg", "--configure", "-a"],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if proc.returncode != 0:
                    return proc.returncode, proc.stdout, proc.stderr

            try:
                cache = apt.Cache()
                if update_cache:
                    cache.update()
                    cache.open(None)
                else:
                    # ensure cache is ready even when not updating
                    cache.open(None)
            except Exception as cache_exc:
                return 1, "", f"Failed to prepare apt cache: {cache_exc}"

            versions = versions or {}
            missing_packages = []
            packages_to_install = []
            logger = _get_logger()

            for pkg_name in packages:
                target_version = versions.get(pkg_name)
                pkg = cache.get(pkg_name)
                if pkg is None:
                    missing_pkg = pkg_name if not target_version else f"{pkg_name}={target_version}"
                    missing_packages.append(missing_pkg)
                    if logger:
                        logger.error(f"Package not found in repository: {missing_pkg}")
                    continue
                if pkg.is_installed and (not target_version or (pkg.installed and pkg.installed.version == target_version)):
                    if logger:
                        logger.debug(f"Package already installed: {pkg_name} (version: {pkg.installed.version if pkg.installed else 'N/A'})")
                    continue
                if target_version:
                    ver_obj = pkg.versions.get(target_version)
                    if ver_obj is None:
                        missing_pkg = f"{pkg_name}={target_version}"
                        missing_packages.append(missing_pkg)
                        if logger:
                            logger.error(f"Package version not found: {missing_pkg}")
                        continue
                    ver_obj.mark_install()
                    if logger:
                        logger.debug(f"Installing package: {pkg_name} (version: {target_version})")
                else:
                    pkg.mark_install()
                    if logger:
                        logger.debug(f"Installing package: {pkg_name}")
                packages_to_install.append(pkg_name)

            if missing_packages:
                error_msg = "Packages not found: {0}".format(", ".join(missing_packages))
                if logger:
                    logger.error(f"Installation failed: {error_msg}")
                return (
                    1,
                    "",
                    error_msg,
                )

            if packages_to_install:
                if logger:
                    logger.info(f"Starting installation of {len(packages_to_install)} package(s): {', '.join(packages_to_install)}")
                try:
                    fetch_progress = apt.progress.text.AcquireProgress()
                    install_progress = apt.progress.base.InstallProgress()
                    cache.commit(
                        fetch_progress=fetch_progress, install_progress=install_progress
                    )
                    if logger:
                        for pkg_name in packages_to_install:
                            logger.info(f"Package installed successfully: {pkg_name}")
                except Exception as commit_exc:
                    if logger:
                        for pkg_name in packages_to_install:
                            logger.error(f"Error installing package {pkg_name}: {commit_exc}")
                    raise

            return 0, " ".join(packages), ""
        except Exception as exc:
            return 1, "", str(exc)

    @staticmethod
    def update_cache(run_dpkg_configure=True):
        """
        Update apt package cache (equivalent to 'apt update').

        Args:
            run_dpkg_configure (bool): Run `dpkg --configure -a` first to
                clean up half-configured packages. Enabled by default.

        Returns:
            tuple: (result_code, stdout_msg, stderr_msg)
        """
        logger = _get_logger()
        try:
            if run_dpkg_configure:
                if logger:
                    logger.debug("Running dpkg --configure -a before cache update")
                proc = subprocess.run(
                    ["dpkg", "--configure", "-a"],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if proc.returncode != 0:
                    if logger:
                        logger.error(f"dpkg --configure -a failed: {proc.stderr}")
                    return proc.returncode, proc.stdout, proc.stderr

            if logger:
                logger.info("Updating apt package cache...")
            try:
                cache = apt.Cache()
                cache.update()
                cache.open(None)
                if logger:
                    logger.info("Apt package cache updated successfully")
                return 0, "Cache updated successfully", ""
            except Exception as cache_exc:
                error_msg = f"Failed to update apt cache: {cache_exc}"
                if logger:
                    logger.error(error_msg)
                return 1, "", error_msg
        except Exception as exc:
            error_msg = f"Error during cache update: {exc}"
            if logger:
                logger.error(error_msg)
            return 1, "", error_msg

    @staticmethod
    def remove_packages(packages, purge=False, update_cache=False, run_dpkg_configure=True):
        """
        Remove (or purge) the given list of packages using python-apt.

        Args:
            packages (list[str]): Package names to remove.
            purge (bool): If True, purge configuration files as well.
            update_cache (bool): Whether to refresh package indexes first.
            run_dpkg_configure (bool): Run `dpkg --configure -a` first. Enabled by default.

        Returns:
            tuple: (result_code, stdout_msg, stderr_msg)
        """
        try:
            if run_dpkg_configure:
                proc = subprocess.run(
                    ["dpkg", "--configure", "-a"],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if proc.returncode != 0:
                    return proc.returncode, proc.stdout, proc.stderr

            try:
                cache = apt.Cache()
                if update_cache:
                    cache.update()
                    cache.open(None)
                else:
                    cache.open(None)
            except Exception as cache_exc:
                return 1, "", f"Failed to prepare apt cache: {cache_exc}"

            missing_packages = []
            packages_to_remove = []
            logger = _get_logger()

            for pkg_name in packages:
                pkg = cache.get(pkg_name)
                if pkg is None:
                    missing_packages.append(pkg_name)
                    if logger:
                        logger.error(f"Package not found in repository: {pkg_name}")
                    continue
                if not pkg.is_installed:
                    if logger:
                        logger.debug(f"Package not installed, skipping: {pkg_name}")
                    continue
                if purge:
                    pkg.mark_delete(purge=True)
                    if logger:
                        logger.debug(f"Removing package (purge): {pkg_name}")
                else:
                    pkg.mark_delete()
                    if logger:
                        logger.debug(f"Removing package: {pkg_name}")
                packages_to_remove.append(pkg_name)

            if packages_to_remove:
                action = "purging" if purge else "removing"
                if logger:
                    logger.info(f"Starting {action} of {len(packages_to_remove)} package(s): {', '.join(packages_to_remove)}")
                try:
                    fetch_progress = apt.progress.text.AcquireProgress()
                    install_progress = apt.progress.base.InstallProgress()
                    cache.commit(
                        fetch_progress=fetch_progress, install_progress=install_progress
                    )
                    if logger:
                        action_past = "purged" if purge else "removed"
                        for pkg_name in packages_to_remove:
                            logger.info(f"Package {action_past} successfully: {pkg_name}")
                except Exception as commit_exc:
                    if logger:
                        for pkg_name in packages_to_remove:
                            logger.error(f"Error {action} package {pkg_name}: {commit_exc}")
                    raise

            # If nothing to remove, still succeed but report missing/absent ones
            if not packages_to_remove and missing_packages:
                skip_msg = "Skipped missing packages: {0}".format(", ".join(missing_packages))
                if logger:
                    logger.warning(skip_msg)
                return 0, skip_msg, ""

            return 0, " ".join(packages), ""
        except Exception as exc:
            return 1, "", str(exc)


def main():
    parser = argparse.ArgumentParser(
        description="Install packages or update cache using python-apt (no shell apt commands)."
    )
    parser.add_argument(
        "packages",
        nargs="*",
        help="Packages to install (optional if --update-only is used)",
    )
    parser.add_argument(
        "--version",
        dest="versions",
        action="append",
        default=None,
        help="Pin package version as name=version (can be repeated)",
    )
    parser.add_argument(
        "--update-cache",
        dest="update_cache",
        action="store_true",
        default=False,
        help="Refresh apt cache before installing",
    )
    parser.add_argument(
        "--update-only",
        dest="update_only",
        action="store_true",
        default=False,
        help="Only update apt cache (equivalent to 'apt update')",
    )
    parser.add_argument(
        "--skip-dpkg-configure",
        dest="run_dpkg_configure",
        action="store_false",
        default=True,
        help="Skip running 'dpkg --configure -a' before installing",
    )

    args = parser.parse_args()

    # If --update-only is specified, just update cache
    if args.update_only:
        result_code, p_out, p_err = AptHelper.update_cache(
            run_dpkg_configure=args.run_dpkg_configure
        )
        if result_code != 0:
            if p_err:
                sys.stderr.write(p_err + "\n")
            sys.exit(result_code)
        if p_out:
            sys.stdout.write(p_out + "\n")
        return

    # Otherwise, install packages
    if not args.packages:
        parser.error("packages argument is required unless --update-only is used")

    version_map = {}
    if args.versions:
        for item in args.versions:
            if "=" in item:
                name, ver = item.split("=", 1)
                version_map[name] = ver

    result_code, p_out, p_err = AptHelper.install_packages(
        args.packages,
        update_cache=args.update_cache,
        run_dpkg_configure=args.run_dpkg_configure,
        versions=version_map or None,
    )

    if result_code != 0:
        if p_err:
            sys.stderr.write(p_err + "\n")
        sys.exit(result_code)

    if p_out:
        sys.stdout.write(p_out + "\n")


if __name__ == "__main__":
    main()

