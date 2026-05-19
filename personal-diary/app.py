from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

DATA_FILE = 'entries.json'

# --- Задание 12: Функции работы с JSON ---

def load_entries():
    """Загружает записи из файла. Если файла нет, возвращает пустой список."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_entries(entries):
    """Сохраняет список записей в файл."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=4)

# Глобальная переменная для хранения записей в памяти (для удобства работы в рамках одного запуска)
# В реальном приложении лучше читать/писать каждый раз или использовать БД.
# Здесь мы будем синхронизировать память с файлом.
entries = load_entries()

# --- Задание 13: Главная страница ---
@app.route('/')
def index():
    # Сортируем записи по дате (новые сверху), если нужно
    sorted_entries = sorted(entries, key=lambda x: x['date'], reverse=True)
    return render_template('index.html', entries=sorted_entries)

# --- Задание 14: Просмотр записи ---
@app.route('/entry/<int:entry_id>')
def detail(entry_id):
    entry = next((e for e in entries if e['id'] == entry_id), None)
    if entry is None:
        return "Запись не найдена", 404
    return render_template('detail.html', entry=entry)

# --- Задание 15: Добавление записи ---
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if title and content:
            # Генерация ID
            if entries:
                new_id = max(e['id'] for e in entries) + 1
            else:
                new_id = 1
            
            new_entry = {
                "id": new_id,
                "title": title,
                "content": content,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            entries.append(new_entry)
            save_entries(entries)
            return redirect(url_for('index'))
            
    return render_template('add.html')

# --- Задание 16: Редактирование записи ---
@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit(entry_id):
    entry = next((e for e in entries if e['id'] == entry_id), None)
    
    if entry is None:
        return "Запись не найдена", 404
        
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if title and content:
            entry['title'] = title
            entry['content'] = content
            # Дату можно обновлять или оставлять старую. Обычно дату создания оставляют, 
            # но можно добавить поле date_updated. В задании не уточняется, оставим старую дату.
            save_entries(entries)
            return redirect(url_for('index'))
            
    return render_template('edit.html', entry=entry)

# --- Задание 17: Удаление записи ---
@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    global entries
    entries = [e for e in entries if e['id'] != entry_id]
    save_entries(entries)
    return redirect(url_for('index'))

# --- Задание 18: Поиск ---
@app.route('/search')
def search():
    q = request.args.get('q', '').lower()
    if q:
        filtered_entries = [e for e in entries if q in e['title'].lower()]
    else:
        filtered_entries = entries
    
    # Сортировка
    filtered_entries = sorted(filtered_entries, key=lambda x: x['date'], reverse=True)
    return render_template('index.html', entries=filtered_entries)

# --- Задание 19: Фильтр по неделе ---
@app.route('/filter/week')
def filter_week():
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    filtered_entries = []
    for e in entries:
        try:
            # Парсим дату записи. Формат: "YYYY-MM-DD HH:MM"
            entry_date = datetime.strptime(e['date'], "%Y-%m-%d %H:%M")
            if entry_date >= week_ago:
                filtered_entries.append(e)
        except ValueError:
            continue
            
    filtered_entries = sorted(filtered_entries, key=lambda x: x['date'], reverse=True)
    return render_template('index.html', entries=filtered_entries)

# --- Задание 20: Запуск ---
if __name__ == '__main__':
    app.run(debug=True)