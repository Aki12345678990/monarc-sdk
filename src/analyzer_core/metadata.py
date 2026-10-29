"""Read APK identity fields inside the isolated child process.

No indicator, attribution, or classification logic lives here.
"""

from androguard.core.bytecode import get_package_class_name
from androguard.misc import AnalyzeAPK


def extract_metadata(apk_path: str) -> dict:
    """Return identity fields and the distinct Java packages defined in DEX.

    ``AnalyzeAPK`` is the androguard 3.3.5 entry point that returns the
    ``APK`` object together with one ``DalvikVMFormat`` per DEX file.
    Class descriptors from those DEX objects are converted with
    ``get_package_class_name``. A class in the default package yields an
    empty package string from that helper and is omitted from ``packages``.
    """

    apk, dex_files, _analysis = AnalyzeAPK(apk_path)
    return {
        "package_name": apk.get_package(),
        "version_name": apk.get_androidversion_name(),
        "version_code": apk.get_androidversion_code(),
        "min_sdk": apk.get_min_sdk_version(),
        "target_sdk": apk.get_target_sdk_version(),
        "n_dex_files": len(dex_files),
        "packages": _java_packages(dex_files),
    }


def _java_packages(dex_files) -> list[str]:
    found: set[str] = set()
    for dex in dex_files:
        for class_name in dex.get_classes_names():
            package, _class_name = get_package_class_name(class_name)
            if package:
                found.add(package)
    return sorted(found)
