
import * as utils from './utils.mjs'
import fs from 'fs';
const URLS = fs.readFileSync('./scenarios/new-list-v2.txt').toString().replace(/\r\n|\r/g, '\n').split("\n");

export async function test(context, commands) {
  for (const url of URLS) {
    if (url == '') break;
    if (url.startsWith('#') || url.startsWith('/'))
      continue;

    await commands.js.run(`window.open('${url}', '_blank')`);
    await commands.wait.byTime(10 * 1000)
  }

  await commands.wait.byTime(45 * 1000)
  const memory_metrics = await utils.getMemoryMetrics(context)

  await commands.measure.start('memory');
  await commands.measure.stop();
  commands.measure.addObject(memory_metrics)
};
