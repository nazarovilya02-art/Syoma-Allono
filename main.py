import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, date

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("800x600")
        
        # Список тренировок
        self.trainings = []
        self.data_file = "trainings.json"
        
        # Типы тренировок
        self.training_types = [
            "Кардио",
            "Силовая",
            "Растяжка",
            "Йога",
            "Пилатес",
            "Кроссфит",
            "Плавание",
            "Бег",
            "Велоспорт",
            "Функциональная",
            "Другое"
        ]
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        # Основной контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Фрейм для добавления тренировки
        add_frame = ttk.LabelFrame(main_container, text="Добавить тренировку", padding=10)
        add_frame.pack(fill="x", pady=(0, 10))
        
        # Поля ввода
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(fill="x")
        
        # Дата
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=(0, 20))
        # Устанавливаем текущую дату по умолчанию
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        # Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.type_combo = ttk.Combobox(input_frame, values=self.training_types, width=15, state="readonly")
        self.type_combo.grid(row=0, column=3, sticky="w", padx=(0, 20))
        self.type_combo.set(self.training_types[0])
        
        # Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w", padx=(0, 5))
        self.duration_entry = ttk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, sticky="w", padx=(0, 20))
        
        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить тренировку", 
                  command=self.add_training).grid(row=0, column=6, padx=(10, 0))
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(main_container, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        filter_input_frame = ttk.Frame(filter_frame)
        filter_input_frame.pack(fill="x")
        
        # Фильтр по типу
        ttk.Label(filter_input_frame, text="Тип тренировки:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.filter_type = ttk.Combobox(filter_input_frame, 
                                       values=["Все"] + self.training_types, 
                                       width=15, 
                                       state="readonly")
        self.filter_type.grid(row=0, column=1, sticky="w", padx=(0, 20))
        self.filter_type.set("Все")
        self.filter_type.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Фильтр по дате
        ttk.Label(filter_input_frame, text="Дата с:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.filter_date_from = ttk.Entry(filter_input_frame, width=15)
        self.filter_date_from.grid(row=0, column=3, sticky="w", padx=(0, 10))
        
        ttk.Label(filter_input_frame, text="по:").grid(row=0, column=4, sticky="w", padx=(0, 5))
        self.filter_date_to = ttk.Entry(filter_input_frame, width=15)
        self.filter_date_to.grid(row=0, column=5, sticky="w", padx=(0, 10))
        
        # Кнопки фильтрации
        ttk.Button(filter_input_frame, text="Применить фильтр", 
                  command=self.apply_filters).grid(row=0, column=6, padx=(0, 5))
        ttk.Button(filter_input_frame, text="Сбросить фильтры", 
                  command=self.reset_filters).grid(row=0, column=7)
        
        # Фрейм для таблицы тренировок
        table_frame = ttk.LabelFrame(main_container, text="Список тренировок", padding=10)
        table_frame.pack(fill="both", expand=True)
        
        # Создаем Treeview для отображения тренировок
        columns = ("id", "date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="№")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("type", width=200, anchor="center")
        self.tree.column("duration", width=150, anchor="center")
        
        # Добавляем скроллбар
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Удалить выбранную", 
                  command=self.delete_training).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Редактировать", 
                  command=self.edit_training).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Очистить всё", 
                  command=self.clear_all).pack(side="left", padx=(0, 10))
        
        # Статистика
        self.stats_label = ttk.Label(button_frame, text="")
        self.stats_label.pack(side="right")
        
        # Обновляем статистику
        self.update_stats()
        
    def validate_date(self, date_string):
        """Проверка корректности даты"""
        try:
            datetime.strptime(date_string, "%d.%m.%Y")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_string):
        """Проверка корректности длительности"""
        try:
            duration = float(duration_string)
            if duration <= 0:
                return False, "Длительность должна быть положительным числом!"
            return True, ""
        except ValueError:
            return False, "Длительность должна быть числом!"
    
    def add_training(self):
        """Добавление новой тренировки"""
        date_str = self.date_entry.get().strip()
        training_type = self.type_combo.get()
        duration_str = self.duration_entry.get().strip()
        
        # Валидация
        if not date_str:
            messagebox.showerror("Ошибка", "Введите дату тренировки!")
            return
            
        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте формат: ДД.ММ.ГГГГ")
            return
            
        if not duration_str:
            messagebox.showerror("Ошибка", "Введите длительность тренировки!")
            return
            
        is_valid, error_msg = self.validate_duration(duration_str)
        if not is_valid:
            messagebox.showerror("Ошибка", error_msg)
            return
        
        # Создаем запись о тренировке
        training = {
            "id": len(self.trainings) + 1,
            "date": date_str,
            "type": training_type,
            "duration": float(duration_str)
        }
        
        self.trainings.append(training)
        self.save_data()
        self.refresh_table()
        self.update_stats()
        
        messagebox.showinfo("Успех", f"Тренировка добавлена!\n{training_type}: {duration_str} минут")
        
    def edit_training(self):
        """Редактирование выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для редактирования!")
            return
        
        # Получаем данные выбранной тренировки
        values = self.tree.item(selected[0])['values']
        training_id = values[0]
        
        # Находим тренировку в списке
        training = next((t for t in self.trainings if t["id"] == training_id), None)
        if not training:
            return
        
        # Создаем окно редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактировать тренировку")
        edit_window.geometry("400x200")
        edit_window.resizable(False, False)
        
        # Делаем окно модальным
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Поля для редактирования
        frame = ttk.Frame(edit_window, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Дата:").grid(row=0, column=0, sticky="w", pady=5)
        date_entry = ttk.Entry(frame, width=20)
        date_entry.grid(row=0, column=1, pady=5)
        date_entry.insert(0, training["date"])
        
        ttk.Label(frame, text="Тип тренировки:").grid(row=1, column=0, sticky="w", pady=5)
        type_combo = ttk.Combobox(frame, values=self.training_types, width=18, state="readonly")
        type_combo.grid(row=1, column=1, pady=5)
        type_combo.set(training["type"])
        
        ttk.Label(frame, text="Длительность (мин):").grid(row=2, column=0, sticky="w", pady=5)
        duration_entry = ttk.Entry(frame, width=10)
        duration_entry.grid(row=2, column=1, sticky="w", pady=5)
        duration_entry.insert(0, str(training["duration"]))
        
        def save_changes():
            new_date = date_entry.get().strip()
            new_type = type_combo.get()
            new_duration = duration_entry.get().strip()
            
            # Валидация
            if not self.validate_date(new_date):
                messagebox.showerror("Ошибка", "Неверный формат даты!")
                return
            
            is_valid, error_msg = self.validate_duration(new_duration)
            if not is_valid:
                messagebox.showerror("Ошибка", error_msg)
                return
            
            # Обновляем данные
            training["date"] = new_date
            training["type"] = new_type
            training["duration"] = float(new_duration)
            
            self.save_data()
            self.refresh_table()
            self.update_stats()
            
            edit_window.destroy()
            messagebox.showinfo("Успех", "Тренировка обновлена!")
        
        ttk.Button(frame, text="Сохранить", command=save_changes).grid(row=3, column=0, columnspan=2, pady=20)
        
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную тренировку?"):
            values = self.tree.item(selected[0])['values']
            training_id = values[0]
            
            self.trainings = [t for t in self.trainings if t["id"] != training_id]
            
            # Обновляем ID
            for i, training in enumerate(self.trainings, 1):
                training["id"] = i
            
            self.save_data()
            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Успех", "Тренировка удалена!")
    
    def clear_all(self):
        """Очистка всех тренировок"""
        if not self.trainings:
            messagebox.showinfo("Информация", "Список тренировок пуст!")
            return
            
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить ВСЕ тренировки?\nЭто действие нельзя отменить!"):
            self.trainings = []
            self.save_data()
            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Успех", "Все тренировки удалены!")
    
    def apply_filters(self, event=None):
        """Применение фильтров к таблице"""
        filter_type = self.filter_type.get()
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()
        
        filtered_trainings = self.trainings.copy()
        
        # Фильтр по типу
        if filter_type != "Все":
            filtered_trainings = [t for t in filtered_trainings if t["type"] == filter_type]
        
        # Фильтр по дате с
        if date_from:
            if self.validate_date(date_from):
                date_from_obj = datetime.strptime(date_from, "%d.%m.%Y")
                filtered_trainings = [t for t in filtered_trainings 
                                    if datetime.strptime(t["date"], "%d.%m.%Y") >= date_from_obj]
            else:
                messagebox.showerror("Ошибка", "Неверный формат даты в поле 'Дата с'!")
                return
        
        # Фильтр по дате по
        if date_to:
            if self.validate_date(date_to):
                date_to_obj = datetime.strptime(date_to, "%d.%m.%Y")
                filtered_trainings = [t for t in filtered_trainings 
                                    if datetime.strptime(t["date"], "%d.%m.%Y") <= date_to_obj]
            else:
                messagebox.showerror("Ошибка", "Неверный формат даты в поле 'Дата по'!")
                return
        
        self.refresh_table(filtered_trainings)
        self.update_stats(filtered_trainings)
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_type.set("Все")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()
        self.update_stats()
    
    def refresh_table(self, trainings=None):
        """Обновление отображения таблицы"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if trainings is None:
            trainings = self.trainings
        
        # Заполняем таблицу
        for training in trainings:
            self.tree.insert("", "end", values=(
                training["id"],
                training["date"],
                training["type"],
                f"{training['duration']:.1f}"
            ))
    
    def update_stats(self, trainings=None):
        """Обновление статистики"""
        if trainings is None:
            trainings = self.trainings
        
        total_count = len(trainings)
        total_duration = sum(t["duration"] for t in trainings)
        avg_duration = total_duration / total_count if total_count > 0 else 0
        
        stats_text = f"Всего тренировок: {total_count} | Общая длительность: {total_duration:.0f} мин | Средняя: {avg_duration:.0f} мин"
        self.stats_label.config(text=stats_text)
    
    def save_data(self):
        """Сохранение данных в JSON"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        self.trainings = json.loads(content)
                    else:
                        self.trainings = []
                self.refresh_table()
                self.update_stats()
            except json.JSONDecodeError:
                # Если файл поврежден, начинаем с чистого списка
                self.trainings = []
                messagebox.showwarning("Предупреждение", "Файл данных поврежден. Начинаем с пустого списка.")
            except Exception as e:
                self.trainings = []
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
