from aiogram.filters.callback_data import CallbackData

class CustomCallBacksActions(CallbackData, prefix="query"):
    func_name: str
    action: str