# ChatManager — Telegram Group & Channel Management Bot

ChatManager is a Telegram bot designed for group and channel moderation, built with a
focus on clean architecture, scalability, and long-term maintainability.

The project is developed as a foundation for a full-featured management platform, combining:
 - a Telegram bot (real-time moderation),
 - a backend API (FastAPI, planned),
 - and a web control panel (React, planned).

## Status
**Active development (Alpha version)**

## Demo

A public demo bot will be available once the core feature set
and stability guarantees are in place.

## Key features

### Implemented

* Telegram group moderation:
  * bans, mutes, kicks, warnings
  * blacklist-based censorship
  * ai-based censorship (experimental)
  * anti-spam filtering

* Internationalization system (en, ru, ua)

### In progress / planned

* Web administration panel (React)
* Backend API (FastAPI)
* User, chat, and moderation analytics
* Post scheduling
* Extended i18n support

## Installation

```bash
git clone https://github.com/JackBacker-lab/chatmanager
cd chatmanager
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install .
```
Create a `.env` file based on `.env.example` and provide the required configuration values.

If you want to use experimental AI-based censorship features, install the optional extra:

```bash
pip install .[censor-ai]
```

## Running the bot
```bash
python -m telegram_bot
# Or
chatmanager-bot
```

## Project structure

```text
src/
  telegram_bot/
    __main__.py            # Entry point for `python -m telegram_bot`
    main.py                # Entry point used by chatmanager-bot script
    config.py              # Bot configuration loading
    .env.example

    handlers/              # Aiogram routers and update handlers
      common/
        bot_added.py
        commands/
          start.py         # /start
          help.py          # /help
      moderation/
        echo.py            # Main group message handler (antispam, censor, antiflood)
        commands/
          ban.py           # /ban, /unban
          mute.py          # /mute, /unmute
          kick.py          # /kick
          warn.py          # /warn, /warns, /warns_reset
          blacklist.py     # /blacklist_add, /blacklist_remove, /blacklist
          filters.py       # /censor_on/off, /antispam_on/off, /ai_censor_on/off, /filters
        filters/
          base.py
          flood.py
          spam.py
          censorship.py
          replacements.py
        guards/            # Access checks and context helpers
          permissions.py
          context.py
        registry.py        # Aggregate all routers

    services/              # Application services (DB, Telegram, external API)
      db/                  # High-level database helpers
        chat_settings_service.py
        users_service.py
        blacklist_service.py
        warns_service.py
        chat_service.py
        logging_service.py
      telegram/
        processor.py
        resolve_targets.py
        build_messages.py
        filters_summary.py
        display.py
        message_links.py
      api/
        post_service.py    # Integration hooks for backend API (disabled by default)

    repositories/          # Low-level DB access (aioSQLite)
      db.py                # Database initialize
      chat_settings.py
      blacklist.py
      users.py
      chats.py
      warn.py
      logs.py

    models/                # Pydantic and dataclass models
      filters.py           # FiltersConfig, FloodConfig, CensorshipConfig, etc.
      user.py              # UserDTO
      log.py               # Log DTO

    i18n/                  # Internationalization (en/ru/ua)
      locales/
        en.json
        ru.json
        ua.json
      loader.py            # I18n load and initialize
      translate.py         # Translate the i18n key into a localized string
      generate_keys.py     # Generate i18n typed keys
      keys.py              # Auto-generated i18n literal

    experiments/           # Non-production experiments
      censor_ai.py         # HF-based toxicity detector prototype
```

## License
MIT License