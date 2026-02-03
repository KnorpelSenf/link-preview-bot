import { type MessageEntity } from "https://deno.land/x/grammy@v1.39.3/types.ts";

export async function getPrettyLinks(
  text: string,
  entities: MessageEntity[],
  resolve = false,
) {
  let urls = getUrls(text, entities).map(addProtocol);
  if (resolve) urls = await Promise.all(urls.map(resolveRedirect));
  return urls;
}

function getUrls(text: string, entities: MessageEntity[]) {
  return entities.reduce<string[]>((agg, e) => {
    if (e.type === "url") {
      agg.push(text.substring(e.offset, e.offset + e.length));
    } else if (e.type === "text_link") {
      agg.push(e.url);
    }
    return agg;
  }, []);
}

function addProtocol(url: string) {
  return url.match(/^[A-Za-z]+:\/\//) ? url : `http://${url}`;
}

async function resolveRedirect(url: string) {
  const response = await fetch(url);
  return response.url;
}
