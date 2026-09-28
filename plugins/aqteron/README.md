# Aqteron для Claude · 0.1.1

Плагин помогает создавать, проверять, публиковать и обновлять приложения в вашем аккаунте Aqteron. Claude получает действующие правила и доступные возможности через MCP, собирает ZIP и передаёт его в Aqteron. Для публикации используется обычная проверка пакета и прав аккаунта.

## Установка в Claude

1. Откройте **Customize → Plugins → Add → Upload plugin** и выберите `aqteron-claude-0.1.1.zip`.
2. Откройте вкладку **Connectors** установленного плагина, выберите Aqteron и нажмите **Connect**. Адрес сервера: `https://aqteron.com/mcp`.
3. Войдите в нужный аккаунт Aqteron и разрешите подключение. Пароль вводится только на сайте Aqteron.
4. В новой беседе попросите: «Покажи мои приложения в Aqteron». Затем: «Создай и опубликуй в Aqteron простой трекер привычек».

Названия пунктов и доступность загрузки плагинов зависят от версии Claude и настроек организации. Если загрузка плагинов недоступна, добавьте **custom connector** с тем же MCP-адресом; инструменты доступны и без установленного навыка. Для сборки и передачи ZIP нужны инструменты выполнения кода и доступа к файлам. Если их нет в выбранном режиме, используйте Claude Code или режим Claude с такими инструментами.

## Claude Code

Распакуйте архив и запустите `claude --plugin-dir /absolute/path/aqteron-claude`. Через `/mcp` выберите Aqteron и пройдите вход. Для проверки структуры: `claude plugin validate /absolute/path/aqteron-claude --strict`.

## Как работает передача

MCP endpoint: `https://aqteron.com/mcp`, Streamable HTTP, OAuth с PKCE. Пользователь разрешает чтение правил и списка своих приложений, загрузку, публикацию и проверку статуса. Доступ отзывается в разделе подключений Aqteron.

ZIP передаётся через три стандартных MCP-инструмента: `begin_app_zip_upload`, `append_app_zip_chunk`, `complete_app_zip_upload`. Передача возобновляется, проверяет точный размер и SHA-256 и использует тот же валидатор, что существующая интеграция. Само завершение загрузки не публикует приложение; публикация — отдельный `deploy_app` по запросу пользователя.

Лимит ZIP — 10 MiB, часть — 24 KiB, незавершённая передача хранится час. У больших архивов существенный расход контекста и времени: для первых запусков лучше небольшие приложения без тяжёлых встроенных ресурсов. Python 3 нужен только для вспомогательного чтения файла; MCP-сервер уже работает удалённо.

Плагин не содержит токенов и не требует ключа API. Автоматические проверки не заменяют проверку установки и входа в реальном аккаунте Claude; этот последний шаг требует сессии пользователя.

## Владелец, данные и поддержка

Aqteron управляет **EIREEN Tech**, SAS, 102 628 047 R.C.S. Paris, 122 rue Amelot, 75011 Paris, France. Контакт для поддержки, вопросов о данных и непубличных сообщений о безопасности: [contact@aqteron.com](mailto:contact@aqteron.com).

[Политика конфиденциальности](https://aqteron.com/privacy?lang=ru) · [Privacy policy](https://aqteron.com/privacy) · [Politique de confidentialité](https://aqteron.com/privacy?lang=fr).

Единственный удалённый сервис плагина — `https://aqteron.com/mcp`. После разрешения доступа он обрабатывает сведения о ваших приложениях, загруженные ZIP и результаты публикации. Локальный Python-помощник читает выбранный ZIP и выводит части файла; сам он не отправляет сетевые запросы. Отдельного адреса для телеметрии в плагине нет. Правила обработки данных самим Claude определяются вашим соглашением с Anthropic.

Отозвать подключение можно в [разделе AI-подключений Aqteron](https://aqteron.com/cabinet/connections/ai). Отключение не удаляет уже опубликованные приложения. Ссылки на опубликованные приложения доступны получателям ссылки. Не включайте пароли, токены или личные исходные материалы в публичные файлы приложения и не прикладывайте их к публичным сообщениям об ошибках.

**Privacy and support (English).** Aqteron is operated by EIREEN Tech (France). The plugin connects only to Aqteron's MCP service and processes authorized app metadata, uploaded ZIP files and publication results. Read the [privacy policy](https://aqteron.com/privacy). Contact [contact@aqteron.com](mailto:contact@aqteron.com) for support, privacy requests and non-public security reports. [English installation guide](https://aqteron.com/cabinet/connections/claude?lang=en) · [Guide français](https://aqteron.com/cabinet/connections/claude?lang=fr).

## Распространение

Это установочный пакет для прямой загрузки. Публикация в каталоге Anthropic и проверка Anthropic не выполнены. `UNLICENSED`: публичная лицензия на распространение кода этим пакетом не предоставляется.
