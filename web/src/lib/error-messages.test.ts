import { describe, expect, test } from "vitest";
import { isKnownErrorCode, messageForErrorCode, SERVICE_ERROR_CODES } from "./error-messages";
import { JOB_STATUS_LABELS } from "./labels";
import { ENGINE_ERROR_CODES } from "./report-types";

const FORBIDDEN = /score|tier|verdict|malicious|\bsafe\b|critical|high risk|low risk|risk score|rating|grade/i;

describe("messageForErrorCode", () => {
  test("has a specific message for every engine and service error code", () => {
    expect(ENGINE_ERROR_CODES.length).toBeGreaterThan(0);
    for (const code of [...ENGINE_ERROR_CODES, ...SERVICE_ERROR_CODES]) {
      expect(isKnownErrorCode(code), code).toBe(true);
      const message = messageForErrorCode(code);
      expect(message.length).toBeGreaterThan(10);
      expect(message).not.toContain("does not recognise");
      expect(message.match(FORBIDDEN)).toBeNull();
    }
  });

  test("unknown code gets a generic message that names the code", () => {
    const message = messageForErrorCode("E_SOMETHING_NEW");
    expect(message).toContain("does not recognise");
    expect(message).toContain("E_SOMETHING_NEW");
  });

  test("missing code gets the generic message", () => {
    expect(messageForErrorCode(null)).toContain("does not recognise");
  });

  test("job status labels use plain words", () => {
    expect(Object.values(JOB_STATUS_LABELS)).toEqual([
      "Waiting for upload",
      "Queued",
      "Analysing",
      "Done",
      "Rejected",
      "Failed",
      "Expired",
    ]);
  });
});
