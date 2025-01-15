
import * as utils from './utils.mjs'

export async function test(context, commands) {
  await commands.wait.byTime(3 * 1000);
  for (const [index, url] of utils.getUrls(context).entries()) {
    const key = new URL(url).hostname + '_' +  index;
    try {
      await commands.cache.clear();
      await commands.measure.start(url, key);
    } catch (e) {
      await commands.measure.start(key);
      commands.measure.addObject({
        'error': key
      });
      await commands.measure.stop();
      console.error(e);
    }
    await commands.navigate('about:blank');
  }
};
