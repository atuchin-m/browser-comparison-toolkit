
import * as utils from './utils.mjs'

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
}

export async function test(context, commands) {
  const urls = utils.getUrls(context)
  shuffle(urls)
  for (const url of urls) {
    await commands.js.run(`window.open('${url}', '_blank')`);
    await commands.wait.byTime(10 * 1000)
  }

  await commands.wait.byTime(45 * 1000)
  const memory_metrics = await utils.getMemoryMetrics(context)

  await commands.measure.start('memory');
  await commands.measure.stop();
  commands.measure.addObject(memory_metrics)
};
