/**
 * app.js
 * ------
 * Vanilla JS for the VTC playground. This file talks ONLY to the
 * `/api/compile` endpoint (see web/main.py) -- it never tries to
 * reimplement any compiler logic client-side. The server is the
 * single source of truth for what VTC means.
 */

const sourceInput = document.getElementById("sourceInput");
const lineNumbers = document.getElementById("lineNumbers");
const compileBtn = document.getElementById("compileBtn");
const clearBtn = document.getElementById("clearBtn");
const outputCode = document.getElementById("outputCode");
const errorPanel = document.getElementById("errorPanel");
const errorTitle = document.getElementById("errorTitle");
const errorMessage = document.getElementById("errorMessage");
const statusText = document.getElementById("statusText");

const DEFAULT_SOURCE = `(button_element=signup)
(event_listener=click)
(action=registerUser)
(add_css_class=active)
`;

sourceInput.value = DEFAULT_SOURCE;
updateLineNumbers();

function updateLineNumbers() {
  const lineCount = sourceInput.value.split("\n").length;
  const digits = [];
  for (let i = 1; i <= lineCount; i++) digits.push(i);
  lineNumbers.textContent = digits.join("\n");
}

sourceInput.addEventListener("input", updateLineNumbers);
sourceInput.addEventListener("scroll", () => {
  lineNumbers.scrollTop = sourceInput.scrollTop;
});

// Compile on Cmd/Ctrl+Enter as a small quality-of-life affordance.
sourceInput.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
    e.preventDefault();
    compile();
  }
});

compileBtn.addEventListener("click", compile);
clearBtn.addEventListener("click", () => {
  sourceInput.value = "";
  updateLineNumbers();
  showOutput("// Cleared. Write some VTC and press \"compile\".");
  setStatus("ready", "");
});

async function compile() {
  const source = sourceInput.value;
  setStatus("compiling…", "");

  try {
    const response = await fetch("/api/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source }),
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
      showOutput(data.javascript);
      setStatus("compiled", "status-ok");
    } else {
      showError(data.error);
      setStatus("intent error", "status-error");
    }
  } catch (err) {
    showError({
      title: "Connection Error",
      message: "Could not reach the compiler service.",
      detail: err.message,
      suggestion: null,
      line: null,
    });
    setStatus("connection error", "status-error");
  }
}

function showOutput(js) {
  errorPanel.hidden = true;
  outputCode.textContent = js;
}

function showError(error) {
  errorPanel.hidden = false;
  errorTitle.textContent = error.title || "Intent Error";

  const parts = [error.message];
  if (error.detail) parts.push(error.detail);
  if (error.suggestion) parts.push(`Did you mean ${error.suggestion}?`);
  if (error.line != null) parts.push(`\n(line ${error.line})`);

  errorMessage.textContent = parts.join("\n");
}

function setStatus(text, cls) {
  statusText.textContent = text;
  statusText.className = cls;
}
