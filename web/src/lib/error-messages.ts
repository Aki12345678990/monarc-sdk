import type { EngineErrorCode } from "./report-types";

/** Codes the job service adds on top of analyzer_core.errors.ErrorCode. */
export const SERVICE_ERROR_CODES = ["E_LEASE_EXHAUSTED"] as const;
export type ServiceErrorCode = (typeof SERVICE_ERROR_CODES)[number];

const MESSAGES: Record<EngineErrorCode | ServiceErrorCode, string> = {
  E_NOT_FOUND:
    "The uploaded file was not found on the server when it was checked. Please upload it again.",
  E_NOT_ZIP:
    "The file is not a ZIP archive. An APK is a ZIP archive, so this file cannot be analysed.",
  E_TOO_LARGE: "The file is larger than the upload limit.",
  E_ZIP_BOMB:
    "The archive declares more uncompressed data, or a higher compression ratio, than the analyser accepts.",
  E_TOO_MANY_ENTRIES: "The archive contains more entries than the analyser accepts.",
  E_PATH_TRAVERSAL:
    "The archive contains an entry with an absolute path or a parent-directory segment (..), so it was not processed.",
  E_NO_MANIFEST:
    "The archive has no AndroidManifest.xml entry, so it is not an Android app package.",
  E_TIMEOUT: "Analysis took longer than the time limit and was stopped.",
  E_PARSE_FAILED: "The static analyser could not parse this APK.",
  E_INTERNAL: "An internal error occurred in the analyser or the job service.",
  E_LEASE_EXHAUSTED:
    "The analysis worker stopped before finishing this job, and the retry limit has been reached.",
};

export function messageForErrorCode(code: string | null | undefined): string {
  if (code && Object.prototype.hasOwnProperty.call(MESSAGES, code)) {
    return MESSAGES[code as keyof typeof MESSAGES];
  }
  return `The job ended with an error this page does not recognise (code: ${code ?? "none"}).`;
}

export function isKnownErrorCode(code: string): boolean {
  return Object.prototype.hasOwnProperty.call(MESSAGES, code);
}
