"""Read APK identity fields inside the isolated child process.

Package identity for indicators lives in measure.py, using v2
``dotted_class`` / ``package_of_class`` and a class-count dict.
"""

from androguard.misc import AnalyzeAPK


def extract_metadata(apk_path: str) -> dict:
    """Return identity fields from the APK object.

    ``AnalyzeAPK`` is the androguard 3.3.5 entry point. Package class counts
    are not returned here; see ``measure.measure_apk``.
    """

    apk, dex_files, _analysis = AnalyzeAPK(apk_path)
    return {
        "package_name": apk.get_package(),
        "version_name": apk.get_androidversion_name(),
        "version_code": apk.get_androidversion_code(),
        "min_sdk": apk.get_min_sdk_version(),
        "target_sdk": apk.get_target_sdk_version(),
        "n_dex_files": len(dex_files),
    }
