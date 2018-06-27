
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Idade', 'Cor Favorita'],
                  ['Número de Irmãos', 'Outra coisa'],
                  ['Pronto']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(bot, update):
    update.message.reply_text(
        "Oi! Meu nome é Zézinho bot. Aprenderei sobre você. "
        "Me diga algo sobre você.",
        reply_markup=markup)

    return CHOOSING


def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(
        'Seu {}? Sim, adoraria ouvir sobre isso!'.format(text.lower()))

    return TYPING_REPLY


def custom_choice(bot, update):
    update.message.reply_text('Certo, primeiro me diga a categoria, '
                              'por exemplo, "Sua habilidade mais impressionante"')

    return TYPING_CHOICE


def received_information(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Ótimo! Isso é o que você já me ensinou sobre você:"
                              "{}"
                              "Você pode me ensinar mais, ou mudar sua opinião sobre algo.".format(
                                  facts_to_str(user_data)), reply_markup=markup)

    return CHOOSING


def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("Aprendi esses fatos sobre você:"
                              "{}"
                              "Ate a próxima!".format(facts_to_str(user_data)))

    user_data.clear()
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater("515660233:AAGFRB-cv0bMofSge7MkkOGFiHyX4Dagyss")
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^(Idade|Cor Favorita|Número de Irmãos)$',
                                    regular_choice,
                                    pass_user_data=True),
                       RegexHandler('^Outra coisa$',
                                    custom_choice),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice,
                                           pass_user_data=True),
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information,
                                          pass_user_data=True),
                           ],
        },

        fallbacks=[RegexHandler('^Pronto$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
