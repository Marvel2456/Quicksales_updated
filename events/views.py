# from django.shortcuts import render, redirect
# import calendar
# from calendar import HTMLCalendar

# # Create your views here.

# def eventsManager(request, year, month):
#     month = month.capitalize()

#     month_number = list(calendar.month_name).index(month)
#     month_number = int(month_number)
#     cal = HTMLCalendar().formatmonth(year, month_number)
#     context = {
#         'year':year,
#         'month':month,
#         'cal':cal
#     }
#     return render(request, 'events/events.html', context)