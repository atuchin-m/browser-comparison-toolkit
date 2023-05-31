async function waitForThrottled(commands, condition, timeoutSeconds = 15 * 60) {
  for (let i = 0; i < timeoutSeconds; ++i) {
    result = await commands.js.run(`return (${condition})`)
    if (result != null && result != '')
      return result
    await commands.wait.byTime(1000)
  }
  return false
}

module.exports = {
  waitForThrottled: waitForThrottled
};
