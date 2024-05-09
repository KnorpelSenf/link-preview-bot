import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import {
  Bot,
  Context,
  Filter,
  NextFunction,
  webhookCallback,
} from "https://deno.land/x/grammy@v1.22.4/mod.ts";
import { type Message } from "https://demo.land/x/grammy@v1.22.4/types.ts";
import {
  EmojiFlavor,
  emojiParser,
} from "https://deno.land/x/grammy_emoji@v1.0.0/mod.ts";
import { getPrettyLinks } from "./linkpreviewbot/extract.ts";

type MyContext = Context & EmojiFlavor;

const token = Deno.env.get("BOT_TOKEN");
if (!token) throw new Error("Missing BOT_TOKEN env var!");

const bot = new Bot<MyContext>(token);
bot.use(emojiParser());

bot.command(
  "help",
  async (ctx) => {
    await ctx.reply(
      `<b>My friend sent me a message without link preview!</b>
Maybe the original sender disabled the preview. Forward me the message and I will give you all the previews.

<b>I have a shortened link!</b>
Reply to a message in this chat with /resolve to see where the links would redirect you.

<b>The link preview is outdated!</b>
Check out the official @WebpageBot to update it.

<b>Where is your source code?</b>
It's <a href="https://github.com/KnorpelSenf/link-preview-bot">on GitHub</a>.`,
      { parse_mode: "HTML", disable_web_page_preview: true /* hehe */ },
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
bot.on("channel_post:text", async (ctx) => {
  const tempText = `Adding link preview: ${ctx.msg.text.substring(0, 4000)}`;
  await ctx.editMessageText(tempText).catch(() => {/* ignore failed edit */});
  await ctx.editMessageText(ctx.msg.text, {
    entities: ctx.msg.entities,
    disable_web_page_preview: false,
  }).catch(() => {/* ignore failed edit */});
});
bot.on(["channel_post", "edited_channel_post", "my_chat_member"], () => {
  // ignore other channel post updates
});
bot.on(["::url", "::text_link"], handleLinks());
bot.on([":text", ":caption"], (ctx) => ctx.reply("No links found."));
bot.use((ctx) => ctx.reply("No text in message."));

bot.on("callback_query", async ctx => {
  if (ctx.callbackQuery.message.date === 0) {
    return await ctx.answerCallbackQuery({
      text: "// outdated button"
    });
  }
  await ctx.answerCallbackQuery();  // answer to avoid spinnier

  const data = ctx.callbackQuery.data;

  let link_preview_options = {
    is_disabled: false,
    url: ctx.callbackQuery.message.text,
    prefer_small_media: false,
    prefer_large_media: false,
    show_above_text: false
  };
  let reply_markup = {
    inline_keyboard: []
  };
  let tmp = [];

  const f = data.charAt(0);
  const tpo = data.substring(1, 4);


  if (f === "e") {
    tmp = [];
    tmp.push(
      {
        text: `${tpo === "plm" ? '✅' : '❌'} Prefer large media`,
        callback_data: "dplm"
      }
    );
    tmp.push(
      {
        text: `${tpo === "psm" ? '✅' : '❌'} Prefer small media`,
        callback_data: "dpsm"
      }
    );
    reply_markup.inline_keyboard.push(tmp);
    tmp = [];
    tmp.push(
      {
        text: `${tpo === "sat" ? '✅' : '❌'} Show above text`,
        callback_data: "dsat"
      }
    );
    reply_markup.inline_keyboard.push(tmp);
    tmp = [];

    if (tpo === "plm") {
      link_preview_options.prefer_large_media = true;
    }
    else if (tpo === "psm") {
      link_preview_options.prefer_small_media = true;
    }
    else if (tpo === "sat") {
      link_preview_options.show_above_text = true;
    }
  }

  else if (f === "d") {
    tmp = [];
    tmp.push(
      {
        text: `${tpo === "plm" ? '❌' : '✅'} Prefer large media`,
        callback_data: "eplm"
      }
    );
    tmp.push(
      {
        text: `${tpo === "psm" ? '❌' : '✅'} Prefer small media`,
        callback_data: "epsm"
      }
    );
    reply_markup.inline_keyboard.push(tmp);
    tmp = [];
    tmp.push(
      {
        text: `${tpo === "sat" ? '❌' : '✅'} Show above text`,
        callback_data: "esat"
      }
    );
    reply_markup.inline_keyboard.push(tmp);
    tmp = [];

    if (tpo === "plm") {
      link_preview_options.prefer_large_media = false;
    }
    else if (tpo === "psm") {
      link_preview_options.prefer_small_media = false;
    }
    else if (tpo === "sat") {
      link_preview_options.show_above_text = false;
    }
  }

  if (reply_markup.inline_keyboard.length === 0) {
    throw new Error("Should not happen (2)");
  }

  await ctx.callbackQuery.message.editMessageText(
    link_preview_options.url,
    {
      link_preview_options: link_preview_options,
      reply_markup: reply_markup
    }
  );

});

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
      );
    }
    for (const url of urls) {
      await ctx.reply(url, {
        reply_parameters: {
          message_id: ctx.msg.message_id,
          allow_sending_without_reply: true,
        },
        link_preview_options: {
          is_disabled: false,
          url: url,
          prefer_small_media: false,
          prefer_large_media: false,
          show_above_text: false
        },
        reply_markup: {
          inline_keyboard: [
            [
              {
                text: "❌ Prefer large media",
                callback_data: "eplm"
              },
              {
                text: "❌ Prefer small media",
                callback_data: "epsm"
              }
            ],
            [
              {
                text: "❌ Show above text",
                callback_data: "esat"
              }
            ]
          ]
        }
      });
    }
  };
}

if (Deno.env.get("DEVELOPMENT")) bot.start();
else serve(webhookCallback(bot, "std/http"));
