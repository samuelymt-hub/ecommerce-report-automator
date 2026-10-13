import { spawn } from "node:child_process";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";

const [url, outputPath, widthArg = "1440", heightArg = "1000", portArg = "9224", clickText = ""] = process.argv.slice(2);

if (!url || !outputPath) {
  throw new Error("Usage: node scripts/capture_portfolio.mjs <url> <output.png> [width] [height] [port]");
}

const edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const width = Number(widthArg);
const height = Number(heightArg);
const port = Number(portArg);
const profileDir = await mkdtemp(`${tmpdir()}\\reportly-capture-`);
const destination = resolve(outputPath);
const expectedHost = new URL(url).host;

await mkdir(dirname(destination), { recursive: true });

const edge = spawn(
  edgePath,
  [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    `--window-size=${width},${height}`,
    url,
  ],
  { stdio: "ignore", windowsHide: true },
);

const wait = (milliseconds) => new Promise((resolveWait) => setTimeout(resolveWait, milliseconds));

async function findPageTarget() {
  let observedUrls = [];
  for (let attempt = 0; attempt < 50; attempt += 1) {
    try {
      const targets = await fetch(`http://127.0.0.1:${port}/json/list`).then((response) => response.json());
      observedUrls = targets.map((target) => target.url);
      const page = targets.find(
        (target) => target.type === "page" && target.url.includes(expectedHost),
      );
      if (page) return page;
    } catch {
      // Edge may still be starting.
    }
    await wait(200);
  }
  edge.kill();
  throw new Error(`Timed out waiting for the Edge debugging target. Observed: ${observedUrls.join(", ")}`);
}

const target = await findPageTarget();
const socket = new WebSocket(target.webSocketDebuggerUrl);
const pending = new Map();
let commandId = 0;

socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (!message.id || !pending.has(message.id)) return;
  const { resolve: resolveCommand, reject } = pending.get(message.id);
  pending.delete(message.id);
  if (message.error) reject(new Error(message.error.message));
  else resolveCommand(message.result);
});

await new Promise((resolveOpen, rejectOpen) => {
  socket.addEventListener("open", resolveOpen, { once: true });
  socket.addEventListener("error", rejectOpen, { once: true });
});

function command(method, params = {}) {
  commandId += 1;
  return new Promise((resolveCommand, reject) => {
    pending.set(commandId, { resolve: resolveCommand, reject });
    socket.send(JSON.stringify({ id: commandId, method, params }));
  });
}

try {
  await command("Page.enable");
  await command("Runtime.enable");
  await command("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: false,
  });

  for (let attempt = 0; attempt < 40; attempt += 1) {
    const result = await command("Runtime.evaluate", {
      expression: "document.body && document.body.innerText.includes('销售运营仪表盘')",
      returnByValue: true,
    });
    if (result.result?.value === true) break;
    await wait(250);
  }

  // Streamlit establishes a WebSocket session before widgets and charts finish painting.
  await wait(6000);
  if (clickText) {
    await command("Runtime.evaluate", {
      expression: `Array.from(document.querySelectorAll('[role="tab"]')).find((element) => element.innerText.includes(${JSON.stringify(clickText)}))?.click()`,
    });
    await wait(1500);
  }
  const screenshot = await command("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  await writeFile(destination, Buffer.from(screenshot.data, "base64"));
  console.log(destination);
} finally {
  socket.close();
  edge.kill();
  if (profileDir.startsWith(tmpdir())) {
    await wait(750);
    try {
      await rm(profileDir, { recursive: true, force: true });
    } catch (error) {
      if (error.code !== "EBUSY") throw error;
    }
  }
}
