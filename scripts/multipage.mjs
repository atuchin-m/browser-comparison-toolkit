import * as utils from './utils.mjs'

export async function test(context, commands) {
  await commands.wait.byTime(3 * 1000);
  for (const [index, url] of utils.getUrls(context).entries()) {
    const key = new URL(url).hostname + '_' +  index;
    let error = false
    try {
      await commands.measure.start(key);
      await commands.navigate(url);
      await commands.wait.byTime(2 * 1000);
    } catch (e) {
      console.error(`Failed to load ${url} due to error:`, e);
      error = true
    }
    await commands.measure.stop();

    if (error) {
      commands.measure.addObject({
        'error': 1
      });
    } else {
      commands.measure.addObject({
        'done': 1
      });
    }
    await commands.navigate('about:blank');
  }
}
