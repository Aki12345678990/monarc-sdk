"""Report schema for Phase 1A. Values are measurements and status fields only."""

import json
from importlib.metadata import version as package_version
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from analyzer_core import __version__
from analyzer_core.reference import verify

LIMITATIONS: list[str] = [
    "Static analysis only; no code was executed.",
    "SDK attribution is namespace-based.",
    "Obfuscation can hide SDK code, so SDK findings are a lower bound.",
    "Cross-platform framework code may not be visible to DEX analysis.",
    "No runtime behaviour was observed.",
    "This is not a malware verdict.",
]

_NOT_IMPLEMENTED_REASON = "Awaiting Phase 1B port from frozen v2 pipeline"
_COMPARISON_REASON = "Corpus comparison deferred until research validation is complete."


class IndicatorResult(BaseModel):
    status: Literal["ok", "unavailable", "not_implemented"]
    value: int | float | None = None
    reason: str | None = None
    definition_source: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class IndicatorBlock(BaseModel):
    P: IndicatorResult
    A: IndicatorResult
    N: IndicatorResult
    M: IndicatorResult
    D: IndicatorResult

    @classmethod
    def not_implemented(cls) -> "IndicatorBlock":
        def item() -> IndicatorResult:
            return IndicatorResult(
                status="not_implemented",
                value=None,
                reason=_NOT_IMPLEMENTED_REASON,
                definition_source=None,
                details={},
            )

        return cls(P=item(), A=item(), N=item(), M=item(), D=item())


class EngineInfo(BaseModel):
    name: Literal["analyzer_core"] = "analyzer_core"
    version: str
    androguard_version: str
    reference_status: str


class ReportInput(BaseModel):
    sha256: str | None = None
    file_size: int | None = None
    package_name: str | None = None
    version_name: str | None = None
    version_code: str | int | None = None
    min_sdk: str | int | None = None
    target_sdk: str | int | None = None


class ReportError(BaseModel):
    code: str
    message: str


def _default_engine() -> EngineInfo:
    return EngineInfo(
        name="analyzer_core",
        version=__version__,
        androguard_version=package_version("androguard"),
        reference_status=verify()["status"],
    )


class Report(BaseModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    engine: EngineInfo = Field(default_factory=_default_engine)
    input: ReportInput = Field(default_factory=ReportInput)
    status: Literal["ok", "error"] = "ok"
    errors: list[ReportError] = Field(default_factory=list)
    frameworks: list[Any] = Field(default_factory=list)
    visibility_caveat: str | None = None
    sdk_inventory: list[Any] = Field(default_factory=list)
    indicators: IndicatorBlock = Field(default_factory=IndicatorBlock.not_implemented)
    comparison: None = None
    comparison_reason: Literal[
        "Corpus comparison deferred until research validation is complete."
    ] = _COMPARISON_REASON
    limitations: list[str] = Field(default_factory=lambda: list(LIMITATIONS))

    @field_validator("limitations")
    @classmethod
    def _limitations_are_fixed(cls, value: list[str]) -> list[str]:
        if value != list(LIMITATIONS):
            raise ValueError("limitations must stay the fixed Phase 1A list")
        return value

    def to_json(self) -> str:
        payload = self.model_dump(mode="json")
        return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    def to_markdown(self) -> str:
        data = self.model_dump(mode="json")
        lines: list[str] = ["# analyzer_core report", ""]

        def emit(label: str, value: object) -> None:
            if value is None:
                rendered = "null"
            elif isinstance(value, str):
                rendered = value
            else:
                rendered = json.dumps(value, ensure_ascii=False)
            lines.append(f"{label}: {rendered}")

        emit("schema_version", data["schema_version"])
        emit("status", data["status"])
        lines.append("")
        lines.append("## engine")
        for key, value in data["engine"].items():
            emit(key, value)
        lines.append("")
        lines.append("## input")
        for key, value in data["input"].items():
            emit(key, value)
        lines.append("")
        lines.append("## errors")
        if not data["errors"]:
            lines.append("(none)")
        else:
            for err in data["errors"]:
                lines.append(f"- {err['code']}: {err['message']}")
        lines.append("")
        lines.append("## frameworks")
        if not data["frameworks"]:
            lines.append("(none)")
        else:
            for item in data["frameworks"]:
                lines.append(f"- {json.dumps(item, ensure_ascii=False)}")
        lines.append("")
        emit("visibility_caveat", data["visibility_caveat"])
        lines.append("")
        lines.append("## sdk_inventory")
        if not data["sdk_inventory"]:
            lines.append("(none)")
        else:
            for item in data["sdk_inventory"]:
                lines.append(f"- {json.dumps(item, ensure_ascii=False)}")
        lines.append("")
        lines.append("## indicators")
        for name, indicator in data["indicators"].items():
            lines.append(f"### {name}")
            for key, value in indicator.items():
                emit(key, value)
            lines.append("")
        lines.append("## comparison")
        emit("comparison", data["comparison"])
        emit("comparison_reason", data["comparison_reason"])
        lines.append("")
        lines.append("## limitations")
        for item in data["limitations"]:
            lines.append(f"- {item}")
        lines.append("")
        return "\n".join(lines)
