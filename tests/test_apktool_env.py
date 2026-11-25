"""Apktool path selection follows ANALYZER_JAVA and ANALYZER_APKTOOL_JAR."""

from analyzer_core import measure


def _capture(monkeypatch):
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"] = list(cmd)

        class Proc:
            returncode = 1
            stdout = ""
            stderr = ""

        return Proc()

    monkeypatch.setattr(measure.os.path, "isfile", lambda path: True)
    monkeypatch.setattr(measure.subprocess, "run", fake_run)
    return seen


def test_apktool_uses_env_paths(monkeypatch):
    monkeypatch.setenv("ANALYZER_JAVA", r"D:\jdk\bin\java.exe")
    monkeypatch.setenv("ANALYZER_APKTOOL_JAR", r"D:\tools\apktool.jar")
    seen = _capture(monkeypatch)
    assert measure.recover_nsc_with_apktool("app.apk") is None
    assert seen["cmd"][:3] == [
        r"D:\jdk\bin\java.exe",
        "-jar",
        r"D:\tools\apktool.jar",
    ]


def test_apktool_defaults_when_env_unset(monkeypatch):
    monkeypatch.delenv("ANALYZER_JAVA", raising=False)
    monkeypatch.delenv("ANALYZER_APKTOOL_JAR", raising=False)
    seen = _capture(monkeypatch)
    assert measure.recover_nsc_with_apktool("app.apk") is None
    assert seen["cmd"][0] == measure.JAVA_EXE
    assert seen["cmd"][2] == measure.APKTOOL_JAR
