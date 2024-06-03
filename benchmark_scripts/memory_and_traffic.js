
const utils = require('./utils.js')
const fs = require('fs');
const URLS = fs.readFileSync('./scenarios/old-set-3.txt').toString().split("\n");

async function perfTest(context, commands) {
  console.log(URLS)

  for (url of URLS) {
    if (url == '') break;
    await commands.measure.start(url);
    await commands.scroll.byPixels(0, 1000*1000)
    await commands.wait.byTime(1000)
    await commands.switch.toNewTab();
  }

  const memory_metrics = await utils.getMemoryMetrics(context)

  commands.measure.addObject(memory_metrics)
};

module.exports = {
  test: perfTest
};
