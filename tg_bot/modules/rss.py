import html
import re

from feedparser import parse
from telegram import ParseMode, constants, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler

from tg_bot import dispatcher, updater
from tg_bot.modules.helper_funcs.chat_status import user_admin
from tg_bot.modules.sql import rss_sql as sql


def show_url(bot, update, args):
    tg_chat_id = str(update.effective_chat.id)

    if len(args) >= 1:
        tg_feed_link = args[0]
        link_processed = parse(tg_feed_link)

        if link_processed.bozo == 0:
            feed_title = link_processed.feed.get("title", default="Unknown")
            feed_description = "<i>{}</i>".format(
                re.sub('<[^<]+?>', '', link_processed.feed.get("description", default="Unknown")))
            feed_link = link_processed.feed.get("link", default="Unknown")

            if len(link_processed.entries) >= 1:
                entry_title = link_processed.entries[0].get("title", default="Unknown")
                entry_description = "<i>{}</i>".format(
                    re.sub('<[^<]+?>', '', link_processed.entries[0].get("description", default="Unknown")))
                entry_link = link_processed.entries[0].get("link", default="Unknown")

                bot.send_message(chat_id=tg_chat_id, text=f"<b>{html.escape(entry_title)}</b>\n<code>{entry_description}</code>",
                                                    reply_markup=InlineKeyboardMarkup(
                                                        [[InlineKeyboardButton(text="Ссылка на новость",
                                                                               url=f"{html.escape(entry_link)}")]]), parse_mode=ParseMode.HTML)
            else:
                bot.send_message(chat_id=tg_chat_id, text=f"<b>{html.escape(feed_title)}</b>\n<code>{feed_description}</code>",
                                                    reply_markup=InlineKeyboardMarkup(
                                                        [[InlineKeyboardButton(text="Ссылка на новость",
                                                                               url=f"{html.escape(feed_link)}")]]), parse_mode=ParseMode.HTML)
                bot.send_message(chat_id=tg_chat_id, text=feed_message, disable_web_page_preview=True, parse_mode=ParseMode.HTML)
        else:
            update.effective_message.reply_text("Эта ссылка не является ссылкой на RSS-канал")
    else:
        update.effective_message.reply_text("URL отсутствует")


def list_urls(bot, update):
    tg_chat_id = str(update.effective_chat.id)

    user_data = sql.get_urls(tg_chat_id)

    # this loops gets every link from the DB based on the filter above and appends it to the list
    links_list = [row.feed_link for row in user_data]

    final_content = "\n\n".join(links_list)

    # check if the length of the message is too long to be posted in 1 chat bubble
    if len(final_content) == 0:
        bot.send_message(chat_id=tg_chat_id, text="Этот чат не подписан ни на какие ссылки")
    elif len(final_content) <= constants.MAX_MESSAGE_LENGTH:
        bot.send_message(chat_id=tg_chat_id, text="Этот чат подписан на следующие новостные каналы:\n" + final_content)
    else:
        bot.send_message(chat_id=tg_chat_id, parse_mode=ParseMode.HTML,
                         text="<b>Внимание:</b> сообщение слишком большое")


@user_admin
def add_url(bot, update, args):
    if len(args) >= 1:
        chat = update.effective_chat

        tg_chat_id = str(update.effective_chat.id)

        tg_feed_link = args[0]

        link_processed = parse(tg_feed_link)

        # check if link is a valid RSS Feed link
        if link_processed.bozo == 0:
            if len(link_processed.entries[0]) >= 1:
                tg_old_entry_link = link_processed.entries[0].link
            else:
                tg_old_entry_link = ""

            # gather the row which contains exactly that telegram group ID and link for later comparison
            row = sql.check_url_availability(tg_chat_id, tg_feed_link)

            # check if there's an entry already added to DB by the same user in the same group with the same link
            if row:
                update.effective_message.reply_text("Ссылка уже добавлена")
            else:
                sql.add_url(tg_chat_id, tg_feed_link, tg_old_entry_link)

                update.effective_message.reply_text("Добавлен URL для подписки")
        else:
            update.effective_message.reply_text("Эта ссылка не является ссылкой на RSS-канал")
    else:
        update.effective_message.reply_text("URL отсутствует")


@user_admin
def remove_url(bot, update, args):
    if len(args) >= 1:
        tg_chat_id = str(update.effective_chat.id)

        tg_feed_link = args[0]

        link_processed = parse(tg_feed_link)

        if link_processed.bozo == 0:
            user_data = sql.check_url_availability(tg_chat_id, tg_feed_link)

            if user_data:
                sql.remove_url(tg_chat_id, tg_feed_link)

                update.effective_message.reply_text("Ссылка удалена из подписок")
            else:
                update.effective_message.reply_text("Вы еще не подписались на этот URL")
        else:
            update.effective_message.reply_text("Эта ссылка не является ссылкой на RSS-канал")
    else:
        update.effective_message.reply_text("URL отсутствует")


