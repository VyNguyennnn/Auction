from django import template
from website.models import messages
from bson import ObjectId
register = template.Library()

@register.filter("mongo_id")
def mongo_id(value):
    return str(value['_id'])

register.filter('mongo_id', mongo_id)

@register.filter("times")
def times(number):
    return range(number)
register.filter('times', times)


@register.filter("update_variable")
def update_variable(value):
    data = value
    return data
register.filter('update_variable', update_variable)

@register.filter("covert_time")
def covert_time(value):
    result = value.strftime("%H:%M")
    return result
register.filter('covert_time', covert_time)

@register.filter("incre_price")
def incre_price(value):
    bid_increment = 0
    current_price = value
    currency = 23000
    currency = float(currency)
    if (0.01 * currency) <= current_price or current_price <= (0.99 * currency):
        bid_increment = 0.05 * currency
    elif (0.1 * currency) <= current_price or current_price <= (4.99 * currency):
        bid_increment = 0.025 * currency
    elif (5.0 * currency) <= current_price or current_price <= (24.99 * currency):
        bid_increment = 0.5 * currency
    elif (25.00 * currency) <= current_price or current_price <= (99.99 * currency):
        bid_increment = 1.0 * currency
    elif (100.00 * currency) <= current_price or current_price <= (249.99 * currency):
        bid_increment = 2.50 * currency
    elif (250.00 * currency) <= current_price or current_price <= (499.99 * currency):
        bid_increment = 5.00 * currency
    elif (500.00 * currency) <= current_price or current_price <= (999.99 * currency):
        bid_increment = 10.00 * currency
    elif (1000.00 * currency) <= current_price or current_price <= (2499.99 * currency):
        bid_increment = 25.00 * currency
    elif (2500.00 * currency) <= current_price or current_price <= (4999.99 * currency):
        bid_increment = 50.00 * currency
    elif (5000.00 * currency) <= current_price:
        bid_increment = 100.00 * currency
    e = bid_increment + current_price
    print(e)
    return bid_increment + current_price
register.filter('incre_price', incre_price)

@register.filter("later_value")
def later_value(value):
    data = 'show'
    tong = 0
    index = ''
    ms = messages.objects(pk=ObjectId(value)).first()
    sender = ms.sender.id
    receiver = ms.receiver.id
    room_id = ms.chat_room
    time = ms.time
    ms1 = messages.objects(chat_room=room_id, sender=sender, receiver=receiver)
    convert_time = time.strftime("%Y-%m-%d %H:%M")
    for m in ms1:
        m_time = m.time
        convert_m_time = m_time.strftime("%Y-%m-%d %H:%M")
        print('--------------------------------')
        print('convert_m_time:' + str(convert_m_time))
        print('convert_time:' + str(convert_time))
        if convert_time == convert_m_time:
            tong = tong + 1
            if m.pk == ms.pk:
                index = tong
    if index < tong:
        data = 'hidden'
    print('tong: '+ str(tong))
    print('data: '+ data)
    return data
register.filter('later_value', later_value)