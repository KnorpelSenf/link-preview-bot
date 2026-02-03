import {
  Bot,
  Context,
  Filter,
  InlineKeyboard,
  NextFunction,
  webhookCallback,
} from "https://deno.land/x/grammy@v1.39.3/mod.ts";
import {
  type LinkPreviewOptions,
  type Message,
} from "https://deno.land/x/grammy@v1.39.3/types.ts";
import {
  EmojiFlavor,
  emojiParser,
} from "https://deno.land/x/grammy_emoji@v1.2.0/mod.ts";
import { autoRetry } from "https://deno.land/x/grammy_auto_retry@v2.0.2/mod.ts";
import {
  getPrettyLinks,
  hasParams,
  stripParams,
} from "./linkpreviewbot/extract.ts";

type MyContext = Context & EmojiFlavor;

const token = Deno.env.get("BOT_TOKEN");
if (!token) throw new Error("Missing BOT_TOKEN env var!");

const bot = new Bot<MyContext>(token);
bot.api.config.use(autoRetry());
bot.use(emojiParser());

bot.command("start", (ctx) => ctx.reply("Hi! Just send me a link. /help"));
bot.command(
  "help",
  async (ctx) => {
    await ctx.reply(
      `<b>My friend sent me a message without link preview!</b>
Maybe the original sender disabled the preview. Forward me the message and I will give you all the previews.

<b>I have a shortened link!</b>
Reply to a message in this chat with /resolve to see where the links would redirect you.

<b>I want to create link preview without visible link in text!</b>
Reply to a text message with /generate <i>URL</i> to add a link preview to the message.

<b>The link preview is outdated!</b>
Check out the official @WebpageBot to update it.

<b>Where is your source code?</b>
It's <a href="https://github.com/KnorpelSenf/link-preview-bot">on GitHub</a>.`,
      {
        parse_mode: "HTML",
        link_preview_options: { is_disabled: true }, // hehe
      },
    );
  },
);

bot.command("resolve").branch(
  (ctx) => ctx.msg.reply_to_message !== undefined,
  handleLinks({ resolve: true }),
  (ctx) =>
    ctx.reply(
      "Reply to a message to follow all redirects of the contained links!",
    ),
);
bot.callbackQuery(/^strip:/, async (ctx) => {
  if (
    ctx.callbackQuery.message?.text === undefined ||
    ctx.callbackQuery.message.date === 0
  ) {
    await ctx.answerCallbackQuery("outdated button");
    return;
  }

  const stripped = stripParams(ctx.callbackQuery.message.text, ctx.entities());
  await Promise.all([
    ctx.answerCallbackQuery(),
    ctx.editMessageText(
      stripped[0],
      generateReplyMarkup(
        ctx.callbackQuery.message.text,
        ctx.callbackQuery.data.substring("strip:".length),
      ),
    ),
  ]);
});
bot.callbackQuery(/^resolve:/, async (ctx) => {
  if (
    ctx.callbackQuery.message?.text === undefined ||
    ctx.callbackQuery.message.date === 0
  ) {
    await ctx.answerCallbackQuery("outdated button");
    return;
  }

  const resolved = await getPrettyLinks(
    ctx.callbackQuery.message.text,
    ctx.entities(),
    /* resolve: */ true,
  );
  await Promise.all([
    ctx.answerCallbackQuery(),
    ctx.editMessageText(
      resolved[0],
      generateReplyMarkup(
        ctx.callbackQuery.message.text,
        ctx.callbackQuery.data.substring("resolve:".length),
      ),
    ),
  ]);
});
bot.command("generate", async (ctx) => {
  const url_entity = ctx.entities("url");
  if (url_entity.length === 0) {
    await ctx.reply("Please provide a URL.");
    return;
  }
  const url = url_entity[0].text;
  if (ctx.msg.reply_to_message === undefined) {
    await ctx.reply("Please reply to the message to add link preview.");
    return;
  }
  const { text, entities } = ctx.msg.reply_to_message;
  if (text === undefined) {
    await ctx.reply("Please reply to a text message.");
    return;
  }
  await ctx.reply(text, {
    entities,
    ...generateReplyMarkup(url, "small-below-resolved"), // disable resolve button
  });
});
bot.on("callback_query:data", async (ctx) => {
  if (
    ctx.callbackQuery.message?.text === undefined ||
    ctx.callbackQuery.message.date === 0
  ) {
    await ctx.answerCallbackQuery("outdated button");
    return;
  }
  if (ctx.callbackQuery.message.link_preview_options?.url === undefined) {
    await ctx.answerCallbackQuery("cannot create link preview");
    return;
  }

  await Promise.all([
    ctx.answerCallbackQuery(),
    ctx.editMessageText(ctx.callbackQuery.message.text, {
      ...generateReplyMarkup(
        ctx.callbackQuery.message.link_preview_options?.url,
        ctx.callbackQuery.data,
      ),
    }),
  ]);
});
bot.on("channel_post:text", async (ctx) => {
  const tempText = `Adding link preview: ${ctx.msg.text.substring(0, 4000)}`;
  await ctx.editMessageText(tempText).catch(() => {/* ignore failed edit */});
  await ctx.editMessageText(ctx.msg.text, {
    entities: ctx.msg.entities,
    link_preview_options: { is_disabled: true }, // hehe
  }).catch(() => {/* ignore failed edit */});
});
bot.on(["channel_post", "edited_channel_post", "my_chat_member"], () => {
  // ignore other channel post updates
});
bot.on(["::url", "::text_link"], handleLinks());
bot.on([":text", ":caption"], (ctx) => ctx.reply("No links found."));
bot.use((ctx) => ctx.reply("No text in message."));

