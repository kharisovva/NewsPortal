from django import template


register = template.Library()

@register.filter()
def censor(value):
    """
    Цензурирует определенные слова, заменяя их на первый символ и звезды.
    Применяется к данным строкового типа
    """
    if not isinstance(value, str):
        return value

    # Список "нехороших" слов для замены
    bad_words = ['салат', 'картофель', 'слово']

    for word in bad_words:
        censored_word = word[0] + '*' * (len(word) - 1)
        value = value.replace(word, censored_word)

    return value