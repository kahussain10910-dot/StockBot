import yfinance as yf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
   
   from ta.momentum import RSIIndicator
   from ta.trend import MACD
   
   from telegram import Update
   from telegram.ext import (
       Application,
       CommandHandler,
       ContextTypes,
   )
   
   # توكن البوت
   TOKEN = "8879406260:AAEvsjQIYgKD-pQ3X8wdYglS9s4uH3eav7s"
   
   
   # /start
   async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
       await update.message.reply_text(
           "👋 أهلاً بك.\n\n"
           "استخدم الأمر:\n"
           "/stock NVDA\n"
           "/stock AAPL\n"
           "/stock TSLA"
       )
   
   
   # /stock
   async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
   
       if len(context.args) == 0:
           await update.message.reply_text(
               "اكتب رمز السهم مثل:\n/stock AAPL"
           )
           return
   
       symbol = context.args[0].upper()
   
       try:
   
           ticker = yf.Ticker(symbol)
   
           info = ticker.info
   
           name = info.get("longName", "غير معروف")
           sector = info.get("sector", "غير معروف")
           price = info.get("currentPrice", "غير متوفر")
   
           data = ticker.history(period="1mo")
   
           if data.empty:
               await update.message.reply_text("لا توجد بيانات لهذا السهم.")
               return
   
           # =====================
           # RSI
           # =====================
   
           rsi = RSIIndicator(
               close=data["Close"],
               window=14
           )
   
           data["RSI"] = rsi.rsi()
   
           last_rsi = round(
               data["RSI"].iloc[-1],
               2
           )
   
           # =====================
           # MACD
           # =====================
   
           macd = MACD(close=data["Close"])
   
           data["MACD"] = macd.macd()
           data["MACD_SIGNAL"] = macd.macd_signal()
   
           last_macd = round(
               data["MACD"].iloc[-1],
               2
           )
   
           last_signal = round(
               data["MACD_SIGNAL"].iloc[-1],
               2
           )
   
           # =====================
           # التوصية
           # =====================
   
           if last_rsi < 30 and last_macd > last_signal:
               signal = "🟢 شراء قوي"
               prediction = "📈 متوقع ارتفاع"
   
           elif last_rsi < 50 and last_macd > last_signal:
               signal = "🟢 شراء"
               prediction = "📈 احتمال ارتفاع"
   
           elif last_rsi > 70 and last_macd < last_signal:
               signal = "🔴 بيع قوي"
               prediction = "📉 متوقع انخفاض"
   
           elif last_rsi > 60 and last_macd < last_signal:
               signal = "🟠 بيع"
               prediction = "📉 احتمال نزول"
   
           else:
               signal = "🟡 انتظار"
               prediction = "➡️ السوق غير واضح"
   
           # =====================
           # رسم الشارت
           # =====================
   
           plt.figure(figsize=(8,4))
   
           plt.plot(
               data.index,
               data["Close"],
               linewidth=2
           )
   
           plt.title(f"{symbol} Stock Price")
   
           plt.xlabel("Date")
           plt.ylabel("Price")
   
           image = f"{symbol}.png"
   
           plt.savefig(image)
   
           plt.close()
   
           # =====================
           # الرسالة
           # =====================
   
           text = (
               f"📈 الشركة: {name}\n"
               f"🏢 القطاع: {sector}\n"
               f"💲 السعر الحالي: {price}\n\n"
               f"📊 RSI: {last_rsi}\n"
               f"📈 MACD: {last_macd}\n"
               f"📉 Signal: {last_signal}\n\n"
               f"📌 التوصية: {signal}\n"
               f"🔮 التوقع: {prediction}"
           )
   
           await update.message.reply_photo(
               photo=open(image, "rb"),
               caption=text
           )
   
       except Exception as e:
   
           await update.message.reply_text(
               f"حدث خطأ:\n{e}"
           )
   
   
   # تشغيل البوت
   
   app = Application.builder().token(TOKEN).build()
   
   app.add_handler(CommandHandler("start", start))
   app.add_handler(CommandHandler("stock", stock))
   
   print("Bot Started...")
   
   app.run_polling()