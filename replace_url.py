with open('templates/base.html', 'r', encoding='utf-8') as file:
    content = file.read()
content = content.replace('finance:transaction_list', 'finance:expense_list')
with open('templates/base.html', 'w', encoding='utf-8') as file:
    file.write(content)
print('Replacement completed') 