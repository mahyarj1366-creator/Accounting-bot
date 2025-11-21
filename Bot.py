import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
import json
import os
from datetime import datetime, timedelta

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORY, AMOUNT, DESCRIPTION = range(3)
DATA_FILE = "/app/financial_data.json"
BOT_TOKEN = os.getenv('BOT_TOKEN')

class PersonalAccountingBot:
    def __init__(self):
        self.load_data()
        self.financial_advice = {
            "income_less": [
                "🎯 فریلنسینگ در حوزه تخصص شما",
                "📝 تولید محتوا برای شبکه‌های اجتماعی", 
                "🛍 فروش محصولات دیجیتال",
                "👨‍🏫 تدریس آنلاین",
                "📊 ورود به بازار سرمایه با سرمایه کم",
                "🛠 ارائه خدمات تخصصی در پونیشا و جابینجا"
            ],
            "income_more": [
                "💰 صندوق‌های سرمایه‌گذاری با درآمد ثابت",
                "🏠 سرمایه‌گذاری در مسکن",
                "📈 خرید سهام شرکت‌های بزرگ",
                "🏦 سپرده‌گذاری بلندمدت", 
                "🎯 صندوق‌های طلا",
                "💸 سرمایه‌گذاری در ارزهای دیجیتال (با ریسک بالا)"
            ]
        }
    
    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {"users": {}}
        except:
            self.data = {"users": {}}
    
    def save_data(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_user_data(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.data["users"]:
            self.data["users"][user_id_str] = {"transactions": [], "balance": 0}
        return self.data["users"][user_id_str]
    
    def add_transaction(self, user_id, transaction_type, category, amount, description):
        user_data = self.get_user_data(user_id)
        transaction = {
            "id": len(user_data["transactions"]) + 1,
            "type": transaction_type,
            "category": category,
            "amount": amount,
            "description": description,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        user_data["transactions"].append(transaction)
        if transaction_type == "income":
            user_data["balance"] += amount
        else:
            user_data["balance"] -= amount
        self.save_data()
        return transaction

accounting_bot = PersonalAccountingBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_text = f"""👋 سلام {user.first_name}!
به ربات حسابدار شخصی خوش آمدید.

💡 **دستورات:**
/start - راهنما
/add_income - افزودن درآمد  
/add_expense - افزودن هزینه
/balance - نمایش موجودی
/report - گزارش مالی
/analysis - تحلیل مالی

📊 **ربات ۲۴ ساعته فعال**"""
    await update.message.reply_text(welcome_text)

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories_text = """📈 **دسته‌بندی درآمد:**
1: حقوق و دستمزد
2: فریلنس  
3: سود سهام
4: فروش سهام
5: اجاره ملک
6: هدیه
7: سود بانکی
8: سایر

عدد 1-8 را بفرستید:"""
    await update.message.reply_text(categories_text)
    context.user_data['transaction_type'] = 'income'
    return CATEGORY

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories_text = """📉 **دسته‌بندی هزینه:**
1: خوراک
2: حمل‌ونقل
3: مسکن
4: قسط وام
5: تفریح
6: سلامتی
7: خرید
8: آموزش
9: بیمه
10: ارتباطات  
11: سایر

عدد 1-11 را بفرستید:"""
    await update.message.reply_text(categories_text)
    context.user_data['transaction_type'] = 'expense'
    return CATEGORY

async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    category_mapping_income = {
        '1': 'حقوق و دستمزد', '2': 'فریلنس', '3': 'سود سهام',
        '4': 'فروش سهام', '5': 'اجاره ملک', '6': 'هدیه',
        '7': 'سود بانکی', '8': 'سایر درآمدها'
    }
    category_mapping_expense = {
        '1': 'خوراک', '2': 'حمل‌ونقل', '3': 'مسکن',
        '4': 'قسط وام', '5': 'تفریح', '6': 'سلامتی',
        '7': 'خرید', '8': 'آموزش', '9': 'بیمه',
        '10': 'ارتباطات', '11': 'سایر هزینه‌ها'
    }
    
    if context.user_data['transaction_type'] == 'income':
        if user_input in category_mapping_income:
            context.user_data['category'] = category_mapping_income[user_input]
            await update.message.reply_text('💰 **مبلغ را به تومان وارد کنید:**')
            return AMOUNT
        else:
            await update.message.reply_text('❌ عدد 1-8 را وارد کنید:')
            return CATEGORY
    else:
        if user_input in category_mapping_expense:
            context.user_data['category'] = category_mapping_expense[user_input]
            await update.message.reply_text('💰 **مبلغ را به تومان وارد کنید:**')
            return AMOUNT
        else:
            await update.message.reply_text('❌ عدد 1-11 را وارد کنید:')
            return CATEGORY

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount_text = update.message.text.replace(',', '').strip()
        amount = float(amount_text)
        if amount <= 0:
            await update.message.reply_text('❌ مبلغ باید بزرگتر از صفر باشد:')
            return AMOUNT
        context.user_data['amount'] = amount
        await update.message.reply_text('📝 **توضیح (اختیاری):**')
        return DESCRIPTION
    except:
        await update.message.reply_text('❌ عدد معتبر وارد کنید:')
        return AMOUNT

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    user_id = update.message.from_user.id
    try:
        transaction = accounting_bot.add_transaction(
            user_id,
            context.user_data['transaction_type'],
            context.user_data['category'],
            context.user_data['amount'],
            description
        )
        response_text = f"""✅ **تراکنش ثبت شد:**

📊 نوع: {'درآمد' if transaction['type'] == 'income' else 'هزینه'}  
🏷 دسته: {transaction['category']}
💰 مبلغ: {transaction['amount']:,} تومان
📝 توضیحات: {transaction['description']}
📅 تاریخ: {transaction['date']}"""
        await update.message.reply_text(response_text)
        return ConversationHandler.END
    except:
        await update.message.reply_text("❌ خطا در ثبت تراکنش")
        return ConversationHandler.END

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data = accounting_bot.get_user_data(user_id)
    total_income = sum(t['amount'] for t in user_data['transactions'] if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in user_data['transactions'] if t['type'] == 'expense')
    balance_text = f"""💼 **وضعیت مالی شما:**

💰 موجودی: {user_data['balance']:,} تومان
📈 کل درآمدها: {total_income:,} تومان  
📉 کل هزینه‌ها: {total_expense:,} تومان
🎯 تفاوت: {total_income - total_expense:,} تومان"""
    
    await update.message.reply_text(balance_text)

async def show_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data = accounting_bot.get_user_data(user_id)
    
    if not user_data['transactions']:
        await update.message.reply_text("📭 **هیچ تراکنشی ثبت نکرده‌اید.**")
        return
    
    total_income = sum(t['amount'] for t in user_data['transactions'] if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in user_data['transactions'] if t['type'] == 'expense')
    
    report_text = f"""📊 **گزارش مالی:**

💰 موجودی: {user_data['balance']:,} تومان
📈 درآمدها: {total_income:,} تومان
📉 هزینه‌ها: {total_expense:,} تومان  
🎯 مانده: {total_income - total_expense:,} تومان"""

    await update.message.reply_text(report_text)

async def financial_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data = accounting_bot.get_user_data(user_id)
    
    if not user_data['transactions']:
        await update.message.reply_text("📭 **هیچ تراکنشی برای تحلیل وجود ندارد.**")
        return
    
    total_income = sum(t['amount'] for t in user_data['transactions'] if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in user_data['transactions'] if t['type'] == 'expense')
    balance = total_income - total_expense
    
    if balance < 0:
        advice_type = "income_less"
        advice_text = "💡 **راه‌های افزایش درآمد:**\n"
        warning = f"\n⚠️ **هشدار:** هزینه‌های شما {abs(balance):,} تومان بیشتر از درآمدتان است!"
    else:
        advice_type = "income_more" 
        advice_text = "💡 **پیشنهادات سرمایه‌گذاری:**\n"
        warning = f"\n🎉 **تبریک!** شما {balance:,} تومان پس‌انداز دارید!"
    
    advice_list = accounting_bot.financial_advice[advice_type]
    for i, advice in enumerate(advice_list, 1):
        advice_text += f"{i}. {advice}\n"
    
    analysis_text = f"""🔍 **تحلیل مالی شما:**

📈 کل درآمد: {total_income:,} تومان
📉 کل هزینه: {total_expense:,} تومان
💰 مانده: {balance:,} تومان

{advice_text}{warning}"""
    
    await update.message.reply_text(analysis_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('❌ عملیات لغو شد.')
    return ConversationHandler.END

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found! Please set in Heroku Config Vars")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('add_income', add_income),
            CommandHandler('add_expense', add_expense)
        ],
        states={
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_category)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", show_balance))
    application.add_handler(CommandHandler("report", show_report))
    application.add_handler(CommandHandler("analysis", financial_analysis))
    application.add_handler(conv_handler)
    
    print("🤖 ربات شروع به کار کرد...")
    application.run_polling()

if __name__ == '__main__':
    main()