function generateReplyMarkup(
  url: string,
  data: string = "small-below-raw",
) {
  const [size, pos, res] = data.split("-") as [
    "large" | "small" | "none",
    "above" | "below",
    "raw" | "resolved",
  ];
  const opts: LinkPreviewOptions = {
    is_disabled: false,
    url,
    prefer_small_media: size === "small",
    prefer_large_media: size === "large",
    show_above_text: pos === "above",
  };
  const resolved = res === "resolved";

  const keyboard = new InlineKeyboard()
    .text(
      `${opts.prefer_large_media ? "✅" : "❌"} Prefer large media`,
      `${opts.prefer_large_media ? "none" : "large"}-${pos}-${res}`,
    ).text(
      `${opts.prefer_small_media ? "✅" : "❌"} Prefer small media`,
      `${opts.prefer_small_media ? "none" : "small"}-${pos}-${res}`,
    ).row().text(
      `${opts.show_above_text ? "✅" : "❌"} Show above text`,
      `${size}-${opts.show_above_text ? "below" : "above"}-${res}`,
    );
  if (hasParams(url)) {
    keyboard.row().text("Strip parameters", `strip:${size}-${pos}-${res}`);
  }
  if (!resolved) {
    // command string
    keyboard.row().text("Resolve redirects", `resolve:${size}-${pos}-resolved`);
  }

  return { link_preview_options: opts, reply_markup: keyboard };
}
function handleLinks(options?: { resolve?: boolean }) {
  return async (ctx: Filter<MyContext, "msg">, next: NextFunction) => {
    let msg: Message = ctx.msg;
    let statusMessage: Message.TextMessage | undefined;
    if (options?.resolve) {
      if (msg.reply_to_message === undefined) {
        throw new Error("Should not happen");
      }
      statusMessage = await ctx.reply(ctx.emoji`${"thinking_face"}`);
      msg = msg.reply_to_message;
    }
    const t = msg.text ?? msg.caption;
    const e = msg.entities ?? msg.caption_entities;
    if (!t || !e?.length) {
      await next();
      return;
    }
    const urls = await getPrettyLinks(t, e, options?.resolve);
    if (urls.length === 0) {
      if (statusMessage !== undefined) {
        await ctx.api.deleteMessage(ctx.msg.chat.id, statusMessage.message_id);
      }
      await next();
      return;
    }
    if (statusMessage !== undefined) {
      const first = urls.shift() ?? "";
      await ctx.api.editMessageText(
        ctx.msg.chat.id,
        statusMessage?.message_id,
        first,
        generateReplyMarkup(first),
      );
    }
    for (const url of urls) {
      await ctx.reply(url, {
        ...generateReplyMarkup(url),
        reply_parameters: {
          message_id: ctx.msg.message_id,
          allow_sending_without_reply: true,
        },
      });
    }
  };
}

if (Deno.env.get("DEBUG")) bot.start();
else Deno.serve(webhookCallback(bot, "std/http"));
