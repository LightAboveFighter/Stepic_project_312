import OAuthSession as auth

""" Для корректной работы моих функций вам нужно создать свое Степик API приложение
    по следующей ссылке: https://stepik.org/oauth2/applications/ (client type = confidential, authorization grant type = client credentials)
    Свой client_id и client_secret нельзя публиковать, поэтому я использовал input()
"""
# После первого удачного теста можете закомментировать эти строки
client_id = input("Client_id: ")            # Для pytest поставьте сюда свой id и secret, но потом не забудьте стереть эти значения
client_secret = input("Client_secret: ")    # OAuthSession создает по заданным id и secret файл с их значениями
                                            # В последующие разы эти значения можно брать оттуда, файл добавлен в .gitignore

""" -------------------------------------------------- Tests for correct working  --------------------------------------------------------- """

auth.OAuthSession(client_id, client_secret) # - при первом запуске с данными своего id и secret, далее примените pytest, убрав эти строчки
