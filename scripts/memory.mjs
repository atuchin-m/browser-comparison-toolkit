
import * as utils from './utils.mjs'

export async function test(context, commands) {
  for (const url of utils.getUrls(context)) {
    await commands.js.run(`window.open('${url}', '_blank')`);
    await commands.wait.byTime(10 * 1000)
  }

  await commands.wait.byTime(45 * 1000)
  const memory_metrics = await utils.getMemoryMetrics(context)

  await commands.measure.start('memory');
  await commands.measure.stop();
  commands.measure.addObject(memory_metrics)
};
