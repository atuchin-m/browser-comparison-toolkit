import {execa} from 'execa'
import fs from 'fs'

const URL_FILE = './scenarios/new-list-v3.txt'
export async function waitForThrottled(commands, condition, timeoutSeconds = 15 * 60) {
  for (let i = 0; i < timeoutSeconds; ++i) {
    const result = await commands.js.run(`return (${condition})`)
    if (result != null && result != '')
      return result
    await commands.wait.byTime(1000)
  }
  return false
}

export function getUrls(context, limit = null) {
  const rawUrls = fs.readFileSync(URL_FILE).toString().split("\n");
  let urls = []
  for (const url of rawUrls) {
    if (url.startsWith('#') || url.startsWith('/'))
      continue;
    if (url == '') break;
    urls.push(url)
  }
  if (limit != null)
    urls = urls.slice(0, limit)
  return urls
}

export function getBrowserAttr(context) {
  const options = context.options
  let binaryPath = null
  let args = null
  if (options.safari?.binaryPath) {
    binaryPath = options.safari.binaryPath
    args = options.safari.args
  } else if  (options.firefox?.binaryPath) {
    binaryPath = options.firefox.binaryPath
    args = options.firefox.args
  } else if(options.edge?.binaryPath) {
    binaryPath = options.edge.binaryPath
    args = options.chrome.args
  } else if(options.chrome?.binaryPath) {
    binaryPath = options.chrome.binaryPath
    args = options.chrome.args
  } else {
    console.log(options)
    throw new Error('Browser is not supported ' + options.browser)
  }

  return {
    type: options.browser,
    binaryPath: binaryPath,
    args: args,
  }
}

export async function getMemoryMetrics(context) {
  const attr = getBrowserAttr(context)
  let executable = ".venv/bin/python3"
  if (process.platform == "win32")
    executable = ".venv\\Scripts\\python.exe"
  let cmd = `${executable} get_memory_metrics.py ${attr.type}`
  if (attr.args != null && attr.args[0].startsWith('user-data'))
    cmd += ` "${attr.args[0]}"`
  console.log(cmd)
  const { stdout } = await execa(cmd, { shell: true });
  console.log(stdout)
  return JSON.parse(stdout)
}
