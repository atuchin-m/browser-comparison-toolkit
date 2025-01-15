
import * as utils from './utils.mjs'

export async function test(context, commands) {
  await commands.wait.byTime(3 * 1000);
  for (const [index, url] of utils.getUrls(context).entries()) {
    const key = new URL(url).hostname + '_' +  index;
    try {
      await commands.cache.clear();
      await commands.measure.start(url, key);
    } catch (e) {
      console.error(e);
    }
    await commands.js.run("document.location.href = 'about:blank'");
    await commands.wait.byTime(1 * 1000);
  }
};
