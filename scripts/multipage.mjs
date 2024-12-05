
import * as utils from './utils.mjs'

export async function test(context, commands) {
  for (const url of utils.getUrls(context)) {
    await commands.measure.start(url);
    await commands.navigate('about:blank');
    await commands.wait.byTime(5 * 1000);
  }
};
