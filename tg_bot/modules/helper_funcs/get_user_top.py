import tg_bot.modules.sql.top_users_sql as sql

def get_user_top():
    rows = sql.user_list_top()
    stripe = "➖" * 15
    count = 0
    result_list = []
    for row in rows[0:30]:
        last_name = row.name
        message = row.message
        count += 1
        result = f'{count} ✅ {last_name} ✉ = {message}\n{stripe}'
        result_list.append(result)
    
    return result_list