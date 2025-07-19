import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

class StudyTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Günlük Çalışma Takipçisi")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Veri dosyası
        self.data_file = "study_data.json"
        self.load_data()
        
        # Timer değişkenleri
        self.timer_running = False
        self.start_time = None
        self.elapsed_time = 0
        self.timer_thread = None
        
        # Saat thread'i
        self.clock_thread = None
        self.clock_running = True
        
        # Dersler
        self.subjects = ["Matematik", "Türkçe", "Fen", "Sosyal", "İngilizce", "Diğer"]
        
        self.setup_ui()
        self.update_display()
        
        # Saati başlat
        self.start_clock()
        
        # Gece yarısı kontrolü
        self.check_day_reset()
        
    def load_data(self):
        """Veri dosyasını yükle"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = {}
        else:
            self.data = {}
    
    def save_data(self):
        """Veriyi kaydet"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Hata", f"Veri kaydedilemedi: {e}")
    
    def get_today_key(self):
        """Bugünün tarih anahtarını döndür"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_today_data(self):
        """Bugünün verilerini getir"""
        today = self.get_today_key()
        if today not in self.data:
            self.data[today] = {
                "questions": {subject: {"correct": 0, "wrong": 0} for subject in self.subjects},
                "pages_read": 0,
                "notes_written": 0,
                "study_time": 0,
                "empty_day": True
            }
        return self.data[today]
    
    def start_clock(self):
        """Saati başlat"""
        self.clock_thread = threading.Thread(target=self.update_clock)
        self.clock_thread.daemon = True
        self.clock_thread.start()
    
    def update_clock(self):
        """Saati güncelle"""
        while self.clock_running:
            try:
                current_time = datetime.now()
                time_str = current_time.strftime("%H:%M:%S")
                date_str = current_time.strftime("%d.%m.%Y")
                day_str = current_time.strftime("%A")
                
                # Türkçe gün isimleri
                days_turkish = {
                    "Monday": "Pazartesi",
                    "Tuesday": "Salı", 
                    "Wednesday": "Çarşamba",
                    "Thursday": "Perşembe",
                    "Friday": "Cuma",
                    "Saturday": "Cumartesi",
                    "Sunday": "Pazar"
                }
                day_turkish = days_turkish.get(day_str, day_str)
                
                # Saati güncelle
                if hasattr(self, 'clock_label'):
                    self.clock_label.config(text=time_str)
                if hasattr(self, 'date_label'):
                    self.date_label.config(text=f"{date_str} - {day_turkish}")
                
                time.sleep(1)
            except:
                break
    
    def setup_ui(self):
        """Arayüzü oluştur"""
        # Ana başlık ve saat frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Sol taraf - başlık
        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(title_frame, text="📚 Günlük Çalışma Takipçisi", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=(10, 0))
        
        # Sağ taraf - saat ve tarih
        clock_frame = tk.Frame(header_frame, bg='#2c3e50')
        clock_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Saat
        self.clock_label = tk.Label(clock_frame, text="--:--:--", 
                                   font=('Arial', 18, 'bold'), fg='#3498db', bg='#2c3e50')
        self.clock_label.pack()
        
        # Tarih
        self.date_label = tk.Label(clock_frame, text="--.--.---- - ---", 
                                  font=('Arial', 10), fg='#95a5a6', bg='#2c3e50')
        self.date_label.pack()
        
        # Ana içerik frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sol panel - Veri girişi
        left_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Timer bölümü
        timer_frame = tk.LabelFrame(left_frame, text="⏱️ Çalışma Süresi", 
                                   font=('Arial', 12, 'bold'), bg='white')
        timer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Timer ve başlangıç saati frame
        timer_info_frame = tk.Frame(timer_frame, bg='white')
        timer_info_frame.pack(pady=5)
        
        # Sol taraf - timer
        timer_left = tk.Frame(timer_info_frame, bg='white')
        timer_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.timer_label = tk.Label(timer_left, text="00:00:00", 
                                   font=('Arial', 20, 'bold'), fg='#e74c3c', bg='white')
        self.timer_label.pack()
        
        # Sağ taraf - başlangıç saati
        timer_right = tk.Frame(timer_info_frame, bg='white')
        timer_right.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(timer_right, text="Başlangıç:", font=('Arial', 9), fg='#7f8c8d', bg='white').pack()
        self.start_time_label = tk.Label(timer_right, text="--:--", 
                                        font=('Arial', 12, 'bold'), fg='#27ae60', bg='white')
        self.start_time_label.pack()
        
        timer_btn_frame = tk.Frame(timer_frame, bg='white')
        timer_btn_frame.pack(pady=5)
        
        self.start_btn = tk.Button(timer_btn_frame, text="Başlat", 
                                  command=self.start_timer, bg='#27ae60', fg='white',
                                  font=('Arial', 10, 'bold'), width=8)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(timer_btn_frame, text="Durdur", 
                                 command=self.stop_timer, bg='#e74c3c', fg='white',
                                 font=('Arial', 10, 'bold'), width=8)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Soru çözme bölümü
        question_frame = tk.LabelFrame(left_frame, text="📝 Soru Çözme", 
                                      font=('Arial', 12, 'bold'), bg='white')
        question_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Ders seçimi
        tk.Label(question_frame, text="Ders:", font=('Arial', 10), bg='white').pack(anchor=tk.W, padx=5)
        self.subject_var = tk.StringVar(value=self.subjects[0])
        subject_combo = ttk.Combobox(question_frame, textvariable=self.subject_var, 
                                    values=self.subjects, state='readonly', width=20)
        subject_combo.pack(pady=5, padx=5)
        
        # Doğru-Yanlış girişi
        qa_frame = tk.Frame(question_frame, bg='white')
        qa_frame.pack(pady=10)
        
        tk.Label(qa_frame, text="Doğru:", font=('Arial', 10), bg='white').grid(row=0, column=0, padx=5)
        self.correct_var = tk.StringVar(value="0")
        correct_entry = tk.Entry(qa_frame, textvariable=self.correct_var, width=10)
        correct_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(qa_frame, text="Yanlış:", font=('Arial', 10), bg='white').grid(row=0, column=2, padx=5)
        self.wrong_var = tk.StringVar(value="0")
        wrong_entry = tk.Entry(qa_frame, textvariable=self.wrong_var, width=10)
        wrong_entry.grid(row=0, column=3, padx=5)
        
        tk.Button(question_frame, text="Soru Ekle", command=self.add_questions,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(pady=5)
        
        # Diğer aktiviteler
        other_frame = tk.LabelFrame(left_frame, text="📖 Diğer Aktiviteler", 
                                   font=('Arial', 12, 'bold'), bg='white')
        other_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Sayfa okuma
        page_frame = tk.Frame(other_frame, bg='white')
        page_frame.pack(pady=5)
        tk.Label(page_frame, text="Okunan Sayfa:", font=('Arial', 10), bg='white').pack(side=tk.LEFT)
        self.pages_var = tk.StringVar(value="0")
        pages_entry = tk.Entry(page_frame, textvariable=self.pages_var, width=10)
        pages_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(page_frame, text="Ekle", command=self.add_pages,
                 bg='#9b59b6', fg='white', font=('Arial', 8, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Not yazma
        notes_frame = tk.Frame(other_frame, bg='white')
        notes_frame.pack(pady=5)
        tk.Label(notes_frame, text="Yazılan Not:", font=('Arial', 10), bg='white').pack(side=tk.LEFT)
        self.notes_var = tk.StringVar(value="0")
        notes_entry = tk.Entry(notes_frame, textvariable=self.notes_var, width=10)
        notes_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(notes_frame, text="Ekle", command=self.add_notes,
                 bg='#f39c12', fg='white', font=('Arial', 8, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Sağ panel - İstatistikler
        right_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Günlük özet
        summary_frame = tk.LabelFrame(right_frame, text="📊 Günlük Özet", 
                                     font=('Arial', 12, 'bold'), bg='white')
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.summary_text = tk.Text(summary_frame, height=8, width=30, 
                                   font=('Arial', 10), bg='#f8f9fa')
        self.summary_text.pack(pady=10, padx=10)
        
        # Butonlar
        btn_frame = tk.Frame(right_frame, bg='white')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="📈 Grafikleri Göster", command=self.show_graphs,
                 bg='#1abc9c', fg='white', font=('Arial', 10, 'bold')).pack(fill=tk.X, pady=2)
        
        tk.Button(btn_frame, text="📅 Haftalık Rapor", command=self.weekly_report,
                 bg='#34495e', fg='white', font=('Arial', 10, 'bold')).pack(fill=tk.X, pady=2)
        
        tk.Button(btn_frame, text="🗑️ Bugünü Sıfırla", command=self.reset_today,
                 bg='#e67e22', fg='white', font=('Arial', 10, 'bold')).pack(fill=tk.X, pady=2)
    
    def start_timer(self):
        """Timer'ı başlat"""
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time()
            
            # Başlangıç saatini göster
            start_time_str = datetime.now().strftime("%H:%M")
            self.start_time_label.config(text=start_time_str)
            
            self.timer_thread = threading.Thread(target=self.update_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
    
    def stop_timer(self):
        """Timer'ı durdur"""
        if self.timer_running:
            self.timer_running = False
            if self.start_time:
                self.elapsed_time += time.time() - self.start_time
                today_data = self.get_today_data()
                today_data["study_time"] = self.elapsed_time
                today_data["empty_day"] = False
                self.save_data()
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.start_time_label.config(text="--:--")
    
    def update_timer(self):
        """Timer'ı güncelle"""
        while self.timer_running:
            if self.start_time:
                current_time = self.elapsed_time + (time.time() - self.start_time)
                hours = int(current_time // 3600)
                minutes = int((current_time % 3600) // 60)
                seconds = int(current_time % 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.timer_label.config(text=time_str)
            time.sleep(1)
    
    def add_questions(self):
        """Soru ekle"""
        try:
            subject = self.subject_var.get()
            correct = int(self.correct_var.get())
            wrong = int(self.wrong_var.get())
            
            if correct < 0 or wrong < 0:
                messagebox.showerror("Hata", "Negatif sayı girilemez!")
                return
            
            today_data = self.get_today_data()
            today_data["questions"][subject]["correct"] += correct
            today_data["questions"][subject]["wrong"] += wrong
            
            if correct > 0 or wrong > 0:
                today_data["empty_day"] = False
            
            self.save_data()
            self.update_display()
            
            # Girişleri sıfırla
            self.correct_var.set("0")
            self.wrong_var.set("0")
            
            messagebox.showinfo("Başarılı", f"{subject} dersine {correct} doğru, {wrong} yanlış eklendi!")
            
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayı girin!")
    
    def add_pages(self):
        """Sayfa ekle"""
        try:
            pages = int(self.pages_var.get())
            if pages < 0:
                messagebox.showerror("Hata", "Negatif sayı girilemez!")
                return
            
            today_data = self.get_today_data()
            today_data["pages_read"] += pages
            
            if pages > 0:
                today_data["empty_day"] = False
            
            self.save_data()
            self.update_display()
            self.pages_var.set("0")
            
            messagebox.showinfo("Başarılı", f"{pages} sayfa eklendi!")
            
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayı girin!")
    
    def add_notes(self):
        """Not ekle"""
        try:
            notes = int(self.notes_var.get())
            if notes < 0:
                messagebox.showerror("Hata", "Negatif sayı girilemez!")
                return
            
            today_data = self.get_today_data()
            today_data["notes_written"] += notes
            
            if notes > 0:
                today_data["empty_day"] = False
            
            self.save_data()
            self.update_display()
            self.notes_var.set("0")
            
            messagebox.showinfo("Başarılı", f"{notes} sayfa not eklendi!")
            
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayı girin!")
    
    def update_display(self):
        """Ekranı güncelle"""
        today_data = self.get_today_data()
        
        # Özet metni
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, f"📅 Bugün: {datetime.now().strftime('%d.%m.%Y')}\n\n")
        
        # Çalışma süresi
        study_time = today_data["study_time"]
        hours = int(study_time // 3600)
        minutes = int((study_time % 3600) // 60)
        self.summary_text.insert(tk.END, f"⏱️ Çalışma Süresi: {hours}s {minutes}d\n\n")
        
        # Sorular
        self.summary_text.insert(tk.END, "📝 Çözülen Sorular:\n")
        total_correct = 0
        total_wrong = 0
        for subject, data in today_data["questions"].items():
            correct = data["correct"]
            wrong = data["wrong"]
            total_correct += correct
            total_wrong += wrong
            if correct > 0 or wrong > 0:
                self.summary_text.insert(tk.END, f"  {subject}: {correct}D/{wrong}Y\n")
        
        self.summary_text.insert(tk.END, f"\nToplam: {total_correct}D/{total_wrong}Y\n\n")
        
        # Diğer aktiviteler
        self.summary_text.insert(tk.END, f"📖 Okunan Sayfa: {today_data['pages_read']}\n")
        self.summary_text.insert(tk.END, f"📝 Yazılan Not: {today_data['notes_written']} sayfa\n")
    
    def show_graphs(self):
        """Grafikleri göster"""
        if not self.data:
            messagebox.showinfo("Bilgi", "Henüz veri yok!")
            return
        
        # Grafik penceresi
        graph_window = tk.Toplevel(self.root)
        graph_window.title("📈 Grafikler")
        graph_window.geometry("800x600")
        
        # Notebook (sekmeler)
        notebook = ttk.Notebook(graph_window)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Doğru/Yanlış grafikleri
        self.create_question_graphs(notebook)
        
        # Günlük aktivite grafiği
        self.create_daily_activity_graph(notebook)
    
    def create_question_graphs(self, notebook):
        """Soru grafiklerini oluştur"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Soru Grafikleri")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Dersler Bazında Soru Çözme İstatistikleri', fontsize=16)
        
        for i, subject in enumerate(self.subjects):
            row = i // 3
            col = i % 3
            ax = axes[row, col]
            
            # Veri toplama
            dates = []
            correct_counts = []
            wrong_counts = []
            
            for date, data in sorted(self.data.items()):
                dates.append(date)
                correct_counts.append(data["questions"][subject]["correct"])
                wrong_counts.append(data["questions"][subject]["wrong"])
            
            # Grafik çizme
            if dates:
                ax.bar(dates, correct_counts, label='Doğru', color='green', alpha=0.7)
                ax.bar(dates, wrong_counts, bottom=correct_counts, label='Yanlış', color='red', alpha=0.7)
                ax.set_title(subject)
                ax.set_xlabel('Tarih')
                ax.set_ylabel('Soru Sayısı')
                ax.legend()
                ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_daily_activity_graph(self, notebook):
        """Günlük aktivite grafiği"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Günlük Aktivite")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        dates = []
        study_times = []
        pages_read = []
        notes_written = []
        
        for date, data in sorted(self.data.items()):
            dates.append(date)
            study_times.append(data["study_time"] / 3600)  # Saate çevir
            pages_read.append(data["pages_read"])
            notes_written.append(data["notes_written"])
        
        if dates:
            ax.plot(dates, study_times, marker='o', label='Çalışma Süresi (saat)', color='blue')
            ax.plot(dates, pages_read, marker='s', label='Okunan Sayfa', color='green')
            ax.plot(dates, notes_written, marker='^', label='Yazılan Not', color='orange')
            
            ax.set_title('Günlük Aktivite Grafiği')
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Miktar')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkinter(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def weekly_report(self):
        """Haftalık rapor"""
        if not self.data:
            messagebox.showinfo("Bilgi", "Henüz veri yok!")
            return
        
        # Son 7 günün verilerini al
        today = datetime.now()
        week_dates = []
        for i in range(7):
            date = today - timedelta(days=i)
            week_dates.append(date.strftime("%Y-%m-%d"))
        
        empty_days = 0
        total_questions = 0
        total_pages = 0
        total_notes = 0
        total_study_time = 0
        
        for date in week_dates:
            if date in self.data:
                data = self.data[date]
                if data["empty_day"]:
                    empty_days += 1
                
                # Toplam soruları hesapla
                for subject_data in data["questions"].values():
                    total_questions += subject_data["correct"] + subject_data["wrong"]
                
                total_pages += data["pages_read"]
                total_notes += data["notes_written"]
                total_study_time += data["study_time"]
            else:
                empty_days += 1
        
        # Rapor penceresi
        report_window = tk.Toplevel(self.root)
        report_window.title("📅 Haftalık Rapor")
        report_window.geometry("400x300")
        
        report_text = tk.Text(report_window, font=('Arial', 11), padx=20, pady=20)
        report_text.pack(fill=tk.BOTH, expand=True)
        
        # Rapor içeriği
        report_content = f"""📅 HAFTALİK RAPOR
{datetime.now().strftime('%d.%m.%Y')} - Son 7 Gün

🚫 Boş Geçen Gün: {empty_days} gün
📝 Toplam Çözülen Soru: {total_questions}
📖 Toplam Okunan Sayfa: {total_pages}
✍️ Toplam Yazılan Not: {total_notes} sayfa
⏱️ Toplam Çalışma Süresi: {int(total_study_time//3600)}s {int((total_study_time%3600)//60)}d

📊 Günlük Ortalamalar:
• Soru: {total_questions/7:.1f}
• Sayfa: {total_pages/7:.1f}
• Not: {total_notes/7:.1f}
• Çalışma: {total_study_time/7/3600:.1f} saat

💡 Öneriler:
{"• Harika! Böyle devam et! 🌟" if empty_days <= 1 else "• Daha düzenli çalışmaya odaklan! 💪"}
{"• Çok aktif bir haftaydı! 🎉" if total_questions > 50 else "• Soru çözmeyi artırabilirsin! 📚"}
"""
        
        report_text.insert(tk.END, report_content)
        report_text.config(state=tk.DISABLED)
    
    def reset_today(self):
        """Bugünü sıfırla"""
        if messagebox.askyesno("Onay", "Bugünkü tüm verileri silmek istediğinizden emin misiniz?"):
            today = self.get_today_key()
            if today in self.data:
                del self.data[today]
                self.save_data()
                self.elapsed_time = 0
                self.stop_timer()
                self.update_display()
                messagebox.showinfo("Başarılı", "Bugünkü veriler silindi!")
    
    def check_day_reset(self):
        """Gün değişikliği kontrolü"""
        # Her dakika kontrol et
        self.root.after(60000, self.check_day_reset)
        
        # Eğer gece yarısı geçtiyse timer'ı sıfırla
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            self.stop_timer()
            self.elapsed_time = 0
            self.update_display()
    
    def __del__(self):
        """Uygulama kapanırken saat thread'ini durdur"""
        self.clock_running = False

def main():
    root = tk.Tk()
    app = StudyTrackerApp(root)
    
    # Uygulama kapanırken saat thread'ini durdur
    def on_closing():
        app.clock_running = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()