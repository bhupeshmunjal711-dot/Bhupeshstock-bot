# Telegram Stock Alerter — Ready Version

Telegram Chat ID is prefilled as **7538903918**.

## 1. Create Telegram bot
Open Telegram and message **@BotFather**.
Use `/newbot`, create your bot, and copy the Bot Token.

Then create `.env` from `.env.example` and put the token there:

TELEGRAM_BOT_TOKEN=YOUR_TOKEN

Do NOT publish the token.

## 2. Start the bot
Open your new bot and send `/start`.

## 3. Run with Docker
docker compose up --build

Then open:
http://localhost:8080

Paste a product URL and click Add Product.

Supported domains:
- Amazon
- Flipkart
- Croma
- Reliance Digital
- JioMart

The checker runs every 5 minutes by default.

Important: retailer pages can change, use anti-bot systems, location/pincode stock, login requirements, or dynamic inventory. This starter checks the public product page and cannot guarantee every SKU/page.