def rss_update(bot, job):
    user_data = sql.get_all()

    # this loop checks for every row in the DB
    for row in user_data:
        row_id = row.id
        tg_chat_id = row.chat_id
        tg_feed_link = row.feed_link

        feed_processed = parse(tg_feed_link)

        tg_old_entry_link = row.old_entry_link

        new_entry_links = []
        new_entry_titles = []
        entry_description = []
        # this loop checks for every entry from the RSS Feed link from the DB row
        for entry in feed_processed.entries:
            # check if there are any new updates to the RSS Feed from the old entry
            if entry.link != tg_old_entry_link:
                new_entry_links.append(entry.link)
                new_entry_titles.append(entry.title)
                entry_description.append(entry.description)
            else:
                break

        # check if there's any new entries queued from the last check
        if new_entry_links:
            sql.update_url(row_id, new_entry_links)
        else:
            pass

        if len(new_entry_links) < 5:
            # this loop sends every new update to each user from each group based on the DB entries
            for link, description ,title in zip(reversed(new_entry_links), reversed(entry_description), reversed(new_entry_titles)):
                final_message = "<b>{}</b>\n{}".format(html.escape(title), html.escape(description))

                if len(final_message) <= constants.MAX_MESSAGE_LENGTH:
                    bot.send_message(chat_id=tg_chat_id, text=f"<b>{html.escape(title)}</b>\n<code>{html.escape(description)}</code>",
                                                        reply_markup=InlineKeyboardMarkup(
                                                            [[InlineKeyboardButton(text="Ссылка на новость",
                                                                                   url=f"{html.escape(link)}")]]), parse_mode=ParseMode.HTML)
                    # bot.send_message(chat_id=tg_chat_id, text=final_message, disable_web_page_preview=True, parse_mode=ParseMode.HTML)
                else:
                    bot.send_message(chat_id=tg_chat_id, text="<b>Внимание:</b> сообщение слишком большое для отправки",
                                     parse_mode=ParseMode.HTML)
        else:
            for link, description, title in zip(reversed(new_entry_links[-5:]), reversed(entry_description), reversed(new_entry_titles[-5:])):
                final_message = "<b>{}</b>\n{}".format(html.escape(title), html.escape(description))

                if len(final_message) <= constants.MAX_MESSAGE_LENGTH:
                    bot.send_message(chat_id=tg_chat_id, text=f"<b>{html.escape(title)}</b>\n<code>{html.escape(description)}</code>",
                                                        reply_markup=InlineKeyboardMarkup(
                                                            [[InlineKeyboardButton(text="Ссылка на новость",
                                                                                   url=f"{html.escape(link)}")]]), parse_mode=ParseMode.HTML)

                    # bot.send_message(chat_id=tg_chat_id, text=final_message, disable_web_page_preview=True, parse_mode=ParseMode.HTML)
                else:
                    bot.send_message(chat_id=tg_chat_id, text="<b>Внимание:</b> сообщение слишком большое для отправки",
                                     parse_mode=ParseMode.HTML)

            bot.send_message(chat_id=tg_chat_id, parse_mode=ParseMode.HTML,
                             text="<b>Предупреждение:</b>{} было исключено, чтобы предотвратить спам."
                             .format(len(new_entry_links) - 5))


def rss_set(bot, job):
    user_data = sql.get_all()

    # this loop checks for every row in the DB
    for row in user_data:
        row_id = row.id
        tg_feed_link = row.feed_link
        tg_old_entry_link = row.old_entry_link

        feed_processed = parse(tg_feed_link)

        new_entry_links = []
        new_entry_titles = []

        # this loop checks for every entry from the RSS Feed link from the DB row
        for entry in feed_processed.entries:
            # check if there are any new updates to the RSS Feed from the old entry
            if entry.link != tg_old_entry_link:
                new_entry_links.append(entry.link)
                new_entry_titles.append(entry.title)
            else:
                break

        # check if there's any new entries queued from the last check
        if new_entry_links:
            sql.update_url(row_id, new_entry_links)
        else:
            pass


__help__ = """
 - /addrss <link>: добавить ссылку RSS в подписки.
 - /removerss <link>: удаляет ссылку RSS из подписок.
 - /rss <link>: показывает данные ссылки и последнюю запись в целях тестирования.
 - /listrss: показывает список RSS-каналов, на которые в данный момент подписан чат.

ПРИМЕЧАНИЕ. В группах только администраторы могут добавлять/удалять RSS-ссылки для подписки группы.
"""

__mod_name__ = "RSS новости"

job = updater.job_queue

job_rss_set = job.run_once(rss_set, 5)
job_rss_update = job.run_repeating(rss_update, interval=60, first=60)
job_rss_set.enabled = True
job_rss_update.enabled = True

SHOW_URL_HANDLER = CommandHandler("rss", show_url, pass_args=True)
ADD_URL_HANDLER = CommandHandler("addrss", add_url, pass_args=True)
REMOVE_URL_HANDLER = CommandHandler("removerss", remove_url, pass_args=True)
LIST_URLS_HANDLER = CommandHandler("listrss", list_urls)

dispatcher.add_handler(SHOW_URL_HANDLER)
dispatcher.add_handler(ADD_URL_HANDLER)
dispatcher.add_handler(REMOVE_URL_HANDLER)
dispatcher.add_handler(LIST_URLS_HANDLER)
