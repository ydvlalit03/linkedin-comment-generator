/**
 * Structured logger for the comment generation pipeline
 * Logs every step with clear formatting for debugging
 */

type LogLevel = "INFO" | "WARN" | "ERROR" | "DEBUG" | "STEP";

const COLORS: Record<LogLevel, string> = {
  INFO: "\x1b[36m",   // cyan
  WARN: "\x1b[33m",   // yellow
  ERROR: "\x1b[31m",  // red
  DEBUG: "\x1b[90m",  // gray
  STEP: "\x1b[35m",   // magenta
};

const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const DIM = "\x1b[2m";

function timestamp(): string {
  return new Date().toISOString().slice(11, 23);
}

function log(level: LogLevel, module: string, message: string, data?: any) {
  const color = COLORS[level];
  const prefix = `${color}[${timestamp()}] [${level}]${RESET} ${BOLD}[${module}]${RESET}`;

  if (data !== undefined) {
    const dataStr = typeof data === "string"
      ? data
      : JSON.stringify(data, null, 2);
    // Truncate at 500 chars for normal logs
    const truncated = dataStr.length > 500 ? dataStr.slice(0, 500) + "..." : dataStr;
    console.log(`${prefix} ${message}\n${color}${truncated}${RESET}`);
  } else {
    console.log(`${prefix} ${message}`);
  }
}

export function createLogger(module: string) {
  return {
    info: (msg: string, data?: any) => log("INFO", module, msg, data),
    warn: (msg: string, data?: any) => log("WARN", module, msg, data),
    error: (msg: string, data?: any) => log("ERROR", module, msg, data),
    debug: (msg: string, data?: any) => log("DEBUG", module, msg, data),
    step: (msg: string, data?: any) => log("STEP", module, msg, data),

    /** Log a major section divider */
    section: (title: string) => {
      console.log(`\n${COLORS.STEP}${"=".repeat(70)}${RESET}`);
      console.log(`${COLORS.STEP}${BOLD}  ${title}${RESET}`);
      console.log(`${COLORS.STEP}${"=".repeat(70)}${RESET}`);
    },

    /** Log a sub-step with index */
    substep: (index: number, total: number, msg: string) => {
      log("STEP", module, `[${index}/${total}] ${msg}`);
    },

    /** Log the full prompt — no truncation, boxed */
    prompt: (label: string, text: string) => {
      const border = `${DIM}${"─".repeat(70)}${RESET}`;
      console.log(`\n${COLORS.STEP}[${timestamp()}] [PROMPT]${RESET} ${BOLD}[${module}]${RESET} ${label}`);
      console.log(border);
      console.log(`${DIM}${text}${RESET}`);
      console.log(border);
      console.log(`${COLORS.INFO}(${text.length} chars)${RESET}\n`);
    },

    /** Log the full LLM response — no truncation, boxed */
    response: (label: string, text: string) => {
      const border = `${DIM}${"─".repeat(70)}${RESET}`;
      console.log(`${COLORS.INFO}[${timestamp()}] [RESPONSE]${RESET} ${BOLD}[${module}]${RESET} ${label}`);
      console.log(border);
      console.log(`${text}`);
      console.log(border);
    },
  };
}
